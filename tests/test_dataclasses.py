from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.dataclass_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'dataclass_overview': 0,
            }
        ),
        (
            dedent("""\
            from dataclasses import dataclass

            @dataclass
            class Person:
                 fname: str
                 lname: str
                 age: int
            """),
            {
                ROOT + 'dataclass_overview': 1,
            }
        ),
        (
            dedent("""\
            from dataclasses import dataclass

            for i in range(2):
                @dataclass
                class Person:
                     fname: str
                     lname: str
                     age: int
            """),
            {
                ROOT + 'dataclass_overview': 1,  ## in one snippet so one message
            }
        ),
        (
            dedent("""\
            from dataclasses import dataclass

            for i in range(2):
                @dataclass
                class Person:
                     fname: str
                     lname: str
                     age: int

                @dataclass
                class Person2:
                     fname: str
                     lname: str
                     age: int
            """),
            {
                ROOT + 'dataclass_overview': 1,  ## in one snippet so still one message
            }
        ),
        (
            dedent("""\
            from dataclasses import dataclass

            @dataclass
            class Person:
                 fname: str
                 lname: str
                 age: int

            @dataclass
            class Person2:
                 fname: str
                 lname: str
                 age: int

            @dataclass
            class Person3:
                 fname: str
                 lname: str
                 age: int
            """),
            {
                ROOT + 'dataclass_overview': 1,
            }
        ),
        (
            dedent("""\
            from collections import namedtuple
            from dataclasses import dataclass

            @dataclass
            class Person:
                 fname: str
                 lname: str
                 age: int

            Fruit = namedtuple('Fruit', 'a, b, c')
            """),
            {
                ROOT + 'dataclass_overview': 0,  ## should be ignored because classes explained in named tuple check
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
