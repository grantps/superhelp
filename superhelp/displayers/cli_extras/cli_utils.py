import logging
import re
import textwrap

from markdown.util import etree  # @UnresolvedImport
from pygments import lex, token  # @UnresolvedImport
from pygments.lexers import get_lexer_by_name  # @UnresolvedImport

from . import cli_colour, cli_conf

## monkey patch so invisible non-text is included in wrapping calculations making a mess of it
def _wrap_text_chunks_only(self, chunks):
    """_wrap_chunks(chunks : [string]) -> [string]

    Wrap a sequence of text chunks and return a list of lines of
    length 'self.width' or less.  (If 'break_long_words' is false,
    some lines may be longer than this.)  Chunks correspond roughly
    to words and the whitespace between them: each chunk is
    indivisible (modulo 'break_long_words'), but a line break can
    come between any two chunks.  Chunks should not have internal
    whitespace; ie. a chunk is either all whitespace or a "word".
    Whitespace chunks will be removed from the beginning and end of
    lines, but apart from that whitespace is preserved.
    """
    lines = []
    if self.width <= 0:
        raise ValueError("invalid width %r (must be > 0)" % self.width)
    if self.max_lines is not None:
        if self.max_lines > 1:
            indent = self.subsequent_indent
        else:
            indent = self.initial_indent
        if len(indent) + len(self.placeholder.lstrip()) > self.width:
            raise ValueError("placeholder too large for max width")

    # Arrange in reverse order so items can be efficiently popped
    # from a stack of chucks.
    chunks.reverse()

    while chunks:

        # Start the list of chunks that will make up the current line.
        # cur_len is just the length of all the chunks in cur_line.
        cur_line = []
        cur_len = 0

        # Figure out which static string will prefix this line.
        if lines:
            indent = self.subsequent_indent
        else:
            indent = self.initial_indent

        # Maximum width for this line.
        width = self.width - len(indent)

        # First chunk on line is whitespace -- drop it, unless this
        # is the very beginning of the text (ie. no lines started yet).
        if self.drop_whitespace and chunks[-1].strip() == '' and lines:
            del chunks[-1]

        while chunks:
            ## GPS - ignoring non-text
            last_chunk = chunks[-1]
            ignore_len = (
                last_chunk.startswith(cli_conf.STX)
                and last_chunk.endswith(cli_conf.ETX))
            l = 0 if ignore_len else len(last_chunk)

            # Can at least squeeze this chunk onto the current line.
            if cur_len + l <= width:
                cur_line.append(chunks.pop())
                cur_len += l

            # Nope, this line is full.
            else:
                break

        # The current line is full, and the next chunk is too big to
        # fit on *any* line (not just this one).
        if chunks and len(chunks[-1]) > width:
            self._handle_long_word(chunks, cur_line, cur_len, width)
            cur_len = sum(map(len, cur_line))

        # If the last chunk on this line is all whitespace, drop it.
        if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
            cur_len -= len(cur_line[-1])
            del cur_line[-1]

        if cur_line:
            if (self.max_lines is None or
                len(lines) + 1 < self.max_lines or
                (not chunks or
                 self.drop_whitespace and
                 len(chunks) == 1 and
                 not chunks[0].strip()) and cur_len <= width):
                # Convert current line back to a string and store it in
                # list of all lines (return value).
                lines.append(indent + ''.join(cur_line))
            else:
                while cur_line:
                    if (cur_line[-1].strip() and
                        cur_len + len(self.placeholder) <= width):
                        cur_line.append(self.placeholder)
                        lines.append(indent + ''.join(cur_line))
                        break
                    cur_len -= len(cur_line[-1])
                    del cur_line[-1]
                else:
                    if lines:
                        prev_line = lines[-1].rstrip()
                        if (len(prev_line) + len(self.placeholder) <=
                                self.width):
                            lines[-1] = prev_line + self.placeholder
                            break
                    lines.append(indent + self.placeholder.lstrip())
                break

    return lines


textwrap.TextWrapper._wrap_chunks = _wrap_text_chunks_only

ansi_escape = re.compile(r"\x1b[^m]*m")

def get_code_hl_tokens():
    code_hl_tokens = {}
    # replace code strs with tokens:
    for token_name, colour in cli_colour.TOKEN_NAME_TO_HL_COLOUR.items():
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
        colour = code_hl_tokens.get(my_token, cli_colour.CODE_COLOUR)
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
                    cli_conf.TEXT_BLOCK_CUT, cli_colour.LOW_VIS_COLOUR,
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
        tpart[1] = cli_colour.colourise(tpart[1], cli_colour.H3_COLOUR)
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
    # this is a code replacement marker of markdown.py. Don't text split the
    # replacement marker:
    if text.startswith(cli_conf.STX) and text.endswith(cli_conf.ETX):
        return text
    new_lines = []
    for line in text.split('\n'):
        dedented = textwrap.dedent(line)
        new_lines.extend(textwrap.wrap(dedented, width=cols))  ## had to monkey patch textwrap to prevent code replacement markers messing up line wrapping
    new_text = '\n'.join(new_lines)
    return new_text

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
