"""
Method advisors are effectively function advisors and are covered there.
"""
from ..advisors import filt_block_advisor
from .. import conf
from ..utils import layout_comment as layout

CLASS_XPATH = ('descendant-or-self::ClassDef')

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
    brief_comment = layout(f"""\

        ### Possible option of converting class{class_plural} to single function{func_plural}

        The following class{class_plural} only {class_have_has} one main
        function at most (excluding `__init__`):

        """)
    for class_name, method_name in classes_sole_methods:
        method2use = (
            f"`{method_name}`" if method_name else 'nothing but `__init__`')
        brief_comment += layout(f"""\
        - {class_name}: {method2use}
        """)
    if repeated_message:
        extra_comment = ''
    else:
        brief_comment += (
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
        extra_comment = layout("""\
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
        conf.BRIEF: brief_comment,
        conf.EXTRA: extra_comment,
    }
    return message
