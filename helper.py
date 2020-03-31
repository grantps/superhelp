import argparse

import ast
import astpath

import conf
from renderers import cli_renderer, html_renderer
import rules

rules.load_rules()

def _get_last_line_no(element, *, first_line_no):
    last_line_no = None
    ancestor = element
    while True:
        ## See if there are any following siblings at this level of the tree.
        next_siblings = ancestor.xpath('./following-sibling::*')
        ## Get the line no of the closest following sibling we can.
        for sibling in next_siblings:
            sibling_line_nos = sibling.xpath(
                './ancestor-or-self::*[@lineno][1]/@lineno')
            if len(sibling_line_nos):
                ## Subtract 1 from the next siblings line_no to get the
                ## last line_no of the element (unless that would be
                ## less than the first_line_no).
                last_line_no = max(
                    (int(sibling_line_nos[0]) - 1), first_line_no)
                break
        ## Continue searching for the next element by going up the tree to the next ancestor
        ancestor_ancestors = ancestor.xpath('./..')
        if len(ancestor_ancestors):
            ancestor = ancestor_ancestors[0]
        else:
            ## Break if we've run out of ancestors
            break
    return last_line_no

def get_xml_element_line_no_range(element):
    element_line_nos = element.xpath(
        './ancestor-or-self::*[@lineno][1]/@lineno')
    if element_line_nos:
        first_line_no = int(element_line_nos[0])
        last_line_no = _get_last_line_no(element, first_line_no=first_line_no)
    else:
        first_line_no, last_line_no = None, None
    return first_line_no, last_line_no

def get_explanations_dets(snippet):
    explanations_dets = []
    try:
        tree = ast.parse(snippet)
    except SyntaxError as e:
        raise SyntaxError(
            f"Something is wrong with what you wrote - details: {e}")
    else:
        lines = snippet.split('\n')
        xml = astpath.asts.convert_to_xml(tree)
        for rule_name, rule_dets in rules.RULES.items():
            ## Find all elements in XML matching this rule's selector
            matching_elements = xml.cssselect(rule_dets.element_type)
            ## Get explanations for each matched element
            for element in matching_elements:
                first_line_no, last_line_no = get_xml_element_line_no_range(
                    element)
                content = '\n'.join(
                    lines[first_line_no-1: last_line_no]).strip()
                explanation = rule_dets.explainer(element)
                if explanation is None:
                    pass  ## it is OK for a rule to have nothing to say about an element e.g. if the rule is concerned with duplicate items in a list and there are none then it probably won't have anything to say
                else:
                    if conf.BRIEF not in explanation.keys():
                        raise Exception(f"'{rule_name}' supplied an explanation"
                            " but didn't include a '{conf.BRIEF}' message")
                    if conf.MAIN not in explanation.keys():
                        explanation[conf.MAIN] = explanation[conf.BRIEF]
                    explanation_dets = conf.ExplanationDets(
                        content, first_line_no, rule_name, rule_dets.warning,
                        rule_dets.element_type, explanation,
                    )
                    explanations_dets.append(explanation_dets)
    return explanations_dets

def show_explanations(renderer, explanations, *, msg_level=conf.BRIEF):
    renderer.show(explanations, msg_level=msg_level)

def superhelp(snippet, renderer, *, msg_level=conf.BRIEF):
    """
    Talk about the snippet supplied
    """
    try:
        explanations_dets = get_explanations_dets(snippet)
        show_explanations(renderer, explanations_dets, msg_level=msg_level)
    except Exception:
        raise Exception("Sorry Dave - I can't help you with that")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Superhelp - Help for Humans!')
    ## don't use type=list ever https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option
    parser.add_argument('-r', '--renderer', type=str,
        required=False, default='html',
        help="Where do you want your help shown? html, cli, etc")
    parser.add_argument('-l', '--level', type=str,
        required=False, default='Brief',
        help="What level of help do you want? Brief, Main, or Extra?")
    parser.add_argument('-s', '--snippet', type=str,
        required=False, default=conf.DEMO_SNIPPET,
        help="Supply a brief snippet of Python code")
    args = parser.parse_args()
    snippet = args.snippet
    ARG2RENDERER = {
        'html': html_renderer,
        'cli': cli_renderer,
    }
    renderer = ARG2RENDERER[args.renderer]
    msg_level = args.level
    superhelp(snippet, renderer, msg_level=msg_level)
