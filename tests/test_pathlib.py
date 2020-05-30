from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.pathlib_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'using_os': 0,
            }
        ),
        (
            dedent("""\
            import os
            """),
            {
                ROOT + 'using_os': 0,
            }
        ),
        (
            dedent("""\
            import os
            os.path.join('a', 'b')
            """),
            {
                ROOT + 'using_os': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                import os
            """),
            {
                ROOT + 'using_os': 0,
            }
        ),
        (
            dedent("""\
            import os
            for i in range(2):
                os.path.join('a', 'b')
            """),
            {
                ROOT + 'using_os': 1,
            }
        ),
        (
            dedent("""\
            import os
            for i in range(2):
                os.getcwd()
            """),
            {
                ROOT + 'using_os': 1,
            }
        ),
        (
            dedent("""\
            import os
            for i in range(2):
                from os import getcwd
            """),
            {
                ROOT + 'using_os': 1,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
