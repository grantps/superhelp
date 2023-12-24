from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.set_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'set_overview': 0,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            if 'chicken' in collection:
                collection.append('chicken')
            """),
            {
                ROOT + 'set_overview': 0,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            if 'chicken' not in collection:
                collection.append('chicken')
            """),
            {
                ROOT + 'set_overview': 0,
                ROOT + 'set_better_than_list': 1,
            }
        ),
        (
            dedent("""\
            if chicken not in collection:
                collection.append(chicken)
            """),
            {
                ROOT + 'set_overview': 0,
                ROOT + 'set_better_than_list': 1,
            }
        ),
        (
            dedent("""\
            if chicken in collection:
                collection.append(chicken)
            """),
            {
                ROOT + 'set_overview': 0,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            if verbose:
                flags.append('--progress')
            """),
            {
                ROOT + 'set_overview': 0,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            if msg:
                print(msg)
            """),
            {
                ROOT + 'set_overview': 0,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            num_set = {1, 2, 3}
            """),
            {
                ROOT + 'set_overview': 1,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            demo = set()
            """),
            {
                ROOT + 'set_overview': 1,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = set([1, 2, 3])
                demo2 = set([8, 9, 10])
            """),
            {
                ROOT + 'set_overview': 1,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            demo1 = set()
            demo2 = set()
            """),
            {
                ROOT + 'set_overview': 2,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                demo1 = set()
                demo2 = set()
            """),
            {
                ROOT + 'set_overview': 1,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            people = set(['Sam', 'Avi', 'Terri', 'Noor'])
            """),
            {
                ROOT + 'set_overview': 1,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (
            dedent("""\
            people = set([])
            """),
            {
                ROOT + 'set_overview': 1,
                ROOT + 'set_better_than_list': 0,
            }
        ),
        (  ## old signature was at risk of to finding sets when actually a named tuple
            dedent("""\
            from collections import namedtuple

            Misc = namedtuple('Misc', 'a, b, c')
            """),
            {
                ROOT + 'set_overview': 0,
            }
        )
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
