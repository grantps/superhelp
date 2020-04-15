from textwrap import dedent

from superhelp import mdv_fixed as mdv

"""
Note - displays properly in the terminal but not necessarily in other output
"""

from .. import conf

TERMINAL_WIDTH = 220

SHORT_LINE = '-' * 2  ## at 3 long it automatically becomes a long line (at least, it does in my bash terminal on Ubuntu)
LONG_LINE = '-' * 120
MDV_CODE_BOUNDARY = "```"

def get_message(message_dets, message_level):
    message = dedent(message_dets.message[message_level])
    if message_level == conf.EXTRA:
        message = dedent(message_dets.message[conf.MAIN]) + message
    warning_str = 'WARNING:\n' if message_dets.warning else ''
    message = dedent(warning_str + message)
    message = (message
        .replace(f"    {conf.PYTHON_CODE_START}", MDV_CODE_BOUNDARY)
        .replace(f"\n    {conf.PYTHON_CODE_END}", MDV_CODE_BOUNDARY)
    )
    message = mdv.main(md=message)
    return message

def display(snippet, messages_dets, *,
        message_level=conf.BRIEF, in_notebook=False):
    """
    Show by code blocks.
    """
    mdv.term_columns = TERMINAL_WIDTH
    text = [mdv.main(f"{LONG_LINE}\n"
        "# SuperHELP - Help for Humans!\n"),
        mdv.main(f"\n{SHORT_LINE}\n"),
        "Help is provided for your overall snippet "
        "and for each line as appropriate.\n",
        f"Currently showing {message_level} content as requested",
    ]
    text.append(mdv.main(dedent(
        "## Overall Snippet\n"
        f"{MDV_CODE_BOUNDARY}\n"
        + snippet
        + f"\n{MDV_CODE_BOUNDARY}")))
    overall_messages_dets, block_messages_dets = messages_dets
    for message_dets in overall_messages_dets:
        message = get_message(message_dets, message_level)
        text.append(message)
    block_messages_dets.sort(key=lambda nt: (nt.first_line_no))
    prev_line_no = None
    for message_dets in block_messages_dets:
        ## display code for line number (once ;-))
        line_no = message_dets.first_line_no
        if line_no != prev_line_no:
            text.append(mdv.main(
                f'{LONG_LINE}\n## Code block starting line {line_no:,}'))
            text.append(mdv.main(dedent(
                f"{MDV_CODE_BOUNDARY}\n"
                + message_dets.code_str
                + f"\n{MDV_CODE_BOUNDARY}")))
            prev_line_no = line_no
        ## process message
        message = get_message(message_dets, message_level)
        text.append(message)  ## setting code_hilite is how you highlight the code - it is about handling MD within code e.g. in doc string
    content = '\n'.join(text)
    print(content)
