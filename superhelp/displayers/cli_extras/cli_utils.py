import logging
import re
import textwrap

from markdown.util import etree  # @UnresolvedImport
from pygments import lex, token  # @UnresolvedImport
from pygments.lexers import get_lexer_by_name  # @UnresolvedImport

from . import cli_colour, cli_conf

ansi_escape = re.compile(r"\x1b[^m]*m")

def get_code_hl_tokens():
    code_hl_tokens = {}
    # replace code strs with tokens:
    for token_name, colour in cli_conf.TOKEN_NAME_TO_HL_COLOUR.items():
        if '.' not in token_name:  ## cope with Operator.Word as token_name
            code_hl_tokens[getattr(token, token_name)] = colour
        else:
            token_names = token_name.split('.')
            token2use = token
            for token_name in token_names:
                token2use = getattr(token2use, token_name)
            code_hl_tokens[token2use] = colour
    return code_hl_tokens

def style_ansi(raw_code):
    """
    Actual code_lines highlighting
    """
    lexer = get_lexer_by_name(cli_conf.PYTHON_LEXER_NAME)
    tokens = lex(raw_code, lexer)
    code_hl_tokens = get_code_hl_tokens()
    code_lines = []
    for my_token, text in tokens:
        if not text:
            continue
        colour = code_hl_tokens.get(my_token, cli_conf.CODE_COLOUR)
        code_lines.append(cli_colour.colourise(text, colour))
        logging.debug(my_token, colour)
    styled_ansi_code = ''.join(code_lines)
    return styled_ansi_code

def set_hr_widths(result):
    if cli_conf.HR_MARKER not in result:
        return result
    hrs = [line for line in result.splitlines() if cli_conf.HR_MARKER in line]
    for hr in hrs:
        hrf = hr.replace(
            cli_conf.HR_MARKER, cli_conf.HR_SEP * cli_conf.TERMINAL_WIDTH)
        result = result.replace(hr, hrf)
    return result

def apply_borders(text):
    border = cli_colour.colourise_low_vis(text[0].replace("-", "─"))
    text[0] = text[-1] = border

def split_blocks(text_block, width, n_cols, part_formatter=None):
    """
    Splits while multi-line blocks vertically (for large tables)
    """
    ts = []
    for line in text_block.splitlines():
        parts = []
        line = line.ljust(width, ' ')  ## make equal length
        # first part full width, others a bit indented:
        parts.append(line[:n_cols])
        scols = n_cols - 2
        # the txt_block_cut in low makes the whole secondary tables
        # low. which i find a feature:
        # if you don't want it remove the colourise(.., LOW_VIS_COLOUR)
        parts.extend(
            [
                (' '
                +
                cli_colour.colourise(
                    cli_conf.TEXT_BLOCK_CUT, cli_conf.LOW_VIS_COLOUR,
                    no_reset=True)
                + line[i : i + scols]
                )
                for i in range(n_cols, len(line), scols)
            ]
        )
        ts.append(parts)
    blocks = []
    for block_part_nr in range(len(ts[0])):
        tpart = []
        for lines_block in ts:
            tpart.append(lines_block[block_part_nr])
        if part_formatter:
            part_formatter(tpart)
        tpart[1] = cli_colour.colourise(tpart[1], cli_conf.H3_COLOUR)
        blocks.append("\n".join(tpart))
    text = 'n' + '\n'.join(blocks) + '\n'
    return text

def rewrap(el, text, indent, prefix, terminal_width):
    """
    Reasonably smart rewrapping checking punctuations.
    """
    cols = max(terminal_width - len(indent + prefix), 5)
    if el.tag == 'code' or len(text) <= cols:
        return text
    # this is a code replacement marker of markdown.py. Don'text split the
    # replacement marker:
    if text.startswith('\x02') and text.endswith('\x03'):
        return text
    dedented = textwrap.dedent(text).strip()
    ret = textwrap.fill(dedented, width=cols)
    return ret

def clean_ansi(s):
    """
    If someone does not want the color foo
    """
    return ansi_escape.sub('', s)

def el2str(el):
    str2use = etree.tostring(el).decode('utf-8')
    return str2use

def get_text_if_inline_markup(el):
    """
    :return: html_str or None if not text with inline markup
    :rtype: str
    """
    el_str = el2str(el)
    ## strip tag
    html_str = (
        el_str.split(f'<{el.tag}', 1)[1].split('>', 1)[1].rsplit('>', 1)[0])
    ## start with another tagged child which is NOT in inlines?
    inlines = ['<a', '<em>', '<code>', '<strong>']
    has_inline_markup = False
    if html_str.startswith('<'):
        for inline in inlines:
            if html_str.startswith(inline):
                has_inline_markup = True
                break
    else:
        has_inline_markup = True
    if has_inline_markup:
        text_with_inline_markup = html_str
    else:
        text_with_inline_markup = None
    return text_with_inline_markup

def replace_links(el, html, link_display_type='it'):
    """
    Digging through inline "<a href=..."
    :return: links_list, and tag
    """
    parts = html.split('<a ')
    if len(parts) == 1:
        links_list = None
        return links_list, html
    links_list, cur_link = [], 0
    links = [l for l in el.getchildren() if "href" in l.keys()]
    if not len(parts) == len(links) + 1:
        ## contains an html element we don't support e.g. blockquote
        links_list = None
        return links_list, html
    cur = ''
    while parts:
        cur += parts.pop(0).rsplit("</a>")[-1]
        if not parts:
            break
        
        cur += cli_conf.LINK_START  ## indicating link formatting start
        # the 'a' xml element:
        link = links[cur_link]
        link_str = link.get('href', '')
        # bug in the markdown api? link el is not providing inlines!!
        # -> get them from the html:
        # cur += link.text or ''
        cur += parts[0].split('>', 1)[1].split('</a', 1)[0] or ''
        cur += cli_conf.LINK_END
        if link_display_type == "i":
            cur += cli_colour.colourise_low_vis(f"({link_str})")
        elif link_display_type != "h":  # inline table (it)
            # we build a link list, add the number like ① :
            cur += f"{chr(cli_conf.LINK_START_ORD + cur_link)} "
            links_list.append(link_str)
        else:
            pass  ## apparently we ignore h
        cur_link += 1
    return links_list, cur
