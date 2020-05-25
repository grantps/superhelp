from collections import namedtuple
import logging

from . import ast_funcs, conf, helpers
from .gen_utils import (get_docstring_start, get_tree,
    layout_comment as layout, xml_from_tree)

BlockDets = namedtuple(
    'BlockDets', 'element, pre_block_code_str, block_code_str, first_line_no')
BlockDets.pre_block_code_str.__doc__ = ("The code up until the line we are "
    "interested in needs to be run - it may depend on names from earlier")

MessageDets = namedtuple('MessageDets',
    'code_str, message, first_line_no, warning, source')
MessageDets.__doc__ += (
    "All the bits and pieces that might be needed to craft a message")
MessageDets.code_str.__doc__ = ("The block of code the message relates to")
MessageDets.source.__doc__ = ("A unique identifier of the source of message "
    "- useful for auditing / testing")

def get_blocks_dets(snippet, snippet_block_els):
    """
    Returning a list of all the details needed to process a line
    (namely BlockDets named tuples)

    Note - lines in the XML sit immediately under body.

    :return: list of BlockDets named tuples
    :rtype: list
    """
    snippet_lines = snippet.split('\n')
    blocks_dets = []
    for snippet_block_el in snippet_block_els:
        first_line_no, last_line_no, _el_lines_n = ast_funcs.get_el_lines_dets(
            snippet_block_el)
        block_code_str = (
            '\n'.join(snippet_lines[first_line_no - 1: last_line_no]).strip())
        pre_block_code_str = (
            '\n'.join(snippet_lines[0: first_line_no - 1]).strip()
            + '\n')
        blocks_dets.append(BlockDets(
            snippet_block_el, pre_block_code_str, block_code_str, first_line_no))
    return blocks_dets

def complete_message(message, *, source):
    """
    Ensure a complete message with all levels is available.

    :param dict message: a dict with as many as three levels
     e.g. conf.BRIEF, MAIN, EXTRA.
    :param str source: usually helper name but might be the system sending the
     message e.g. if no advice given or a bug happened.
    :return: fixed version of original dict with all levels populated
    :rtype: dict
    """
    try:
        message_keys = message.keys()
    except TypeError:
        raise TypeError(f"message had no keys - message: {message} "
            f"(type {type(message).__name__})")
    if conf.BRIEF not in message_keys:
        raise Exception(f"'{source}' gave a message lacking the mandatory "
            f"'{conf.BRIEF}' level")
    if conf.MAIN not in message_keys:
        message[conf.MAIN] = message[conf.BRIEF]
    if conf.EXTRA not in message_keys:
        message[conf.EXTRA] = ''
    return message

def get_message_dets_from_input(helper_dets, *,
        helper_input, code_str, first_line_no, execute_code=True, repeat=False):
    """
    :param namedtuple helper_dets: details of the helper e.g. name, function,
     etc depending on type of HelperDets (e.g. FiltHelperDets)
    :param obj helper_input: the main input to the helper function
     e.g. block_dets, blocks_dets, or snippet_str.
    """
    name = helper_dets.helper_name
    docstring = helper_dets.helper.__doc__
    if not docstring:
        raise Exception(f'Helper "{name}" lacks a docstring - add one!')
    try:
        message = helper_dets.helper(
            helper_input, execute_code=execute_code, repeat=repeat)
    except Exception as e:
        brief_name = '.'.join(name.split('.')[-2:])  ## last two parts only
        message = {
            conf.BRIEF: (
                layout(f"""\
                    ### Helper "`{brief_name}`" unable to run

                    Helper {brief_name} unable to run. Helper description:
                    """)
                +  ## show first line of docstring (subsequent lines might have more technical, internally-oriented comments)
                layout(get_docstring_start(docstring) + '\n')
                +
                layout(str(e))
            )
        }
        source = conf.SYSTEM_MESSAGE
        warning = True
    else:
        source = name
        warning = helper_dets.warning
        if message is None:
            return None
    message = complete_message(message, source=source)
    message_dets = MessageDets(
        code_str, message, first_line_no, warning, source=source)
    return message_dets

def _get_ancestor_block_element(element):
    """
    The item immediately under body that this element is under.
    """
    ancestor_elements = element.xpath('ancestor-or-self::*')
    ancestor_block_element = ancestor_elements[2]  ## [0] will be Module, 1 is body, and blocks are the children of body
    return ancestor_block_element

def _get_filtered_blocks_dets(helper_dets, xml, blocks_dets):
    """
    Identify source block elements according to xpath supplied. Then filter
    blocks_dets accordingly.

    :return: filtered_blocks_dets
    :rtype: list
    """
    matching_elements = xml.xpath(helper_dets.xpath)
    if matching_elements:
        logging.debug(f"{helper_dets.helper_name} had at least one match")
    else:
        logging.debug(f"{helper_dets.helper_name} had no matches")
    filt_block_elements = set(
        [_get_ancestor_block_element(element) for element in matching_elements])
    filtered_blocks_dets = [block_dets for block_dets in blocks_dets
        if block_dets.element in filt_block_elements]
    if filtered_blocks_dets:
        logging.debug(f"{helper_dets.helper_name} had at least one block")
    else:
        logging.debug(f"{helper_dets.helper_name} had no blocks")
    return filtered_blocks_dets

def get_block_level_messages_dets(blocks_dets, xml, *,
        warnings_only=False, execute_code=True, repeat_set=None):
    """
    For each helper, get advice on every relevant block. Element type specific
    helpers process filtered blocks_dets; all block helpers process all blocks
    (as you'd expect ;-)).

    As we iterate through the blocks, only the first block under an helper
    should get the full message.
    """
    messages_dets = []
    all_helpers_dets = helpers.FILT_BLOCK_HELPERS + helpers.ANY_BLOCK_HELPERS
    for helper_dets in all_helpers_dets:
        logging.debug(f"About to process '{helper_dets.helper_name}'")
        if warnings_only and not helper_dets.warning:
            continue
        element_filtering = hasattr(helper_dets, 'xpath')
        if element_filtering:
            filtered_blocks_dets = _get_filtered_blocks_dets(
                helper_dets, xml, blocks_dets)
            blocks_dets2use = filtered_blocks_dets
            logging.debug(
                f"'{helper_dets.helper_name}' has element filtering for "
                f"{len(blocks_dets2use)} matching blocks")
        else:  ## no filtering by element type so process all blocks
            blocks_dets2use = blocks_dets
        for block_dets in blocks_dets2use:
            repeat = (helper_dets.helper_name in repeat_set)
            message_dets = get_message_dets_from_input(helper_dets,
                helper_input=block_dets, code_str=block_dets.block_code_str,
                first_line_no=block_dets.first_line_no,
                execute_code=execute_code, repeat=repeat)
            if message_dets:
                repeat_set.add(helper_dets.helper_name)
                messages_dets.append(message_dets)
    return messages_dets

def get_overall_snippet_messages_dets(snippet, blocks_dets, *,
        warnings_only=False, execute_code=True, repeat_set=None):
    """
    Returns messages which apply to snippet as a whole, not just specific
    blocks. E.g. looking at every block to look for opportunities to unpack. Or
    reporting on linting results.
    """
    messages_dets = []
    all_helpers_dets = (
        helpers.ALL_BLOCKS_HELPERS + helpers.SNIPPET_STR_HELPERS)
    for helper_dets in all_helpers_dets:
        logging.debug(f"About to process '{helper_dets.helper_name}'")
        if warnings_only and not helper_dets.warning:
            continue
        if helper_dets.input_type == conf.BLOCKS_DETS:
            helper_input = blocks_dets
        elif helper_dets.input_type == conf.SNIPPET_STR:
            helper_input = snippet
        else:
            raise Exception(
                f"Unexpected input_type: '{helper_dets.input_type}'")
        repeat = (helper_dets.helper_name in repeat_set)
        message_dets = get_message_dets_from_input(helper_dets,
            helper_input=helper_input, code_str=snippet, first_line_no=None,
            execute_code=execute_code, repeat=repeat)
        if message_dets:
            repeat_set.add(helper_dets.helper_name)
            messages_dets.append(message_dets)
    return messages_dets

def get_separated_messages_dets(snippet, snippet_block_els, xml, *,
        warnings_only=False, execute_code=True, repeat_set=None):
    """
    Break snippet up into syntactical parts and blocks of code. Apply helper
    functions and get message details. Split into overall messages and block-
    specific messages.

    :param str snippet: code snippet
    :param list snippet_block_els: list of block elements for snippet
    :param xml xml: snippet code as xml object
    :param bool warnings_only: if True, warnings only
    :param bool execute_code: if False, do not execute any code and rely
     exclusively on AST inspection
    :param set repeat_set: we need to track if a help message is a repeat
     especially across multiple scripts being processed.
    :return: a tuple of two MessageDets lists
     (overall_snippet_messages_dets, block_level_messages_dets)
     or None if no messages
    :rtype: tuple (or None)
    """
    blocks_dets = get_blocks_dets(snippet, snippet_block_els)
    overall_snippet_messages_dets = get_overall_snippet_messages_dets(
        snippet, blocks_dets,
        warnings_only=warnings_only, execute_code=execute_code,
        repeat_set=repeat_set)
    block_level_messages_dets = get_block_level_messages_dets(
        blocks_dets, xml,
        warnings_only=warnings_only, execute_code=execute_code,
        repeat_set=repeat_set)
    for messages_dets in [
            overall_snippet_messages_dets, block_level_messages_dets]:
        if None in messages_dets:
            raise Exception("messages_dets in meant to be a list of "
                "MessageDets named tuples yet a None item was found")
    if not (overall_snippet_messages_dets or block_level_messages_dets):
        message = {
            conf.BRIEF: conf.NO_ADVICE_MESSAGE,
        }
        message = complete_message(message, source=conf.SYSTEM_MESSAGE)
        overall_snippet_messages_dets = [
            MessageDets(snippet, message,
                first_line_no=None, warning=False, source=conf.SYSTEM_MESSAGE)]
    return overall_snippet_messages_dets, block_level_messages_dets

def get_snippet_dets(snippet, *,
        warnings_only=False, execute_code=True, repeat_set=None):
    """
    Get details for snippet of code.

    :return: snippet_messages_dets
     (overall_snippet_messages_dets, block_level_messages_dets),
     multi_block_snippet (bool)
    :rtype: tuple
    """
    tree = get_tree(snippet)
    xml = xml_from_tree(tree)
    if conf.RECORD_AST:
        ast_funcs.store_ast_output(xml)
    snippet_block_els = xml.xpath('body')[0].getchildren()  ## [0] because there is only one body under root
    multi_block_snippet = len(snippet_block_els) > 1
    snippet_messages_dets = get_separated_messages_dets(
        snippet, snippet_block_els, xml,
        warnings_only=warnings_only, execute_code=execute_code,
        repeat_set=repeat_set)
    return snippet_messages_dets, multi_block_snippet

def get_system_messages_dets(snippet, brief_message, *, warning=True):
    """
    Even though only one message is needed, supplying the details in the
    standard format the displayers expect means they can operate in their usual
    messages_dets consuming ways :-).
    """
    message = {
        conf.BRIEF: brief_message,
    }
    message = complete_message(message, source=conf.SYSTEM_MESSAGE)
    overall_messages_dets = [
        MessageDets(snippet, message,
            first_line_no=None, warning=warning, source=conf.SYSTEM_MESSAGE)]
    block_messages_dets = []
    messages_dets = (overall_messages_dets, block_messages_dets)
    return messages_dets

def get_error_messages_dets(e, snippet):
    """
    If unable to produce any messages, supply the problem in the form of
    standard messages_dets so the displayers can operate in their usual
    messages_dets consuming ways :-).
    """
    brief_message = layout(f"""\
        ### No advice sorry :-(

        Unable to provide advice - some sort of problem.

        Details: {e}
        """)
    return get_system_messages_dets(snippet, brief_message)

def get_community_message(snippet):
    brief_message = layout("""\

        ### Join in!

        Python has always had a great community. Learn more at
        <https://www.python.org/community/>. Better still - get involved :-)

        """)
    return get_system_messages_dets(snippet, brief_message)

def get_xkcd_warning(snippet):
    brief_message = layout("""\

        ### According to XKCD this code could be *very* dangerous

        See <https://xkcd.com/2261/>

        """)
    return get_system_messages_dets(snippet, brief_message)
