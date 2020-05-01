BOLD = '\u001b[1m'
UNDERLINE = '\u001b[4m'
REVERSED = '\u001b[7m'

PYTHON_LEXER_NAME = 'Python3'

HEADER_TAGS = [f"h{n}" for n in range(1, 9)]  ## h1, h2, ...

TERMINAL_WIDTH = 80  ## just hard-wiring this

## ANSI colour codes from http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
H1_COLOUR = 231
H2_COLOUR = 153
H3_COLOUR = 117
H4_COLOUR = 109
H5_COLOUR = 65
RED = 124  ## warnings
LOW_VIS_COLOUR = 59  ## low visibility
BG = 16  ## background
BG_LIGHT = 188  ## background light
T = 188
TL = 59
CODE_COLOUR = 102  ## code
MAGENTA = 89
GREEN = 28
RUST = 196
WHITE = 231

TOKEN_NAME_TO_HL_COLOUR = {
    "Comment": LOW_VIS_COLOUR,
    "Error": RED,
    "Generic": H2_COLOUR,
    "Keyword": GREEN,
    "Name": H1_COLOUR,
    "Number": H4_COLOUR,
    "Operator": WHITE,
    "String": H4_COLOUR,
    "Operator.Word": MAGENTA,
    "Literal.String.Single": RUST,
    "Literal.String.Double": RUST,  ## double-quoted string
    "Punctuation": WHITE,
    "Literal.Number.Integer": WHITE,
    "Literal.Number.Float": WHITE,
    "Keyword.Constant": GREEN,
}

LEVEL2COLOUR = {
    1: H1_COLOUR,
    2: H2_COLOUR,
    3: H3_COLOUR,
    4: H4_COLOUR,
    5: H5_COLOUR,
}

DEFAULT_ANSI_COLOUR_BYTE_STR = '\033[0m'

ADMON_START = '!!! '
ADMONS = { ## Will be extended dynamically to avoid pointless recalculation if admonitions with other keys found in markdown text received
    'note': 'H3_COLOUR',
    'warning': 'RED',
    'attention': 'H1_COLOUR',
    'hint': 'H4_COLOUR',
    'summary': 'H1_COLOUR',
    'hint': 'H4_COLOUR',
    'question': 'H5_COLOUR',
    'danger': 'RED',
    'dev': 'H5_COLOUR',
    'hint': 'H4_COLOUR',
    'caution': 'H2_COLOUR',
}

BQUOTE_PREFIX = '|'
LIST_PREFIX = '- '
CODE_PREFIX = '| '
TEXT_BLOCK_CUT = '✂'
HR_SEP = '─'

## nesting indentation
N_LEFT_INDENT = 2
LEFT_INDENT = ' ' * N_LEFT_INDENT

# markers: tab is 09, omit that
CODE_START, CODE_END = '\x07', '\x08'
STRONG_START, STRONG_END = '\x16', '\x10'
EMPH_START, EMPH_END = '\x11', '\x12'
LINK_START, LINK_END = '\x17', '\x18'
HR_MARKER = '\x15'
HR_ENDS = '◈'

CODE_BOUNDS = (CODE_START, CODE_END)
STRONG_BOUNDS = (STRONG_START, STRONG_END)
EMPH_BOUNDS = (EMPH_START, EMPH_END)
LINK_BOUNDS = LINK_START, LINK_END

TAG2BOUNDS = {
    '<code>': CODE_BOUNDS,
    '<strong>': STRONG_BOUNDS,
    '<em>': EMPH_BOUNDS,
}

BOUNDS2COLOUR = {
    CODE_BOUNDS: H2_COLOUR,
    STRONG_BOUNDS: H2_COLOUR,
    LINK_BOUNDS: H2_COLOUR,
    EMPH_BOUNDS: H3_COLOUR,
}

## https://en.wikipedia.org/wiki/Control_character
STX = '\x02'  ## Start of transmission of non-data characters
ETX = '\x03'  ## End of transmission

BADLY_PARSED_UNDERSCORE = f'{STX}95{ETX}'

LINK_START_ORD = ord("①")
