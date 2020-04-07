from textwrap import dedent

import advisors
from advisors import gen_advisor, type_advisor
import conf

def get_func_name(element):
    """
    :return: None if no name
    :rtype: str
    """
    name = element.get('name')
    return name

@type_advisor(element_type=conf.FUNC_DEF_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY, warning=True)
def func_len_check(line_dets):
    name = get_func_name(line_dets.element)
    crude_loc = len(line_dets.line_code_str.split('\n'))
    if crude_loc < 3: #conf.MAX_BRIEF_FUNC_LOC:
        return None
    message = {
        conf.BRIEF: dedent(f"""\
            #### Function possibly too long

            `{name}` has {crude_loc:,} lines of code
            (including comments). Sometimes it is OK for a function to be that
            long but you should consider refactoring the code into smaller
            units.
            """)
    }
    return message

## TODO: too many parameters; camel case; boolean vars but not enforced keywords