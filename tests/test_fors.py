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
                'superhelp.advisors.for_advisors.for_overview': 0,  ## too long to get advice on a possible list comprehension etc
            }
        ),
        (
            dedent("""\
            name_lengths = []
            for name in ['Noor', 'Grant', ]:
                for pet in ['cat', 'dog']:
                    pass
            for name in ['Noor', 'Grant', ]:
                pass
            """),
            {
                'superhelp.advisors.for_advisors.for_overview': 1,  ## one is not too long to get advice on a possible list comprehension etc
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
