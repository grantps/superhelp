"""
Add help modules inside this folder.

To add more helpers, just declare more helper functions inside the helpers
modules with the @..._help decorators :-). Make sure the first paragraph of the
docstring is a good, user-facing description of its purpose so it can be
automatically processed into lists of available help in SuperHELP.

So which help decorator to use?

Is the advice for the snippet as a whole? If so, are you processing the raw
snippet string or the XML code block elements? If processing the snippet string
e.g. passing into flake8 linter use snippet_str_help; if processing XML use
all_blocks_help.

If looking at individual code blocks, are you prefiltering or looking at every
sort? If prefiltering use filt_block_help; if not use any_block_help.
Simple really :-)

The basic pattern within an help function is:

* Get the correct elements and see if the target pattern is found e.g. a value
  being assigned to a name

* If not, exit returning None

* Otherwise create all the different message parts ready to assemble in the
  message.

  Some parts will have two versions - one for the first time the message appears
  for a block of the code snippet; and one for subsequent appearances. These
  "repeat" versions are sometimes empty strings; other times they are simply
  much shorter versions.

  Don't manually try to dedent etc the message parts - use the layout_comment
  function and follow the example of other helper modules. It is very easy to
  break markdown in ways which mess up the terminal output.

* Assemble the message. There can be up to three parts: brief, main, and extra.
  Only the brief component is mandatory. If not supplied, the main component is
  just a repeat of the brief component.

* Add to the appropriate test module. Only test helpers within the module.
"""
import builtins
from collections import namedtuple
from importlib import import_module
import keyword
from pkgutil import iter_modules
import sys
from textwrap import dedent

from .. import conf
from ..gen_utils import get_docstring_start, layout_comment as layout


FILT_BLOCK_HELPERS = []  ## block-based helpers which only apply to blocks filtered to contain specified element types

FiltHelperDets = namedtuple('FilteredHelperDets',
    'helper_name, helper, xpath, warning')
FiltHelperDets.__doc__ += ('\n\nDetails for block-based helpers that only '
    'apply to blocks filtered to contain specified elements')
FiltHelperDets.helper.__doc__ = ('Functions which takes prefiltered '
    'block dets containing the required elements and return message')
FiltHelperDets.xpath.__doc__ = ('xpath filtering to get specified elements '
    'e.g. body/Assign/value/Str')

ANY_BLOCK_HELPERS = []  ## block-based helpers which apply to all blocks

AnyBlockHelperDets = namedtuple('AnyBlockHelperDets',
    'helper_name, helper, warning')
AnyBlockHelperDets.__doc__ += (
    '\n\nDetails for block-based helpers that work on each block')
AnyBlockHelperDets.helper.__doc__ = ('Functions which take block dets '
    '(including element and block code string) and return message')

ALL_BLOCKS_HELPERS = []  ## all-blocks-based helpers (have to look at multiple blocks together at once)
AllBlocksHelperDets = namedtuple('AllBlocksHelperDets',
    'helper_name, helper, warning, input_type')
AllBlocksHelperDets.__doc__ += (
    '\n\nDetails for helpers that work on all blocks together')
AllBlocksHelperDets.helper.__doc__ = ('Functions which take blocks dets '
    '(multiple) and return message')
AllBlocksHelperDets.input_type.__doc__ = (
    'Input type for all blocks helper functions')

SNIPPET_STR_HELPERS = []  ## works on entire code snippet as a single string

SnippetStrHelperDets = namedtuple('SnippetStrHelperDets',
    'helper_name, helper, warning, input_type')
SnippetStrHelperDets.__doc__ += (
    '\n\nDetails for helpers that work on code snippet as a single string')
SnippetStrHelperDets.helper.__doc__ = ('Functions which take the snippet as a'
    ' single code str and return message')
SnippetStrHelperDets.input_type.__doc__ = (
    'Input type for all blocks helper functions')

def filt_block_help(*, xpath, warning=False):
    """
    Simple decorator that registers an unchanged helper function in the list of
    FILT_BLOCK_HELPERS.

    :param str xpath: Used by xpath on the block element being examined. Can
     only use XPath 1.0 syntax.
    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        """
        :param func func: func expecting block_dets
        """
        FILT_BLOCK_HELPERS.append(
            FiltHelperDets(
                f"{func.__module__}.{func.__name__}", func, xpath, warning))
        return func
    return decorator

def any_block_help(*, warning=False):
    """
    Simple decorator that registers an unchanged helper function in the list of
    ANY_BLOCK_HELPERS.

    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        """
        :param func func: func expecting block_dets
        """
        ANY_BLOCK_HELPERS.append(
            AnyBlockHelperDets(
                f"{func.__module__}.{func.__name__}", func, warning))
        return func
    return decorator

def all_blocks_help(*, warning=False):
    """
    Use when processing XML for all blocks at once. Probably looking for first
    instance of something rather than processing code block by code block.

    Simple decorator that registers an unchanged helper function in the list of
    ALL_BLOCKS_HELPERS.

    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        """
        :param func func: func expecting blocks_dets (note plural)
        """
        ALL_BLOCKS_HELPERS.append(
            AllBlocksHelperDets(f"{func.__module__}.{func.__name__}", func,
                warning, conf.BLOCKS_DETS))
        return func
    return decorator

def snippet_str_help(*, warning=False):
    """
    Use when processing the snippet string e.g. passing into flake8 linter.

    Simple decorator that registers an unchanged helper function in the list of
    SNIPPET_STR_HELPERS.

    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        """
        :param func func: func expecting a single code string for the entire
         snippet as input
        """
        SNIPPET_STR_HELPERS.append(
            SnippetStrHelperDets(f"{func.__module__}.{func.__name__}", func,\
                warning, conf.SNIPPET_STR))
        return func
    return decorator

def load_helpers():
    this_module = sys.modules[__name__]
    submodules = iter_modules(
        this_module.__path__,
        this_module.__name__ + '.')
    for submodule in submodules:
        import_module(submodule.name)

def get_helper_comments():
    helper_comments = []
    all_helpers_dets = (
        FILT_BLOCK_HELPERS + ANY_BLOCK_HELPERS + ALL_BLOCKS_HELPERS)
    all_helpers_dets.sort(key=lambda helper_dets: helper_dets.helper.__module__)
    for helper_dets in all_helpers_dets:
        docstring = helper_dets.helper.__doc__
        helper_comment = get_docstring_start(docstring)
        source = helper_dets.helper.__module__.split('.')[-1]
        warning = 'Warning: ' if helper_dets.warning else ''
        helper_comments.append((helper_comment, source, warning))
    return helper_comments

## =============================================================================

## Put into functions so layout etc overheads only incurred in cases when
## actually used

def is_reserved_name(name):
    is_reserved = name in set(keyword.kwlist + dir(builtins) + conf.STD_LIBS)
    return is_reserved

def get_aop_msg():
    return layout("""

        Some aspects of code apply to lots of different parts of the code base
        e.g. logging, or security. These can be thought of as "cross-cutting
        concerns" from an Aspect-Oriented Programming point of view. The problem
        is that a lot of code gets repeated e.g. if every function has to
        implement its own logging or has to handle its own security. Even if
        there is some shared functionality it can often require special wiring
        into other code. In short, coping with cross-cutting concerns can be
        painful.

        Decorators and Context Managers are ways Python provides of
        concentrating cross-cutting concerns into single pieces of code in an
        elegant way. They DRY out your code (see
        <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>). And because
        they are very widely used, it is worth learning how to use them, even if
        you don't take the step of writing your own.

    """)

def get_unpacking_msg():
    return (
        layout("""\
            Unpacking is much more pythonic than using indexes to pull a
            sequence apart into names (variables). For example:

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
            ignore or even mop up multiple unused values into a single value
            using an asterisk.

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

def get_general_comprehension_msg():
    return layout("""\
        Comprehensions are one the great things about Python. To see why, have a
        look at Raymond Hettinger's classic talk "Transforming Code into
        Beautiful, Idiomatic Python" <https://youtu.be/OSGv2VnC0go?t=2738> where
        he explains the rationale. In short, if the goal of your code can be
        expressed as a single English sentence then it might belong on one line.
        The code should say what it is doing more than how it is doing it.
        Comprehensions are declarative and that is A Very Good Thing™.

        Pro tip: don't make comprehensions *in*comprehensions ;-). If your
        comprehension is hard to read it is probably better rewritten as a
        looping structure.
        """)

def get_list_comprehension_msg():
    return (
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
        layout('`' + str(
            {
                len(name)
                for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            }
            ) + '`')
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
        layout('`' + str(
            {
                len(name)
                for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
                if not name.startswith('T')
            }
            ) + '`')
    )

def get_dict_comprehension_msg():
    return (
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
        layout('`' + str(
            {
                country: capital
                for country, capital
                in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            }
            ) + '`')
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
        layout('`' + str(
            {
                country: capital
                for country, capital
                in [('NZ', 'Wellington'), ('Italy', 'Rome')]
                if country == 'NZ'
            }
            ) + '`')
    )

def get_set_comprehension_msg():
    return (
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
        layout('`' + str(
            {
                pet for _person, pet
                    in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
            }
            ) + '`')
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
        layout('`' + str(
            {
                pet for person, pet
                    in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
                    if person != 'Elliot'
            }
            ) + '`')
    )
