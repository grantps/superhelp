from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.class_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'one_method_classes': 0,
                ROOT + 'selfless_methods': 0,
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
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
                ROOT + 'getters_setters': 0,
            }
        ),
        (
            dedent("""\
            class Demo:
                def __init__(self, x):
                    self.__x = x
                def get_x(self):
                    return self.__x
                def set_x(self, x):
                    self.__x  == x
            """),
            {
                ROOT + 'one_method_classes': 0,
                ROOT + 'selfless_methods': 0,
                ROOT + 'getters_setters': 1,
            }
        ),
        (
            dedent("""\
            from dataclass import dataclasses
            @dataclass
            class Demo:
                def __init__(self, x):
                    self.__x = x
                def get_x(self):
                    return self.__x
                def set_x(self, x):
                    self.__x  == x
            """),
            {
                ROOT + 'one_method_classes': 0,
                ROOT + 'selfless_methods': 0,
                ROOT + 'getters_setters': 0,  ## ignored because considered a dataclass and so should be handled by dataclass helper instead
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
