from itertools import product
import logging
from pathlib import Path
from textwrap import dedent

from superhelp import conf
from superhelp.gen_utils import layout_comment as layout
from superhelp.helper import this

def test_this():
    conf.SHOW_OUTPUT = False
    file_path = Path(__file__).parent / 'demo_NOT_using_this.py'  ## already protection against infinite recursion (see _neutralise_superhelp_import_in_code)
    ## not testing output as this is suppressed by setting SHOW_OUTPUT to False
    bools = [True, False]
    for n, (theme_name, detail_level, warnings_only, execute_code) in enumerate(
            product(conf.THEME_OPTIONS, conf.LEVEL_OPTIONS, bools, bools), 1):
        logging.info(f"Run #{n} of test_this (approx a few dozen)")
        this(file_path=file_path,
            output=conf.Format.HTML, theme_name=theme_name, detail_level=detail_level,
            warnings_only=warnings_only, execute_code=execute_code)

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
        assert actual_res == expected_res, f"'{actual_res}'"

# test_layout()
# test_this()
