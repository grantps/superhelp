from collections import namedtuple

"""
Goals - simple, simple, simple. NOT trying to replicate HTML, markdown etc.

Semantic not style. Main information is the nature of the information e.g. extra
vs brief.
"""

Explanation = namedtuple('Explanation','type, content')

BRIEF = 'Brief'
MAIN = 'Main'
EXTRA = 'Extra'
MSG_TYPES = [BRIEF, MAIN, EXTRA]

H1 = 'heading level 1'
H2 = 'heading level 2'
H3 = 'heading level 3'
P = 'paragraph'
C = 'code'

LIST = 'List'
