from collections import namedtuple

MessageDets = namedtuple('MessageDets',
    'content, line_no, advisor_name, warning, element_type, message')

BRIEF = 'Brief'  ## no spaces; used as labels and as parts of class names in CSS
MAIN = 'Main'
EXTRA = 'Extra'
MESSAGE_TYPES = [BRIEF, MAIN, EXTRA]

LIST_ELEMENT_TYPE = 'List'
NUM_ELEMENT_TYPE = 'Num'

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
