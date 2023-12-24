"""
Add help modules inside this folder.

To add more helpers, just declare more helper functions inside the helpers modules
with the @..._help decorators :-).

To identify xpath signatures for target language constructs use ast_funcs.general.ast_detective.

The load_helpers function below will import each of the helpers.
Doing so will trigger the decorators which will add the functions to some constants
ready to be applied to blocks (e.g. a class definition) or snippets (e.g. the entire content of a script).

Make sure the first paragraph of the docstring is a good, user-facing description of its purpose so it can be
automatically processed into lists of available help in SuperHELP.

So which help decorator to use?

Is the advice for the snippet as a whole? Perhaps commenting on the number of usages
and focusing some help on the first instance.

General comments will appear before the block-by-block comments.

    If so, are you processing the raw snippet string or the XML code block elements?
    If processing the snippet string e.g. passing into flake8 linter use snippet_str_help;
    if processing XML use multi_block_help.

If looking at individual code blocks and wanting to comment on each block individually use indiv_block_help.
For example:
Comments on block 1:
It is a list with four items namely ....
AND here are some general comments on lists;
Comments on block 2:
It is a list with three items namely ...
(not repeating general comments on lists)

Usually quite simple really :-)

Some helper modules will have both indiv and multi block_spec helpers.

Re: function signatures:
* block_spec for filt_block_help and any_block_help; block_specs (note plural)
  for snippet_str_help and all_blocks_help.
* kwargs is used to stop too many needless parameters when a function doesn't use everything supplied e.g. execute_code.
   (block_spec, *, repeat=False, **_kwargs)
or (block_spec, *, repeat=False, execute_code=True, **_kwargs)
See messages.get_message_dets_from_input() which actually runs the helper functions and supplies the arguments

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
from dataclasses import dataclass
from importlib import import_module
from pkgutil import iter_modules
import sys
from typing import Callable

from superhelp import conf
from superhelp.gen_utils import get_docstring_start, layout_comment as layout


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
        if not submodule.name.endswith('shared_messages'):
            import_module(submodule.name)  ## e.g. superhelp.helpers.class_help


class HelperSpec:
    pass

@dataclass(frozen=True)
class IndivBlockHelperSpec(HelperSpec):
    """
    Block-based helper functions that provide messages block by block spec (including element and block code string) and return a message.
    Might be looking exclusively at class blocks only.

    xpath: xpath filtering to get specified elements e.g. body/Assign/value/Str
    warning: tags messages as warning or not - up to displayer, e.g. HTML,
     to decide what to do with that information, if anything.
    """
    helper_name: str
    helper: Callable
    xpath: str | None = None
    warning: bool = False

@dataclass(frozen=True)
class OverallCodeHelperSpec(HelperSpec):
    """
    Helper functions which deal with the entire code snippet at once.
    Whether the input is a list of BlockSpec's or a snippet.
    """
    helper_name: str
    helper: Callable
    input_type: conf.InputType
    warning: bool = False

INDIV_BLOCK_HELPERS = []  ## block-based helpers
MULTI_BLOCK_HELPERS = []  ## looks at multiple blocks, possibly looking for first that meets a condition
SNIPPET_STR_HELPERS = []  ## works on entire code snippet as a single string

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
        MULTI_BLOCK_HELPERS.append(OverallCodeHelperSpec(
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
        SNIPPET_STR_HELPERS.append(OverallCodeHelperSpec(
            f"{func.__module__}.{func.__name__}", func, conf.InputType.SNIPPET_STR, warning))
        return func
    return decorator

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
