from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.packing_advisors.unpacking': 0,
                'superhelp.advisors.packing_advisors.unpacking_opportunity': 0,
            }
        ),
        (
            dedent("""\
            x, y = coord
            """),
            {
                'superhelp.advisors.packing_advisors.unpacking': 1,
                'superhelp.advisors.packing_advisors.unpacking_opportunity': 0,
            }
        ),
        (
            dedent("""\
            x, y = coord1
            x, y = coord2
            """),
            {
                'superhelp.advisors.packing_advisors.unpacking': 2,
                'superhelp.advisors.packing_advisors.unpacking_opportunity': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                x, y = coord1
                x, y = coord2
            """),
            {
                'superhelp.advisors.packing_advisors.unpacking': 1,  ## in one block so one message
                'superhelp.advisors.packing_advisors.unpacking_opportunity': 0,
            }
        ),
        (
            dedent("""\
            x = coord[0]
            y = coord[1]
            """),
            {
                'superhelp.advisors.packing_advisors.unpacking': 0,
                'superhelp.advisors.packing_advisors.unpacking_opportunity': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                x = coord[0]
                y = coord[1]
            """),
            {
                'superhelp.advisors.packing_advisors.unpacking': 0,
                'superhelp.advisors.packing_advisors.unpacking_opportunity': 1,
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
                'superhelp.advisors.packing_advisors.unpacking': 0,
                'superhelp.advisors.packing_advisors.unpacking_opportunity': 1,  ## snippet-level message so only the one
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
