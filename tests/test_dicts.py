from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.dict_advisors.dict_overview': 0,
                'superhelp.advisors.dict_advisors.mixed_key_types': 0,
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
                'superhelp.advisors.dict_advisors.dict_overview': 1,
                'superhelp.advisors.dict_advisors.mixed_key_types': 0,
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
                'superhelp.advisors.dict_advisors.dict_overview': 1,
                'superhelp.advisors.dict_advisors.mixed_key_types': 0,
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
                'superhelp.advisors.dict_advisors.dict_overview': 2,
                'superhelp.advisors.dict_advisors.mixed_key_types': 0,
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
                'superhelp.advisors.dict_advisors.dict_overview': 1,
                'superhelp.advisors.dict_advisors.mixed_key_types': 1,
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
                'superhelp.advisors.dict_advisors.dict_overview': 1,
                'superhelp.advisors.dict_advisors.mixed_key_types': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
