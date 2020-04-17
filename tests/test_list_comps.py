from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            "names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', ]",  ## snippet
            {
                'superhelp.advisors.listcomp_advisors.listcomp_overview': 0,
            }
        ),
        (
            dedent("""\
            names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', ]
            names_lower = [name.lower() for name in names]  ## not a list assignment as such so handled as a list comprehension separately
            """),
            {
                'superhelp.advisors.listcomp_advisors.listcomp_overview': 1,
            }
        ),
        (
            dedent("""\
            names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', ]
            names_lower = [name.lower() for name in names]  ## not a list assignment as such so handled as a list comprehension separately
            evens_squared = [x**2 for x in range(1, 6) if x % 2 == 0]
            """),
            {
                'superhelp.advisors.listcomp_advisors.listcomp_overview': 2,
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
                'superhelp.advisors.listcomp_advisors.listcomp_overview': 2,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
