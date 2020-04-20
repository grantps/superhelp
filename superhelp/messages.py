import ast
from collections import namedtuple
import logging

import astpath  # @UnresolvedImport

## importing from superhelp only works properly after I've installed superhelp as a pip package (albeit as a link to this code using python3 -m pip install --user -e <path_to_proj_folder>)
## Using this as a library etc works with . instead of superhelp but I want to be be able to run the helper module from within my IDE
from superhelp import advisors, ast_funcs, conf  # @UnresolvedImport
from superhelp.utils import layout_comment  # @UnresolvedImport

BlockDets = namedtuple(
    'BlockDets', 'element, pre_block_code_str, block_code_str, first_line_no')
BlockDets.pre_block_code_str.__doc__ = ("The code up until the line we are "
    "interested in needs to be run - it may depend on names from earlier")

MessageDets = namedtuple('MessageDets',
    'code_str, message, first_line_no, warning, source')
MessageDets.__doc__ += (
    "All the bits and pieces that might be needed to craft a message")
MessageDets.source.__doc__ = ("A unique identifier of the source of message "
    "- useful for auditing / testing")

def get_tree(snippet):
    try:
        tree = ast.parse(snippet)
    except SyntaxError as e:
        raise SyntaxError(
            f"Oops - something seems broken in the snippet - details: {e}")
    return tree

def get_blocks_dets(xml, snippet_lines):
    """
    Returning a list of all the details needed to process a line
    (namely BlockDets named tuples)

    Note - lines in the XML sit immediately under body.

    :return: list of BlockDets named tuples
    :rtype: list
    """
    blocks_dets = []
    all_elements = xml.xpath('body')[0].getchildren()  ## [0] because there is only one body under root
    for element in all_elements:
        line_nos = ast_funcs.get_xml_element_line_no_range(element)
        first_line_no, last_line_no = line_nos
        block_code_str = (
            '\n'.join(snippet_lines[first_line_no - 1: last_line_no]).strip())
        pre_block_code_str = (
            '\n'.join(snippet_lines[0: first_line_no - 1]).strip()
            + '\n')
        blocks_dets.append(BlockDets(
            element, pre_block_code_str, block_code_str, first_line_no))
    return blocks_dets

def complete_message(message, *, source):
    """
    Ensure a complete message with all levels is available.

    :param dict message: a dict with as many as three levels
     e.g. conf.BRIEF, MAIN, EXTRA.
    :param str source: usually advisor name but might be the system sending the
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

def get_message_dets_from_input(advisor_dets, *,
        advisor_input, code_str, first_line_no, repeated_message):
    name = advisor_dets.advisor_name
    docstring = advisor_dets.advisor.__doc__
    if not docstring:
        raise Exception(f'Advisor "{name}" lacks a docstring - add one!')
    try:
        try:
            message = advisor_dets.advisor(advisor_input,
                repeated_message=repeated_message)
        except TypeError as e:
            if "unexpected keyword argument 'repeated_message'" in str(e):
                message = advisor_dets.advisor(advisor_input)
            else:
                raise
    except Exception as e:
        message = {
            conf.BRIEF: (
                layout_comment(f"""\
                    #### Advisor "`{name}`" unable to run

                    Advisor {name} unable to run. Advisor description:
                    """)
                +  ## show first line of docstring (subsequent lines might have more technical, internally-oriented comments)
                layout_comment(docstring.lstrip('\n').split('\n\n')[0] + '\n')
                +
                layout_comment(str(e))
            )
        }
        warning = True
    else:
        warning = advisor_dets.warning
        if message is None:
            return None
    message = complete_message(message, source=advisor_dets.advisor_name)
    message_dets = MessageDets(
        code_str, message, first_line_no, warning, source=name)
    return message_dets

def _get_ancestor_block_element(element):
    """
    The item immediately under body that this element is under.
    """
    ancestor_elements = element.xpath('ancestor-or-self::*')
    ancestor_block_element = ancestor_elements[2]  ## [0] will be Module, 1 is body, and blocks are the children of body
    return ancestor_block_element

def _get_filtered_blocks_dets(advisor_dets, xml, blocks_dets):
    """
    Identify source block elements according to xpath supplied. Then filter
    blocks_dets accordingly.

    :return: filtered_blocks_dets
    :rtype: list
    """
    matching_elements = xml.xpath(advisor_dets.xpath)
    if matching_elements:
        logging.debug(f"{advisor_dets.advisor_name} had at least one match")
    else:
        logging.debug(f"{advisor_dets.advisor_name} had no matches")
    filt_block_elements = set(
        [_get_ancestor_block_element(element) for element in matching_elements])
    filtered_blocks_dets = [block_dets for block_dets in blocks_dets
        if block_dets.element in filt_block_elements]
    if filtered_blocks_dets:
        logging.debug(f"{advisor_dets.advisor_name} had at least one block")
    else:
        logging.debug(f"{advisor_dets.advisor_name} had no blocks")
    return filtered_blocks_dets

def get_block_level_messages_dets(blocks_dets, xml):
    """
    For each advisor, get advice on every relevant block. Element type specific
    advisors process filtered blocks_dets; all block advisors process all blocks
    (as you'd expect ;-)).

    As we iterate through the blocks, only the first block under an advisor
    should get the full message.
    """
    messages_dets = []
    all_advisors_dets = (
        advisors.FILT_BLOCK_ADVISORS + advisors.ANY_BLOCK_ADVISORS)
    for advisor_dets in all_advisors_dets:
        logging.debug(f"About to process '{advisor_dets.advisor_name}'")
        element_filtering = hasattr(advisor_dets, 'xpath')
        if element_filtering:
            filtered_blocks_dets = _get_filtered_blocks_dets(
                advisor_dets, xml, blocks_dets)
            blocks_dets2use = filtered_blocks_dets
            logging.debug(
                f"'{advisor_dets.advisor_name}' has element filtering for "
                f"{len(blocks_dets2use)} matching blocks")
        else:  ## no filtering by element type so process all blocks
            blocks_dets2use = blocks_dets
        repeated_message = False
        for block_dets in blocks_dets2use:
            message_dets = get_message_dets_from_input(advisor_dets,
                advisor_input=block_dets, code_str=block_dets.block_code_str,
                first_line_no=block_dets.first_line_no,
                repeated_message=repeated_message)
            if message_dets:
                messages_dets.append(message_dets)
                repeated_message = True
    return messages_dets

def get_overall_snippet_messages_dets(snippet, blocks_dets):
    """
    Returns messages which apply to snippet as a whole, not just specific
    blocks. E.g. looking at every block to look for opportunities to unpack.
    """
    messages_dets = []
    for advisor_dets in advisors.SNIPPET_ADVISORS:
        message_dets = get_message_dets_from_input(advisor_dets,
            advisor_input=blocks_dets, code_str=snippet, first_line_no=None,
            repeated_message=False)
        if message_dets:
            messages_dets.append(message_dets)
    return messages_dets

def get_separated_messages_dets(snippet):
    """
    Break snippet up into syntactical parts and blocks of code. Apply advisor
    functions and get message details. Split into overall messages and block-
    specific messages.

    :param str snippet: code snippet
    :return: a tuple of two MessageDets lists
     (overall_snippet_messages_dets, block_level_messages_dets)
     or None if no messages
    :rtype: tuple (or None)
    """
    tree = get_tree(snippet)
    xml = astpath.asts.convert_to_xml(tree)
    if conf.DEV_MODE:
        xml.getroottree().write(str(conf.AST_OUTPUT_XML), pretty_print=True)
    snippet_lines = snippet.split('\n')
    blocks_dets = get_blocks_dets(xml, snippet_lines)
    overall_snippet_messages_dets = get_overall_snippet_messages_dets(
        snippet, blocks_dets)
    block_level_messages_dets = get_block_level_messages_dets(blocks_dets, xml)
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

def get_error_messages_dets(e, snippet):
    """
    If unable to produce any messages, supply the problem in the form of
    standard messages_dets so the displayers can operate in their usual
    messages_dets consuming ways :-).
    """
    message = {
        conf.BRIEF: layout_comment(f"""\
            #### No advice sorry :-(

            Unable to provide advice - some sort of problem.

            Details: {e}
            """),
    }
    message = complete_message(message, source=conf.SYSTEM_MESSAGE)
    overall_messages_dets = [
        MessageDets(snippet, message,
            first_line_no=None, warning=True, source=conf.SYSTEM_MESSAGE)]
    block_messages_dets = []
    messages_dets = (overall_messages_dets, block_messages_dets)
    return messages_dets