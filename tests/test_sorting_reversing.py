from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.sorting_reversing_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'sorting_reversing_overview': 0,
                ROOT + 'list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            pets = sorted(['cat', 'dog', 'budgie'])
            """),
            {
                ROOT + 'sorting_reversing_overview': 1,
                ROOT + 'list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            my_pets = sorted(['cat', 'dog', 'budgie'])
            your_pets = sorted(['cat', 'dog', 'budgie'])
            """),
            {
                ROOT + 'sorting_reversing_overview': 2,
                ROOT + 'list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            my_pets = reversed(['cat', 'dog', 'budgie'])
            your_pets = sorted(['cat', 'dog', 'budgie'])
            """),
            {
                ROOT + 'sorting_reversing_overview': 2,
                ROOT + 'list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                my_pets = reversed(['cat', 'dog', 'budgie'])
                your_pets = sorted(['cat', 'dog', 'budgie'])
            """),
            {
                ROOT + 'sorting_reversing_overview': 1,
                ROOT + 'list_sort_as_value': 0,
            }
        ),
        (
            dedent("""\
            demo = [1, 2].sort()
            """),
            {
                ROOT + 'sorting_reversing_overview': 1,
                ROOT + 'list_sort_as_value': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo = [1, 2].sort()
            """),
            {
                ROOT + 'sorting_reversing_overview': 1,
                ROOT + 'list_sort_as_value': 1,
            }
        ),
        (
            dedent("""\
            my_pets = reversed(['cat', 'dog', 'budgie'])
            for i in range(2):
                demo = [1, 2].sort()
            """),
            {
                ROOT + 'sorting_reversing_overview': 2,
                ROOT + 'list_sort_as_value': 1,
            }
        ),
        (
            dedent("""\
            hours, mins, secs = Utils._get_time_parts_since_t1(t1)
            """),
            {
                ROOT + 'sorting_reversing_overview': 0,
                ROOT + 'list_sort_as_value': 0,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
