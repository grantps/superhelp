from collections import namedtuple
from importlib import import_module
from pkgutil import iter_modules
import sys

RuleDets = namedtuple('RuleDets', 'element_type, warning, explainer')
Explanation = namedtuple('Explanation', 'semantic_role, msg')

RULES = {}


def rule(element_type, *, warning=False):
    """
    Simple decorator that registers an unchanged rule function in the list of
    RULES.

    :param str element_type: e.g. conf.LIST_ELEMENT_TYPE
    :param bool warning: tags rules as warning or not - up to rendered e.g. HTML
     to decide what to do with that information, if anything.
    """
    def decorator(func):
        RULES[func.__name__] = RuleDets(element_type, warning, func)
        return func
    return decorator


def load_rules():
    this_module = sys.modules[__name__]
    submodules = iter_modules(this_module.__path__,
                              this_module.__name__ + '.')
    for submodule in submodules:
        import_module(submodule.name)
