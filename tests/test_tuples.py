from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.tuple_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'tuple_overview': 0,
            }
        ),
        (
            dedent("""\
            coord = (1, 2)
            """),
            {
                ROOT + 'tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            pets = ('cat', 'dog')
            """),
            {
                ROOT + 'tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            pets = ('cat', 'dog',
            )
            """),
            {
                ROOT + 'tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            pets1 = ('cat', 'dog')
            pets2 = ('cat', 'dog')
            """),
            {
                ROOT + 'tuple_overview': 2,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pets = ('cat', 'dog')
            """),
            {
                ROOT + 'tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pets1 = ('cat', 'dog')
                pets2 = ('cat', 'dog')
            """),
            {
                ROOT + 'tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pets1 = ('cat', 'dog')
            for i in range(2):
                pets2 = ('cat', 'dog')
            """),
            {
                ROOT + 'tuple_overview': 2,
            }
        ),
        (  ## old signature was at risk of to finding tuples when actually a named tuple
            dedent("""\
            from collections import namedtuple

            Misc = namedtuple('Misc', 'a, b, c')
            """),
            {
                ROOT + 'tuple_overview': 0,
            }
        )
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
