from textwrap import dedent

from tests import check_as_expected

pad = 16
pass_padding = ('\n' + (pad * ' ')).join(['pass']*100)

excess_args = ', '.join(['arg' + str(i) for i in range(100)])

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.func_advisors.func_overview': 0,
                'superhelp.advisors.func_advisors.func_len_check': 0,
                'superhelp.advisors.func_advisors.func_excess_parameters': 0,
                'superhelp.advisors.func_advisors.positional_boolean': 0,
                'superhelp.advisors.func_advisors.docstring_issues': 0,
            }
        ),
        (
            dedent("""\
            def square(num):
                return num ** 2
            """),
            {
                'superhelp.advisors.func_advisors.func_overview': 1,
                'superhelp.advisors.func_advisors.func_len_check': 0,
                'superhelp.advisors.func_advisors.func_excess_parameters': 0,
                'superhelp.advisors.func_advisors.positional_boolean': 0,
                'superhelp.advisors.func_advisors.docstring_issues': 1,
            }
        ),
        (
            dedent("""\
            def square(num):
                # faulty doc string
                return num ** 2
            """),
            {
                'superhelp.advisors.func_advisors.func_overview': 1,
                'superhelp.advisors.func_advisors.func_len_check': 0,
                'superhelp.advisors.func_advisors.func_excess_parameters': 0,
                'superhelp.advisors.func_advisors.positional_boolean': 0,
                'superhelp.advisors.func_advisors.docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            def square(num):
                {pass_padding}
                return num ** 2
            """),
            {
                'superhelp.advisors.func_advisors.func_overview': 1,
                'superhelp.advisors.func_advisors.func_len_check': 1,
                'superhelp.advisors.func_advisors.func_excess_parameters': 0,
                'superhelp.advisors.func_advisors.positional_boolean': 0,
                'superhelp.advisors.func_advisors.docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            def demo({excess_args}):
                return num ** 2
            """),
            {
                'superhelp.advisors.func_advisors.func_overview': 1,
                'superhelp.advisors.func_advisors.func_len_check': 0,
                'superhelp.advisors.func_advisors.func_excess_parameters': 1,
                'superhelp.advisors.func_advisors.positional_boolean': 0,
                'superhelp.advisors.func_advisors.docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            def demo({excess_args}, too_many=True, n_lines=2):
                return num ** 2
            """),
            {
                'superhelp.advisors.func_advisors.func_overview': 1,
                'superhelp.advisors.func_advisors.func_len_check': 0,
                'superhelp.advisors.func_advisors.func_excess_parameters': 1,
                'superhelp.advisors.func_advisors.positional_boolean': 1,
                'superhelp.advisors.func_advisors.docstring_issues': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
