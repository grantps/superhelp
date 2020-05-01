from textwrap import dedent

from tests import check_as_expected, get_repeated_lines

excess_args = ', '.join(['arg' + str(i) for i in range(100)])

ROOT = 'superhelp.advisors.func_advisors.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'func_overview': 0,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 0,
            }
        ),
        (
            dedent("""\
            def square(num):
                return num ** 2
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
            }
        ),
        (
            dedent("""\
            def square(num):
                # faulty doc string
                return num ** 2
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            def square(num):
                {get_repeated_lines(item='pass', lpad=16, n_lines=100)}
                return num ** 2
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 1,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            def demo({excess_args}):
                return num ** 2
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 1,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            def demo({excess_args}, too_many=True, n_lines=2):
                return num ** 2
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 1,
                ROOT + 'positional_boolean': 1,
                ROOT + 'docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            def demo(too_many=True, n_lines=2):
                return None
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 1,
                ROOT + 'docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            def demo():
                '''
                One line
                '''
                return True
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            def demo():
                '''
                One line
                Two lines
                Three lines
                '''
                return True
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 0,  ## Just squeaks through
            }
        ),
        (
            dedent(f"""\
            def demo():
                {get_repeated_lines(item='', lpad=16, n_lines=100)}  ## if included would be enough to blow the limit
                {get_repeated_lines(item='pass', lpad=16, n_lines=8)}  ## only a few non-empty lines
                return True
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            class Demo:
                def demo(self):
                    '''
                    A short doc string only
                    '''
                    return True
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
            }
        ),
        (
            dedent(f"""\
            class Demo:
                def lacks_any_docstring(self):
                    666
                    name = 'Grant'
                    '''
                    Ho
                    '''
                    return True
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
