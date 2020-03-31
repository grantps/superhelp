from advisors import advisor, get_element_name

import conf

@advisor(conf.LIST_ELEMENT_TYPE)
def list_overview(element):
    name = get_element_name(element)
    items = element[0]
    message = {
        conf.BRIEF: f"""
            #### Info on *{name}*\n
            *{name}* is a list with {len(items):,} items
        """,
    }
    return message

@advisor(conf.LIST_ELEMENT_TYPE, warning=True)
def mixed_list_types(element):
    """
    Warns about lists with mixed types.

    NOTE: This isn't actually checking variable types, just AST node types ;-)
    """
    item_types = sorted(set([item.tag for item in element[0]]))
    if len(item_types) <= 1:
        ## No explanation needed if there aren't multiple types.
        return None
    else:
        list_name = get_element_name(element)
        message = {
            conf.BRIEF: f"""
                #### Risky code - has mix of different data types
                *{list_name}* contains more than one data type -
                which is probably a bad idea.
            """,
            conf.MAIN: f"""
                #### Risky code - has mix of different data types
                *{list_name}* contains more than one data type -
                which is probably a bad idea. The data types found were:
                {", ".join(item_types)}.
            """,
        }
        return message

# To add more advice, just declare more advisor functions with the @advisor decorator!
