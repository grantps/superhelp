from textwrap import dedent

from tests import check_as_expected, get_repeated_lines, get_actual_result

from superhelp.helpers.func_help import count_args

excess_args = ', '.join(['arg' + str(i) for i in range(100)])

ROOT = 'superhelp.helpers.func_help.'

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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
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
                ROOT + 'mutable_default': 0,
            }
        ),
        (
            dedent(f"""\
            def demo(items=[]):
                pass
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
                ROOT + 'mutable_default': 1,
            }
        ),
        (
            dedent(f"""\
            class Demo:
                def demo(self, items=[]):
                    pass
            """),
            {
                ROOT + 'func_overview': 1,
                ROOT + 'func_len_check': 0,
                ROOT + 'func_excess_parameters': 0,
                ROOT + 'positional_boolean': 0,
                ROOT + 'docstring_issues': 1,
                ROOT + 'mutable_default': 1,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

def test_arg_count():
    """
    Testing positional-only arguments so Python 3.8+ only
    """
    xpath = 'descendant-or-self::FunctionDef'
    inc_posonly_func_snippet = dedent("""\
    def multifunc(posonly_arg1=1, posonly_arg2=[], /,
            arg1=2, arg2=3, arg3=[], *, kwonly_arg1={}):
        pass
    """)
    func_snippet1 = dedent("""\
    def multifunc(arg1=2, arg2=3, arg3=[], *, kwonly_arg1={}):
        pass
    """)
    func_snippet2 = dedent("""\
    def multifunc(arg1, arg2, arg3, arg4, arg5, arg6, arg7):
        pass
    """)
    tests = [
        (inc_posonly_func_snippet, count_args, 6),
        (func_snippet1, count_args, 4),
        (func_snippet2, count_args, 7),
    ]
    for snippet, test_func, expected_result in tests:
        actual_result = get_actual_result(snippet, xpath, test_func)
        assert expected_result == actual_result

# test_misc()
# test_arg_count()
