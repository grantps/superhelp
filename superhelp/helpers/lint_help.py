from collections import defaultdict, namedtuple
from pathlib import Path
import re
from subprocess import run, PIPE
import sys

from ..helpers import snippet_str_help
from .. import conf, lint_conf
from ..gen_utils import (get_nice_str_list, get_os_platform,
    layout_comment as layout, make_open_tmp_file)

prog = re.compile(lint_conf.LINT_PATTERN, flags=re.VERBOSE)  # @UndefinedVariable

MsgDets = namedtuple('MsgDets', 'msg, line_no')

already_supplemented = set()

MISC_ISSUES_TITLE = layout("""\
    #### Misc lint issues
    """)

def _store_snippet(snippet):
    """
    At least one test (E501 line too long) only triggered if a trailing newline.
    Note - if more than one newline we trigger W391 (blank line at end of file)
    so an rstrip('\n') needed.
    Having done this need to deactivate W292 (blank line at end of file) LOL
    """
    with make_open_tmp_file(conf.SNIPPET_FNAME, mode='w') as tmp_dets:
        _superhelp_tmpdir, tmp_fh, fpath = tmp_dets
        tmp_fh.write(snippet.rstrip('\n') + '\n')
    return fpath

def _get_env_flake8_fpath():
    """
    Perhaps we are in a virtual environment which hides flake8 from which /
    where commands. Worth a try.
    """
    bin_path = Path(sys.executable).parent
    flake8_fpath = str(bin_path / 'flake8')
    return flake8_fpath

def _get_flake8_fpath():
    os_platform = get_os_platform()
    if os_platform == conf.WINDOWS:
        """
        The Joys of Where

        The "where" statement won't always point to an actual executable -
        sometimes it finds a stub which, when executed, opens up an MS app store
        LOL FAIL. Sometimes refers to two places - one on a C: drive and another
        on a D: drive!!
        """
        which_statement = 'where'
    else:
        which_statement = 'which'
    args = [which_statement, 'flake8']
    res = run(args=args, stdout=PIPE)
    flake8_fpath = str(res.stdout, encoding='utf-8').strip()
    if not flake8_fpath:
        flake8_fpath = _get_env_flake8_fpath()
    return flake8_fpath

def _get_flake8_results(fpath):
    flake8_fpath = _get_flake8_fpath()
    args = [flake8_fpath, str(fpath)]
    if lint_conf.IGNORED_LINT_RULES:
        ignored = ','.join(lint_conf.IGNORED_LINT_RULES)
        args.append(f"--ignore={ignored}")
    res = run(args=args, stdout=PIPE)
    return res

def _msg_type_to_placeholder_key(msg_type):
    return f"{msg_type}_placeholder"

def _msg_type_to_placeholder(msg_type):
    placeholder_key = _msg_type_to_placeholder_key(msg_type)
    placeholder = '{' + placeholder_key + '}'  ## ready for .format()
    return placeholder

def _get_msg_type_and_dets(lint_regex_dicts):
    """
    Gather MsgDets named tuples by message type e.g. all the E123s together.
    Some lint message types are consolidated as per
    lint_conf.CONSOLIDATE_MSG_TYPE.

    Each message type may have messages for multiple lines. These lines may have
    the same or different messages. E.g. "line too long (91 > 79 characters)" vs
    "line too long (100 > 79 characters)".

    We may also want to supplement / replace the standard messages with special
    messages. When replacing a message, we automatically want to consolidate to
    one message. If not replacing the message, we want our special content to
    appear after the unconsolidated messages for the (possibly consolidated)
    message type. We use placeholders to make this possible. These are replaced
    later on when making message level-specific messages (brief and main only).

    Message consolidation: for example, "line too long (91 > 79 characters)" and
    "line too long (100 > 79 characters)" become "line too long", and there will
    be one message with multiple line numbers listed rather than multiple
    messages, one per line.

    Note: just because a message type is consolidated doesn't mean its messages
    will be consolidated or vice versa. They are independent transformations.

    :param list lint_regex_dicts: list of dicts - one per regex.
     Basically a list of pulled apart lint messages.
    :return: dict of message types as keys (possibly consolidated e.g.
     E123-9 -> line continuation message type) and MsgDets tuples as values.
    :rtype: dict
    """
    msg_type_and_dets = defaultdict(list)
    for lint_regex_dict in lint_regex_dicts:
        raw_msg_type = lint_regex_dict[conf.LINT_MSG_TYPE]
        msg_type = lint_conf.consolidated_msg_type(raw_msg_type)
        msg = layout(lint_regex_dict[conf.LINT_MSG])
        line_no = int(lint_regex_dict[conf.LINT_LINE_NO])
        msg_dets = MsgDets(msg, line_no)
        msg_type_and_dets[msg_type].append(msg_dets)
    return msg_type_and_dets

def _get_msg_line(msgs_dets):
    """
    Get a single message string. Handle details for message type across all
    lines and specific messages.

    :rtype: string
    :return: a single line
    """
    msg_type_details = []
    msg_line_nos = defaultdict(set)
    for msg_dets in msgs_dets:
        msg_line_nos[msg_dets.msg].add(msg_dets.line_no)
    for msg, line_nos in msg_line_nos.items():
        plural = 's' if len(line_nos) > 1 else ''
        nice_lines = get_nice_str_list(sorted(line_nos))
        msg2use = msg[0].upper() + msg[1:]  ## note - .capitalize() lower cases the remaining letters
        msg2use = msg2use.replace('>', '\>').replace('<', '\<')
        msg_type_details.append(f"{msg2use} (line{plural}:{nice_lines})")
    msg_line = layout('; '.join(msg_type_details))
    return msg_line

def _get_unfinished_messages(msg_type_and_dets):
    """
    Get list of unfinished messages. May contain placeholders that need to be
    replaced.

    Messages are possibly unfinished in the sense that placeholders need to be
    replaced with actual message content.

    :return: list of strings. Individual strings may contain placeholders.
    :rtype: list
    """
    unfinished_msgs = []
    global already_supplemented  ## needs to persist over multiple calls (e.g. running lint help every script in a project)
    for msg_type, msgs_dets in msg_type_and_dets.items():
        unfinished_msg = _get_msg_line(msgs_dets)
        generic_msg_type = msg_type not in lint_conf.CUSTOM_LINT_MSGS
        if generic_msg_type:
            unfinished_msg = '* ' + unfinished_msg.lstrip('\n')  ## bullet points for generic messages (custom messages have full layout treatment e.g. code highlighting)
        ## add custom supplementary lint message?
        supplement_configured = msg_type in lint_conf.CUSTOM_LINT_MSGS
        if msg_type not in already_supplemented and supplement_configured:
            msg_placeholder = _msg_type_to_placeholder(msg_type)
            unfinished_msg = (
                msg_placeholder
                    + '\n\nDetails: '
                    + unfinished_msg.lstrip('\n')
                )  ## will be replaced by appropriate level message in brief and main
            already_supplemented.add(msg_type)
        unfinished_msgs.append(unfinished_msg)
    return unfinished_msgs

def _get_extra_msg(msg_type_and_dets):
    msg_types_used = msg_type_and_dets.keys()
    extra_lines = []
    for msg_type in msg_types_used:
        msgs = lint_conf.CUSTOM_LINT_MSGS.get(msg_type)
        if not msgs:
            continue
        extra_lines.append(msgs.extra)
    extra_msg = '\n\n'.join(extra_lines)
    return extra_msg

def _heading_sort_order(msg_line):
    """
    Custom first (i.e. generic False first), then by message i.e. by title
    """
    custom = ' #### ' in msg_line[: 10]  ## Custom all start with #### ...
    return (not custom, msg_line)  ## for sorting - False is first

def _get_final_msgs_for_level(msgs_for_msg_level):
    """
    Can only add Misc heading once everything is sorted by actual message
    content (i.e. placeholders replaced and then sorted)
    """
    final_msgs_for_level = []
    has_generic_header = False
    for msg_for_msg_level in msgs_for_msg_level:
        starting_misc = '* ' in msg_for_msg_level[:5]
        if not has_generic_header and starting_misc:
            msgs2extend = [MISC_ISSUES_TITLE, msg_for_msg_level]
            has_generic_header = True
        else:
            msgs2extend = [msg_for_msg_level, ]
        final_msgs_for_level.extend(msgs2extend)
    return final_msgs_for_level

def get_lint_messages_by_level(raw_lint_feedback_str):
    """
    Gets lists of lint messages grouped by message level (brief, main, extra).

    Each message in a list is for a particular error / warning type e.g. E501.

    A message might be consolidated (e.g. foo has prob; bar has prob etc) or be
    a composite message (e.g. various have prob). It might be followed by
    supplementary content.

    :param str raw_lint_feedback_str: feedback as received from the linter as
     stdout (told you it was raw ;-))
    :return: brief_msg, main_msg, extra_msg
    :rtype list
    """
    ## split into lines
    raw_lint_lines = (
        str(raw_lint_feedback_str, encoding='utf-8').strip().split('\n'))
    lint_lines = [line.strip() for line in raw_lint_lines if line.strip()]
    ## REGEX the lines
    lint_regex_dicts = []
    for lint_line in lint_lines:
        result = prog.match(lint_line)
        lint_regex_dicts.append(result.groupdict())
    ## misc
    msg_type_and_dets = _get_msg_type_and_dets(lint_regex_dicts)
    unfinished_messages = _get_unfinished_messages(msg_type_and_dets)
    ## replace placeholders with level-appropriate messages
    ## we can finally sort messages within a brief / main message level!
    lint_msgs = []
    for msg_level in ['brief', 'main']:
        msg_type_to_msg_for_level = {
            _msg_type_to_placeholder_key(msg_type): getattr(msg_dets, msg_level)
            for msg_type, msg_dets in lint_conf.CUSTOM_LINT_MSGS.items()
        }
        msgs_for_level = [
            unfinished_message.format(**msg_type_to_msg_for_level)  ## maps msg_type e.g. E501 to e.g. "Line too long", E666_msg='Code is generally evil'
            for unfinished_message in unfinished_messages]
        msgs_for_level.sort(key=_heading_sort_order)
        ## Can only add Misc heading once everything is sorted by actual message
        ## content (i.e. placeholders replaced and then sorted)
        final_msgs_for_level = _get_final_msgs_for_level(msgs_for_level)
        final_msg_for_level = '\n\n'.join(final_msgs_for_level)
        lint_msgs.append(final_msg_for_level)
    ## handle extra - see which placeholders are present and provide extra for those only
    extra_msg = _get_extra_msg(msg_type_and_dets)
    lint_msgs.append(extra_msg)
    return lint_msgs

@snippet_str_help(warning=True)
def lint_snippet(snippet, *, repeat=False, **_kwargs):
    """
    Look for "lint" as defined by flake8 linter and share the results.

    The repeat argument is used to avoid repeating all the generic linter
    information. But we also need to know if specific linter msg_types have been
    repeated or not. We track those with module-level set
    `already_supplemented`.
    """
    if not conf.INCLUDE_LINTING:  ## disabled when testing for speed reasons
        return None
    fpath = _store_snippet(snippet)
    res = _get_flake8_results(fpath)
    if not res.stdout:
        return None

    title = layout("""\
    ### Python code issues (found by flake8 linter)
    """)
    if not repeat:
        linting = layout("""\

        "Linters" are software tools. They detect everything from trivial style
        mistakes of no consequence to program behaviour through to show-stopper
        syntax errors.

        Software developers can be notoriously fussy about the smallest details
        of code styling and a linter can not only detect actual errors in code
        it can also prevent developers becoming completely distracted by trivial
        irritants. Distracted developers miss real issues with programs so it
        can be of practical importance to pick up the "small stuff". Plus it
        enables teams of programmers to work on the same code base without
        spending all their time restyling each other's code and arguing about
        "standards".
        """)
        obviousness = layout("""\
        #### Good code is simple enough to reason about

        Linting is especially useful for an interpreted language like Python
        because there is no compiler to pick up "lint" errors. Linting is no
        substitute for unit testing though. And neither are a substitute for
        writing readable code that can be reasoned about with confidence - the
        single best protection against code not doing what it is meant to do.
        The goal should be code where there is obviously nothing wrong rather
        than code where there nothing obviously wrong.

        > "There are two ways of constructing a software design. One way is to
        make it so simple that there are obviously no deficiencies. And the
        other way is to make it so complicated that there are no obvious
        deficiencies." C.A.R. Hoare
        """)
    else:
        linting = ''
        obviousness = ''
    findings = layout("""\
    Here is what the linter reported about your snippet.
    """)
    brief_msg, main_msg, extra_msg = get_lint_messages_by_level(
        raw_lint_feedback_str=res.stdout)

    message = {
        conf.BRIEF: title + findings + brief_msg,
        conf.MAIN: title + linting + findings + main_msg,
        conf.EXTRA: obviousness + extra_msg,
    }
    return message
