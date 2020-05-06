from collections import defaultdict
from pathlib import Path
import re
from subprocess import run, PIPE
import sys

from ..advisors import snippet_str_advisor
from .. import conf
from ..utils import get_nice_str_list, get_os_platform, \
    layout_comment as layout, make_open_tmp_file

## extract patterns e.g. from:
## /tmp/snippet.py:1:23: W291 trailing whitespace
## /tmp/snippet.py:4:1: E999 IndentationError: unexpected indent
prog = re.compile(
    fr"""^.+?:                                             ## starts with misc until first colon e.g. /tmp/snippet.py: (+? to be non-greedy)
        (?P<{conf.LINT_LINE_NO}>\d+)                       ## line_no = one or more digits after snippet.py: and before the next : e.g. 4
        :\d+:\s{{1}}                                       ## one or more digits, :, and one space e.g. '1: '
        (?P<{conf.LINT_MSG_TYPE}>\w{{1}}\d{{1,3}})\s{{1}}  ## msg_type = (one letter, 1-3 digits) and one space e.g. E999
        (?P<{conf.LINT_MSG}>.*)                            ## msg = everything else e.g. 'IndentationError: unexpected indent'
    """, flags=re.VERBOSE)  # @UndefinedVariable

def _store_snippet(snippet):
    tmp_fh, fpath = make_open_tmp_file(conf.SNIPPET_FNAME, mode='w')
    tmp_fh.write(snippet)
    tmp_fh.close()
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
    if conf.IGNORED_LINT_RULES:
        ignored = ','.join(conf.IGNORED_LINT_RULES)
        args.append(f"--extend-ignore={ignored}")
    res = run(args=args, stdout=PIPE)
    return res

def _msg_type_to_placeholder_key(msg_type):
    return f"{msg_type}_msg"

def _msg_type_to_placeholder(msg_type):
    placeholder_key = _msg_type_to_placeholder_key(msg_type)
    placeholder = '{' + placeholder_key + '}'  ## ready for .format()
    return placeholder

def _get_lint_dets_by_msg_type(lint_regex_dicts):
    """
    Gather by message type e.g. all the E123s together. Each may have messages
    for multiple lines. These lines may have the same or different messages.
    E.g. "line too long (91 > 79 characters)" vs "line too long (100 > 79
    characters)".

    We may also want to supplement / replace the standard messages with special
    messages. When replacing a message, we automatically want to consolidate to
    one message. If not replacing the message, we want our special content to
    appear after the unconsolidated messages for the message type.

    Consolidation: for example, "line too long (91 > 79 characters)" and "line
    too long (100 > 79 characters)" become "line too long", and there will be
    one message with multiple line numbers listed rather than multiple messages,
    one per line.

    :rtype: dict
    """
    lint_dets_by_msg_type = defaultdict(list)
    for lint_regex_dict in lint_regex_dicts:
        line_no = int(lint_regex_dict[conf.LINT_LINE_NO])
        msg_type = lint_regex_dict[conf.LINT_MSG_TYPE]
        msg = lint_regex_dict[conf.LINT_MSG]
        try:
            msg_dets = conf.CUSTOM_LINT_MSGS[msg_type]
        except KeyError:
            pass
        else:
            if msg_dets.replacement:
                ## Can't consolidate on the actual replacement message because
                ## we need different versions for different message levels.
                ## So we store a placeholder which enables us to consolidate AND
                ## replace for brief and then main. Will be using .format() so
                ## want to do something like:
                ## "{E123_msg} (lines 1 and 2)".format(E123_msg=e123_brief_msg)
                msg_placeholder = _msg_type_to_placeholder(msg_type)
                msg = msg_placeholder
        msg_line_no_pair = (msg, line_no)
        lint_dets_by_msg_type[msg_type].append(msg_line_no_pair)
    return lint_dets_by_msg_type

def _get_msg_line(msg_lineno_pairs):
    """
    Handle details for message type across all lines and specific messages.
    """
    msg_type_details = []
    msg_line_nos = defaultdict(set)
    for msg, line_no in msg_lineno_pairs:
        msg_line_nos[msg].add(line_no)
    for msg, line_nos in msg_line_nos.items():
        plural = 's' if len(line_nos) > 1 else ''
        nice_lines = get_nice_str_list(sorted(line_nos))
        msg2use = msg[0].upper() + msg[1:]  ## note - .capitalize() lower cases the remaining letters
        msg2use = msg2use.replace('>', '\>').replace('<', '\<')
        msg_type_details.append(f"{msg2use} (line{plural}:{nice_lines})")
    msg_line = '; '.join(msg_type_details)
    return msg_line

def _get_msg_lines(lint_dets_by_msg_type):
    msg_lines = []
    already_supplemented = set()
    for msg_type, msg_lineno_pairs in lint_dets_by_msg_type.items():
        msg_line = _get_msg_line(msg_lineno_pairs)
        msg_lines.append(msg_line)
        ## add supplementary line?
        supplement_configured = msg_type in conf.CUSTOM_LINT_MSGS
        if msg_type not in already_supplemented and supplement_configured:
            msg_dets = conf.CUSTOM_LINT_MSGS[msg_type]
            supplement_needed = not msg_dets.replacement
            if supplement_needed:
                msg_placeholder = _msg_type_to_placeholder(msg_type)
                msg_lines[-1] = msg_lines[-1] + ' ' + msg_placeholder  ## will be replaced by appropriate level message in brief and main
                already_supplemented.add(msg_type)
    return msg_lines

def _get_lint_msg(raw_lint_message, msg_level):
    """
    Make a dict mapping e.g. E501_msg to a message appropriate for the msg_level

    msg_dets is a named tuple including brief, main fields
    """
    msg_type_to_msg_level = {
        _msg_type_to_placeholder_key(msg_type): getattr(msg_dets, msg_level)
        for msg_type, msg_dets in conf.CUSTOM_LINT_MSGS.items()
    }
    lint_msg = raw_lint_message.format(**msg_type_to_msg_level)  ## e.g. E501_msg="Line too long", E666_msg='Code is generally evil'
    return lint_msg

def _get_extra_msg(lint_dets_by_msg_type):
    msg_types_used = lint_dets_by_msg_type.keys()
    extra_lines = []
    for msg_type in msg_types_used:
        msgs = conf.CUSTOM_LINT_MSGS.get(msg_type)
        if not msgs:
            continue
        extra_lines.append(msgs.extra)
    extra_msg = '\n\n'.join(extra_lines)
    return extra_msg

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
    ## gather by msg_type e.g. E501s grouped together
    lint_dets_by_msg_type = _get_lint_dets_by_msg_type(lint_regex_dicts)
    ## within message types gather by actual message (or msg_placeholder if we're replacing the standard message) and list line numbers
    msg_lines = _get_msg_lines(lint_dets_by_msg_type)
    ## assemble
    raw_lint_message = layout('* ' + '\n\n* '.join(msg_lines))
    ## replace placeholders with level-appropriate messages
    lint_msgs = []
    for msg_level in ['brief', 'main']:
        lint_msg = _get_lint_msg(raw_lint_message, msg_level)
        lint_msgs.append(layout(lint_msg))
    ## handle extra - see which placeholders are present and provide extra for those only
    extra_msg = _get_extra_msg(lint_dets_by_msg_type)
    lint_msgs.append(extra_msg)
    return lint_msgs

@snippet_str_advisor(warning=True)
def lint_snippet(snippet):
    """
    Look for "lint" as defined by flake8 linter and share the results.
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
    findings = layout("""\

        Here is what the linter reported about your snippet. Note - if your
        snippet is taken from a broader context the linter might be concerned
        about names it doesn't know about, variables not used (yet) etc - i.e.
        there may be some unavoidable false alarms.

        """)
    brief_msg, main_msg, extra_msg = get_lint_messages_by_level(
        raw_lint_feedback_str=res.stdout)
    obviousness = layout("""\

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

    message = {
        conf.BRIEF: title + findings + brief_msg,
        conf.MAIN: title + linting + findings + main_msg,
        conf.EXTRA: obviousness + extra_msg,
    }
    return message
