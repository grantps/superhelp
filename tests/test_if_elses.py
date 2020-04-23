from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.advisors.if_else_advisors.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'if_else_overview': 0,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
            }
        ),
        (
            dedent("""\
            if 1 == 1:
                pass
            """),
            {
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
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
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 1,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
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
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
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
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 1,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
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
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
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
                ROOT + 'if_else_overview': 2,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
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
                ROOT + 'if_else_overview': 2,
                ROOT + 'missing_else': 1,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
            }
        ),
        (
            dedent("""\
            if x == 'a' or x == 'b' or x == 'c':
                item = x
            """),
            {
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 1,
                ROOT + 'implicit_boolean_enough': 0,
            }
        ),
        (
            dedent("""\
            if x == 'a' or x == 'b' or x == 'c' or x is None:
                item = x
            """),
            {
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 0,  ## only dealing with simple cases of all same type and either str or num
                ROOT + 'implicit_boolean_enough': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                if x == 'a' or x == 'b' or x == 'c':
                    item = x
            """),
            {
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 1,
                ROOT + 'implicit_boolean_enough': 0,
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
                ROOT + 'if_else_overview': 5,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 1,  ## per block but no repeats
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
                ROOT + 'if_else_overview': 5,
                ROOT + 'missing_else': 0,
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,  ## explicit counts not used as empty/non-empty boolean
            }
        ),
        (
            dedent("""\
            def centuryFromYear(year):
                if 1 <= year <= 100:
                    return 1
                else:
                    if year % 100 == 0:
                        return year // 100
                    return year // 100 + 1
            """),
            {
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 0,  ## saved from being an elif by having a return inside the else:
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
            }
        ),
        (
            dedent("""\
            def centuryFromYear(year):
                if 1 <= year <= 100:
                    return 1
                else:
                    if year % 100 == 0:
                        return year // 100
            #        return year // 100 + 1
            """),
            {
                ROOT + 'if_else_overview': 1,
                ROOT + 'missing_else': 1,  ## the else: if is effectively an elif because nothing else under it
                ROOT + 'split_group_membership': 0,
                ROOT + 'implicit_boolean_enough': 0,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
