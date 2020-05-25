from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.packing_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'unpacking': 0,
                ROOT + 'unpacking_opportunity': 0,
            }
        ),
        (
            dedent("""\
            x, y = coord
            """),
            {
                ROOT + 'unpacking': 1,
                ROOT + 'unpacking_opportunity': 0,
            }
        ),
        (
            dedent("""\
            x, y = coord1
            x, y = coord2
            """),
            {
                ROOT + 'unpacking': 2,
                ROOT + 'unpacking_opportunity': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                x, y = coord1
                x, y = coord2
            """),
            {
                ROOT + 'unpacking': 1,  ## in one block so one message
                ROOT + 'unpacking_opportunity': 0,
            }
        ),
        (
            dedent("""\
            x = coord[0]
            y = coord[1]
            """),
            {
                ROOT + 'unpacking': 0,
                ROOT + 'unpacking_opportunity': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                x = coord[0]
                y = coord[1]
            """),
            {
                ROOT + 'unpacking': 0,
                ROOT + 'unpacking_opportunity': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                x = coord1[0]
                y = coord1[1]
            for i in range(2):
                x = coord2[0]
                y = coord2[1]
            """),
            {
                ROOT + 'unpacking': 0,
                ROOT + 'unpacking_opportunity': 1,  ## snippet-level message so only the one
            }
        ),
        (
            dedent("""\
            nz_capital = capitals['NZ']
            aus_capital = capitals['Australia']
            """),
            {
                ROOT + 'unpacking': 0,
                ROOT + 'unpacking_opportunity': 0,  ## snippet-level message so only the one
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
