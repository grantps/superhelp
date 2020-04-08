"""
Add advisors modules inside this folder.

To add more advice, just declare more advisor functions inside the advisors
modules with the @type_advisor decorator :-).

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
from textwrap import dedent

import conf

## TYPE-specific advisors e.g. for list, or numbers etc

TYPE_ADVISORS = []
TypeAdvisorDets = namedtuple('ElementTypeAdvisorDets',
    'element_type, xml_root, warning, advisor_name, advisor')
TypeAdvisorDets.__doc__ += ('\n\nDetails for advisors which only work on '
    'specific element types')
TypeAdvisorDets.xml_root.__doc__ = ('XML starting point for xpath filtering to '
    'get specified element type e.g. body/Assign/value')
TypeAdvisorDets.advisor.__doc__ = ('Functions which takes prefiltered elements '
    'of the required type and return message')

## ALL Line advisors

ALL_LINE_ADVISORS = []
AllLineAdvisorDets = namedtuple(
    'AllLineAdvisorDets', 'warning, advisor_name, advisor')
AllLineAdvisorDets.__doc__ += ('\n\nDetails for advisors which only work on '
    'specific element types')
AllLineAdvisorDets.advisor.__doc__ = ('Functions which take line dets '
    '(including element and line code string) and return message')


def code_indent(text):
    lines = [conf.PYTHON_CODE_START] + text.split('\n') + [conf.PYTHON_CODE_END]
    indented_lines = [f"{' ' * 4}{line}" for line in lines]
    return f'\n'.join(indented_lines)

def get_assigned_name(element):
    """
    :return: None if no name (perhaps an incomplete expression) e.g.
      5, 1.123, in the middle of a multi-line list definition
    :rtype: str
    """
    ## Get the name of the element if we can.
    name_elements = element.xpath('targets/Name')
    if len(name_elements) == 1 and name_elements[0].get('id'):
        name_id = name_elements[0].get('id')
        name = name_id
    else:
        name = None
    return name

def type_advisor(*, element_type, xml_root, warning=False):
    """
    Simple decorator that registers an unchanged advisor function in the list of
    TYPE_ADVISORS.

    :param str element_type: e.g. conf.LIST_ELEMENT_TYPE
    :param str xml_root: Used by xpath on the line element being examined. Can
     use XPath 1.0 syntax.
    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        TYPE_ADVISORS.append(
            TypeAdvisorDets(
                element_type, xml_root, warning, func.__name__, func))
        return func
    return decorator

def gen_advisor(*, warning=False):
    """
    Simple decorator that registers an unchanged advisor function in the list of
    ALL_LINE_ADVISORS.

    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        ALL_LINE_ADVISORS.append(
            AllLineAdvisorDets(warning, func.__name__, func))
        return func
    return decorator

def load_advisors():
    this_module = sys.modules[__name__]
    submodules = iter_modules(
        this_module.__path__,
        this_module.__name__ + '.')
    for submodule in submodules:
        import_module(submodule.name)
