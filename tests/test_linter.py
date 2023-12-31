import re
from textwrap import dedent

from tests import check_as_expected

from superhelp import conf, lint_conf

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
        assert actual_dict == expected_dict

ROOT = 'superhelp.helpers.lint_help.'

def test_misc():
    test_conf = [
        (
            "pet = 'cat'",
            {
                ROOT + 'lint_snippet': 0,
            }
        ),
        (
            "names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', ]",
            {
                ROOT + 'lint_snippet': 0,
            }
        ),
        (
            "names = ( 'Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', )",  ## spaces around parentheses
            {
                ROOT + 'lint_snippet': 1,
            }
        ),
        (
            "names = ('Noor' , 'Grant', 'Hyeji', 'Vicky', 'Olek')",  ## spaces before comma
            {
                ROOT + 'lint_snippet': 1,
            }
        ),
        (
            "a = 2+1",  ## no spaces around operators
            {
                ROOT + 'lint_snippet': 1,
            }
        ),
        (
            "a = 2 + 1",  ## OK now it has spaces around operators
            {
                ROOT + 'lint_snippet': 0,
            }
        ),
        (
            "a=2",
            {
                ROOT + 'lint_snippet': 1,
            }
        ),
        (
            dedent("""\
            def TooJammedUp():
                pass
            class LetMeBreathe:
                pass
                """),
            {
                ROOT + 'lint_snippet': 1,
            }
        ),
        (
            "a = '" + 'v' * (lint_conf.MAX_LINE_LENGTH + 10) + "'",
            {
                ROOT + 'lint_snippet': 1,
            }
        ),
        (
            "a = '" + 'v' * (lint_conf.MAX_LINE_LENGTH - 10) + "'",
            {
                ROOT + 'lint_snippet': 0,
            }
        ),
        (
            dedent("""
                print("abc"
                    "def")
                """),
            {
                ROOT + 'lint_snippet': 1,
            }
        ),
        (
            dedent("""
                print("abc"
                      "def")
                """),
            {
                ROOT + 'lint_snippet': 0,
            }
        ),
    ]
    conf.INCLUDE_LINTING = True  ## or else never gets even run to make or fail to make a message!
    check_as_expected(test_conf)
    conf.INCLUDE_LINTING = False

# test_misc()
# test_linter_regex()
