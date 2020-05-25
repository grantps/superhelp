from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.print_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'print_overview': 0,
            }
        ),
        (
            dedent("""\
            pet = 'cat'
            print(pet)
            """),
            {
                ROOT + 'print_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                print('Hi')
            """),
            {
                ROOT + 'print_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                print(f'Hi {i}')
            """),
            {
                ROOT + 'print_overview': 1,
            }
        ),
        (
            dedent("""\
            print('Hi')
            print('Hi')
            print('Hi')
            """),
            {
                ROOT + 'print_overview': 1,
            }
        ),
        (
            dedent("""\
            p = print
            p('Hi')
            p('Hi')
            """),
            {
                ROOT + 'print_overview': 1,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
