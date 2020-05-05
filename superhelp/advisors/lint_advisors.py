from pathlib import Path
import re
from subprocess import run, PIPE
import sys

from ..advisors import snippet_str_advisor
from .. import conf
from ..utils import get_os_platform, layout_comment as layout,\
    make_open_tmp_file

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
    cmd = [which_statement, 'flake8']
    res = run(args=cmd, stdout=PIPE)
    flake8_fpath = str(res.stdout, encoding='utf-8').strip()
    if not flake8_fpath:
        flake8_fpath = _get_env_flake8_fpath()
    return flake8_fpath

def _get_flake8_results(fpath):
    flake8_fpath = _get_flake8_fpath()
    cmd = [flake8_fpath, str(fpath)]
    res = run(args=cmd, stdout=PIPE)
    return res

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

        Here is what the linter reported about your snippet:

        """)
    lint_lines = [line.strip()
        for line in str(res.stdout, encoding='utf-8').strip().split('\n')
        if line.strip()]
    ## /tmp/snippet.py:1:23: W291 trailing whitespace
    ## /tmp/snippet.py:4:1: E999 IndentationError: unexpected indent
    prog = re.compile(
        fr"""^{fpath}:
            (?P<{conf.LINT_LINE_NO}>\d+)       ## line_no = one or more digits after snippet.py: and before the next : 
            :\d+:\s{{1}}                       ## one or more digits, :, and one space
            (?P<{conf.LINT_MSG_TYPE}>\w{{1}})  ## msg_type = one letter
            \d{{1,3}}\s{{1}}                   ## 1-3 digits and one space
            (?P<{conf.LINT_MSG}>.*)            ## msg = everything else
        """, flags=re.VERBOSE)  # @UndefinedVariable
    lint_details = []
    for lint_line in lint_lines:
        result = prog.match(lint_line)
        lint_details.append(result.groupdict())
    lint_details.sort(
        key=lambda d: (d[conf.LINT_LINE_NO], d[conf.LINT_MSG_TYPE]))
    msg_lines = []
    for lint_detail in lint_details:
        line_no = lint_detail[conf.LINT_LINE_NO]
        if lint_detail[conf.LINT_MSG_TYPE] == 'E':
            msg_type = 'ERROR'
        elif lint_detail[conf.LINT_MSG_TYPE] == 'W':
            msg_type = 'Warning'
        else:
            msg_type = 'Other'
        msg = lint_detail[conf.LINT_MSG]
        msg_lines.append(f"Line {line_no:>3}: {msg_type} - {msg}")
    lint_message = layout('\n\n'.join(msg_lines))
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
        conf.BRIEF: title + lint_message,
        conf.EXTRA: obviousness,
    }
    return message
