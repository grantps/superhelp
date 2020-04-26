from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.advisors.class_advisors.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'one_method_classes': 0,
            }
        ),
        (
            dedent("""\
            class Demo:
                pass
            """),
            {
                ROOT + 'one_method_classes': 1,
            }
        ),
        (
            dedent("""\
            class Demo:
                def __init__(self):
                    pass
            """),
            {
                ROOT + 'one_method_classes': 1,
            }
        ),
        (
            dedent("""\
            class Demo:
                def __init__(self):
                    pass
                def one(self):
                    pass
            """),
            {
                ROOT + 'one_method_classes': 1,
            }
        ),
        (
            dedent("""\
            class Demo:
                def one(self):
                    pass
            """),
            {
                ROOT + 'one_method_classes': 1,
            }
        ),
        (
            dedent("""\
            class Demo:
                def __init__(self):
                    pass
                def one(self):
                    pass
                def two(self):
                    pass
            """),
            {
                ROOT + 'one_method_classes': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                class Demo:
                    def __init__(self):
                        pass
                    def one(self):
                        pass
                    def two(self):
                        pass
            """),
            {
                ROOT + 'one_method_classes': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                class Demo:
                    def __init__(self):
                        pass
                    def one(self):
                        pass
            """),
            {
                ROOT + 'one_method_classes': 1,
            }
        ),
        (
            dedent("""\
            class Demo:
                def one(self):
                    pass
                def two(self):
                    pass
            """),
            {
                ROOT + 'one_method_classes': 0,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
