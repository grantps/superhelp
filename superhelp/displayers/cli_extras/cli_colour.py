
from . import cli_conf

def colourise(text, colour, *, reverse=False, bold=False, no_reset=False):
    """
    Colour is toggled on and will keep being applied unless toggled off (back to
    default colour).

    We apply this colour to everything except for nested content. That gets its
    own colours depending on what type of thing it is e.g. code.

    The only reason you'd supply an empty string to this is if you were setting
    a colour and had no_reset=True. Otherwise an empty line only would be
    coloured which makes no sense.

    Testing: print('Should be red spam', colourise('spam', cli_conf.RED))

    :param str text: text (if any) to be coloured.
    :param int colour: the colour to be applied to this text and, if no_reset
     is True, all subsequent text until toggled off (if ever).
    :param bool no_reset: colour set kept toggled on so will colour subsequent
     content until toggled off.
    """
    reset_colour = '' if no_reset else cli_conf.DEFAULT_ANSI_COLOUR_BYTE_STR
    for (start, end), inner_colour in cli_conf.BOUNDS2COLOUR.items():
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
    return colourise(text, cli_conf.LOW_VIS_COLOUR)

def colourise_plain(text, **_kwargs):
    """
    Useful when a tag is not found.

    Used in context where multiple args supplied but we ignore them here.
    """
    return colourise(text, cli_conf.T)
