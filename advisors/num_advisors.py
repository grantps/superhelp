from advisors import advisor, get_element_name

import conf

@advisor(conf.NUM_ELEMENT_TYPE)
def num_overview(element):
    name = get_element_name(element)
    message = {
        conf.BRIEF: f"""
            #### Info on *{name}*\n
            *{name}* is a number
        """,
    }
    return message

# To add more advice, just declare more advisor functions with the @advisor decorator!
