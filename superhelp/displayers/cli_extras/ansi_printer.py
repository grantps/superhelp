from html import unescape
from markdown.extensions import Extension  # @UnresolvedImport
from markdown.treeprocessors import Treeprocessor  # @UnresolvedImport
from tabulate import tabulate  # @UnresolvedImport

from . import cli_colour, cli_conf, cli_utils, tag_formatting


class AnsiPrinter(Treeprocessor):

    @staticmethod
    def handle_admonitions(text):
        """
        Admonitions are blocks that stand out and might start with an icon e.g.
        alert. They are indicated by a leading '!!! ' and have other words with
        space separation
        """
        admon_lbl_used = None
        prefix = body_prefix = ''
        len_admon_start = len(cli_conf.ADMON_START)
        if text.startswith(cli_conf.ADMON_START):
            ## we have to handle admon labels with spaces so check with startswith not ==
            for admon_lbl in cli_colour.ADMONS:
                if text[len_admon_start:].startswith(admon_lbl):
                    break
            else:  ## i.e. never exited
                admon_lbl = text[len_admon_start:].split(" ", 1)[0]
                cli_colour.ADMONS[admon_lbl] = cli_colour.ADMONS.values()[0]
            prefix = body_prefix = '┃ '
            prefix += admon_lbl.capitalize()
            admon_lbl_used = admon_lbl
            text = text.split(admon_lbl, 1)[1]
        return text, prefix, body_prefix, admon_lbl_used 

    @staticmethod
    def handle_blockquotes(el, out, *, nesting_level):
        for el1 in el.getchildren():
            iout = []
            AnsiPrinter.formatter(el1, iout, nesting_level + 2, parent=el)
            pr = cli_colour.colourise(
                cli_conf.BQUOTE_PREFIX, cli_colour.H1_COLOUR)
            sp = ' ' * (nesting_level + 2)
            for l in iout:
                for l1 in l.splitlines():
                    if sp in l1:
                        l1 = ''.join(l1.split(sp, 1))
                    out.append(pr + l1)

    @staticmethod
    def handle_list_item(el, out, *, nesting_level):
        childs = el.getchildren()
        for nested in ['ul', 'ol']:
            if childs and childs[-1].tag == nested:
                ul = childs[-1]
                # Nested sublist? The li was inline formatted so
                # split all from <ul> off and format it as own tag:
                # (ul always at the end of an li)
                out[-1] = out[-1].split(f"<{nested}>", 1)[0]
                AnsiPrinter.formatter(
                    ul, out, nesting_level + 1, parent=el)

    @staticmethod
    def handle_table(el, out, *, nesting_level):
        """
        All processed here in one sweep. Markdown ext gave us a xml tree from
        the ascii. Our part here is the cell formatting and into a python nested
        list, then tabulate spits out ascii again.
        """
        def fmt(cell, parent):
            """ we just run the whole formatter - just with a fresh new
            result list so that our 'out' is untouched """
            _cell = []
            AnsiPrinter.formatter(
                cell, out=_cell, nesting_level=0, parent=parent)
            return "\n".join(_cell)

        text = []
        for el_idx in 0, 1:
            for Row in el[el_idx].getchildren():
                row = []
                text.append(row)
                for cell in Row.getchildren():
                    row.append(fmt(cell, row))
        # good ansi handling:
        tbl = tabulate(text)
        # do we have right room to indent it?
        # first line is seps, so no ansi escapes foo:
        width = len(tbl.split('\n', 1)[0])
        if width <= cli_conf.TERMINAL_WIDTH:
            text = tbl.splitlines()
            cli_utils.apply_borders(text)
            # center:
            indent = (cli_conf.TERMINAL_WIDTH - width) / 2
            # too much:
            indent = nesting_level
            tt = []
            for line in text:
                tot_indent = indent * cli_conf.LEFT_INDENT
                tt.append(f"{tot_indent}{line}")
            out.extend(tt)
        else:
            # TABLE CUTTING WHEN NOT WIDTH FIT
            # oh snap, the table bigger than our screen. hmm.
            # hey lets split into vertical parts:
            # but len calcs are hard, since we are crammed with escaping
            # seqs.
            # -> get rid of them:
            tc = []
            for row in text:
                tc.append([])
                l = tc[-1]
                for cell in row:
                    l.append(cli_utils.clean_ansi(cell))
            # again sam:
            # note: we had to patch it, it inserted '\n' within cells!
            table = tabulate(tc)
            out.append(
                cli_utils.split_blocks(
                    text_block=table, width=width,
                    n_cols=cli_conf.TERMINAL_WIDTH,
                    part_formatter=cli_utils.apply_borders)
            )

    @staticmethod
    def handle_lists(el, out, *, nesting_level):
        nr = 0
        for c in el:
            if el.tag == 'ul':
                c.set('prefix', cli_conf.LIST_PREFIX)
            elif el.tag == 'ol':
                nr += 1
                c.set('prefix', str(nr) + '. ')
            # handle the ``` style unindented code blocks -> parsed as p:
            AnsiPrinter.formatter(c, out, nesting_level + 1, parent=el)

    @staticmethod
    def formatter(el, out, nesting_level=0, prefix='', parent=None):
        """
        Main recursion down tree applying ANSI formatting.

        :param int nesting_level: nesting_level
        :param str prefix: might be set by admonitions e.g. '| WARNING' or set
         by parent ol ('1.', '2.' etc) or ul ('-'). Lists seems to override
         admonitions if the admonition has internal lists. A bug?
        """
        if el.tag == 'br':
            out.append('\n')
            return

        links_list = None
        is_txt_and_inline_markup = False

        if el.tag == 'blockquote':
            AnsiPrinter.handle_blockquotes(el, out, nesting_level=nesting_level)
            return

        if el.tag == 'hr':
            out.append(tag_formatting.hr('', nesting_level=nesting_level))
            return

        is_text = (
            bool(el.text)
            or el.tag == 'p'
            or el.tag == 'li'
            or el.tag.startswith('h')
        )
        if is_text:
            el.text = el.text or ''
            # <a attributes>foo... -> we want "foo....". Is it a sub
            # tag or inline text?
            text_with_inline_markup = cli_utils.get_text_if_inline_markup(el)
            if text_with_inline_markup:
                is_txt_and_inline_markup = True
                # foo:  \nbar -> will be seeing a foo:<br>bar with
                # mardkown.py. Code blocks are already quoted -> no prob.
                text_with_inline_markup = text_with_inline_markup.replace(
                    '<br />', '\n')
                # strip our own closing tag:
                text = text_with_inline_markup.rsplit('<', 1)[0]
                links_list, text = cli_utils.replace_links(
                    el, html=text, link_display_type='it')
                for tg, (start, end) in cli_conf.TAG2BOUNDS.items():
                    text = text.replace(tg, start)
                    tag_lbl = tg[1:]
                    close_tag = f"</{tag_lbl}"
                    text = text.replace(close_tag, end)
                text = unescape(text)
            else:
                text = el.text
            if cli_conf.BADLY_PARSED_UNDERSCORE in text:
                text = text.replace(cli_conf.BADLY_PARSED_UNDERSCORE, '_')  ## so __doc__ is displayed not 9595doc9595 when the source md has \_\_doc|_|_
            text = text.strip()

            admon_res = AnsiPrinter.handle_admonitions(text)
            text, prefix, body_prefix, admon_lbl_used = admon_res
            # set the parent, e.g. nrs in ols:
            if el.get('prefix'):
                # first line prefix, like '-':
                prefix = el.get('prefix')
                # next line prefs:
                body_prefix = ' ' * len(prefix)
                el.set('prefix', '')

            indent = cli_conf.LEFT_INDENT * nesting_level
            if el.tag in cli_conf.HEADER_TAGS:
                header_level = int(el.tag[1:])
                indent = ' ' # * (header_level - 1)
                nesting_level += header_level

            text = cli_utils.rewrap(el, text, indent, prefix,
                terminal_width=cli_conf.TERMINAL_WIDTH)

            # indent. can color the prefixes now, no more len checks:
            if admon_lbl_used:
                out.append("\n")
                colour = globals()[cli_colour.ADMONS[admon_lbl_used]]
                prefix = cli_colour.colourise(prefix, colour)
                body_prefix = cli_colour.colourise(body_prefix, colour)

            if prefix:
                h_level = ((nesting_level - 2) % 5) + 1
                colour = getattr(cli_colour, f"H{h_level}_COLOUR")
                if (prefix == cli_conf.LIST_PREFIX
                        or prefix.split('.', 1)[0].isdigit()):
                    prefix = cli_colour.colourise(prefix, colour)

            text = ('\n' + indent + body_prefix).join((text).splitlines())
            text = indent + prefix + text

            # headers outer left: go sure.
            # actually... NO. commented out.
            # if el.tag in self.header_tags:
            #    prefix = ''

            # calling the class Tags  functions
            # IF the parent is li and we have a linebreak then the renderer
            # delivers <li><p>foo</p> instead of <li>foo, i.e. we have to
            # omit the linebreak and append the text of p to the previous
            # result, (i.e. the list separator):
            tag_fmt_func = getattr(tag_formatting, el.tag,
                cli_colour.colourise_plain)  ## default
            if (
                type(parent) == type(el)
                and parent.tag == 'li'
                and not parent.text
                and el.tag == 'p'
            ):
                _out = tag_fmt_func(
                    text.lstrip(), nesting_level=nesting_level)
                out[-1] += _out
            else:
                out.append(
                    tag_fmt_func(text, nesting_level=nesting_level))

            if admon_lbl_used:
                out.append('\n')

            if links_list:
                for i, l in enumerate(links_list, 1):
                    out.append(cli_colour.colourise_low_vis(
                        f"{indent}[{i}] {l}"))

        if is_txt_and_inline_markup:
            if el.tag == 'li':
                AnsiPrinter.handle_list_item(
                    el, out, nesting_level=nesting_level)
            return

        if el.tag == 'table':
            AnsiPrinter.handle_table(el, out, nesting_level=nesting_level)
            return

        AnsiPrinter.handle_lists(el, out, nesting_level=nesting_level)

    def run(self, doc):
        out = []
        AnsiPrinter.formatter(doc, out)
        ansi = '\n'.join(out)
        self.markdown.ansi = ansi


class AnsiPrintExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        ansi_print_ext = AnsiPrinter(md)
        md.treeprocessors.add('ansi_print_ext', ansi_print_ext, '>inline')
