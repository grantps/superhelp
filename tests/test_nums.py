from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.num_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'num_overview': 0,
            }
        ),
        (
            dedent("""\
            demo = [1, 2]
            """),
            {
                ROOT + 'num_overview': 0,
            }
        ),
        (
            dedent("""\
            demo = 1
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            demo1 = 1
            demo2 = 2
            """),
            {
                ROOT + 'num_overview': 2,  # two blocks so two messages
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = 1
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = 1
                demo2 = 2
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = 1
                demo2 = 2.666
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            class Demo:
                pass
            Demo.num = 5
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            mydict = {}
            mydict[1] = 5
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            mydict = {}
            mydict['val'] = 5
            """),
            {
                ROOT + 'num_overview': 1,
            }
        ),
        (
            dedent("""\
            mydict = {}
            mydict['val'] = '5'
            """),
            {
                ROOT + 'num_overview': 0,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
