import argparse

import ast
import astpath

import advisors, ast_funcs, conf
from displayers import cli_displayer, html_displayer

advisors.load_advisors()

def get_messages_dets(snippet, *, debug=False):
    """
    Break snippet up into syntactical parts.
    Messages relate to specific syntax parts.
    Apply matching advisor functions and get message details. 
    """
    messages_dets = []
    try:
        tree = ast.parse(snippet)
    except SyntaxError as e:
        raise SyntaxError(
            f"Oops - something is wrong with what you wrote - details: {e}")
    else:
        analyser = ast_funcs.Analyser()
        analyser.visit(tree)
        safe_imports = ('; '.join(analyser.safe_imports) + '; '
            if analyser.safe_imports else '')
        lines = snippet.split('\n')
        xml = astpath.asts.convert_to_xml(tree)
        if debug:
            xml.getroottree().write('ast_output.xml')
        for advisor_name, advisor_dets in advisors.ADVISORS.items():
            ## Find all elements in XML matching this rule's selector
            ## xml.cssselect would mix up match on ListComp when searching for List. Fun ensued ;-)
            matching_elements = xml.xpath(
                f"body/Assign/value/{advisor_dets.element_type}")
            ## Get explanations for each matched element
            for element in matching_elements:
                (first_line_no,
                 last_line_no) = ast_funcs.get_xml_element_line_no_range(
                    element)
                code_str = '\n'.join(
                    lines[first_line_no-1: last_line_no]).strip()
                message = advisor_dets.advisor(element, safe_imports, code_str)
                if message is None:
                    pass  ## it is OK for a rule to have nothing to say about an element e.g. if the rule is concerned with duplicate items in a list and there are none then it probably won't have anything to say
                else:
                    if conf.BRIEF not in message.keys():
                        raise Exception(f"'{advisor_name}' gave advice "
                            "but didn't include a '{conf.BRIEF}' message")
                    if conf.MAIN not in message.keys():
                        message[conf.MAIN] = message[conf.BRIEF]
                    if conf.EXTRA not in message.keys():
                        message[conf.EXTRA] = ''
                    message_dets = conf.MessageDets(
                        code_str, first_line_no, advisor_name, 
                        advisor_dets.warning, advisor_dets.element_type,
                        message,
                    )
                    messages_dets.append(message_dets)
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
    superhelp(snippet, displayer, message_level=message_level, debug=False)
