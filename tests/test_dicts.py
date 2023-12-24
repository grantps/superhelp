from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.dict_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'dict_overview': 0,
                ROOT + 'mixed_key_types': 0,
            }
        ),
        (
            dedent("""\
            capitals = {
                'NZ': 'Wellington',
                'Australia': 'Canberra',
                'Japan': 'Tokyo',
            }
            """),
            {
                ROOT + 'dict_overview': 1,
                ROOT + 'mixed_key_types': 0,
            }
        ),
        (
            dedent("""\
            capitals = {


                'NZ': 'Wellington',
                'Australia': 'Canberra',
                'Japan': 'Tokyo',


            }
            """),
            {
                ROOT + 'dict_overview': 1,
                ROOT + 'mixed_key_types': 0,
            }
        ),
        (
            dedent("""\
            capitals = {
                'NZ': 'Wellington',
                'Australia': 'Canberra',
                'Japan': 'Tokyo',
            }
            capitals2 = {
                'NZ': 'Wellington',
                'Australia': 'Canberra',
                'Japan': 'Tokyo',
            }
            """),
            {
                ROOT + 'dict_overview': 2,
                ROOT + 'mixed_key_types': 0,
            }
        ),
        (
            dedent("""\
            mixed = {
                'a': 'string',
                1: 'integer',
            }
            """),
            {
                ROOT + 'dict_overview': 1,
                ROOT + 'mixed_key_types': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                mixed = {
                    'a': 'string',
                    1: 'integer',
                }
            """),
            {
                ROOT + 'dict_overview': 1,
                ROOT + 'mixed_key_types': 1,
            }
        ),
        (
            dedent("""\
            name = dict([('NZ', 'Wellington'), ('Australia', 'Canberra')])
            """),
            {
                ROOT + 'dict_overview': 1,
                ROOT + 'mixed_key_types': 0,
            }
        ),
        (
            dedent("""\
            name = dict([('NZ', 'Wellington'), (1, 'Canberra')])
            """),
            {
                ROOT + 'dict_overview': 1,
                ROOT + 'mixed_key_types': 1,
            }
        ),
        (
            dedent("""\
            name = dict([])
            """),
            {
                ROOT + 'dict_overview': 1,
                ROOT + 'mixed_key_types': 0,
            }
        ),
        (  ## old signature used to find dicts when actually a named tuple
            dedent("""\
            from collections import namedtuple

            Misc = namedtuple('Misc', 'a, b, c')
            """),
            {
                ROOT + 'dict_overview': 0,
            }
        )
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
