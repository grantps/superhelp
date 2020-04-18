from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.tuple_advisors.tuple_overview': 0,
            }
        ),
        (
            dedent("""\
            coord = (1, 2)
            """),
            {
                'superhelp.advisors.tuple_advisors.tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            pets = ('cat', 'dog')
            """),
            {
                'superhelp.advisors.tuple_advisors.tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            pets1 = ('cat', 'dog')
            pets2 = ('cat', 'dog')
            """),
            {
                'superhelp.advisors.tuple_advisors.tuple_overview': 2,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pets = ('cat', 'dog')
            """),
            {
                'superhelp.advisors.tuple_advisors.tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pets1 = ('cat', 'dog')
                pets2 = ('cat', 'dog')
            """),
            {
                'superhelp.advisors.tuple_advisors.tuple_overview': 1,
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
                'superhelp.advisors.tuple_advisors.tuple_overview': 2,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
