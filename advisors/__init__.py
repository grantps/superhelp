"""
Advisors return None if a selected element doesn't match.

WARNING: Dedenting can be broken by a single line which is not indented like the
rest. It is surprisingly easy to create this problem using new line characters
in your strings. So don't ;-). Use triple quotes and actual line breaks. Don't
believe me? See examples below:

Note - the backslash after the triple quotes below is a standard Python trick to
prevent an extra implicit new line character.

E.g. dedent(
'''\
    line 1
    line 2

    line 100\n Extra text  FAIL - will not dedent beyond the one space before 'Extra text'.
''')

E.g. dedent(
'''\
    line 1
    \nline 2  ## FAIL - no indentation for line 2 so no dedenting possible
''')

E.g. dedent(
'''\
    line 1\n  ## SUCCESS - lines 1 and 2 are indented and the new line character won't interfere
    line 2
''')

Subtle huh!!? And you thought whitespace in Python was a risk!
"""
from collections import namedtuple
from importlib import import_module
from pkgutil import iter_modules
import sys

import conf

AdvisorDets = namedtuple('AdvisorDets', 'element_type, warning, advisor')

ADVISORS = {}

def code_indent(text):
    lines = text.split('\n')
    indented_lines = [f"{' ' * 4}{line}" for line in lines]
    return f'\n'.join(indented_lines)

def get_name(element):
    """
    Python AST explorer: https://python-ast-explorer.com/

    :return: None if no name (perhaps an incomplete expression) e.g.
      5, 1.123, in the middle of a multi-line list definition
    :rtype: str
    """
    ## Get the name of the element if we can.
    name_elements = element.xpath('../../targets/Name')
    if len(name_elements) == 1 and name_elements[0].get('id'):
        name_id = name_elements[0].get('id')
        name = name_id
    else:
        name = None
    return name

def get_val(std_imports, code_str, name):
    """
    Executing supplied code from end users - nope - nothing to see here from a
    security point of view ;-) Needs addressing if this code is ever used as a
    service for other users.
    """
    exp_dets = {}
    exec(std_imports + code_str, exp_dets)
    try:
        val = exp_dets[name]
    except KeyError:
        raise KeyError(f"Unable to find name '{name}' in code_str\n{code_str}")
    return val

def advisor(element_type, *, warning=False):
    """
    Simple decorator that registers an unchanged advisor function in the list of
    ADVISORS.

    :param str element_type: e.g. conf.LIST_ELEMENT_TYPE
    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        ADVISORS[func.__name__] = AdvisorDets(element_type, warning, func)
        return func
    return decorator

def load_advisors():
    this_module = sys.modules[__name__]
    submodules = iter_modules(
        this_module.__path__,
        this_module.__name__ + '.')
    for submodule in submodules:
        import_module(submodule.name)
