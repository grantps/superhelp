from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.lambda_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'lambda_advice': 0,
            }
        ),
        (
            dedent("""\
            a.sort(key=lambda x: x**2)
            """),
            {
                ROOT + 'lambda_advice': 1,
            }
        ),
        (
            dedent("""\
            normalized_colors = map(lambda s: s.casefold(), colors)
            """),
            {
                ROOT + 'lambda_advice': 1,
            }
        ),
        (
            dedent("""\
            total = reduce(lambda x, y: x + y, numbers)
            """),
            {
                ROOT + 'lambda_advice': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                total = reduce(lambda x, y: x + y, numbers)
            """),
            {
                ROOT + 'lambda_advice': 1,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
