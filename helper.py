import ast, astpath

import conf, html
from rules import RULES

def get_xml_element_line_no(element):
    """
    See:
    https://github.com/hchasestevens/astpath/blob/master/astpath/search.py#L84
    (linenos_from_xml)
    """
    return int(element.xpath('./ancestor-or-self::*[@lineno][1]/@lineno')[0])

def get_explanations_dets(text):
    explanations_dets = []
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        raise SyntaxError(
            f"Something is wrong with what you wrote - details: {e}")
    else:
        xml = astpath.asts.convert_to_xml(tree)
        for rule_name, rule_dets in RULES.items():
            ## Find all elements in XML matching this rule's selector
            matching_elements = xml.cssselect(rule_dets.element_type)
            ## Get explanations for each matched element
            for element in matching_elements:
                line_no = get_xml_element_line_no(element)
                explanation = rule_dets.explainer(element)
                if explanation is not None:
                    explanation_dets = conf.ExplanationDets(
                        line_no, rule_name, rule_dets.warning,
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
medium = html
superhelp(text, medium)
