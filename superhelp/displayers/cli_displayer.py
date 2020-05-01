import logging
from textwrap import dedent

from .cli_extras import md2cli
from ..utils import layout_comment as layout

"""
Note - displays properly in the terminal but not necessarily in other output
e.g. Eclipse console
"""

from .. import conf

TERMINAL_WIDTH = 80

MDV_CODE_BOUNDARY = "```"

def get_message(message_dets, message_level):
    message = dedent(message_dets.message[message_level])
    if message_level == conf.EXTRA:
        message = dedent(message_dets.message[conf.MAIN]) + message
    message = dedent(message)
    message = (message
        .replace(f"    {conf.PYTHON_CODE_START}", MDV_CODE_BOUNDARY)
        .replace(f"\n    {conf.PYTHON_CODE_END}", MDV_CODE_BOUNDARY)
    )
    message = md2cli.main(md=message.replace('`', ''))  ## They create problems in formatting
    return message

def display(snippet, messages_dets, *,
        message_level=conf.BRIEF, in_notebook=False):
    """
    Show by code blocks.
    """
    logging.debug(f"{__name__} doesn't use in_notebook setting {in_notebook}")
    md2cli.term_columns = TERMINAL_WIDTH
    text = [
        md2cli.main(layout(f"""\
            # SuperHELP - Help for Humans!

            Help is provided for your overall snippet and for each block of code
            as appropriate.

            Currently showing {message_level} content as requested.

            {conf.MISSING_ADVICE_MESSAGE}
            """
        )),
    ]
    text.append(md2cli.main(dedent(
        "## Overall Snippet"
        f"\n{MDV_CODE_BOUNDARY}\n"
        + snippet
        + f"\n{MDV_CODE_BOUNDARY}")))
    overall_messages_dets, block_messages_dets = messages_dets
    for message_dets in overall_messages_dets:
        message = get_message(message_dets, message_level)
        text.append(message)
    block_messages_dets.sort(key=lambda nt: (nt.first_line_no, nt.warning))
    prev_line_no = None
    for n, message_dets in enumerate(block_messages_dets):
        if n > 41:
            has_prob = True
            print(has_prob)
        ## display code for line number (once ;-))
        line_no = message_dets.first_line_no
        new_block = (line_no != prev_line_no)
        if new_block:
            block_has_warning_header = False
            text.append(md2cli.main(dedent(
                f'## Code block starting line {line_no:,}'
                f"\n{MDV_CODE_BOUNDARY}\n"
                + message_dets.code_str
                + f"\n{MDV_CODE_BOUNDARY}")))
            prev_line_no = line_no
        if message_dets.warning and not block_has_warning_header:
            text.append(md2cli.main(layout("""\
                ### Questions / Warnings

                There may be some issues with this code block you want to
                address.
                """)))
            block_has_warning_header = True
        ## process message
        message = get_message(message_dets, message_level)
        text.append(message)
    content = '\n'.join(text)
    print(content)
