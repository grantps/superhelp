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

AllLineAdvisorDets = namedtuple(
    'AllLineAdvisorDets', 'warning, advisor_name, advisor')
AllLineAdvisorDets.__doc__ += ('\n\nDetails for advisors which only work on '
    'specific element types')
AllLineAdvisorDets.advisor.__doc__ = ('Functions which take line dets '
    '(including element and line code string) and return message')

def name_style_check(line_dets):
    name = get_assigned_name(line_dets.element)
    if not name:
        return None
    all_lower_case = (name.lower() == name)
    all_upper_case = (name.upper() == name)
    if not (all_lower_case or all_upper_case):
        comment = dedent(f"""\
            #### UnPythonic name (`{name}`)

            Generally speaking Python variables should be snake case -
            that is lower case, with multiple words joined by underscores
            e.g. `high_scores` (not `highScores` or `HighScores`)
            """)
    elif all_upper_case:
        comment = dedent(f"""\
            #### UnPythonic name (`{name}`)

            Upper case Python variables should only be used as 'constants'.
            When there are multiple parts, these are joined by underscores
            and the style is called screaming snake case :-)
            """)
    else:
        comment = None
    if not comment:
        return None
    message = {
        conf.BRIEF: comment,
        conf.MAIN: (
            comment
            + '\n\n'
            + dedent("""\
                In Python class names and named tuples are expected to be in
                Pascal Case (also known as upper camel case) rather than the
                usual snake case. E.g. `collections.ChainMap`

                Exceptions can also be made when a higher priority is
                consistency with other code e.g. a library the Python is ported
                from, or the non-Python code that Python is wrapping.
                """)
        ),
    }
    return message

ALL_LINE_ADVISORS = [
    AllLineAdvisorDets(True, name_style_check.__name__, name_style_check),
]

def code_indent(text):
    lines = [conf.PYTHON_CODE_START] + text.split('\n') + [conf.PYTHON_CODE_END]
    indented_lines = [f"{' ' * 4}{line}" for line in lines]
    return f'\n'.join(indented_lines)

GENERAL_COMPREHENSION_COMMENT = dedent(f"""\
    Comprehensions are one the great things about Python. To see why,
    have a look at Raymond Hettinger's classic talk "Transforming Code
    into Beautiful, Idiomatic Python"
    <https://youtu.be/OSGv2VnC0go?t=2738> where he explains the
    rationale. In short, if the goal of your code can be expressed as a
    single English sentence then it might belong on one line. The code
    should say what it is doing more than how it is doing it.
    Comprehensions are declarative and that is A Very Good Thing™.

    Pro tip: don't make comprehensions *in*comprehensions ;-).
    If your comprehension is hard to read it is probably better rewritten as a
    looping structure.
    """)

LIST_COMPREHENSION_COMMENT = (
    dedent("""\
    ##### Example List Comprehension:
    """)
    +
    code_indent(
    dedent(f"""\
        names_lengths = [
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
        ]
        """)
    )
    +
    dedent("""\

    produces an ordinary list:

    """)
    +
    dedent(str(
        {
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
        }
    ))
    +
    dedent("""\


    It is also possible to add a simple filter using `if`

    """)
    +
    code_indent(
    dedent(f"""\
        names_lengths = [
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            if not name.startswith('T')
        ]
        """)
    )
    +
    dedent("""\

    produces an ordinary list:

    """)
    +
    dedent(str(
        {
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            if not name.startswith('T')
        }
    ))
)

DICT_COMPREHENSION_COMMENT = (
    dedent("""\
    ##### Example Dictionary Comprehension:
    """)
    +
    code_indent(
        dedent(f"""\
            country2capital = {{
                country: capital
                for country, capital in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            }}
            """)
    )
    +
    dedent("""\

    produces an ordinary dictionary:

    """)
    +
    dedent(str(
        {
            country: capital
            for country, capital
            in [('NZ', 'Wellington'), ('Italy', 'Rome')]
        }
    ))
    +
    dedent("""\


    It is also possible to add a simple filter using `if`

    """)
    +
    code_indent(
        dedent(f"""\
            country2capital = {{
                country: capital
                for country, capital in [('NZ', 'Wellington'), ('Italy', 'Rome')]
                if country == 'NZ'
            }}
            """)
    )
    +
    dedent("""\

    produces an ordinary dictionary:

    """)
    +
    dedent(str(
        {
            country: capital
            for country, capital
            in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            if country == 'NZ'
        }
    ))
)

SET_COMPREHENSION_COMMENT = (
    dedent("""\
    ##### Example Set Comprehension
    """)
    +
    code_indent(
        dedent(f"""\
            pets = {{
                pet for _person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
            }}
            """)
    )
    +
    dedent("""\

    produces an ordinary set (i.e. unique members only):

    """)
    +
    dedent(str(
        {
            pet for _person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
        }
    ))
    +
    dedent("""\


    It is also possible to add a simple filter using `if`

    """)
    +
    code_indent(
        dedent(f"""\
            pets = {{
                pet for person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
                if person != 'Elliot'
            }}
            """)
    )
    +
    dedent("""\

    produces an ordinary set (i.e. unique members only):

    """)
    +
    dedent(str(
        {
            pet for person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
                if person != 'Elliot'
        }
    ))
)

def get_assigned_name(element):
    """
    Python AST explorer: https://python-ast-explorer.com/

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

def get_val(pre_line_code_str, line_code_str, name):
    """
    Executing supplied code from end users - nope - nothing to see here from a
    security point of view ;-) Needs addressing if this code is ever used as a
    service for other users.

    Note - can be the source of mysterious output in stdout (e.g. exec a print
    function).
    """
    exp_dets = {}
    exec(pre_line_code_str + line_code_str, exp_dets)
    try:
        val = exp_dets[name]
    except KeyError:
        val = None
#         raise KeyError(
#             f"Unable to find name '{name}' in code_str\n{line_code_str}")
    return val

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
