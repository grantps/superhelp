"""
Main is not more material to add after Brief - it is a complete replacement of
it. Extra is additional to Main.
"""

from collections import namedtuple

import conf

RuleDets = namedtuple('RuleDets', 'element_type, warning, explainer')
Explanation = namedtuple('Explanation', 'semantic_role, msg')

RULES = {}

def rule(element_type, *, warning=False):
    """
    Simple decorator that registers an unchanged rule function in the list of
    RULES.

    :param bool warning: tags rules as warning or not - up to rendered e.g. HTML
     to decide what to do with that information, if anything.
    """
    def decorator(func):
        RULES[func.__name__] = RuleDets(element_type, warning, func)
        return func
    return decorator

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
        conf.BRIEF: [
            Explanation(conf.H1, f'Details for "{list_name}" list'),
            Explanation(conf.P, f'{list_name} has {len(items):,} elements'),
        ]
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
            conf.BRIEF: [
                Explanation(conf.H1, 'Risky code'),
                Explanation(conf.P,
                    (f'{list_name} contains more than one data type - probably '
                     'a bad idea.')),
            ],
            conf.MAIN: [
                Explanation(conf.H1, 'Dangers of mixed data types in lists'),
                Explanation(conf.P,
                    (f'{list_name} contains more than one data type - probably '
                     'a bad idea.')),
                Explanation(conf.P,
                    (f'{list_name} contains the following data types: '
                     f'{item_types}')),
            ],
        }
        return explanation

# To add more rules, just declare more rule functions with the @rule decorator!
