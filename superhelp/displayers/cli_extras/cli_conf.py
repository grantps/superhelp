BOLD = '\u001b[1m'
UNDERLINE = '\u001b[4m'
REVERSED = '\u001b[7m'

PYTHON_LEXER_NAME = 'Python3'

HEADER_TAGS = [f"h{n}" for n in range(1, 9)]  ## h1, h2, ...

TERMINAL_WIDTH = 80  ## just hard-wiring this

ADMON_START = '!!! '

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

## https://en.wikipedia.org/wiki/Control_character
STX = '\x02'  ## Start of transmission of non-data characters
ETX = '\x03'  ## End of transmission

BADLY_PARSED_UNDERSCORE = f'{STX}95{ETX}'

LINK_START_ORD = ord("①")
