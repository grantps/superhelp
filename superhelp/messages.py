import ast
from collections import namedtuple
from functools import partial
import logging

from lxml import etree
import astpath  # @UnresolvedImport

from astpath.asts import _set_encoded_literal, _strip_docstring

## Monkey-patch as at astpath Python 3.8 as at 2020-04-26
## Need to be able to tell val = 1 from val = '1' (that little detail ;-))
def convert_to_xml(node, omit_docstrings=False, node_mappings=None):
    """Convert supplied AST node to XML."""
    possible_docstring = isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module))

    xml_node = etree.Element(node.__class__.__name__)
    for attr in ('lineno', 'col_offset'):
        value = getattr(node, attr, None)
        if value is not None:
            _set_encoded_literal(
                partial(xml_node.set, attr),
                value
            )
    if node_mappings is not None:
        node_mappings[xml_node] = node

    node_fields = zip(
        node._fields,
        (getattr(node, attr) for attr in node._fields)
    )

    for field_name, field_value in node_fields:
        if isinstance(field_value, ast.AST):
            field = etree.SubElement(xml_node, field_name)
            field.append(
                convert_to_xml(
                    field_value,
                    omit_docstrings,
                    node_mappings,
                )
            )

        elif isinstance(field_value, list):
            field = etree.SubElement(xml_node, field_name)
            if possible_docstring and omit_docstrings and field_name == 'body':
                field_value = _strip_docstring(field_value)

            for item in field_value:
                if isinstance(item, ast.AST):
                    field.append(
                        convert_to_xml(
                            item,
                            omit_docstrings,
                            node_mappings,
                        )
                    )
                else:
                    subfield = etree.SubElement(field, 'item')
                    _set_encoded_literal(
                        partial(setattr, subfield, 'text'),
                        item
                    )

        elif field_value is not None:

            ## The only change is this immediate function call below
            ## add type attribute e.g. so we can distinguish strings from numbers etc
            ## <Constant lineno="1" col_offset="6" type="int" value="1"/>
            _set_encoded_literal(
                partial(xml_node.set, 'type'),
                type(field_value).__name__
            )

            _set_encoded_literal(
                partial(xml_node.set, field_name),
                field_value
            )

    return xml_node

astpath.asts.convert_to_xml = convert_to_xml

## importing from superhelp only works properly after I've installed superhelp as a pip package (albeit as a link to this code using python3 -m pip install --user -e <path_to_proj_folder>)
## Using this as a library etc works with . instead of superhelp but I want to be be able to run the helper module from within my IDE

try:
    from . import advisors, ast_funcs, conf  # @UnresolvedImport @UnusedImport
    from ..utils import get_docstring_start, layout_comment as layout, make_open_tmp_file  # @UnresolvedImport @UnusedImport
except (ImportError, ValueError):
    from pathlib import Path
    import sys
    parent = str(Path.cwd().parent)
    sys.path.insert(0, parent)
    from superhelp import advisors, ast_funcs, conf  # @Reimport
    from superhelp.utils import get_docstring_start, layout_comment as layout, make_open_tmp_file  # @Reimport

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

def _get_tree(snippet):
    try:
        tree = ast.parse(snippet)
    except SyntaxError as e:
        raise SyntaxError(
            f"Oops - something seems broken in the snippet - details: {e}")
    return tree

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
        advisor_input, code_str, first_line_no, repeat):
    name = advisor_dets.advisor_name
    docstring = advisor_dets.advisor.__doc__
    if not docstring:
        raise Exception(f'Advisor "{name}" lacks a docstring - add one!')
    try:
        try:
            message = advisor_dets.advisor(advisor_input,
                repeat=repeat)
        except TypeError as e:
            if "unexpected keyword argument 'repeat'" in str(e):
                message = advisor_dets.advisor(advisor_input)
            else:
                raise
    except Exception as e:
        brief_name = '.'.join(name.split('.')[-2:])  ## last two parts only
        message = {
            conf.BRIEF: (
                layout(f"""\

                    ### Advisor "`{brief_name}`" unable to run

                    Advisor {brief_name} unable to run. Advisor description:
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
        warning = advisor_dets.warning
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
        repeat = False
        for block_dets in blocks_dets2use:
            message_dets = get_message_dets_from_input(advisor_dets,
                advisor_input=block_dets, code_str=block_dets.block_code_str,
                first_line_no=block_dets.first_line_no,
                repeat=repeat)
            if message_dets:
                messages_dets.append(message_dets)
                repeat = True
    return messages_dets

def get_overall_snippet_messages_dets(snippet, blocks_dets):
    """
    Returns messages which apply to snippet as a whole, not just specific
    blocks. E.g. looking at every block to look for opportunities to unpack. Or
    reporting on linting results.
    """
    messages_dets = []
    all_advisors_dets = (
        advisors.ALL_BLOCKS_ADVISORS + advisors.SNIPPET_STR_ADVISORS)
    for advisor_dets in all_advisors_dets:
        if advisor_dets.input_type == conf.BLOCKS_DETS:
            advisor_input = blocks_dets
        elif advisor_dets.input_type == conf.SNIPPET_STR:
            advisor_input = snippet
        else:
            raise Exception(
                f"Unexpected input_type: '{advisor_dets.input_type}'")
        message_dets = get_message_dets_from_input(advisor_dets,
            advisor_input=advisor_input, code_str=snippet, first_line_no=None,
            repeat=False)
        if message_dets:
            messages_dets.append(message_dets)
    return messages_dets

def get_separated_messages_dets(snippet, snippet_block_els, xml):
    """
    Break snippet up into syntactical parts and blocks of code. Apply advisor
    functions and get message details. Split into overall messages and block-
    specific messages.

    :param str snippet: code snippet
    :param list snippet_block_els: list of block elements for snippet
    :param xml xml: snippet code as xml object
    :return: a tuple of two MessageDets lists
     (overall_snippet_messages_dets, block_level_messages_dets)
     or None if no messages
    :rtype: tuple (or None)
    """
    blocks_dets = get_blocks_dets(snippet, snippet_block_els)
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

def store_ast_output(xml):
    _tmp_ast_fh, tmp_ast_output_xml_fpath = make_open_tmp_file(
        conf.AST_OUTPUT_XML_FNAME, mode='w')
    xml.getroottree().write(str(tmp_ast_output_xml_fpath), pretty_print=True)
    logging.info("\n\n\n\n\nUpdating AST\n\n\n\n\n")

def get_snippet_dets(snippet):
    tree = _get_tree(snippet)
    xml = astpath.asts.convert_to_xml(tree)
    if conf.RECORD_AST:
        store_ast_output(xml)
    snippet_block_els = xml.xpath('body')[0].getchildren()  ## [0] because there is only one body under root
    multi_block_snippet = len(snippet_block_els) > 1
    snippet_messages_dets = get_separated_messages_dets(
        snippet, snippet_block_els, xml)
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
