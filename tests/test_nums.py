from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.advisors.num_advisors.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'num_overview': 0,
            }
        ),
        (
            dedent("""\
            demo = [1, 2]
            """),
            {
                ROOT + 'num_overview': 0,
            }
        ),
        (
            dedent("""\
            demo = 1
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            demo1 = 1
            demo2 = 2
            """),
            {
                ROOT + 'num_overview': 2,  # two blocks so two messages
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = 1
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = 1
                demo2 = 2
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = 1
                demo2 = 2.666
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
