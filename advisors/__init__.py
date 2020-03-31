"""
Advisors return None if a selected element doesn't match.

Warning - putting an explicit newline character (backslash n) before a line in a
message messes up dedenting and thus the markdown-to-HTML display. It is
treated as raw code which is probably not what you want.
"""
from collections import namedtuple
from importlib import import_module
from pkgutil import iter_modules
import sys

AdvisorDets = namedtuple('AdvisorDets', 'element_type, warning, advisor')

ADVISORS = {}

def get_element_name(element):
    """
    Python AST explorer: https://python-ast-explorer.com/
    """
    ## Get the name of the element if we can.
    name_elements = element.xpath('../../targets/Name')
    if len(name_elements) == 1 and name_elements[0].get('id'):
        name_id = name_elements[0].get('id')
        name = name_id
    else:
        name = 'Anonymous'
    return name

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
