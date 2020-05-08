from . import cli_colour, cli_conf, cli_utils

def _get_vertical_padding_line(length):
    return length * ' '

def h(text, level):
    level_colour = cli_conf.LEVEL2COLOUR.get(level)
    bold = False
    if level <= 2:
        text = text.center(cli_conf.TERMINAL_WIDTH)
        vertical_padding_line = _get_vertical_padding_line(
            length=cli_conf.TERMINAL_WIDTH)
    else:
        if level == 3:
            lstar_padding = '**** '
            rstar_padding = ' ****'
        else:
            lstar_padding, rstar_padding = '', ''
        text = f"{lstar_padding}{text}{rstar_padding} "  ## extra space at end so right side of reversed background has a space between it and the text
        vertical_padding_line = _get_vertical_padding_line(length=len(text))
    if level <= 2:
        text = f"{vertical_padding_line}\n{text}\n{vertical_padding_line}"
        bold = True
    if level == 1:
        text = f"\n{text}"
    return cli_colour.colourise(
        text, level_colour, reverse=True, bold=bold) + '\n'

def h1(s, **_kwargs):
    return h(s, level=1)

def h2(s, **_kwargs):
    return h(s, level=2)

def h3(s, **_kwargs):
    return h(s, level=3)

def h4(s, **_kwargs):
    return h(s, level=4)

def h5(s, **_kwargs):
    return h(s, level=5)

def p(text, **_kwargs):
    return cli_colour.colourise(text.strip('\n') + '\n', cli_conf.T)

def a(text, **_kwargs):
    return cli_colour.colourise_low_vis(text)

def hr(_text, **kw):
    """
    Horizontal line (rule) that has colour of appropriate heading level.
    """
    nesting_level = kw.get('nesting_level', 1)
    indent = (nesting_level - 1) * cli_conf.LEFT_INDENT
    colour = cli_conf.LEVEL2COLOUR[nesting_level]
    start = end = cli_colour.colourise(cli_conf.HR_ENDS, colour)
    return cli_colour.colourise_low_vis(
        f"\n{indent}{start}{cli_conf.HR_MARKER}{end}{indent}\n")

def code(text, from_fenced_block=None, **kw):
    """
    md code AND ``` style fenced raw code ends here
    """
    if not from_fenced_block:
        text = ('\n' + text).replace('\n    ', '\n')[1:]
    n_text_lines = len(text.split('\n'))
    # funny: ":-" confuses the tokenizer. replace/backreplace:
    raw_code = text.replace(':-', '\x01--')
    raw_code = raw_code.replace('## &gt;&gt;&gt;', '## >>>')
    text = cli_utils.style_ansi(raw_code)
    # unnested level has indent of N_LEFT_INDENT, use it for fenced
    indent = ' ' * kw.get('nesting_level', cli_conf.N_LEFT_INDENT)
    # if from_fenced_block: ... WE treat equal.
    # shift to the far left, no matter the indent (screen space matters):
    firstl = text.split('\n')[0]
    n_spaces2delete = len(firstl) - len(firstl.lstrip())
    spaces2delete = ' ' * n_spaces2delete
    width = len(str(n_text_lines))  ## e.g. 3 so we can cope with line number 100 onwards
    width_of_line_num_1 = 1
    missing_indents = width - width_of_line_num_1  ## so if 3 wide to handle 100+ we need 2
    indent_for_first_line_num = missing_indents * ' '
    text = (
            '\n'
            + indent_for_first_line_num
            + (f"\n{text}").replace(f"\n{spaces2delete}", '\n')[1:]
        )
    # we want an indent of one and low vis prefix. this does it:
    code_lines = text.splitlines()
    code_prefix = cli_colour.colourise_low_vis(cli_conf.CODE_PREFIX)
    empty = cli_colour.colourise('', cli_conf.CODE_COLOUR, no_reset=True)
    prefix = f"\n{indent}{code_prefix} {empty}"
    if code_lines[-1] == '\x1b[0m':
        code_lines.pop()
    code_str = prefix.join(code_lines)
    code_str = code_str.replace('\x01--', ':-')
    return code_str + '\n' + cli_conf.DEFAULT_ANSI_COLOUR_BYTE_STR
