from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.context_manager_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'content_manager_overview': 0,
                ROOT + 'file_cm_needed': 0,
            }
        ),
        (
            dedent("""\
            open = 'Bad idea for a name but should flush out naive detection of open()'
            """),
            {
                ROOT + 'content_manager_overview': 0,
                ROOT + 'file_cm_needed': 0,
            }
        ),
        (
            dedent("""\
            with open('using_cm.txt') as f:
                text = f.read()
            """),
            {
                ROOT + 'content_manager_overview': 1,
                ROOT + 'file_cm_needed': 0,
            }
        ),
        (
            dedent("""\
            f = open('no_cm,txt')
            text = f.read()
            """),
            {
                ROOT + 'content_manager_overview': 0,
                ROOT + 'file_cm_needed': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                f = open('no_cm,txt')
                text = f.read()
            """),
            {
                ROOT + 'content_manager_overview': 0,
                ROOT + 'file_cm_needed': 1,
            }
        ),
        (
            dedent("""\
            f = open('no_cm,txt')
            text = f.read()
            with open('using_cm.txt') as f:
                text = f.read()
            """),
            {
                ROOT + 'content_manager_overview': 1,
                ROOT + 'file_cm_needed': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                with open('using_cm.txt') as f:
                    text = f.read()
            """),
            {
                ROOT + 'content_manager_overview': 1,
                ROOT + 'file_cm_needed': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                f = open('no_cm,txt')
                text = f.read()
                with open('using_cm.txt') as f:
                    text = f.read()
            """),
            {
                ROOT + 'content_manager_overview': 1,
                ROOT + 'file_cm_needed': 1,
            }
        ),
        (
            dedent("""\
            def test():
                pass
            """),
            {
                ROOT + 'content_manager_overview': 0,
                ROOT + 'file_cm_needed': 0,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
