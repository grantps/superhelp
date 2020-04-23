from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.advisors.name_advisors.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = 'cat'
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 1,
            }
        ),
        (
            dedent("""\
            myPet = 'cat'
            """),
            {
                ROOT + 'unpythonic_name_check': 1,
                ROOT + 'short_name_check': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                myPet = 'cat'
            """),
            {
                ROOT + 'unpythonic_name_check': 1,
                ROOT + 'short_name_check': 1,
            }
        ),
        (
            dedent("""\
            def myPet():
                pass
            """),
            {
                ROOT + 'unpythonic_name_check': 1,
                ROOT + 'short_name_check': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                def myPet():
                    pass
            """),
            {
                ROOT + 'unpythonic_name_check': 1,
                ROOT + 'short_name_check': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                def myPet():
                    pass
            for i in range(2):
                def myPet():
                    pass
            """),
            {
                ROOT + 'unpythonic_name_check': 2,
                ROOT + 'short_name_check': 2,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                def my_pet():
                    myCat = 'Boris'
            for i in range(2):
                def my_pet():
                    pass
            """),
            {
                ROOT + 'unpythonic_name_check': 1,
                ROOT + 'short_name_check': 2,
            }
        ),
        (
            dedent("""\
            for x, y in [(1, 2), (3, 4), ]:
                pass
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 1,  ## Looks at both together
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
