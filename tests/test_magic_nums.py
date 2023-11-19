from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.magic_num_help.'

def test_misc():
    test_conf = [
        (
            "pet = 'cat'",
            {
                ROOT + 'magic_number': 0,  ## expect 0 times
            }
        ),
        (
            "num = 123",
            {
                ROOT + 'magic_number': 0,
            }
        ),
        (
            dedent("""\
            if num == 123:
                is_num = True
            """),
            {
                ROOT + 'magic_number': 1,  ## expect 1 warning about a magic_number
            }
        ),
        (
            dedent("""\
            if num == -123:
                is_num = True
            """),
            {
                ROOT + 'magic_number': 1,
            }
        ),
        (
            dedent("""\
            if num != -123:
                is_num = True
            """),
            {
                ROOT + 'magic_number': 1,
            }
        ),
        (
            dedent("""\
            if num != -1:  ## not magic
                is_num = True
            """),
            {
                ROOT + 'magic_number': 0,
            }
        ),
        (
            dedent("""\
            if num != 100:  ## not magic
                is_num = True
            """),
            {
                ROOT + 'magic_number': 0,
            }
        ),
        (
            dedent("""\
            if status == 404:  ## not magic
                fail = True
            """),
            {
                ROOT + 'magic_number': 0,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
