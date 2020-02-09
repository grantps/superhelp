import ast

import conf, html, syntaxer

statement = """names = [
    5, 'Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', 'Jess', 'Nicole',
]
"""

def get_item(item):
    try:
        item = item.n
    except AttributeError:
        item = item.s
    return item

def explain_list_pattern(objs):
    name_obj, list_obj = objs
    name = name_obj.id
    list_content = [get_item(elt) for elt in list_obj.elts]
    elt_types = set([type(elt).__name__ for elt in list_obj.elts])
    explanation = {
        conf.BRIEF: [
            conf.Explanation(
                conf.P,
                f"{name} = {list_content}"),
        ],
        conf.MAIN: [
            conf.Explanation(
                conf.H1,
                'Lists - one of the most important data structures in Python'),
            conf.Explanation(
                conf.P,
                f"The first item is {list_content[0]}"),
        ],
    }
    if len(elt_types) > 1:
        explanation[conf.EXTRA] = [
                conf.Explanation(
                    conf.H1,
                    ("WARNING!")),
                conf.Explanation(
                    conf.P,
                    ("Your list has more than one data type - that is almost "
                     "always a bad idea")),
            ]
    return explanation

def get_explanation(statement):
    try:
        parsed = ast.parse(statement)
    except SyntaxError as e:
        raise SyntaxError(
            f"Something is wrong with what you wrote - details: {e}")
    analyser = syntaxer.Analyser()
    analyser.visit(parsed)
    pattern_type, objs = analyser.get_patterns()
    if pattern_type == syntaxer.LIST_ONLY:
        explanation = explain_list_pattern(objs)
    else:
        raise Exception("Only simple lists are supported in the MVP")
    return explanation

def superhelp(statement):
    """
    Talk about the snippet supplied
    """
    try:
        explanation = get_explanation(statement)
        html.show_explanation(explanation)
    except Exception:
        raise Exception("Sorry Dave - I can't help you with that")

superhelp(statement)
