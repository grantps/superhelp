import conf, html

statement = """names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', 'Jess', 'Nicole']"""

def get_item_type(item):
    raw_item_type = type(item)
    if raw_item_type.__name__ == 'list':
        item_type = conf.LIST
    else:
        raise Exception("Only list statements supported in MVP")
    return item_type

def explain_list(list_name, list_val):
    explanation = {
        conf.BRIEF: [
            conf.Explanation(
                conf.P,
                f"{list_name} = {list_val}"),
        ],
        conf.MAIN: [
            conf.Explanation(
                conf.H1,
                'Lists - one of the Big Two data structures in Python'),
            conf.Explanation(
                conf.P,
                f"The first item is {list_val[0]}"),
        ],
    }
    return explanation

def explain(name, val):
    item_type = get_item_type(val)
    if item_type == conf.LIST:
        explanation = explain_list(list_name=name, list_val=val)
    else:
        raise Exception(f"Unexpected item_type: {item_type}")
    return explanation


def get_name_val(statement):
    orig_locals = locals()
    new_locals = {}
    exec(statement, new_locals)
    new_keys = list(set(new_locals.keys()) - set(orig_locals.keys()))
    new_keys.remove('__builtins__')
    name = new_keys[0]
    val = new_locals[name]
    return name, val

def superhelp(statement):
    """
    Talk about the snippet supplied
    """
    name, val = get_name_val(statement)
    explanation = explain(name, val)
    html.show_explanation(explanation)
    return "Sorry Dave - I can't help you with that"

superhelp(statement)
