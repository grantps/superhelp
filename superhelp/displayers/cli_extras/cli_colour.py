
from . import cli_conf

DEFAULT_ANSI_COLOUR_BYTE_STR = '\033[0m'

## ANSI colour codes from http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
dark = {
    'H1_COLOUR': 231,
    'H2_COLOUR': 153,
    'H3_COLOUR': 117,
    'H4_COLOUR': 109,
    'H5_COLOUR': 65,
    'ERROR': 124,  ## red
    'LOW_VIS_COLOUR': 59,  ## low visibility
    'TEXT': 188,
    'TL': 59,
    'CODE_COLOUR': 102,  ## code
    'OPERATOR_WORD': 89,  ## Magenta
    'KEYWORD': 28,  ## Green
    'QUOTE_MARKS': 196,  ## Rust
    'OPERATOR': 231,  ## white
    'PUNCTUATION': 231,  ## white
    'INTEGER': 231,  ## white
    'FLOAT': 231,  ## white
}
light = {
    'H1_COLOUR': 17,
    'H2_COLOUR': 21,
    'H3_COLOUR': 24,
    'H4_COLOUR': 235,
    'H5_COLOUR': 52,
    'ERROR': 124,  ## red
    'LOW_VIS_COLOUR': 59,  ## low visibility
    'TEXT': 233,
    'TL': 59,
    'CODE_COLOUR': 236,  ## code
    'OPERATOR_WORD': 89,  ## Magenta
    'KEYWORD': 28,  ## Green
    'QUOTE_MARKS': 196,  ## Rust
    'OPERATOR': 232,  ## black
    'PUNCTUATION': 232,  ## black
    'INTEGER': 232,  ## black
    'FLOAT': 232,  ## black
}

def set_global_colours(theme_name):
    """
    Given I had no desire to completely refactor the CLI code I focused the evil
    in this one place. If you read this, please forgive me.
    """
    theme = globals()[theme_name]
    global H1_COLOUR
    global TOKEN_NAME_TO_HL_COLOUR
    global LEVEL2COLOUR
    global BOUNDS2COLOUR
    global TEXT
    global CODE_COLOUR
    global LOW_VIS_COLOUR
    TOKEN_NAME_TO_HL_COLOUR = {
        "Comment": theme['LOW_VIS_COLOUR'],
        "Error": theme['ERROR'],
        "Generic": theme['H2_COLOUR'],
        "Keyword": theme['KEYWORD'],
        "Name": theme['H1_COLOUR'],
        "Number": theme['H4_COLOUR'],
        "Operator": theme['OPERATOR'],
        "String": theme['H4_COLOUR'],
        "Operator.Word": theme['OPERATOR_WORD'],
        "Literal.String.Single": theme['QUOTE_MARKS'],
        "Literal.String.Double": theme['QUOTE_MARKS'],  ## double-quoted string
        "Punctuation": theme['PUNCTUATION'],
        "Literal.Number.Integer": theme['INTEGER'],
        "Literal.Number.Float": theme['FLOAT'],
        "Keyword.Constant": theme['KEYWORD'],
    }
    LEVEL2COLOUR = {
        1: theme['H1_COLOUR'],
        2: theme['H2_COLOUR'],
        3: theme['H3_COLOUR'],
        4: theme['H4_COLOUR'],
        5: theme['H5_COLOUR'],
    }
    BOUNDS2COLOUR = {
        cli_conf.CODE_BOUNDS: theme['H2_COLOUR'],
        cli_conf.STRONG_BOUNDS: theme['H2_COLOUR'],
        cli_conf.LINK_BOUNDS: theme['H2_COLOUR'],
        cli_conf.EMPH_BOUNDS: theme['H3_COLOUR'],
    }
    TEXT = theme['TEXT']
    H1_COLOUR = theme['H1_COLOUR']
    CODE_COLOUR = theme['CODE_COLOUR']
    LOW_VIS_COLOUR = theme['LOW_VIS_COLOUR']

ADMONS = { ## Will be extended dynamically to avoid pointless recalculation if admonitions with other keys found in markdown text received
    'note': 'H3_COLOUR',
    'warning': 'ERROR',
    'attention': 'H1_COLOUR',
    'hint': 'H4_COLOUR',
    'summary': 'H1_COLOUR',
    'hint': 'H4_COLOUR',
    'question': 'H5_COLOUR',
    'danger': 'ERROR',
    'dev': 'H5_COLOUR',
    'hint': 'H4_COLOUR',
    'caution': 'H2_COLOUR',
}

def colourise(text, colour, *, reverse=False, bold=False, no_reset=False):
    """
    Colour is toggled on and will keep being applied unless toggled off (back to
    default colour).

    We apply this colour to everything except for nested content. That gets its
    own colours depending on what type of thing it is e.g. code.

    The only reason you'd supply an empty string to this is if you were setting
    a colour and had no_reset=True. Otherwise an empty line only would be
    coloured which makes no sense.

    Testing: print('Should be red spam', colourise('spam', cli_conf.ERROR))

    :param str text: text (if any) to be coloured.
    :param int colour: the colour to be applied to this text and, if no_reset
     is True, all subsequent text until toggled off (if ever).
    :param bool no_reset: colour set kept toggled on so will colour subsequent
     content until toggled off.
    """
    reset_colour = '' if no_reset else DEFAULT_ANSI_COLOUR_BYTE_STR
    for (start, end), inner_colour in BOUNDS2COLOUR.items():
        if start in text:
            if start == cli_conf.LINK_START:
                uon, uoff = "\033[4m", "\033[24m"
            else:
                uon, uoff = '', ''
            text = text.replace(
                start, colourise('', inner_colour, no_reset=True) + uon)
            text = text.replace(
                end, uoff + colourise('', colour, no_reset=True))
    ansi_reverse = cli_conf.REVERSED if reverse else ''
    ansi_bold = cli_conf.BOLD if bold else ''
    text = f"\033[38;5;{colour}m{ansi_bold}{ansi_reverse}{text}{reset_colour}"
    return text

def colourise_low_vis(text):
    return colourise(text, LOW_VIS_COLOUR)

def colourise_plain(text, **_kwargs):
    """
    Useful when a tag is not found.

    Used in context where multiple args supplied but we ignore them here.
    """
    return colourise(text, TEXT)
