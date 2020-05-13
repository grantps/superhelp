"""
Method advisors are effectively function advisors and are covered there.
"""
from collections import defaultdict

from ..advisors import filt_block_advisor
from .. import conf
from ..utils import get_nice_str_list, layout_comment as layout

CLASS_XPATH = ('descendant-or-self::ClassDef')

@filt_block_advisor(xpath=CLASS_XPATH, warning=True)
def getters_setters(block_dets, *, repeat=False):
    """
    Look for getters and setters and suggest @property if appropriate.
    """
    class_els = block_dets.element.xpath(CLASS_XPATH)
    if not class_els:
        return None
    class_getter_setter_methods = defaultdict(list)
    for class_el in class_els:
        class_name = class_el.get('name')
        method_els = class_el.xpath('body/FunctionDef')
        for method_el in method_els:
            method_name = method_el.get('name')
            if method_name.startswith(('set_', 'get_')):
                class_getter_setter_methods[class_name].append(method_name)
    if not class_getter_setter_methods:
        return None

    title = layout("""\
    ### Alternative to getters and setters
    """)
    simple_class_msg_bits = []
    for class_name, method_names in sorted(class_getter_setter_methods.items()):
        multiple = len(method_names) > 1
        if multiple:
            nice_list = get_nice_str_list(method_names, quoter='`')
            simple_class_msg_bits.append(layout(f"""\

            Class `{class_name}` has the following methods that look like either
            getters or setters: {nice_list}.
            """))
        else:
            method_type = (
                'getter' if method_name.startswith('get_') else 'setter')
            simple_class_msg_bits.append(layout(f"""\

            Class `{class_name}` has a `{method_names[0]}` method that looks
            like a {method_type}.
            """))
    simple_class_msg = ''.join(simple_class_msg_bits)
    if not repeat:
        properties_option = layout("""\

        Python doesn't need getters and setters. Instead, you can use
        properties. These are easily added using decorators e.g. `@property`.
        """)
        tm = '\N{TRADE MARK SIGN}'
        why_getters_etc = layout(f"""\

        A good discussion of getters, setters, and properties can be found at
        <https://www.python-course.eu/python3_properties.php>.

        Getters and setters are usually added in other languages such as Java
        because direct attribute access doesn't give the ability to calculate
        results or otherwise run a process when a value is accessed / written.

        And it is common for lots of getters and setters to be added, whether or
        not they are actually needed - Just In Case{tm}. The fear is that if you
        point other code to an attribute, and you later need to process the
        attribute or derive it before it is served up or stored, then you'll
        need to make a breaking change to your code. All the client code
        referencing the attribute will have to be rewritten to replace direct
        access with a reference to the appropriate getter or setter.
        Understandably then the inclination is to point to a getter or setter in
        the first case even if it doesn't actually do anything different (for
        now at least) from direct access. Using these getters and setters is
        wasteful, and bloats code unnecessarily, but it avoids the worse evil of
        regularly broken interfaces. The benefit is that you can change
        implementation later if you need to and nothing will break. But in
        Python there is a much better way :-).
        """)
        comparison = (
            layout(f"""\

            Let's compare the getter / setter approach and the property
            approach.

            #### Using getters / setters
            """)
            +
            layout("""
            class Person:

                def __init__(self, name):
                    self.__name = name

                def get_name(self):
                    return self.__name

                def set_name(self, name):
                    if name is not None:
                        self.__name = name
            """, is_code=True)
            +
            layout("""\
            #### Using properties
            """)
            +
            layout("""
            class Person:

                def __init__(self, name):
                    self.name = name

                @property  ## the getter
                def name(self):
                    return self.__name

                @name.setter  ## the setter
                def name(self, name):
                    if name is not None:
                        self.__name = name
            """, is_code=True)
            +
            layout("""\

            We must define the getter earlier in the script than the setter
            because the setter references the getter name. If it is not already
            defined above it we will get a `NameError` because Python doesn't
            yet know the variable_name part of the `@<variable_name>.setter`.

            In the `\_\_init\_\_` method we can either directly set the
            "private" variable `self.__name` (note - unenforced in Python)
            or set the public variable `self.name` and pass through the
            setter. Passing through the setter makes more sense - presumably
            there are some smarts in the setter we want applied otherwise we
            wouldn't have gone to the trouble of making it ;-).

            You will have also noticed that the method name is defined twice
            without the second one overwriting the first (the standard
            behaviour). The decorators take care of all that. The only thing to
            remember is to use exactly the same attribute name in three places
            (assuming both getting and setting):
            """)
            +
            layout("""\
            @property
            def here():  ## <== 1
                ...

            @here.setter  ## <== 2
            def here():  ## <== 3
                ...
            """, is_code=True)
        )
        deleter = (
            layout("""\

            Python also has a `deleter` decorator which handle deletion of the
            attribute e.g.
            """)
            +
            layout("""\
            @name.deleter
            def name(self):
                ...
            """, is_code=True)
        )
    else:
        properties_option = ''
        why_getters_etc = ''
        comparison = ''
        deleter = ''

    brief_msg = title + simple_class_msg + properties_option
    main_msg = (title + simple_class_msg + properties_option
        + why_getters_etc + comparison)
    extra_msg = deleter
    message = {
        conf.BRIEF: brief_msg,
        conf.MAIN: main_msg,
        conf.EXTRA: extra_msg,
    }
    return message

@filt_block_advisor(xpath=CLASS_XPATH, warning=True)
def selfless_methods(block_dets, *, repeat=False):
    """
    Look for class methods that don't use self as candidates for @staticmethod
    decorator. Note - not worried about detecting sophisticated cases with
    packing etc although it doesn't have to be named "self".
    """
    class_els = block_dets.element.xpath(CLASS_XPATH)
    if not class_els:
        return None
    class_selfless_methods = defaultdict(list)
    for class_el in class_els:
        class_name = class_el.get('name')
        method_els = class_el.xpath('body/FunctionDef')
        for method_el in method_els:
            method_name = method_el.get('name')
            arg_els = method_el.xpath('args/arguments/args/arg')
            if not arg_els:
                continue
            first_arg_name = arg_els[0].get('arg')
            used_first_names = [
                name_el for name_el in method_el.xpath('descendant::Name')
                if name_el.get('id') == first_arg_name]
            if not used_first_names:
                class_selfless_methods[class_name].append(method_name)
    if not class_selfless_methods:
        return None

    title = layout("""\
    ### Method doesn't use instance
    """)
    simple_class_msg_bits = []
    for class_name, method_names in sorted(class_selfless_methods.items()):
        multiple = len(method_names) > 1
        if multiple:
            nice_list = get_nice_str_list(method_names, quoter='`')
            simple_class_msg_bits.append(layout(f"""\

            Class `{class_name}` has the following methods that don't use the
            instance (usually called `self`): {nice_list}.
            """))
        else:
            simple_class_msg_bits.append(layout(f"""\

            Class `{class_name}` has a `{method_names[0]}` method that doesn't
            use the instance (usually called `self`).
            """))
    simple_class_msg = ''.join(simple_class_msg_bits)
    if not repeat:
        staticmethod_msg = layout("""\

        If a method doesn't use the instance it can be either pulled into a
        function outside the class definition or decorated with `@staticmethod`.
        The decorator stops the method expecting the instance object to be
        supplied as the first argument.
        """)
        staticmethod_demo = (
            layout("""
            For example, instead of:
            """)
            +
            layout("""
            def calc_approx_days(self, years):  ## <== self not used!
                return round(years * 365.25)
            """, is_code=True)
            +
            layout("""
            you could write:
            """)
            +
            layout("""
            @staticmethod
            def calc_approx_days(years):
                return round(years * 365.25)
            """, is_code=True)
        )
        call_it_self = layout("""\

        It is not obligatory to call the first parameter of a bound method
        `self` but you should call it that unless you have a good reason to
        break convention.
        """)
    else:
        staticmethod_msg = ''
        staticmethod_demo = ''
        call_it_self = ''

    brief_msg = title + simple_class_msg + staticmethod_msg
    main_msg = title + simple_class_msg + staticmethod_msg + staticmethod_demo
    extra_msg = call_it_self
    message = {
        conf.BRIEF: brief_msg,
        conf.MAIN: main_msg,
        conf.EXTRA: extra_msg,
    }
    return message

@filt_block_advisor(xpath=CLASS_XPATH, warning=True)
def one_method_classes(block_dets, *, repeat=False):
    """
    Look for classes with only one method (other than __init__) and suggest a
    simple function as an alternative.
    """
    class_els = block_dets.element.xpath(CLASS_XPATH)
    if not class_els:
        return None
    classes_sole_methods = []
    for class_el in class_els:
        method_els = class_el.xpath('body/FunctionDef')
        method_names = [method_el.get('name') for method_el in method_els]
        non_init_method_names = [method_name for method_name in method_names
            if method_name != '__init__']
        n_non_init_methods = len(non_init_method_names)
        if n_non_init_methods < 2:
            class_name = class_el.get('name')
            try:
                sole_method_name = non_init_method_names.pop()
            except IndexError:
                sole_method_name = None
            classes_sole_methods.append((class_name, sole_method_name))
    if not classes_sole_methods:
        return None

    multi_sole = len(classes_sole_methods) > 1
    class_plural = 'es' if multi_sole else ''
    class_have_has = 'have' if multi_sole else 'has'
    func_plural = 's' if multi_sole else ''
    summary = layout(f"""\

    ### Possible option of converting class{class_plural} to single
    function{func_plural}

    The following class{class_plural} only {class_have_has} one main method at
    most (excluding `__init__`):
    """)
    n_methods_msg_bits = []
    for class_name, method_name in classes_sole_methods:
        method2use = (f"`{method_name}`" if method_name
            else 'nothing but `__init__` (if even that)')
        n_methods_msg_bits.append(layout(f"""\
        - `{class_name}`: {method2use}
        """))
    n_methods_msg = ''.join(n_methods_msg_bits)
    if not repeat:
        not_just_oo = layout("""\

        Python allows procedural, object-oriented, and functional styles of
        programming. Event-based programming is also used in GUI contexts, for
        example. Programmers coming to Python from languages that only support
        object-orientation sometimes overdo the classes when there is a simpler,
        more elegant way of writing readable code in Python.

        If only a simple function is required, then write a simple function.

        Note - there may be exceptions. It has been suggested that the class
        structure can make it easier to test intermediate state rather than just
        function outputs. So, as with most things, it depends.
        """)
        function_option = layout(f"""\

        It may be simpler to replace the class{class_plural} with simple
        functions.
        """)
        function_demo = (
            layout('''\
            class GetSquare:

                def __init__(self, num):
                    self.num = num

                def get_square(self):
                    """
                    Get square of number
                    """
                    return self.num ** 2
            ''', is_code=True)
            +
            layout("""\
            with:
            """)
            +
            layout('''\
            def get_square(num):
                """
                Get square of number ...
                """
                return self.num ** 2
            ''', is_code=True)
            +
            layout("""\

            Sometimes, less is more. Bugs need somewhere to hide and
            unnecessarily verbose code gives them plenty of room to hide.
            """)
        )
    else:
        not_just_oo = ''
        function_option = ''
        function_demo = ''

    message = {
        conf.BRIEF: summary + n_methods_msg + function_option,
        conf.MAIN: summary + n_methods_msg + function_option + function_demo,
        conf.EXTRA: not_just_oo,
    }
    return message
