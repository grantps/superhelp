from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.name_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 0,
                ROOT + 'names_and_values': 0,
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
                ROOT + 'names_and_values': 0,
            }
        ),
        (
            dedent("""\
            myPet = 'cat'
            """),
            {
                ROOT + 'unpythonic_name_check': 1,
                ROOT + 'short_name_check': 0,
                ROOT + 'names_and_values': 0,
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
                ROOT + 'names_and_values': 0,
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
                ROOT + 'names_and_values': 0,
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
                ROOT + 'names_and_values': 0,
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
                ROOT + 'names_and_values': 0,
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
                ROOT + 'names_and_values': 0,
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
                ROOT + 'names_and_values': 0,
            }
        ),
        (
            dedent("""\
            people = ['Bob', 'Anj', 'Erin']
            person = people[2]
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 0,
                ROOT + 'names_and_values': 1,
            }
        ),
        (
            dedent("""\
            capitals = {'NZ': 'Wellington', 'Australia': 'Canberra'}
            nz_capital = capitals['NZ']
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 0,
                ROOT + 'names_and_values': 1,
            }
        ),
        (
            dedent("""\
            animal = 'cat'
            pet = animal
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 0,
                ROOT + 'names_and_values': 1,
            }
        ),
        (
            dedent("""\
            for item in range(2):
                animal = 'cat'
                pet = animal
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 0,
                ROOT + 'names_and_values': 1,
            }
        ),
        (
            dedent("""\
            class Family:
                pass
            Family.pet = 'cat'
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 0,
                ROOT + 'names_and_values': 0,
            }
        ),
        (
            dedent("""\
            pet = 'cat'
            class Family:
                pass
            Family.pet = pet
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 0,
                ROOT + 'names_and_values': 1,
            }
        ),
        (
            dedent("""\
            pet = 'cat'
            car = 'Porsche'
            vehicles = {}
            class Family:
                pass
            pet_car = (pet, car)
            Family.pet, vehicles['car'] = pet_car
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 0,
                ROOT + 'names_and_values': 1,
            }
        ),
        (
            dedent("""\
            details = [(1, 2), ]
            a, b = details[0]
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 1,
                ROOT + 'names_and_values': 1,
            }
        ),
        (
            dedent("""\
            details = [(1, 2), ]
            a, b = details[-1]
            """),
            {
                ROOT + 'unpythonic_name_check': 0,
                ROOT + 'short_name_check': 1,
                ROOT + 'names_and_values': 1,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
