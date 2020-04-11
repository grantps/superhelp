import argparse
import ast
from collections import namedtuple

import astpath  # @UnresolvedImport

## importing from superhelp only works properly after I've installed superhelp as a pip package (albeit as a link to this code using python3 -m pip install --user -e <path_to_proj_folder>)
## Using this as a library etc works with . instead of superhelp but I want to be be able to run the helper module from within my IDE
from superhelp import advisors, ast_funcs, conf  # @UnresolvedImport
from superhelp.displayers import cli_displayer, html_displayer  # @UnresolvedImport

advisors.load_advisors()

BlockDets = namedtuple(
    'BlockDets', 'element, pre_block_code_str, block_code_str, first_line_no')
BlockDets.pre_block_code_str.__doc__ = ("The code up until the line we are "
    "interested in needs to be run - it may depend on names from earlier")

MessageDets = namedtuple('MessageDets',
    'code_str, first_line_no, advisor_name, warning, message')
MessageDets.__doc__ += (
    "All the bits and pieces that might be needed to craft a message")

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

def fix_message(message, advisor_name):
    try:
        message_keys = message.keys()
    except TypeError:
        raise TypeError(f"message had no keys - message: {message} "
            f"(type {type(message).__name__})")
    if conf.BRIEF not in message_keys:
        raise Exception(f"'{advisor_name}' gave advice but didn't "
            f"include a '{conf.BRIEF}' message")
    if conf.MAIN not in message_keys:
        message[conf.MAIN] = message[conf.BRIEF]
    if conf.EXTRA not in message_keys:
        message[conf.EXTRA] = ''
    return message

def get_message_dets_from_input(advisor_dets, advisor_input,
        code_str, *, first_line_no):
    message = advisor_dets.advisor(advisor_input)
    if message is None:
        return None
    message = fix_message(message, advisor_dets.advisor_name)
    message_dets = MessageDets(
        code_str, first_line_no,
        advisor_dets.advisor_name, advisor_dets.warning,
        message
    )
    return message_dets

def get_ancestor_block_element(element):
    """
    The item immediately under body that this element is under.
    """
    ancestor_elements = element.xpath('ancestor-or-self::*')
    ancestor_block_element = ancestor_elements[2]  ## [0] will be Module, 1 is body, and blocks are the children of body
    return ancestor_block_element

def get_filtered_blocks_dets(advisor_dets, xml, blocks_dets, *, debug=False):
    """
    Identify source block elements for matching element types. Then filter
    blocks_dets accordingly.

    :return: filtered_blocks_dets
    :rtype: list
    """
    xml_path = f"{advisor_dets.xml_root}/{advisor_dets.element_type}"
    matching_elements = xml.xpath(xml_path)
    if debug:
        if matching_elements:
            print(f"{advisor_dets.advisor_name} had at least one match")
        else:
            print(f"{advisor_dets.advisor_name} had no matches")
    filt_block_elements = set(
        [get_ancestor_block_element(element) for element in matching_elements])
    filtered_blocks_dets = [block_dets for block_dets in blocks_dets
        if block_dets.element in filt_block_elements]
    if debug:
        if filtered_blocks_dets:
            print(f"{advisor_dets.advisor_name} had at least one block")
        else:
            print(f"{advisor_dets.advisor_name} had no blocks")
    return filtered_blocks_dets

def get_messages_dets_from_blocks(blocks_dets, xml):
    """
    For each advisor, get advice on every relevant block. Element type specific
    advisors process filtered blocks_dets; all block advisors process all blocks
    (as you'd expect ;-)).
    """
    messages_dets = []
    all_advisors_dets = (
        advisors.TYPE_BLOCK_ADVISORS + advisors.ANY_BLOCK_ADVISORS)
    for advisor_dets in all_advisors_dets:
        type_filtering = hasattr(advisor_dets, 'xml_root')
        if type_filtering:
            filtered_blocks_dets = get_filtered_blocks_dets(
                advisor_dets, xml, blocks_dets)
            blocks_dets2use = filtered_blocks_dets
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

def get_messages_dets(snippet, *, debug=False):
    """
    Break snippet up into syntactical parts and blocks of code.
    Apply matching advisor functions and get message details.
    """
    tree = get_tree(snippet)
    ast_funcs.check_tree(tree)
    xml = astpath.asts.convert_to_xml(tree)
    if debug:
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
    return overall_messages_dets, block_messages_dets

def display_messages(displayer, snippet,
        overall_messages_dets, block_messages_dets, *,
        message_level=conf.BRIEF):
    displayer.display(snippet, overall_messages_dets, block_messages_dets,
        message_level=message_level)

def superhelp(snippet, *,
        displayer=None, message_level=conf.BRIEF, debug=False):
    """
    Provide advice about the snippet supplied

    :param bool debug: when True generates pretty-printed AST as XML file. Very
     useful for working out how to find elements of interest in AST
     (look in conf.AST_OUTPUT_XML after a run). Using
     https://python-ast-explorer.com/ is another option
    """
    try:
        overall_messages_dets, block_messages_dets = get_messages_dets(
            snippet, debug=debug)
        if displayer is None:
            print("Display is currently suppressed - please supply a displayer "
                "if you want advice displayed")
        else:
            display_messages(displayer, snippet,
                overall_messages_dets, block_messages_dets,
                message_level=message_level)
    except Exception:
        raise Exception("Sorry Dave - I can't help you with that")

if __name__ == '__main__':

    t = True
    f = False

    do_test = t
    do_html = t
    do_displayer = t

    default_displayer = 'html' if do_html else 'cli'
    default_snippet = conf.TEST_SNIPPET if do_test else conf.DEMO_SNIPPET

    ## don't use type=list ever https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option
    parser = argparse.ArgumentParser(
        description='Superhelp - Help for Humans!')
    parser.add_argument('-s', '--snippet', type=str,
        required=False, default=default_snippet,
        help="Supply a brief snippet of Python code")
    parser.add_argument('-l', '--level', type=str,
        required=False, default='Extra',
        help="What level of help do you want? Brief, Main, or Extra?")
    parser.add_argument('-d', '--displayer', type=str,
        required=False, default=default_displayer,
        help="Where do you want your help shown? html, cli, etc")
    args = parser.parse_args()
    snippet = args.snippet
    ARG2DISPLAYER = {
        'html': html_displayer,
        'cli': cli_displayer,
    }
    displayer = ARG2DISPLAYER[args.displayer] if do_displayer else None
    message_level = args.level
    superhelp(snippet, displayer=displayer, message_level=message_level,
        debug=True)
