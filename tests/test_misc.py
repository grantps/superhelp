from textwrap import dedent

from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false  # @UnusedImport @UnresolvedImport

from superhelp.gen_utils import layout_comment as layout

def test_layout():
    """
    After layout is applied should start with two empty lines. If code, should
    also end with a single empty line.

    In non-code content, titles, links, and lists should not be split. Ordinary
    text lines should be split to a maximum of conf.MAX_STD_LINE_LEN.
    """
    tests = [
        ("Hi", "\n\nHi", False),

        ("""\
        1. [The Dictionary Even Mightier](https://www.youtube.com/watch?v=66P5FMkWoVU)

        2. [The Mighty Dictionary](https://www.youtube.com/watch?v=oMyy4Sm0uBs)
        """,
        dedent("""\


        1. [The Dictionary Even Mightier](https://www.youtube.com/watch?v=66P5FMkWoVU)

        2. [The Mighty Dictionary](https://www.youtube.com/watch?v=oMyy4Sm0uBs)"""),
        False),

        ("Hi this is a really long line which should be split at some point shouldn't it",
         dedent("""\


         Hi this is a really long line which should be split at some point
         shouldn't it"""),
         False),

    ]
    for raw, expected_res, is_code in tests:
        actual_res = layout(raw, is_code=is_code)
        assert_equal(actual_res, expected_res, f"'{actual_res}'")

# test_layout()
