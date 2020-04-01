from collections import namedtuple

MessageDets = namedtuple('MessageDets',
    'code_str, line_no, advisor_name, warning, element_type, message')

BRIEF = 'Brief'  ## no spaces; used as labels and as parts of class names in CSS
MAIN = 'Main'
EXTRA = 'Extra'
MESSAGE_TYPES = [BRIEF, MAIN, EXTRA]

ANON_NAME = 'Anonymous'

## Only include elements which are safe to exec
## To see what 
LIST_ELEMENT_TYPE = 'List'
LISTCOMP_ELEMENT_TYPE = 'ListComp'
NUM_ELEMENT_TYPE = 'Num'
STR_ELEMENT_TYPE = 'Str'

CLASS2NAME = {
    'int': 'integer',
    'float': 'float',
    'str': 'string',
}
CLASS2ARTICLE = {
    'int': 'an',
    'float': 'a',
    'str': 'a',
}

ADVANCED_DEMO_SNIPPET = """\
import datetime
import math
mixed = [
    datetime.datetime.strptime('2020-02-10', '%Y-%m-%d'),
    math.pi, 5, 1.234, 'Noor',
]
names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', 'Jess', 'Nicole']
empty = []
myint = 666
"""
DEMO_SNIPPET = """\
person = 'Guido van Rossum'
mixed = [
    5, 1.234, 'Noor',
]
names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', 'Jess', 'Nicole']
names_lower = [name.lower() for name in names]
empty = []
myint = 666
myfloat = 6.667
myscinot = 1.23E-7
"""
TEST_SNIPPET = """\
names_lower = [name.lower() for name in ['Noor', 'Grant', 'Hyeji']]
evens_squared = [x**2 for x in range(1, 6) if x % 2 == 0]
"""
