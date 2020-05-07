from collections import namedtuple

from . import conf  # @UnresolvedImport

## extract patterns e.g. from:
## /tmp/snippet.py:1:23: W291 trailing whitespace
## /tmp/snippet.py:4:1: E999 IndentationError: unexpected indent
LINT_PATTERN = fr"""^.+?:                                  ## starts with misc until first colon e.g. /tmp/snippet.py: (+? to be non-greedy)
        (?P<{conf.LINT_LINE_NO}>\d+)                       ## line_no = one or more digits after snippet.py: and before the next : e.g. 4
        :\d+:\s{{1}}                                       ## one or more digits, :, and one space e.g. '1: '
        (?P<{conf.LINT_MSG_TYPE}>\w{{1}}\d{{1,3}})\s{{1}}  ## msg_type = (one letter, 1-3 digits) and one space e.g. E999
        (?P<{conf.LINT_MSG}>.*)                            ## msg = everything else e.g. 'IndentationError: unexpected indent'
    """

## https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes
## https://flake8.pycqa.org/en/latest/user/error-codes.html
IGNORED_LINT_RULES = [
    'E128',  ## flake8 wants visual alignment on line continuation - I don't - I want standardised alignment on indent multiples of 4 (idea taken from Brandon Rhodes thanks Brandon!)
    'E266', 'E262',  ## I like ## before comments and # before commented out code (idea copied off Tom Eastman - thanks Tom!)
    'E305',  ## for classes I agree with 2 spaces but not functions
]
LintMsgs = namedtuple('LintMsgs', 'brief, main, extra, replacement')
CUSTOM_LINT_MSGS = {
    'E501': LintMsgs(
        """\
        One or more lines are longer than the recommended 79 characters. This is
        not necessarily a problem but long lines should be an exception to the
        rule
        """,
        """\
        One or more lines are longer than the recommended 79 characters. This is
        not necessarily a problem given that we have wider monitors than when
        the guidelines were formulated. But long lines should be an exception to
        the rule. All being equal, short lines are easier to read and understand
        than long lines. There are multiple strategies for shortening lines but
        the overall goal has to be readability. Sometimes we have to live with
        broken "rules". And that's official. Read PEP 8 - the official Python
        style guide - especially the section "A Foolish Consistency is the
        Hobgoblin of Little Minds".
        """,
        '',
        True),
    'F401': LintMsgs(
        """\
        One or more imports not used in snippet.
        """,
        """\
        One or more imports not used in snippet. If the snippet was extracted
        from a larger piece of code and the imports are used in that code then
        there is no problem.
        """,
        '',
        False
        )
}
