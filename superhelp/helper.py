import argparse
import ast
from collections import namedtuple
import logging
from superhelp import conf
logging.basicConfig(
    level=conf.LOG_LEVEL,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

import astpath  # @UnresolvedImport

## importing from superhelp only works properly after I've installed superhelp as a pip package (albeit as a link to this code using python3 -m pip install --user -e <path_to_proj_folder>)
## Using this as a library etc works with . instead of superhelp but I want to be be able to run the helper module from within my IDE
from superhelp import advisors, ast_funcs
from superhelp.displayers import cli_displayer, html_displayer
from superhelp.utils import layout_comment

advisors.load_advisors()

BlockDets = namedtuple(
    'BlockDets', 'element, pre_block_code_str, block_code_str, first_line_no')
BlockDets.pre_block_code_str.__doc__ = ("The code up until the line we are "
    "interested in needs to be run - it may depend on names from earlier")

MessageDets = namedtuple('MessageDets',
    'code_str, message, first_line_no, warning')
MessageDets.__doc__ += (
    "All the bits and pieces that might be needed to craft a message")

t = True
f = False

do_test = t  ## use test snippet rather than the larger demo snippet
do_html = t  ## use html displayer vs cli displayer
do_displayer = t  ## for dev testing only

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

def get_message_dets_from_input(advisor_dets, advisor_input,
        code_str, *, first_line_no):
    name = advisor_dets.advisor_name
    docstring = advisor_dets.advisor.__doc__
    if not docstring:
        raise Exception(f'Advisor "{name}" lacks a docstring - add one!')
    try:
        message = advisor_dets.advisor(advisor_input)
    except Exception as e:
        message = {
            conf.BRIEF: (
                layout_comment(f"""\
                    #### Advisor "`{name}`" unable to run

                    Advisor {name} unable to run. Advisor description:
                    """)
                +  ## show first line of docstring (subsequent lines might have more technical, internally-oriented comments)
                layout_comment(docstring.lstrip('\n').split('\n')[0] + '\n')
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
    message_dets = MessageDets(code_str, message, first_line_no, warning)
    return message_dets

def get_ancestor_block_element(element):
    """
    The item immediately under body that this element is under.
    """
    ancestor_elements = element.xpath('ancestor-or-self::*')
    ancestor_block_element = ancestor_elements[2]  ## [0] will be Module, 1 is body, and blocks are the children of body
    return ancestor_block_element

def get_filtered_blocks_dets(advisor_dets, xml, blocks_dets):
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
        [get_ancestor_block_element(element) for element in matching_elements])
    filtered_blocks_dets = [block_dets for block_dets in blocks_dets
        if block_dets.element in filt_block_elements]
    if filtered_blocks_dets:
        logging.debug(f"{advisor_dets.advisor_name} had at least one block")
    else:
        logging.debug(f"{advisor_dets.advisor_name} had no blocks")
    return filtered_blocks_dets

def get_messages_dets_from_blocks(blocks_dets, xml):
    """
    For each advisor, get advice on every relevant block. Element type specific
    advisors process filtered blocks_dets; all block advisors process all blocks
    (as you'd expect ;-)).
    """
    messages_dets = []
    all_advisors_dets = (
        advisors.FILT_BLOCK_ADVISORS + advisors.ANY_BLOCK_ADVISORS)
    for advisor_dets in all_advisors_dets:
        logging.debug(f"About to process '{advisor_dets.advisor_name}'")
        element_filtering = hasattr(advisor_dets, 'xpath')
        if element_filtering:
            filtered_blocks_dets = get_filtered_blocks_dets(
                advisor_dets, xml, blocks_dets)
            blocks_dets2use = filtered_blocks_dets
            logging.debug(
                f"'{advisor_dets.advisor_name}' has element filtering for "
                f"{len(blocks_dets2use)} matching blocks")
        else:  ## no filtering by element type so process all blocks
            blocks_dets2use = blocks_dets
        for block_dets in blocks_dets2use:
            message_dets = get_message_dets_from_input(advisor_dets, block_dets,
                block_dets.block_code_str,
                first_line_no=block_dets.first_line_no)
            if message_dets:
                messages_dets.append(message_dets)
    return messages_dets

def get_messages_dets_from_snippet(snippet, blocks_dets):
    messages_dets = []
    for advisor_dets in advisors.SNIPPET_ADVISORS:
        message_dets = get_message_dets_from_input(advisor_dets, blocks_dets,
            snippet, first_line_no=None)
        if message_dets:
            messages_dets.append(message_dets)
    return messages_dets

def get_messages_dets_from_xml(xml, snippet):
    messages_dets = []
    snippet_lines = snippet.split('\n')
    blocks_dets = get_blocks_dets(xml, snippet_lines)
    messages_dets_from_blocks = get_messages_dets_from_blocks(blocks_dets, xml)
    messages_dets.extend(messages_dets_from_blocks)
    messages_dets_from_snippet = get_messages_dets_from_snippet(
        snippet, blocks_dets)
    messages_dets.extend(messages_dets_from_snippet)
    return messages_dets

def get_messages_dets(snippet):
    """
    Break snippet up into syntactical parts and blocks of code.
    Apply matching advisor functions and get message details.

    :param str snippet: code snippet
    :return: a tuple of two MessageDets lists
     (overall_messages_dets, block_messages_dets) or None if no messages
    :rtype: tuple (or None)
    """
    tree = get_tree(snippet)
    xml = astpath.asts.convert_to_xml(tree)
    if conf.DEV_MODE:
        xml.getroottree().write(conf.AST_OUTPUT_XML, pretty_print=True)
    messages_dets = get_messages_dets_from_xml(xml, snippet)
    if None in messages_dets:
        raise Exception("messages_dets in meant to be a list of MessageDets "
            "named tuples yet a None item was found")
    overall_messages_dets = []
    block_messages_dets = []
    for message_dets in messages_dets:
        if message_dets.first_line_no is None:
            overall_messages_dets.append(message_dets)
        else:
            block_messages_dets.append(message_dets)
    if not (overall_messages_dets or block_messages_dets):
        message = {
            conf.BRIEF: conf.NO_ADVICE_MESSAGE,
        }
        message = complete_message(message, source=conf.SYSTEM_MESSAGE)
        overall_messages_dets = [MessageDets(snippet, message, None, False)]
    return overall_messages_dets, block_messages_dets

def display_messages(displayer, snippet, messages_dets, *,
        message_level=conf.BRIEF, in_notebook=False):
    res = displayer.display(snippet,
        messages_dets, message_level=message_level, in_notebook=in_notebook)
    if in_notebook:
        return res

def get_error_messages_dets(e, snippet):
    message = {
        conf.BRIEF: layout_comment(f"""\
            #### No advice sorry :-(

            Unable to provide advice - some sort of problem.

            Details: {e}
            """),
    }
    message = complete_message(message, source=conf.SYSTEM_MESSAGE)
    overall_messages_dets = [
        MessageDets(snippet, message, first_line_no=None, warning=True)]
    block_messages_dets = []
    messages_dets = (overall_messages_dets, block_messages_dets)
    return messages_dets

def _get_snippet(snippet, file_path):
    if snippet and file_path:
        raise Exception("Either set snippet or file-path, not both")
    elif file_path:
        with open(file_path) as f:
            snippet = f.read()
    elif snippet:
        pass
    else:
        snippet = conf.TEST_SNIPPET if do_test else conf.DEMO_SNIPPET
        logging.info("Using default snippet because no snippet provided")
    return snippet

def _get_displayer_module(displayer):
    ARG2DISPLAYER = {
        'html': html_displayer,
        'cli': cli_displayer,
    }
    displayer_module = ARG2DISPLAYER.get(displayer)
    if displayer_module is None:
        logging.info("Display is currently suppressed - please supply "
            "a displayer if you want advice displayed")
    return displayer_module

def superhelp(snippet=None, *, file_path=None,
        displayer='html', message_level=conf.EXTRA, in_notebook=False):
    """
    Provide advice about the snippet supplied

    :param str snippet: (optional) snippet of valid Python code to provide
     advice on. If None will try the file_path and if that is None will use the
     default snippet
    :param str file_path: (optional) file path containing snippet
    :param str displayer: displayer to use e.g. 'html' or 'cli'. Defaults to
     'html'.
    :param str message_level: e.g. 'Brief', 'Main', 'Extra'
    :param bool in_notebook: if True might change way display happens e.g. HTML
     not sent to browser but returned for display by notebook itself
    """
    snippet = _get_snippet(snippet, file_path)
    displayer_module = _get_displayer_module(displayer)
    try:
        messages_dets = get_messages_dets(snippet)
    except Exception as e:
        messages_dets = get_error_messages_dets(e, snippet)
    if displayer_module:
        res = display_messages(displayer_module, snippet, messages_dets,
            message_level=message_level, in_notebook=in_notebook)
        if in_notebook:
            return res

def shelp():
    """
    To get help

    $ shelp -h
    """
    default_displayer = 'html' if do_html else 'cli'
    ## don't use type=list ever https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option
    parser = argparse.ArgumentParser(
        description='Superhelp - Help for Humans!')
    parser.add_argument('-s', '--snippet', type=str,
        required=False,
        help="Supply a line or brief snippet of Python code")
    parser.add_argument('-f', '--file-path', type=str,
        required=False,
        help="File location of a line or brief snippet of Python code")
    parser.add_argument('-l', '--level', type=str,
        required=False, default='Extra',
        help="What level of help do you want? Brief, Main, or Extra?")
    parser.add_argument('-d', '--displayer', type=str,
        required=False, default=default_displayer,
        help="Where do you want your help shown? html, cli, etc")
    args = parser.parse_args()
    displayer = args.displayer if do_displayer else None
    superhelp(args.snippet,
        file_path=args.file_path, displayer=displayer, message_level=args.level)

if __name__ == '__main__':
    shelp()
