from collections import namedtuple

from . import conf
from .gen_utils import layout_comment as layout

## extract patterns e.g. from:
## /tmp/snippet.py:1:23: W291 trailing whitespace
## /tmp/snippet.py:4:1: E999 IndentationError: unexpected indent
LINT_PATTERN = fr"""^.+?:                                  ## starts with misc until first colon e.g. /tmp/snippet.py: (+? to be non-greedy)
        (?P<{conf.LINT_LINE_NO}>\d+)                       ## line_no = one or more digits after snippet.py: and before the next : e.g. 4  # @UndefinedVariable
        :\d+:\s{{1}}                                       ## one or more digits, :, and one space e.g. '1: '
        (?P<{conf.LINT_MSG_TYPE}>\w{{1}}\d{{1,3}})\s{{1}}  ## msg_type = (one letter, 1-3 digits) and one space e.g. 'E999 '
        (?P<{conf.LINT_MSG}>.*)                            ## msg = everything else e.g. 'IndentationError: unexpected indent'
    """

## https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes
## https://flake8.pycqa.org/en/latest/user/error-codes.html
IGNORED_LINT_RULES = [
    'E266', 'E262',  ## I like ## before comments and # before commented out code (idea copied off Tom Eastman - thanks Tom!)
    'E305',  ## for classes I agree with 2 spaces but not functions
    'W292',  ## no newline at end of file inappropriate for snippets as opposed to modules
]

def title2msg_type(title):
    return title.upper().replace(' ', '_') + '_MSG_TYPE'
## Ensure brief AND main are the same so titles don't shift when
## changing message level
line_indentation_title = "Line indentation issues"
whitespace_title = "White space issues"
blank_line_title = "Blank line issues"
line_length_title = "Excessive line length"
unused_imports_title = "Unused imports"
undefined_names_title = "Undefined names"
## nice to keep placeholder names etc aligned with actual titles but nothing breaks if we don't
LINE_INDENTATION_MSG_TYPE = title2msg_type(line_indentation_title)
WHITESPACE_MSG_TYPE = title2msg_type(whitespace_title)
BLANK_LINES_MSG_TYPE = title2msg_type(blank_line_title)
LINE_LENGTH_MSG_TYPE = title2msg_type(line_length_title)
UNUSED_IMPORTS_MSG_TYPE = title2msg_type(unused_imports_title)
UNDEFINED_NAMES_MSG_TYPE = title2msg_type(undefined_names_title)

def consolidated_msg_type(msg_type):
    if msg_type.startswith('E1'):
        msg_type = LINE_INDENTATION_MSG_TYPE
    elif msg_type.startswith('E2'):
        msg_type = WHITESPACE_MSG_TYPE
    elif msg_type.startswith('E3'):
        msg_type = BLANK_LINES_MSG_TYPE
    elif msg_type == 'E501':
        msg_type = LINE_LENGTH_MSG_TYPE
    elif msg_type == 'F401':
        msg_type = UNUSED_IMPORTS_MSG_TYPE
    elif msg_type == 'F821':
        msg_type = UNDEFINED_NAMES_MSG_TYPE
    return msg_type

LevelMsgs = namedtuple('LintMsgsByLevel', 'brief, main, extra')

undefined_names_level_msgs = LevelMsgs(
    layout(f"""

        #### {undefined_names_title}

        The linter has raised questions about undefined names.

        """),
    layout(f"""\

        #### {undefined_names_title}

        The linter has raised questions about undefined names. That isn't a
        problem if the snippet was extracted from a larger piece of code and the
        names were defined before the snippet.

        """),
    ''
)

unused_imports_level_msgs = LevelMsgs(
    layout(f"""\

        #### {unused_imports_title}

        One or more imports have not been used in the snippet.

        """),
    layout(f"""\

        #### {unused_imports_title}

        One or more imports have not been used in the snippet. That isn't a
        problem if the snippet was extracted from a larger piece of code and the
        imports are used later after the snippet.

        """),
    ''
)

line_length_level_msgs = LevelMsgs(
    layout(f"""\

        #### {line_length_title}

        One or more lines are longer than the recommended 79 characters. This is
        not necessarily a problem but long lines should be an exception to the
        rule.

        """),
    layout(f"""\

        #### {line_length_title}

        One or more lines are longer than the recommended 79 characters. This is
        not necessarily a problem given that we have wider monitors than when
        the guidelines were formulated. But long lines should be an exception to
        the rule. All being equal, short lines are easier to read and understand
        than long lines. There are multiple strategies for shortening lines but
        the overall goal has to be readability. Sometimes we have to live with
        broken "rules". And that's official. Read PEP 8 - the official Python
        style guide - especially the section "A Foolish Consistency is the
        Hobgoblin of Little Minds".

        """),
    ''
)

blank_lines_level_msgs = LevelMsgs(
    layout(f"""

        #### {blank_line_title}

        The linter has raised questions about blank lines.

        """),
    layout(f"""

        #### {blank_line_title}

        The linter has raised questions about blank lines. Class definitions
        should have two blank lines before. On function definitions there is
        more flexibility. It should either be one or two.

        """),
    ''
)

whitespace_level_msgs = LevelMsgs(
    layout(f"""

        #### {whitespace_title}

        The linter has raised questions about "whitespace" (tabs, spaces).

        """),
    layout(f"""

        #### {whitespace_title}

        The linter has raised questions about "whitespace" (tabs, spaces). Even
        when whitespace doesn't seem to matter it is best to follow Python
        whitespace conventions when writing Python. Conventions may differ in
        other languages.

        """),
    ''
)

line_indentations_level_msgs = LevelMsgs(
    layout(f"""

        #### {line_indentation_title}

        The linter has raised questions about indentation. There are at least
        two styles of indentation. Whichever you follow be consistent.
    """),
    (
        layout(f"""\

            #### {line_indentation_title}

            The linter has raised questions about indentation. There are at
            least two styles of indentation:

            1) Visual line continuation e.g. note how `parameter_3` lines up
            with the opening parenthesis:

            """)
        +
        layout("""\

            def function_with_long_name(parameter_1, parameter_2,
                                        parameter_3, parameter_4):
                '''
                Doc string for function
                '''
            """, is_code=True)
        +
        layout("""\
            Pros:

            * a common convention

            Cons:

            * every time you rename a function you have to realign parameters

            * code will generally not align tidily with multiples of standard
            indentation

            * room for parameters squeezed

            * you have to look to the right to make sense of the function

            2) Leftwards alignment with multiples of standard indentation e.g.

            """)
        +
        layout("""\

            def function_with_long_name(parameter_1, parameter_2,
                    parameter_3, parameter_4):
                '''
                Doc string for function
                '''

            """, is_code=True)
        +
        layout("""\

            or

            """)
        +
        layout("""\

            def function_with_long_name(
                    parameter_1, parameter_2, parameter_3, parameter_4):
                '''
                Doc string for function
                '''
            """, is_code=True)
        +
        layout("""\

            or

            """)
        +
        layout("""\

            def function_with_long_name(
                    parameter_1,
                    parameter_2,
                    parameter_3,
                    parameter_4):
                '''
                Doc string for function
                '''

            """, is_code=True)
        +
        layout("""\

            Pros:

            * readability is enhanced because the main content of the code is as
            leftward as possible

            * beautiful alignment across entire module

            Cons:

            * you may need to change your IDE's default indenting behaviour

            Whichever of the two style you follow, be consistent.
            """)
        ),
    layout("""\

        See <https://rhodesmill.org/brandon/slides/2012-11-pyconca/#id183> for
        some thought-provoking ideas on code style and much more.

        """)
)

CUSTOM_LINT_MSGS = {
    UNDEFINED_NAMES_MSG_TYPE: undefined_names_level_msgs,
    LINE_LENGTH_MSG_TYPE: line_length_level_msgs,
    UNUSED_IMPORTS_MSG_TYPE: unused_imports_level_msgs,
    BLANK_LINES_MSG_TYPE: blank_lines_level_msgs,
    WHITESPACE_MSG_TYPE: whitespace_level_msgs,
    LINE_INDENTATION_MSG_TYPE: line_indentations_level_msgs,
}
