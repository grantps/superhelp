from textwrap import dedent

from tests import check_as_expected, get_repeated_lines

ROOT = 'superhelp.helpers.nested_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'bloated_nested_block': 0,
            }
        ),
        (
            dedent("""\
            if 1 == 1:
                pass
            """),
            {
                ROOT + 'bloated_nested_block': 0,
            }
        ),
        (
            dedent(f"""\
            if 1 == 1:
                {get_repeated_lines(item='pass', lpad=16, n_lines=40)}
            """),
            {
                ROOT + 'bloated_nested_block': 1,
            }
        ),
        (
            dedent(f"""\
            for i in range(2):
                {get_repeated_lines(item='pass', lpad=16, n_lines=40)}
            """),
            {
                ROOT + 'bloated_nested_block': 1,
            }
        ),
        (
            dedent(f"""\
            while True:
                {get_repeated_lines(item='pass', lpad=16, n_lines=40)}
                break
            """),
            {
                ROOT + 'bloated_nested_block': 1,
            }
        ),
        (
            dedent(f"""\
            while True:
                {get_repeated_lines(item='pass', lpad=16, n_lines=40)}
                break
            for i in range(2):
                {get_repeated_lines(item='pass', lpad=16, n_lines=40)}
            """),
            {
                ROOT + 'bloated_nested_block': 2,
            }
        ),
        (
            dedent(f"""\
            while True:
                {get_repeated_lines(item='pass', lpad=16, n_lines=2)}
                break
            for i in range(2):
                {get_repeated_lines(item='pass', lpad=16, n_lines=40)}
            """),
            {
                ROOT + 'bloated_nested_block': 1,
            }
        ),
        (
            dedent(f"""\
            while True:
                for i in range(2):
                    {get_repeated_lines(item='pass', lpad=16, n_lines=40)}
                break
            """),
            {
                ROOT + 'bloated_nested_block': 1,  ## consolidated message
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
