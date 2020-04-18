from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 0,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
            }
        ),
        (
            dedent("""\
            if 1 == 1:
                pass
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 1,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
            }
        ),
        (
            dedent("""\
            if n == 1:
                pass
            elif n == 2:
                pass
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 1,
                'superhelp.advisors.if_else_advisors.missing_else': 1,
            }
        ),
        (
            dedent("""\
            if n == 1:
                pass
            elif n == 2:
                pass
            else:
                pass
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 1,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                if n == 1:
                    pass
                elif n == 2:
                    pass
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 1,
                'superhelp.advisors.if_else_advisors.missing_else': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                if n == 1:
                    pass
                elif n == 2:
                    pass
                else:
                    pass
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 1,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                if n == 1:
                    pass
                elif n == 2:
                    pass
                else:
                    pass
            for i in range(2):
                if n == 1:
                    pass
                elif n == 2:
                    pass
                else:
                    pass
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 2,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                if n == 1:
                    pass
                elif n == 2:
                    pass
                else:
                    pass
            for i in range(2):
                if n == 1:
                    pass
                elif n == 2:
                    pass
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 2,
                'superhelp.advisors.if_else_advisors.missing_else': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
