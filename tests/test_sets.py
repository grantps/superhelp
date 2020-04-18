from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.set_advisors.set_overview': 0,
            }
        ),
        (
            dedent("""\
            demo = set()
            """),
            {
                'superhelp.advisors.set_advisors.set_overview': 1,
            }
        ),
        (
            dedent("""\
            demo1 = set()
            demo2 = set()
            """),
            {
                'superhelp.advisors.set_advisors.set_overview': 2,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = set()
                demo2 = set()
            """),
            {
                'superhelp.advisors.set_advisors.set_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = set([1, 2, 3])
                demo2 = set([8, 9, 10])
            """),
            {
                'superhelp.advisors.set_advisors.set_overview': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
