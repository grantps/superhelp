import logging
from textwrap import dedent

from .cli_extras import md2cli
from .cli_extras.cli_colour import set_global_colours
from superhelp.gen_utils import (get_code_desc, get_intro,
    get_line_numbered_snippet, layout_comment as layout)

"""
Note - displays properly in the terminal but not necessarily in other output
e.g. Eclipse console.

Lots in common with md displayer but risks of DRYing probably outweigh benefits
at this stage.
"""

from .. import conf

TERMINAL_WIDTH = 80

MDV_CODE_BOUNDARY = "```"

def get_message(message_dets, detail_level):
    message = dedent(message_dets.message[detail_level])
    if detail_level == conf.EXTRA:
        message = dedent(message_dets.message[conf.MAIN]) + message
    message = dedent(message)
    message = (message
        .replace(f"    {conf.PYTHON_CODE_START}", MDV_CODE_BOUNDARY)
        .replace(f"\n    {conf.PYTHON_CODE_END}", MDV_CODE_BOUNDARY)
    )
    message = md2cli.main(md=message.replace('`', ''))  ## They create problems in formatting
    return message

def _need_snippet_displayed(overall_messages_dets, block_messages_dets, *,
        multi_block=False):
    """
    Don't need to see the code snippet displayed when it is already visible:
    * because there is only one block in snippet and there is a block message
      for it (which will display the block i.e. the entire snippet) UNLESS there
      is an overall message separating them
    Otherwise we need it displayed.
    """
    mono_block_snippet = not multi_block
    if mono_block_snippet and block_messages_dets and not overall_messages_dets:
        return False
    return True

def display(snippet, file_path, messages_dets, *,
        detail_level=conf.BRIEF,
        warnings_only=False, multi_block=False, multi_script=False,
        theme_name=None):
    """
    Show by code blocks.
    """
    set_global_colours(theme_name)
    md2cli.term_columns = TERMINAL_WIDTH
    if warnings_only:
        options_msg = conf.WARNINGS_ONLY_MSG
    else:
        options_msg = conf.ALL_HELP_SHOWING_MSG
    intro = get_intro(file_path, multi_block=multi_block)
    text = [
        md2cli.main(layout(f"""\
            # SuperHELP - Help for Humans!

            {intro}

            Currently showing {detail_level} content as requested.
            {options_msg}.

            {conf.MISSING_ADVICE_MESSAGE}

            ## Help by spreading the word about SuperHELP on social media.
            {conf.FORCE_SPLIT}Twitter: {conf.TWITTER_HANDLE}. Thanks!
            """
        )),
    ]
    overall_messages_dets, block_messages_dets = messages_dets
    display_snippet = _need_snippet_displayed(
        overall_messages_dets, block_messages_dets, multi_block=multi_block)
    if display_snippet:
        line_numbered_snippet = get_line_numbered_snippet(snippet)
        code_desc = get_code_desc(file_path)
        text.append(md2cli.main(dedent(
            f"## {code_desc}"
            f"\n{MDV_CODE_BOUNDARY}\n"
            + line_numbered_snippet
            + f"\n{MDV_CODE_BOUNDARY}")))
    for message_dets in overall_messages_dets:
        message = get_message(message_dets, detail_level)
        text.append(message)
    block_messages_dets.sort(key=lambda nt: (nt.first_line_no, nt.warning))
    prev_line_no = None
    for message_dets in block_messages_dets:
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
        message = get_message(message_dets, detail_level)
        text.append(message)
    content = '\n'.join(text)
    print(content)
    if multi_script:
        input("Press any key to continue ...")
