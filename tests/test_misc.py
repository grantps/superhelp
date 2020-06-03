from textwrap import dedent

from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false  # @UnusedImport @UnresolvedImport

from superhelp.gen_utils import layout_comment as layout

def test_layout():
    tests = [
        ("Hi", "\nHi"),

        ("""\
        1. [The Dictionary Even Mightier](https://www.youtube.com/watch?v=66P5FMkWoVU)

        2. [The Mighty Dictionary](https://www.youtube.com/watch?v=oMyy4Sm0uBs)
        """,
        dedent("""\

        1. [The Dictionary Even Mightier](https://www.youtube.com/watch?v=66P5FMkWoVU)

        2. [The Mighty Dictionary](https://www.youtube.com/watch?v=oMyy4Sm0uBs)

        """)),

    ]
    for raw, expected_res in tests:
        actual_res = layout(raw, is_code=False)
        assert_equal(actual_res, expected_res, f"'{actual_res}'")

# test_layout()
