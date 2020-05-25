from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.operator_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'compound_operator_possible': 0,
            }
        ),
        (
            dedent("""\
            x = x + 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x - 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x * 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x / 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x % 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x // 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x ** 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x & 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x | 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x ^ 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x >> 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            x = x << 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                x = x << 1
            """),
            {
                ROOT + 'compound_operator_possible': 1,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
