"""
Add advisors modules inside this folder.

To add more advice, just declare more advisor functions inside the advisors
modules with the @advisor decorator!

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
TypeAdvisorDets = namedtuple(
    'TypeAdvisorDets', 'element_type, xml_root, warning, advisor_name, advisor')

## GENERIC advisors

GenericAdvisorDets = namedtuple(
    'GenericAdvisorDets', 'warning, advisor_name, advisor')

def name_style_check(element):
    name = get_name(element)
    if not name:
        return None
    all_lower_case = (name.lower() == name)
    all_upper_case = (name.upper() == name)
    if not (all_lower_case or all_upper_case):
        comment = dedent(f"""\
            #### UnPythonic name (`{name}`)

            Generally speaking Python variables should be snake case -
            that is lower case, with multiple words joined by underscores
            e.g. high_scores (not highScores or HighScores)
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
                usual snake case. E.g. collections.ChainMap

                Exceptions can also be made when a higher priority is
                consistency with other code e.g. a library the Python is ported
                from, or the non-Python code that Python is wrapping.
                """)
        ),
    }
    return message

GENERIC_ADVISORS = [
    GenericAdvisorDets(True, name_style_check.__name__, name_style_check),
]

def code_indent(text):
    lines = text.split('\n')
    indented_lines = [f"{' ' * 4}{line}" for line in lines]
    return f'\n'.join(indented_lines)

GENERAL_COMPREHENSION_COMMENT = dedent(f"""\
    Comprehensions are one the great things about Python. To see why,
    have a look at Raymond Hettinger's classic talk "Transforming Code
    into Beautiful, Idiomatic Python"
    https://youtu.be/OSGv2VnC0go?t=2738 where he explains the
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
        {conf.MD_PYTHON_CODE_START}
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
        {conf.MD_PYTHON_CODE_START}
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
            {conf.MD_PYTHON_CODE_START}
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
            {conf.MD_PYTHON_CODE_START}
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
            {conf.MD_PYTHON_CODE_START}
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
            {conf.MD_PYTHON_CODE_START}
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

def get_val(pre_line_code_str, line_code_str, name):
    """
    Executing supplied code from end users - nope - nothing to see here from a
    security point of view ;-) Needs addressing if this code is ever used as a
    service for other users.
    """
    exp_dets = {}
    exec(pre_line_code_str + line_code_str, exp_dets)
    try:
        val = exp_dets[name]
    except KeyError:
        raise KeyError(
            f"Unable to find name '{name}' in code_str\n{line_code_str}")
    return val

def advisor(*, element_type, xml_root, warning=False):
    """
    Simple decorator that registers an unchanged advisor function in the list of
    TYPE_ADVISORS.

    :param str element_type: e.g. conf.LIST_ELEMENT_TYPE
    :param bool warning: tags messages as warning or not - up to displayer
     e.g. HTML to decide what to do with that information, if anything.
    """
    def decorator(func):
        TYPE_ADVISORS.append(
            TypeAdvisorDets(
                element_type, xml_root, warning, func.__name__, func))
        return func
    return decorator

def load_advisors():
    this_module = sys.modules[__name__]
    submodules = iter_modules(
        this_module.__path__,
        this_module.__name__ + '.')
    for submodule in submodules:
        import_module(submodule.name)
