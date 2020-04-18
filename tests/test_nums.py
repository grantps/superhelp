from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.num_advisors.num_overview': 0,
            }
        ),
        (
            dedent("""\
            demo = [1, 2]
            """),
            {
                'superhelp.advisors.num_advisors.num_overview': 0,
            }
        ),
        (
            dedent("""\
            demo = 1
            """),
            {
                'superhelp.advisors.num_advisors.num_overview': 1,
            }
        ),
        (
            dedent("""\
            demo1 = 1
            demo2 = 2
            """),
            {
                'superhelp.advisors.num_advisors.num_overview': 2,  # two blocks so two messages
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = 1
            """),
            {
                'superhelp.advisors.num_advisors.num_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = 1
                demo2 = 2
            """),
            {
                'superhelp.advisors.num_advisors.num_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = 1
                demo2 = 2.666
            """),
            {
                'superhelp.advisors.num_advisors.num_overview': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
