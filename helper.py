import argparse
import ast

import astpath

import advisors, ast_funcs, conf
from displayers import cli_displayer, html_displayer

advisors.load_advisors()

def get_tree(snippet):
    try:
        tree = ast.parse(snippet)
    except SyntaxError as e:
        raise SyntaxError(
            f"Oops - something is wrong with what you wrote - details: {e}")
    return tree

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

def get_type_advisor_message_dets(advisor_dets, element,
        pre_line_code_str, line_code_str, first_line_no):
    message = advisor_dets.advisor(
        element, pre_line_code_str, line_code_str)
    if message is None:
        return None
    message = fix_message(message, advisor_dets.advisor_name)
    message_dets = conf.MessageDets(
        line_code_str, first_line_no,
        advisor_dets.advisor_name, advisor_dets.warning,
        message
    )
    return message_dets

def get_generic_advisor_message_dets(advisor_dets, line_code_dets):
    message = advisor_dets.advisor(line_code_dets.element)
    if message is None:  ## it is OK for a rule to have nothing to say about an element e.g. if the rule is concerned with duplicate items in a list and there are none then it probably won't have anything to say
        return None
    message = fix_message(message, advisor_dets.advisor_name)
    message_dets = conf.MessageDets(
        line_code_dets.line_code_str, line_code_dets.first_line_no,
        advisor_dets.advisor_name, advisor_dets.warning,
        message
    )
    return message_dets

def get_messages_dets(snippet, *, debug=False):
    """
    Break snippet up into syntactical parts.
    Messages relate to specific syntax parts.
    Apply matching advisor functions and get message details.
    Also run general checks e.g. variable naming, on the elements advised upon.
    """
    tree = get_tree(snippet)
    ast_funcs.check_tree(tree)
    lines = snippet.split('\n')
    xml = astpath.asts.convert_to_xml(tree)
    if debug:
        xml.getroottree().write(conf.AST_OUTPUT_XML, pretty_print=True)
    advised_line_code_dets = set()
    messages_dets = []
    ## Get advice according to type e.g. Lists
    for type_advisor_dets in advisors.TYPE_ADVISORS:
        advisor_relevant_elements = xml.xpath(  ## xml.cssselect would mix up match on ListComp when searching for List. Fun ensued ;-)
            f"{type_advisor_dets.xml_root}/{type_advisor_dets.element_type}")
        for element in advisor_relevant_elements:
            line_nos = ast_funcs.get_xml_element_line_no_range(element)
            first_line_no, last_line_no = line_nos
            ## need to run entire code up to point where name is set - may derive from other names set earlier in code
            pre_line_code_str = '\n'.join(lines[0: first_line_no - 1]).strip() + '\n'
            line_code_str = '\n'.join(lines[first_line_no - 1: last_line_no]).strip()
            type_advisor_message_dets = get_type_advisor_message_dets(
                type_advisor_dets, element,
                pre_line_code_str, line_code_str, first_line_no)
            advised_line_code_dets.add(conf.LineCodeDets(
                element, line_code_str, first_line_no))
            if type_advisor_message_dets:
                messages_dets.append(type_advisor_message_dets)
    ## Get generic advice e.g. looking at variable names. Only for items already covered by type-specific advisors
    for generic_advisor_dets in advisors.GENERIC_ADVISORS:
        for line_code_dets in advised_line_code_dets:
            generic_advisor_message_dets = get_generic_advisor_message_dets(
                generic_advisor_dets, line_code_dets)
            if generic_advisor_message_dets:
                messages_dets.append(generic_advisor_message_dets)
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
        required=False, default=conf.DEMO_SNIPPET,
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
