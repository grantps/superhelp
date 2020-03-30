from collections import namedtuple

ExplanationDets = namedtuple('ExplanationDets',
    'content, line_no, rule_name, warning, element_type, explanation')

BRIEF = 'Brief'  ## no spaces; used as labels and as parts of class names in CSS
MAIN = 'Main'
EXTRA = 'Extra'
MSG_TYPES = [BRIEF, MAIN, EXTRA]

LIST_ELEMENT_TYPE = 'List'

DEMO_SNIPPET = """\
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
