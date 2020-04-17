from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            try:
                names = ['Noor', ]
                name_2 = names[1]
            except KeyError:
                pass
            except Exception:
                pass
            """),
            {
                'superhelp.advisors.exception_advisors.exception_overview': 1,  ## one try block
                'superhelp.advisors.exception_advisors.unspecific_exception': 0,
            }
        ),
        (
            dedent("""\
            try:
                names = ['Noor', ]
                name_2 = names[1]
            except Exception:
                pass
            """),
            {
                'superhelp.advisors.exception_advisors.exception_overview': 1,
                'superhelp.advisors.exception_advisors.unspecific_exception': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                try:
                    names = ['Noor', ]
                    name_2 = names[1]
                except Exception:
                    pass
            """),
            {
                'superhelp.advisors.exception_advisors.exception_overview': 1,
                'superhelp.advisors.exception_advisors.unspecific_exception': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                try:
                    names = ['Noor', ]
                    name_2 = names[1]
                except Exception:
                    pass
            for i in range(2):
                try:
                    names = ['Noor', ]
                    name_2 = names[1]
                except Exception:
                    pass
            for i in range(2):
                try:
                    names = ['Noor', ]
                    name_2 = names[1]
                except IndexError:
                    pass
            """),
            {
                'superhelp.advisors.exception_advisors.exception_overview': 1,  ## only one message because the message handles each exception internally - so still one message per snippet
                'superhelp.advisors.exception_advisors.unspecific_exception': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

test_misc()
