import mdv

"""
Note - displays properly in the terminal but not necessarily in other output
"""

import conf

SHORT_LINE = '-'*2  ## at 3 long it automatically becomes a long line (at least, it does in my bash terminal on Ubuntu)
LONG_LINE = '-'*50

def show(explanations_dets, *, msg_level=conf.BRIEF):
    """
    Show by lines and then by list_rules within line.
    """
    text = [f"{LONG_LINE}\n"
        "# SuperHELP - Help for Humans!\n"
        f"\n{SHORT_LINE}\n"
        "Help is provided for each line of your snippet. "
        f"Currently showing {msg_level} content as requested"]
    explanations_dets.sort(key=lambda nt: (nt.line_no))
    prev_line_no = None
    for explanation_dets in explanations_dets:
        ## display code for line number (once ;-))
        line_no = explanation_dets.line_no
        if line_no != prev_line_no:
            text.append(LONG_LINE)
            text.append(f'## Line {line_no:,}')
            text.append(explanation_dets.content)
            prev_line_no = line_no
        ## process messages
        warning_str = 'WARNING:\n' if explanation_dets.warning else ''
        msg = warning_str + explanation_dets.explanation[msg_level]
        text.append(msg)
    content = mdv.main('\n'.join(text))
    print(content)
