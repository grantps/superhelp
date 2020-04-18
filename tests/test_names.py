from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.name_advisors.name_check': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = 'cat'
            """),
            {
                'superhelp.advisors.name_advisors.name_check': 0,
            }
        ),
        (
            dedent("""\
            myPet = 'cat'
            """),
            {
                'superhelp.advisors.name_advisors.name_check': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                myPet = 'cat'
            """),
            {
                'superhelp.advisors.name_advisors.name_check': 1,
            }
        ),
        (
            dedent("""\
            def myPet():
                pass
            """),
            {
                'superhelp.advisors.name_advisors.name_check': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                def myPet():
                    pass
            """),
            {
                'superhelp.advisors.name_advisors.name_check': 1,
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
                'superhelp.advisors.name_advisors.name_check': 2,
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
                'superhelp.advisors.name_advisors.name_check': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
