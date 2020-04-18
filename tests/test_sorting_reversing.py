from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.sorting_reversing_advisors.sorting_reversing_overview': 0,
                'superhelp.advisors.sorting_reversing_advisors.list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            pets = sorted(['cat', 'dog', 'budgie'])
            """),
            {
                'superhelp.advisors.sorting_reversing_advisors.sorting_reversing_overview': 1,
                'superhelp.advisors.sorting_reversing_advisors.list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            my_pets = sorted(['cat', 'dog', 'budgie'])
            your_pets = sorted(['cat', 'dog', 'budgie'])
            """),
            {
                'superhelp.advisors.sorting_reversing_advisors.sorting_reversing_overview': 2,
                'superhelp.advisors.sorting_reversing_advisors.list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            my_pets = reversed(['cat', 'dog', 'budgie'])
            your_pets = sorted(['cat', 'dog', 'budgie'])
            """),
            {
                'superhelp.advisors.sorting_reversing_advisors.sorting_reversing_overview': 2,
                'superhelp.advisors.sorting_reversing_advisors.list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                my_pets = reversed(['cat', 'dog', 'budgie'])
                your_pets = sorted(['cat', 'dog', 'budgie'])
            """),
            {
                'superhelp.advisors.sorting_reversing_advisors.sorting_reversing_overview': 1,
                'superhelp.advisors.sorting_reversing_advisors.list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            demo = [1, 2].sort()
            """),
            {
                'superhelp.advisors.sorting_reversing_advisors.sorting_reversing_overview': 1,
                'superhelp.advisors.sorting_reversing_advisors.list_sort_as_value': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo = [1, 2].sort()
            """),
            {
                'superhelp.advisors.sorting_reversing_advisors.sorting_reversing_overview': 1,
                'superhelp.advisors.sorting_reversing_advisors.list_sort_as_value': 1,
            }
        ),
        (
            dedent("""\
            my_pets = reversed(['cat', 'dog', 'budgie'])
            for i in range(2):
                demo = [1, 2].sort()
            """),
            {
                'superhelp.advisors.sorting_reversing_advisors.sorting_reversing_overview': 2,
                'superhelp.advisors.sorting_reversing_advisors.list_sort_as_value': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
