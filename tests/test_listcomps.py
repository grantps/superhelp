from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.listcomp_help.'

def test_misc():
    test_conf = [
        (
            "pet = 'cat'",  ## snippet
            {
                ROOT + 'listcomp_overview': 0,
            }
        ),
        (
            "names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', ]",  ## snippet
            {
                ROOT + 'listcomp_overview': 0,
            }
        ),
        (
            dedent("""\
            names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', ]
            names_lower = [name.lower() for name in names]  ## not a list assignment as such so handled as a list comprehension separately
            """),
            {
                ROOT + 'listcomp_overview': 1,
            }
        ),
        (
            dedent("""\
            names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', ]
            names_lower = [name.lower() for name in names]  ## not a list assignment as such so handled as a list comprehension separately
            evens_squared = [x**2 for x in range(1, 6) if x % 2 == 0]
            """),
            {
                ROOT + 'listcomp_overview': 2,
            }
        ),
        (
            dedent("""\
            names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', ]
            for i in range(2):
                names_lower = [name.lower() for name in names]  ## not a list assignment as such so handled as a list comprehension separately
            evens_squared = [x**2 for x in range(1, 6) if x % 2 == 0]
            """),
            {
                ROOT + 'listcomp_overview': 2,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
