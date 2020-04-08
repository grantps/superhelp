from textwrap import dedent

import advisors
from advisors import shared, type_advisor
import code_execution, conf, utils

@type_advisor(element_type=conf.LISTCOMP_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def listcomp_overview(line_dets):
    name = advisors.get_assigned_name(line_dets.element)
    items = code_execution.get_val(
        line_dets.pre_line_code_str, line_dets.line_code_str, name)
    message = {
        conf.BRIEF: dedent(f"""
            `{name}` is a list comprehension returning a list
            with {utils.int2nice(len(items))} items: {items}
        """),
        conf.EXTRA: (
            dedent(f"""\
            #### Other "comprehensions"

            """)
            + shared.GENERAL_COMPREHENSION_COMMENT
            + dedent("""\


            List comprehensions aren't the only type of comprehension you can
            make. Python also lets you write Dictionary and Set Comprehensions:

            """)
            + shared.DICT_COMPREHENSION_COMMENT
            + '\n\n'
            + shared.SET_COMPREHENSION_COMMENT
            + '\n\n'
            + dedent("""\
            Pro tip: don't make comprehension *in*comprehensions ;-). If it is
            hard to read it is probably better written as a looping structure.
            """)
        ),
    }
    return message
