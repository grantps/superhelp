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
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
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
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
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
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
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
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
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
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
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
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
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
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
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
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
            }
        ),
        (
            dedent("""\
            if x == 'a' or x == 'b' or x == 'c':
                item = x
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 1,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
                'superhelp.advisors.if_else_advisors.split_group_membership': 1,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
            }
        ),
        (
            dedent("""\
            if x == 'a' or x == 'b' or x == 'c' or x is None:
                item = x
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 1,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,  ## only dealing with simple cases of all same type and either str or num
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                if x == 'a' or x == 'b' or x == 'c':
                    item = x
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 1,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
                'superhelp.advisors.if_else_advisors.split_group_membership': 1,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,
            }
        ),
        (
            dedent("""\
            if len(mylist) > 0:
                print(my_list)
            if len(mylist) >= 1:
                print(my_list)
            if len(mylist) == 0:
                print(my_list)
            if len(mylist) <= 0:
                print(my_list)
            if len(mylist) < 1:
                print(my_list)
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 5,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 1,  ## per block but no repeats
            }
        ),
        (
            dedent("""\
            if len(mylist) > 10:
                print(my_list)
            if len(mylist) >= 10:
                print(my_list)
            if len(mylist) == 10:
                print(my_list)
            if len(mylist) <= 1:
                print(my_list)
            if len(mylist) < 0:
                print(my_list)
            """),
            {
                'superhelp.advisors.if_else_advisors.if_else_overview': 5,
                'superhelp.advisors.if_else_advisors.missing_else': 0,
                'superhelp.advisors.if_else_advisors.split_group_membership': 0,
                'superhelp.advisors.if_else_advisors.implicit_boolean_enough': 0,  ## explicit counts not used as empty/non-empty boolean
            }
        ),
    ]
    check_as_expected(test_conf)

test_misc()
