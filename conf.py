from collections import namedtuple

ExplanationDets = namedtuple('ExplanationDets',
    'content, line_no, rule_name, warning, element_type, explanation')

BRIEF = 'Brief'  ## no spaces; used as labels and as parts of class names in CSS
MAIN = 'Main'
EXTRA = 'Extra'
MSG_TYPES = [BRIEF, MAIN, EXTRA]

LIST_ELEMENT_TYPE = 'List'
