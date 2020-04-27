"""
Method advisors are effectively function advisors and are covered there.
"""
from collections import defaultdict

from ..advisors import filt_block_advisor
from .. import conf
from ..utils import get_nice_str_list, layout_comment as layout

CLASS_XPATH = ('descendant-or-self::ClassDef')

@filt_block_advisor(xpath=CLASS_XPATH, warning=True)
def selfless_methods(block_dets, *, repeated_message=False):
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
    brief_msg = layout("""\

        ### Method doesn't use instance

        """)
    for class_name, method_names in class_selfless_methods.items():
        multiple = len(method_names) > 1
        if multiple:
            nice_list = get_nice_str_list(method_names, quoter='`')
            brief_msg += layout(f"""\

                Class `{class_name}` has the following methods that don't use
                the instance (usually called `self`): {nice_list}.
                """)
    if not repeated_message:
        brief_msg += layout("""\

            If a method doesn't use the instance it can be either pulled into a
            function outside the class definition or decorated with
            `@staticmethod`. The decorator stops the method expecting the
            instance object to be supplied as the first argument.

            """)
    main_msg = brief_msg

    if not repeated_message:
        main_msg += (
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

    if repeated_message:
        extra_msg = ''
    else:
        extra_msg = layout("""\
            It is not obligatory to call the first parameter of a bound method
            `self` but you should call it that unless you have a good reason to
            break convention.
            """)
    message = {
        conf.BRIEF: brief_msg,
        conf.MAIN: main_msg,
        conf.EXTRA: extra_msg,
    }
    return message

@filt_block_advisor(xpath=CLASS_XPATH, warning=True)
def one_method_classes(block_dets, *, repeated_message=False):
    """
    Look for classes with only one method (other than __init__) and suggest a
    simple function as an alternative..
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
    brief_msg = layout(f"""\

        ### Possible option of converting class{class_plural} to single function{func_plural}

        The following class{class_plural} only {class_have_has} one main
        function at most (excluding `__init__`):

        """)
    for class_name, method_name in classes_sole_methods:
        method2use = (
            f"`{method_name}`" if method_name else 'nothing but `__init__`')
        brief_msg += layout(f"""\
        - {class_name}: {method2use}
        """)
    if repeated_message:
        extra_msg = ''
    else:
        brief_msg += (
            layout(f"""\

                It may be simpler to replace the class{class_plural} with simple
                functions e.g. we could replace:

            """)
            +
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
            layout(f"""\

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
            layout(f"""\

                Sometimes, less is more. Bugs need somewhere to hide and
                unnecessarily verbose code gives them plenty of room to hide.

            """)
        )
        extra_msg = layout("""\
            Python allows procedural, object-oriented, and functional styles of
            programming. Event-based programming is also used in GUI contexts,
            for example. Programmers coming to Python from languages that only
            support object-orientation sometimes overdo the classes when there
            is a simpler, more elegant way of writing readable code in Python.

            If only a simple function is required, then write a simple function.

            Note - there may be exceptions. It has been suggested that the class
            structure can make it easier to test intermediate state rather than
            just function outputs. So, as with most things, it depends.
            """)
    message = {
        conf.BRIEF: brief_msg,
        conf.EXTRA: extra_msg,
    }
    return message
