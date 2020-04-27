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
                ROOT + 'selfless_methods': 0,
            }
        ),
        (
            dedent("""\
            class Demo:
                pass
            """),
            {
                ROOT + 'one_method_classes': 1,
                ROOT + 'selfless_methods': 0,
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
                ROOT + 'selfless_methods': 1,
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
                ROOT + 'selfless_methods': 1,
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
                ROOT + 'selfless_methods': 1,
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
                ROOT + 'selfless_methods': 1,
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
                ROOT + 'selfless_methods': 1,
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
                ROOT + 'selfless_methods': 1,
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
                ROOT + 'selfless_methods': 1,
            }
        ),
        (
            dedent("""\
            class Demo:
                def one(self):
                    print(self)
                def two(self):
                    print(self)
            """),
            {
                ROOT + 'one_method_classes': 0,
                ROOT + 'selfless_methods': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                class Demo:
                    def one(self):
                        pass
                    def two(self):
                        print(self)
            """),
            {
                ROOT + 'one_method_classes': 0,
                ROOT + 'selfless_methods': 1,
            }
        ),
        (
            dedent("""\
            class Demo:
                def one(self):
                    print(self)
                def two(self):
                    print(self)
            class Demo2:
                def one(self):
                    pass
                def two(self):
                    pass
            """),
            {
                ROOT + 'one_method_classes': 0,
                ROOT + 'selfless_methods': 1,
            }
        ),
        (
            dedent("""\
            class Demo:
                def one(self):
                    pass
                def two(self):
                    pass
            class Demo2:
                def one(self):
                    pass
                def two(self):
                    pass
            """),
            {
                ROOT + 'one_method_classes': 0,
                ROOT + 'selfless_methods': 2,
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
