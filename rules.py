import conf

RULES = {}

def rule(selector):
    """
    Simple decorator that registers a rule in the list of RULES.
    """
    def decorator(func):
        RULES[func.__name__] = {'selector': selector, 'explainer': func}
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
        list_name = f'The "{name_id}" list'
    else:
        list_name = 'An anonymous list'
    return list_name

@rule('List')
def overview(line_no, element):
    list_name = _get_list_name(element)
    items = element[0]
    explanation = {
        conf.BRIEF: [
            conf.Explanation(conf.H1, f'Your list on line {line_no:,}'),
            conf.Explanation(
                conf.P, f'{list_name} has {len(items):,} elements'),
        ]
    }
    return explanation

@rule('List')
def mixed_list_rule(line_no, element):
    """
    Warns about lists with mixed types.

    NOTE: This isn't actually checking variable types, just AST node types ;-)
    """
    item_types = set([item.tag for item in element[0]])
    if len(item_types) <= 1:
        ## No explanation needed if there aren't multiple types.
        return None
    else:
        list_name = _get_list_name(element)
        explanation = {
            conf.BRIEF: [
                conf.Explanation(conf.H1, 'Risky code'),
                conf.Explanation(conf.P,
                    (f'{list_name} on line {line_no:,} contains more than one '
                     'data type, probably a bad idea.')),
            ],
            conf.MAIN: [
                conf.Explanation(
                    conf.H1, 'Dangers of mixed data types in lists'),
                conf.Explanation(conf.P,
                    (f'{list_name} contains the following data types: '
                     f'{item_types}')),
            ],
        }
        return explanation

# To add more rules, just declare more rule functions with the @rule decorator!
