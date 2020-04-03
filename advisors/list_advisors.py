from textwrap import dedent

import advisors
from advisors import advisor
import conf

@advisor(element_type=conf.LIST_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def list_overview(element, std_imports, code_str):
    name = advisors.get_name(element)
    items = advisors.get_val(std_imports, code_str, name)
    message = {
        conf.BRIEF: dedent(f"""
            `{name}` is a list with {len(items):,} items
        """),
    }
    return message

@advisor(element_type=conf.LIST_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE, warning=True)
def mixed_list_types(element, pre_line_code_str, line_code_str):
    """
    Warns about lists with mixed types.

    NOTE: This isn't actually checking variable types, just AST node types ;-)
    """
    name = advisors.get_name(element)
    items = advisors.get_val(pre_line_code_str, line_code_str, name)
    item_types = sorted(set([
        conf.CLASS2NAME.get(type(item).__name__, type(item).__name__)
        for item in items]
    ))
    if len(item_types) <= 1:
        ## No explanation needed if there aren't multiple types.
        return None
    else:
        message = {
            conf.BRIEF: dedent(f"""
                #### Mix of different data types in list
                `{name}` contains more than one data type -
                which is probably a bad idea.
            """),
            conf.MAIN: dedent(f"""
                #### Mix of different data types in list
                `{name}` contains more than one data type -
                which is probably a bad idea. The data types found were:
                {", ".join(item_types)}.
            """),
        }
        return message
