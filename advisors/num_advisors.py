from advisors import advisor, get_name, get_val

import conf

@advisor(conf.NUM_ELEMENT_TYPE)
def num_overview(element, code_str):
    name = get_name(element)
    if not name:
        return None
    val = get_val(code_str, name)
    val_type = type(val).__name__
    num_type = conf.CLASS2NAME[val_type]
    article = conf.CLASS2ARTICLE[val_type]
    message = {
        conf.BRIEF: f"""
            #### Info on *{name}*\n
            *{name}* is {article} {num_type}
        """,
    }
    return message

# To add more advice, just declare more advisor functions with the @advisor decorator!
