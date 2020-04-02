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

def get_message_dets(advisor_dets, element, lines):
    line_nos = ast_funcs.get_xml_element_line_no_range(element)
    first_line_no, last_line_no = line_nos
    ## need to run entire code up to point where name is set - may derive from other names set earlier in code
    pre_line_code_str = '\n'.join(lines[0: first_line_no - 1]).strip() + '\n'
    line_code_str = '\n'.join(lines[first_line_no - 1: last_line_no]).strip()
    message = advisor_dets.advisor(
        element, pre_line_code_str, line_code_str)
    if message is None:  ## it is OK for a rule to have nothing to say about an element e.g. if the rule is concerned with duplicate items in a list and there are none then it probably won't have anything to say
        return None
    if conf.BRIEF not in message.keys():
        raise Exception(f"'{advisor_dets.advisor_name}' gave advice but didn't include a "
            f"'{conf.BRIEF}' message")
    if conf.MAIN not in message.keys():
        message[conf.MAIN] = message[conf.BRIEF]
    if conf.EXTRA not in message.keys():
        message[conf.EXTRA] = ''
    message_dets = conf.MessageDets(
        line_code_str, first_line_no,
        advisor_dets.advisor_name, advisor_dets.warning, advisor_dets.element_type,
        message
    )
    return message_dets

def get_messages_dets(snippet, *, debug=False):
    """
    Break snippet up into syntactical parts.
    Messages relate to specific syntax parts.
    Apply matching advisor functions and get message details. 
    """
    messages_dets = []
    tree = get_tree(snippet)
    ast_funcs.check_tree(tree)
    lines = snippet.split('\n')
    xml = astpath.asts.convert_to_xml(tree)
    if debug:
        xml.getroottree().write(conf.AST_OUTPUT_XML, pretty_print=True)
    for advisor_dets in advisors.ADVISORS:
        advisor_relevant_elements = xml.xpath(  ## xml.cssselect would mix up match on ListComp when searching for List. Fun ensued ;-)
            f"body/Assign/value/{advisor_dets.element_type}")
        for element in advisor_relevant_elements:
            advisor_message_dets = get_message_dets(
                advisor_dets, element, lines)
            if advisor_message_dets:
                messages_dets.append(advisor_message_dets)
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
        required=False, default=conf.TEST_SNIPPET,
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
