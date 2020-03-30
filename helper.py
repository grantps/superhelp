import ast, astpath

import conf
import html_renderer
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

def get_explanations_dets(text):
    explanations_dets = []
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        raise SyntaxError(
            f"Something is wrong with what you wrote - details: {e}")
    else:
        lines = text.split('\n')
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

def show_explanations(medium, explanations):
    medium.show(explanations)

def superhelp(text, medium):
    """
    Talk about the snippet supplied
    """
    try:
        explanations_dets = get_explanations_dets(text)
        show_explanations(medium, explanations_dets)
    except Exception:
        raise Exception("Sorry Dave - I can't help you with that")


text = """
broken = [
    datetime.datetime.strptime('%Y-%m-%d', '2020-02-10'),
    fake.bogus.spam('sausage', 'eggs'),
    5,
    1.234,
    'Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', 'Jess', 'Nicole',
]
names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', 'Jess', 'Nicole']
empty = []
myint = 666
"""
medium = html_renderer
superhelp(text, medium)
