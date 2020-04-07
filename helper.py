import argparse
import ast
from collections import namedtuple

import astpath

import advisors, ast_funcs, conf
from displayers import cli_displayer, html_displayer

advisors.load_advisors()

LineDets = namedtuple(
    'LineDets', 'element, pre_line_code_str, line_code_str, first_line_no')
LineDets.pre_line_code_str.__doc__ = ("The code up until the line we are "
    "interested in needs to be run - it may depend on names from earlier")

MessageDets = namedtuple('MessageDets',
    'code_str, line_no, advisor_name, warning, message')
MessageDets.__doc__ += ("All the bits and pieces that might be needed to craft "
    "a message")

def get_tree(snippet):
    try:
        tree = ast.parse(snippet)
    except SyntaxError as e:
        raise SyntaxError(
            f"Oops - something is wrong with what you wrote - details: {e}")
    return tree

def get_lines_dets(xml, snippet_lines):
    """
    Returning a list of all the details needed to process a line
    (namely LineDets named tuples)

    Note - lines in the XML sit immediately under body.

    :return: list of LineDets named tuples
    :rtype: list
    """
    lines_dets = []
    all_elements = xml.xpath('body')[0].getchildren()  ## [0] because there is only one body under root
    for element in all_elements:
        line_nos = ast_funcs.get_xml_element_line_no_range(element)
        first_line_no, last_line_no = line_nos
        line_code_str = (
            '\n'.join(snippet_lines[first_line_no - 1: last_line_no]).strip())
        pre_line_code_str = (
            '\n'.join(snippet_lines[0: first_line_no - 1]).strip()
            + '\n')
        lines_dets.append(LineDets(
            element, pre_line_code_str, line_code_str, first_line_no))
    return lines_dets

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

def get_message_dets(advisor_dets, line_dets):
    message = advisor_dets.advisor(line_dets)
    if message is None:
        return None
    message = fix_message(message, advisor_dets.advisor_name)
    message_dets = MessageDets(
        line_dets.line_code_str, line_dets.first_line_no,
        advisor_dets.advisor_name, advisor_dets.warning,
        message
    )
    return message_dets

def get_filtered_lines_dets(advisor_dets, xml, lines_dets):
    """
    Identify first line numbers for matching element types. Then filter
    lines_dets accordingly.

    :return: filtered_lines_dets
    :rtype: list
    """
    xml_path = f"{advisor_dets.xml_root}/{advisor_dets.element_type}"
    matching_elements = xml.xpath(xml_path)
    filt_first_line_nos = set(
        ast_funcs.get_xml_element_first_line_no(element)
        for element in matching_elements)
    filtered_lines_dets = [line_dets for line_dets in lines_dets
        if line_dets.first_line_no in filt_first_line_nos]
    return filtered_lines_dets

def get_messages_dets_from_xml(xml, snippet_lines):
    """
    For each advisor, get advice on every relevant line. Element type specific
    advisors process filtered lines_dets; all line advisors process all lines
    (as you'd expect ;-)).
    """
    messages_dets = []
    all_advisors_dets = advisors.TYPE_ADVISORS + advisors.ALL_LINE_ADVISORS
    lines_dets = get_lines_dets(xml, snippet_lines)
    for advisor_dets in all_advisors_dets:
        type_filtering = hasattr(advisor_dets, 'xml_root')
        if type_filtering:
            filtered_lines_dets = get_filtered_lines_dets(
                advisor_dets, xml, lines_dets)
            lines_dets2use = filtered_lines_dets
        else:  ## no filtering by element type so process all lines
            lines_dets2use = lines_dets
        for line_dets in lines_dets2use:
            message_dets = get_message_dets(advisor_dets, line_dets)
            if message_dets:
                messages_dets.append(message_dets)
    return messages_dets

def get_messages_dets(snippet, *, debug=False):
    """
    Break snippet up into syntactical parts and blocks of code.
    Apply matching advisor functions and get message details.
    """
    tree = get_tree(snippet)
    ast_funcs.check_tree(tree)
    snippet_lines = snippet.split('\n')
    xml = astpath.asts.convert_to_xml(tree)
    if debug:
        xml.getroottree().write(conf.AST_OUTPUT_XML, pretty_print=True)
    messages_dets = get_messages_dets_from_xml(xml, snippet_lines)
    return messages_dets

def display_messages(displayer, messages_dets, *, message_level=conf.BRIEF):
    displayer.display(messages_dets, message_level=message_level)

def superhelp(snippet, displayer, *, message_level=conf.BRIEF, debug=False):
    """
    Talk about the snippet supplied
    """
    try:
        messages_dets = get_messages_dets(snippet, debug=debug)
        display_messages(displayer, messages_dets, message_level=message_level)
    except Exception:
        raise Exception("Sorry Dave - I can't help you with that")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Superhelp - Help for Humans!')
    ## don't use type=list ever https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option
    parser.add_argument('-d', '--displayer', type=str,
        required=False, default='html',
        help="Where do you want your help shown? html, cli, etc")
    parser.add_argument('-l', '--level', type=str,
        required=False, default='Extra',
        help="What level of help do you want? Brief, Main, or Extra?")
    parser.add_argument('-s', '--snippet', type=str,
        required=False, default=conf.FUNC_SNIPPET,
        help="Supply a brief snippet of Python code")
    args = parser.parse_args()
    snippet = args.snippet
    ARG2DISPLAYER = {
        'html': html_displayer,
        'cli': cli_displayer,
    }
    displayer = ARG2DISPLAYER[args.displayer]
    message_level = args.level
    superhelp(snippet, displayer, message_level=message_level, debug=True)
