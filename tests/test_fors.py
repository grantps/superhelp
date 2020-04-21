from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            name_lengths = []
            """),
            {
                'superhelp.advisors.for_advisors.for_overview': 0,
                'superhelp.advisors.for_advisors.for_index_iteration': 0,
            }
        ),
        (
            dedent("""\
            name_lengths = []
            for name in ['Noor', 'Grant', ]:
                name_lengths.append(len(name))
            """),
            {
                'superhelp.advisors.for_advisors.for_overview': 1,
                'superhelp.advisors.for_advisors.for_index_iteration': 0,
            }
        ),
        (
            dedent("""\
            name_lengths = []
            for name in ['Noor', 'Grant', ]:
                for pet in ['cat', 'dog']:
                    pass
            """),
            {
                'superhelp.advisors.for_advisors.for_overview': 1,  ## the inner one not too long to get advice on a possible list comprehension etc
                'superhelp.advisors.for_advisors.for_index_iteration': 0,
            }
        ),
        (
            dedent("""\
            name_lengths = []
            for name in ['Noor', 'Grant', ]:
                for pet in ['cat', 'dog']:  ## <=========== short
                    pass
            for name in ['Noor', 'Grant', ]:  ## <=========== short
                pass
            for name in ['Noor', 'Grant', ]:
                pass
                pass
                pass
            for name in ['Noor', 'Grant', ]:  ## <=========== short
                pass
            """),
            {
                'superhelp.advisors.for_advisors.for_overview': 3,  ## three of four are not too long to get advice on a possible list comprehension etc
                'superhelp.advisors.for_advisors.for_index_iteration': 0,
            }
        ),
        (
            dedent("""\
            pets = ['cat', 'dog']
            for i in range(len(pets)):
                print(f"My {pets[i]}")
            """),
            {
                'superhelp.advisors.for_advisors.for_overview': 1,
                'superhelp.advisors.for_advisors.for_index_iteration': 1,
            }
        ),
        (
            dedent("""\
            for x in range(2):
                pets = ['cat', 'dog']
                for i in range(len(pets)):
                    comment = f"My {pets[i]}"
            """),
            {
                'superhelp.advisors.for_advisors.for_overview': 1,  ## one block
                'superhelp.advisors.for_advisors.for_index_iteration': 1,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
