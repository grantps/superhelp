from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.regex_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            name_lengths = []
            """),
            {
                ROOT + 'verbose_option': 0,
            }
        ),
        (
            dedent("""\
            import re
            """),
            {
                ROOT + 'verbose_option': 1,
            }
        ),
        (
            dedent("""\
            import re
            re.match(r'car', 'cardboard', flags=re.VERBOSE)
            """),
            {
                ROOT + 'verbose_option': 0,
            }
        ),
        (
            dedent("""\
            import re
            re.match(r'(?x)car', 'cardboard')
            """),
            {
                ROOT + 'verbose_option': 0,
            }
        ),
        (
            dedent("""\
            import re
            re.match(r'(?)car', 'cardboard')
            """),
            {
                ROOT + 'verbose_option': 1,  ## (?x) isn't the (?x) in-line flag
            }
        ),
        (
            dedent("""\
            from re import match
            match(r'(?x)car', 'cardboard')
            """),
            {
                ROOT + 'verbose_option': 0,
            }
        ),
        (
            dedent("""\
            from re import match
            match(r'car', 'cardboard')
            """),
            {
                ROOT + 'verbose_option': 1,
            }
        ),
        (
            dedent("""\
            from re import match
            match(r'car', 'cardboard', flags=re.VERBOSE)
            """),
            {
                ROOT + 'verbose_option': 0,
            }
        ),
        (
            dedent("""\
            from re import match, VERBOSE
            match(r'car', 'cardboard', VERBOSE)
            """),
            {
                ROOT + 'verbose_option': 0,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
