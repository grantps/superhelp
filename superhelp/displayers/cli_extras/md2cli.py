from html import unescape
import markdown  # @UnresolvedImport
from markdown.extensions import fenced_code  # @UnresolvedImport
from markdown.extensions.tables import TableExtension  # @UnresolvedImport

from . import ansi_printer, cli_utils, tag_formatting

def get_ansi(md):
    """
    Covert markdown string into formatted and code-highlighted terminal code.
    """
    MD = markdown.Markdown(
        tab_length=4,
        extensions=[
            ansi_printer.AnsiPrintExtension(),
            TableExtension(),
            fenced_code.FencedCodeExtension(),
        ],
    )
    MD.convert(md)
    ansi = MD.ansi + '\n'
    ansi = cli_utils.set_hr_widths(ansi) + "\n"
    ## The raw HTML within the source includes fenced code blocks.
    ## Placeholders are numbered like this in the md, we replace back
    ansi_placeholder_tpl = markdown.util.HTML_PLACEHOLDER
    stash = MD.htmlStash
    for i, html_block_str in enumerate(stash.rawHtmlBlocks):
        ansi_placeholder = ansi_placeholder_tpl % i
        raw = unescape(html_block_str)
        if raw.lower().startswith('<br'):
            raw = '\n'
        pre = '<pre><code'
        if raw.startswith(pre):
            _, raw = raw.split(pre, 1)
            raw = raw.split('>', 1)[1].rsplit('</code>', 1)[0]
            raw = tag_formatting.code(raw.strip(), from_fenced_block=True)
        ansi = ansi.replace(ansi_placeholder, raw)
    return ansi

def main(md):
    ansi = get_ansi(md) if md else ''
    return ansi
