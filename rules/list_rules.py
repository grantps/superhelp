from rules import rule

import conf

# Python AST explorer: https://python-ast-explorer.com/
# Selectors can use any CSS-style selector supported according to: https://cssselect.readthedocs.io/en/latest/#supported-selectors
#   - You could also use xpath instead of CSS-style if you wanted more power.
# Return None from a rule if it a selected element doesn't match.

def _get_list_name(list_element):
    ## Get the name of the list if we can.
    name_elements = list_element.xpath('../../targets/Name')
    if len(name_elements) == 1 and name_elements[0].get('id'):
        name_id = name_elements[0].get('id')
        list_name = name_id
    else:
        list_name = 'Anonymous'
    return list_name

@rule(conf.LIST_ELEMENT_TYPE)
def overview(element):
    list_name = _get_list_name(element)
    items = element[0]
    explanation = {
        conf.BRIEF: f"""
            #### Info on *{list_name}*\n
            *{list_name}* is a list with {len(items):,} items
        """,
    }
    return explanation

@rule(conf.LIST_ELEMENT_TYPE, warning=True)
def mixed_list_rule(element):
    """
    Warns about lists with mixed types.

    NOTE: This isn't actually checking variable types, just AST node types ;-)
    """
    item_types = sorted(set([item.tag for item in element[0]]))
    if len(item_types) <= 1:
        ## No explanation needed if there aren't multiple types.
        return None
    else:
        list_name = _get_list_name(element)
        explanation = {
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
        return explanation

# To add more rules, just declare more rule functions with the @rule decorator!
