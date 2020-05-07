import re

from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false  # @UnusedImport @UnresolvedImport

try:
    from ..superhelp import lint_conf  # @UnresolvedImport @UnusedImport
except (ImportError, ValueError):
    from pathlib import Path
    import sys
    parent = str(Path.cwd().parent.parent)
    sys.path.insert(0, parent)
    from superhelp import lint_conf  # @Reimport

def test_linter_regex():
    tests = [
        (r'/tmp/snippet.py:1:23: W291 trailing whitespace',
         {'line_no': '1', 'msg_type': 'W291', 'msg': 'trailing whitespace'}),

        (r'/tmp/snippet.py:4:1: E999 IndentationError: unexpected indent' ,
         {'line_no': '4', 'msg_type': 'E999', 'msg': 'IndentationError: unexpected indent'}),

        (r'path location:2222:333333333: E000 this has lots of spaces in it and punctuation ;:!@#$%^&*()_+|{}[]<>?/' ,
         {'line_no': '2222', 'msg_type': 'E000', 'msg': 'this has lots of spaces in it and punctuation ;:!@#$%^&*()_+|{}[]<>?/'}),
    ]
    for lint_str, expected_dict in tests:
        actual_dict = re.match(
            lint_conf.LINT_PATTERN, lint_str, flags=re.VERBOSE).groupdict()  # @UndefinedVariable
        assert_equal(actual_dict, expected_dict)

# test_linter_regex()
