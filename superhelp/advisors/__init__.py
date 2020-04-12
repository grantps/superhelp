"""
Add advisors modules inside this folder.

To add more advice, just declare more advisor functions inside the advisors
modules with the @..._advisor decorators :-).

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

from .. import conf

FILT_BLOCK_ADVISORS = []  ## block-based advisors which only apply to blocks filtered to contain specified element types

FiltAdvisorDets = namedtuple('FilteredAdvisorDets',
    'advisor_name, advisor, xpath, warning')
FiltAdvisorDets.__doc__ += ('\n\nDetails for block-based advisors that only '
    'apply to blocks filtered to contain specified elements')
FiltAdvisorDets.advisor.__doc__ = ('Functions which takes prefiltered '
    'block dets containing the required elements and return message')
FiltAdvisorDets.xpath.__doc__ = ('xpath filtering to get specified elements '
    'e.g. body/Assign/value/Str')

ANY_BLOCK_ADVISORS = []  ## block-based advisors which apply to all blocks

AnyBlockAdvisorDets = namedtuple('AnyBlockAdvisorDets',
    'advisor_name, advisor, warning')
AnyBlockAdvisorDets.__doc__ += (
    '\n\nDetails for block-based advisors that work on each block')
AnyBlockAdvisorDets.advisor.__doc__ = ('Functions which take block dets '
    '(including element and block code string) and return message')

SNIPPET_ADVISORS = []  ## snippet-based advisors (have to look at multiple blocks at once)
SnippetAdvisorDets = namedtuple('SnippetAdvisorDets',
    'advisor_name, advisor, warning')
SnippetAdvisorDets.__doc__ += (
    '\n\nDetails for advisors that work on all blocks together')
SnippetAdvisorDets.advisor.__doc__ = ('Functions which take blocks dets '
    '(multiple) and return message')

def filt_block_advisor(*, xpath, warning=False):
    """
    Simple decorator that registers an unchanged advisor function in the list of
    FILT_BLOCK_ADVISORS.

    :param str xpath: Used by xpath on the block element being examined. Can
     only use XPath 1.0 syntax.
    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        """
        :param func func: func expecting block_dets
        """
        FILT_BLOCK_ADVISORS.append(
            FiltAdvisorDets(func.__name__, func, xpath, warning))
        return func
    return decorator

def any_block_advisor(*, warning=False):
    """
    Simple decorator that registers an unchanged advisor function in the list of
    ANY_BLOCK_ADVISORS.

    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        """
        :param func func: func expecting block_dets
        """
        ANY_BLOCK_ADVISORS.append(
            AnyBlockAdvisorDets(func.__name__, func, warning))
        return func
    return decorator

def snippet_advisor(*, warning=False):
    """
    Simple decorator that registers an unchanged advisor function in the list of
    ANY_BLOCK_ADVISORS.

    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        """
        :param func func: func expecting blocks_dets (note plural)
        """
        SNIPPET_ADVISORS.append(
            SnippetAdvisorDets(func.__name__, func, warning))
        return func
    return decorator

def load_advisors():
    this_module = sys.modules[__name__]
    submodules = iter_modules(
        this_module.__path__,
        this_module.__name__ + '.')
    for submodule in submodules:
        import_module(submodule.name)
