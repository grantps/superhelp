from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.named_tuple_advisors.named_tuple_overview': 0,
            }
        ),
        (
            dedent("""\
            Person = namedtuple('PersonDetails', 'a, b, c')
            """),
            {
                'superhelp.advisors.named_tuple_advisors.named_tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                Person = namedtuple('PersonDetails', 'a, b, c')
            """),
            {
                'superhelp.advisors.named_tuple_advisors.named_tuple_overview': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                Person = namedtuple('PersonDetails', 'a, b, c')
                Person2 = namedtuple('PersonDetails2', 'a, b, c')
            """),
            {
                'superhelp.advisors.named_tuple_advisors.named_tuple_overview': 1, ## in one snippet so one message
            }
        ),
        (
            dedent("""\
            Person = namedtuple('PersonDetails', 'a, b, c')
            Person2 = namedtuple('PersonDetails2', 'a, b, c')
            Person3 = namedtuple('PersonDetails3', 'a, b, c')
            """),
            {
                'superhelp.advisors.named_tuple_advisors.named_tuple_overview': 1, ## in one snippet so one message
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
