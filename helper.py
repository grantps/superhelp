import ast, astpath

import html
from rules import RULES

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
def get_xml_element_linenos(element):
    """
    See:
    https://github.com/hchasestevens/astpath/blob/master/astpath/search.py#L84
    (linenos_from_xml)
    """
    return element.xpath('./ancestor-or-self::*[@lineno][1]/@lineno')

def get_explanations(text):
    explanations = []
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        raise SyntaxError(
            f"Something is wrong with what you wrote - details: {e}")
    else:
        xml = astpath.asts.convert_to_xml(tree)
        for rule_name, rule in RULES.items():
            print(f"Processing {rule_name}")
            ## Find all elements in XML matching this rule's selector
            matching_elements = xml.cssselect(rule['selector'])
            ## Get explanations for each matched element
            for element in matching_elements:
                line_no = int(get_xml_element_linenos(element)[0])
                explanation = rule['explainer'](line_no, element)
                if explanation is not None:
                    explanations.append(explanation)
    return explanations

def show_explanations(explainer, explanations):
    explainer(explanations)

def superhelp(text):
    """
    Talk about the snippet supplied
    """
    try:
        explanations = get_explanations(text)
        explainer = html.show_explanations
        show_explanations(explainer, explanations)
    except Exception:
        raise Exception("Sorry Dave - I can't help you with that")

superhelp(text)
