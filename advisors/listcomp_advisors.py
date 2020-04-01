from advisors import advisor, get_name, get_val

import conf

@advisor(conf.LISTCOMP_ELEMENT_TYPE)
def listcomp_overview(element, code_str):
    name = get_name(element)
    items = get_val(code_str, name)
    message = {
        conf.BRIEF: f"""
            #### Info on *{name}*\n
            *{name}* is a list comprehension returning a list
            with {len(items):,} items: {items}
        """,
    }
    return message
