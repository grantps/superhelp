from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            "pet = 'cat'",  ## snippet
            {
                'superhelp.advisors.list_advisors.list_overview': 0,
                'superhelp.advisors.list_advisors.mixed_list_types': 0,  ## basically banned
            }
        ),
        (
            "names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', ]",  ## snippet
            {
                'superhelp.advisors.list_advisors.list_overview': 1,
                'superhelp.advisors.list_advisors.mixed_list_types': 0,  ## basically banned
            }
        ),
        (
            dedent("""\
            persons = ['Noor', 'Grant', 'Hyeji']
            for person in persons:
                person_pets = ['cat', 'dog']
                person_toys = ['ball', 'doll', 'frisbee']
            """),
            {
                'superhelp.advisors.list_advisors.list_overview': 2,  ## both person_pets and person_toys are combined in one message so 1 + 1 it is
                'superhelp.advisors.list_advisors.mixed_list_types': 0,  ## basically banned
            }
        ),
        (
            dedent("""\
            import datetime
            from math import pi as π
            mixedTypes = [
                datetime.datetime.strptime('2020-02-10', '%Y-%m-%d'),
                π, 5, 1.234, 'Noor', False,
            ]
            """),
            {
                'superhelp.advisors.list_advisors.list_overview': 1,
                'superhelp.advisors.list_advisors.mixed_list_types': 1,
            }
        ),
        (
            dedent("""\
            import datetime
            from math import pi as π
            names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', ]
            for i in range(10):
                mixedTypes = [
                    datetime.datetime.strptime('2020-02-10', '%Y-%m-%d'),
                    π, 5, 1.234, 'Noor', False,
                ]
            """),
            {
                'superhelp.advisors.list_advisors.list_overview': 2,  ## should be a message for names and another message for the mixedTypes assignments (the fact it is in a loop is ignored thankfully)
                'superhelp.advisors.list_advisors.mixed_list_types': 1,  ## just once - see above
            }
        ),
        (
            dedent("""\
            names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', 'Jess', 'Nicole']
            names_lower = [name.lower() for name in names]  ## not a list assignment as such so handled as a list comprehension separately
            """),
            {
                'superhelp.advisors.list_advisors.list_overview': 1,  ## one list assignment only
                'superhelp.advisors.list_advisors.mixed_list_types': 0,
            }
        ),
        (
            dedent("""\
            def countPositivesAndNegatives(list):
                countNegative, countPositive = 0,0
                listToReturn = []
                for number in list:
                    if number > 0:
                        countPositive += 1 #increment by one
                    else:
                        countNegative+= number #incrementally sum
                listToReturn.append(countPositive)
                listToReturn.append(countNegative)
                return listToReturn
            """),
            {
                'superhelp.advisors.list_advisors.list_overview': 1,  ## one list assignment only even if we can't evaluate its content because not run, just part of a function definition
                'superhelp.advisors.list_advisors.mixed_list_types': 0,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
