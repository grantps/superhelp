from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.import_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'internal_imports': 0,
            }
        ),
        (
            dedent("""\
            import requests
            """),
            {
                ROOT + 'internal_imports': 0,
            }
        ),
        (
            dedent("""\
            import os
            """),
            {
                ROOT + 'internal_imports': 0,
            }
        ),
        (
            dedent("""\
            import os, requests
            """),
            {
                ROOT + 'internal_imports': 0,
            }
        ),
        (
            dedent("""\
            import os, conf
            """),
            {
                ROOT + 'internal_imports': 1,
            }
        ),
        (
            dedent("""\
            import conf
            """),
            {
                ROOT + 'internal_imports': 1,
            }
        ),
        (
            dedent("""\
            import conf, helper, displayer
            """),
            {
                ROOT + 'internal_imports': 1,
            }
        ),
        (
            dedent("""\
            from requests import get
            """),
            {
                ROOT + 'internal_imports': 0,
            }
        ),
        (
            dedent("""\
            from os import getcwd
            """),
            {
                ROOT + 'internal_imports': 0,
            }
        ),
        (
            dedent("""\
            import os as chicken, requests
            """),
            {
                ROOT + 'internal_imports': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                from os import getcwd
            """),
            {
                ROOT + 'internal_imports': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                from requests import get
            """),
            {
                ROOT + 'internal_imports': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                from qat import spatial
            """),
            {
                ROOT + 'internal_imports': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                from qat import mapping, spatial
            """),
            {
                ROOT + 'internal_imports': 1,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
