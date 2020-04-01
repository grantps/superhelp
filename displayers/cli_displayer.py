from textwrap import dedent

import mdv

"""
Note - displays properly in the terminal but not necessarily in other output
"""

import conf

TERMINAL_WIDTH = 220

SHORT_LINE = '-' * 2  ## at 3 long it automatically becomes a long line (at least, it does in my bash terminal on Ubuntu)
LONG_LINE = '-' * 120

def display(messages_dets, *, message_level=conf.BRIEF):
    """
    Show by lines and then by list_rules within line.
    """
    mdv.term_columns = TERMINAL_WIDTH
    text = [mdv.main(f"{LONG_LINE}\n"
        "# SuperHELP - Help for Humans!\n"),
        mdv.main(f"\n{SHORT_LINE}\n"),
        "Help is provided for each line of your snippet.",
        f"Currently showing {message_level} content as requested",
    ]
    messages_dets.sort(key=lambda nt: (nt.line_no))
    prev_line_no = None
    for message_dets in messages_dets:
        ## display code for line number (once ;-))
        line_no = message_dets.line_no
        if line_no != prev_line_no:
            text.append(mdv.main(f'{LONG_LINE}\n## Line {line_no:,}'))
            text.append(mdv.main(dedent(message_dets.code_str)))
            prev_line_no = line_no
        ## process messages
        message = dedent(message_dets.message[message_level])
        if message_level == conf.EXTRA:
            message = dedent(message_dets.message[conf.MAIN]) + message
        warning_str = 'WARNING:\n' if message_dets.warning else ''
        message = warning_str + message
        text.append(mdv.main(message))
    content = '\n'.join(text)
    print(content)
