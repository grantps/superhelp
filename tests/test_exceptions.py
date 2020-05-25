from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.exception_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'exception_overview': 0,  ## one try block
                ROOT + 'unspecific_exception': 0,
            }
        ),
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
                ROOT + 'exception_overview': 1,  ## one try block
                ROOT + 'unspecific_exception': 0,
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
                ROOT + 'exception_overview': 1,
                ROOT + 'unspecific_exception': 1,
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
                ROOT + 'exception_overview': 1,
                ROOT + 'unspecific_exception': 1,
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
                ROOT + 'exception_overview': 1,  ## only one message because the message handles each exception internally - so still one message per snippet
                ROOT + 'unspecific_exception': 1,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
