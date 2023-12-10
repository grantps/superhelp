"""
Add help modules inside this folder.

To add more helpers, just declare more helper functions inside the helpers modules
with the @..._help decorators :-).

The load_helpers function below will import each of the helpers.
Doing so will trigger the decorators which will add the functions to some constants
ready to be applied to blocks (e.g. a class definition) or snippets (e.g. the entire content of a script).

Make sure the first paragraph of the docstring is a good, user-facing description of its purpose so it can be
automatically processed into lists of available help in SuperHELP.

So which help decorator to use?

Is the advice for the snippet as a whole? If so, are you processing the raw snippet string
or the XML code block elements?
If processing the snippet string e.g. passing into flake8 linter use snippet_str_help;
if processing XML use collected_blocks_help.

If looking at individual code blocks, use indiv_block_help.
Simple really :-)

Re: function signatures:
* block_spec for filt_block_help and any_block_help; block_specs (note plural)
  for snippet_str_help and all_blocks_help.
* kwargs is used to stop too many needless parameters when a function doesn't use everything supplied e.g. execute_code.
   (block_spec, *, repeat=False, **_kwargs)
or (block_spec, *, repeat=False, execute_code=True, **_kwargs)

Re: decorator signatures, see actual code below after comment:

The basic pattern within a help function is:

* Get the correct elements and see if the target pattern is found e.g. a value being assigned to a name

* If not, exit returning None

* Otherwise create all the different message parts ready to assemble in the message.

  Some parts will have two versions - one for the first time the message appears for a block of the code snippet;
  and one for subsequent appearances.
  These "repeat" versions are sometimes empty strings; other times they are simply much shorter versions.

  Don't manually try to dedent and otherwise format the message parts - use the layout_comment function
  and follow the example of other helper modules.
  It is very easy to break markdown in ways which mess up the terminal output.

* Assemble the message. There can be up to three parts: brief, main, and extra.
  Only the brief component is mandatory. If not supplied, the main component is just a repeat of the brief component.

* Add to the appropriate test module. Only test helpers within the module.
"""
import builtins
from dataclasses import dataclass
from importlib import import_module
import keyword
from pkgutil import iter_modules
import sys
from typing import Callable

from superhelp import conf
from superhelp.gen_utils import get_docstring_start, layout_comment as layout


INDIV_BLOCK_HELPERS = []  ## block-based helpers

@dataclass(frozen=True)
class IndivBlockHelperSpec:
    """
    Block-based helper functions that take a block spec (including element and block code string) and return a message.
    Might be looking exclusively at class blocks only.

    xpath: xpath filtering to get specified elements e.g. body/Assign/value/Str
    warning: tags messages as warning or not - up to displayer, e.g. HTML,
     to decide what to do with that information, if anything.
    """
    helper_name: str
    helper: Callable
    xpath: str | None = None
    warning: bool = False

MULTI_BLOCK_HELPERS = []  ## looks at multiple blocks, possibly looking for first that meets a condition

@dataclass(frozen=True)
class MultipleBlocksHelperSpec:
    """
    Helper functions which deal with multiple block specs at once.
    E.g. looking at every block to look for opportunities to unpack.
    """
    helper_name: str
    helper: Callable
    input_type: conf.InputType
    warning: bool = False

SNIPPET_STR_HELPERS = []  ## works on entire code snippet as a single string

@dataclass(frozen=True)
class SnippetStrHelperSpec:  ## same structure as MultipleBlocksHelperSpec but helpers are different
    """
    Snippet-based helpers that work on code snippet as a single string and return message
    """
    helper_name: str
    helper: Callable
    input_type: conf.InputType
    warning: bool = False

def indiv_block_help(*, xpath: str | None = None, warning=False):
    """
    Simple decorator that registers a helper function in the list of INDIV_BLOCK_HELPERS.

    :param xpath: Used by xpath on the block element being examined. Can only use XPath 1.0 syntax.
    :param warning: tags messages as warning or not - up to displayer, e.g. HTML,
     to decide what to do with that information, if anything.
    """
    def decorator(func: Callable):
        """
        :param func func: func expecting block_spec
        """
        INDIV_BLOCK_HELPERS.append(IndivBlockHelperSpec(f"{func.__module__}.{func.__name__}", func, xpath, warning))
        return func
    return decorator

def multi_block_help(*, warning=False):
    """
    Simple decorator that registers a helper function in the list of MULTI_BLOCK_HELPERS.

    :param warning: tags messages as warning or not - up to displayer, e.g. HTML,
     to decide what to do with that information, if anything.
    """
    def decorator(func: Callable):
        """
        :param func: func expecting block_specs
        """
        MULTI_BLOCK_HELPERS.append(MultipleBlocksHelperSpec(
            f"{func.__module__}.{func.__name__}", func, conf.InputType.BLOCKS_SPECS, warning))
        return func
    return decorator

def snippet_str_help(*, warning=False):
    """
    Use when processing the snippet string e.g. passing into flake8 linter.

    Simple decorator that registers a helper function in the list of SNIPPET_STR_HELPERS.

    :param bool warning: tags messages as warning or not - up to displayer, e.g. HTML,
     to decide what to do with that information, if anything.
    """
    def decorator(func: Callable):
        """
        :param func func: func expecting a single code string for the entire snippet as input
        """
        SNIPPET_STR_HELPERS.append(
            SnippetStrHelperSpec(f"{func.__module__}.{func.__name__}", func, conf.InputType.SNIPPET_STR, warning))
        return func
    return decorator

def load_helpers():
    """
    Looking under this module package folder (i.e. helper) finds, for example:
        [ModuleInfo(module_finder=FileFinder('.../helpers'), name='superhelp.helpers.class_help', ispkg=False),
        ModuleInfo(module_finder=FileFinder('.../helpers'), name='superhelp.helpers.context_manager_help', ispkg=False),
        ModuleInfo(module_finder=FileFinder('.../helpers'), name='superhelp.helpers.dataclass_help', ispkg=False), ...
    and then loads them which then runs all the decorators which store the helper functions in the lists like
    INDIV_BLOCK_HELPERS and MULTI_BLOCK_HELPERS.
    """
    this_module = sys.modules[__name__]
    submodules = iter_modules(
        this_module.__path__,  ## e.g. ['/home/g/projects/superhelp/superhelp/helpers', ]
        this_module.__name__ + '.'  ## e.g. superhelp.helpers.
    )
    for submodule in submodules:
        import_module(submodule.name)

def get_helper_comments():
    helper_comments = []
    all_helpers_dets = (INDIV_BLOCK_HELPERS + MULTI_BLOCK_HELPERS + SNIPPET_STR_HELPERS)
    all_helpers_dets.sort(key=lambda helper_spec: helper_spec.helper.__module__)
    for helper_spec in all_helpers_dets:
        docstring = helper_spec.helper.__doc__
        helper_comment = get_docstring_start(docstring)
        source = helper_spec.helper.__module__.split('.')[-1]
        warning = 'Warning: ' if helper_spec.warning else ''
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
