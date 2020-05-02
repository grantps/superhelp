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
import builtins
from collections import namedtuple
from importlib import import_module
import keyword
from pkgutil import iter_modules
import sys
from textwrap import dedent

from .. import conf
from ..utils import layout_comment as layout


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
            FiltAdvisorDets(
                f"{func.__module__}.{func.__name__}", func, xpath, warning))
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
            AnyBlockAdvisorDets(
                f"{func.__module__}.{func.__name__}", func, warning))
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
            SnippetAdvisorDets(
                f"{func.__module__}.{func.__name__}", func, warning))
        return func
    return decorator

def load_advisors():
    this_module = sys.modules[__name__]
    submodules = iter_modules(
        this_module.__path__,
        this_module.__name__ + '.')
    for submodule in submodules:
        import_module(submodule.name)


## =============================================================================


def is_reserved_name(name):
    is_reserved = name in set(keyword.kwlist + dir(builtins) + conf.STD_LIBS)
    return is_reserved

AOP_COMMENT = layout("""

    Some aspects of code apply to lots of different parts of the code base e.g.
    logging, or security. These can be thought of as "cross-cutting concerns"
    from an Aspect-Oriented Programming point of view. The problem is that a lot
    of code gets repeated e.g. if every function has to implement its own
    logging or has to handle its own security. Even if there is some shared
    functionality it can often require special wiring into other code. In
    short, coping with cross-cutting concerns can be painful.

    Decorators and Context Managers are ways Python provides of concentrating
    cross-cutting concerns into single pieces of code in an elegant way. They
    DRY out your code (see
    <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>). And because they
    are very widely used, it is worth learning how to use them, even if you
    don't take the step of writing your own.

    """)

UNPACKING_COMMENT = (
    layout("""\
        Unpacking is much more pythonic than using indexes to pull a sequence
        apart into names (variables). For example:

        """)
    +
    layout("""\

        #### Un-pythonic :-(

        location = (-37, 174, 'Auckland', 'Mt Albert')
        lat = location[0]
        lon = location[1]
        city = location[2]
        suburb = location[3]

        #### Pythonic :-)

        lat, lon, city, suburb = location
        """, is_code=True)
    +
    layout(f"""\

        If you don't need all the values you can indicate which you want to
        ignore or even mop up multiple unused values into a single value using
        an asterisk.

        For example:

        """)
    +
    layout("""\
        lat, lon, _city, _suburb = location
        """, is_code=True)
    +
    layout(f"""\

        or:

        """)
    +
    layout(f"""\
        lat, lon, *_ = location
        """, is_code=True)
    +
    layout("""\

        or:

        """)
    +
    layout("""\
        lat, lon, *unused = location
        """, is_code=True)
    +
    layout(f"""\

        Note - unused, in this case, would be ['Auckland', 'Mt Albert']

        """)
)

GENERAL_COMPREHENSION_COMMENT = layout("""\
    Comprehensions are one the great things about Python. To see why, have a
    look at Raymond Hettinger's classic talk "Transforming Code into Beautiful,
    Idiomatic Python" <https://youtu.be/OSGv2VnC0go?t=2738> where he explains
    the rationale. In short, if the goal of your code can be expressed as a
    single English sentence then it might belong on one line. The code should
    say what it is doing more than how it is doing it. Comprehensions are
    declarative and that is A Very Good Thing™.

    Pro tip: don't make comprehensions *in*comprehensions ;-). If your
    comprehension is hard to read it is probably better rewritten as a looping
    structure.
    """)

LIST_COMPREHENSION_COMMENT = (
    layout("""\

        #### Example List Comprehension:

        """)
    +
    layout("""\
        names_lengths = [
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
        ]
        """, is_code=True)
    +
    layout("""\

        produces an ordinary list:

        """)
    +
    layout(str(
        {
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
        }
        ))
    +
    layout("""\

        It is also possible to add a simple filter using `if`

        """)
    +
    layout("""\
        names_lengths = [
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            if not name.startswith('T')
        ]
        """, is_code=True)
    +
    layout("""\

        produces an ordinary list:

        """)
    +
    layout(str(
        {
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            if not name.startswith('T')
        }
        ))
)

DICT_COMPREHENSION_COMMENT = (
    layout("""\

    #### Example Dictionary Comprehension:

    """)
    +
    layout("""\
        country2capital = {{
            country: capital
            for country, capital in [('NZ', 'Wellington'), ('Italy', 'Rome')]
        }}
        """, is_code=True)
    +
    layout("""\

        produces an ordinary dictionary:

        """)
    +
    layout(str(
        {
            country: capital
            for country, capital
            in [('NZ', 'Wellington'), ('Italy', 'Rome')]
        }
        ))
    +
    layout("""\

        It is also possible to add a simple filter using `if`

        """)
    +
    layout("""\
        country2capital = {{
            country: capital
            for country, capital in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            if country == 'NZ'
        }}
        """, is_code=True)
    +
    layout("""\

        produces an ordinary dictionary:

        """)
    +
    layout(str(
        {
            country: capital
            for country, capital
            in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            if country == 'NZ'
        }
        ))
)

SET_COMPREHENSION_COMMENT = (
    layout("""\

        #### Example Set Comprehension

        """)
    +
    layout("""\
        pets = {{
            pet for _person, pet
            in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
        }}
        """, is_code=True)
    +
    layout("""\

        produces an ordinary set (i.e. unique members only):

        """)
    +
    layout(str(
        {
            pet for _person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
        }
        ))
    +
    layout("""\

        It is also possible to add a simple filter using `if`

        """)
    +
    layout("""\
        pets = {{
            pet for person, pet
            in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
            if person != 'Elliot'
        }}
        """, is_code=True)
    +
    layout("""\

        produces an ordinary set (i.e. unique members only):

        """)
    +
    layout(str(
        {
            pet for person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
                if person != 'Elliot'
        }
        ))
)

