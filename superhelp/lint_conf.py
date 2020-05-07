from collections import namedtuple

from . import conf  # @UnresolvedImport
from .utils import layout_comment as layout

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
]

def title2msg_type(title):
    return title.upper().replace(' ', '_') + '_MSG_TYPE'
## Ensure brief AND main are the same so titles don't shift when
## changing message level
line_continuation_title = "Line continuation"
line_length_title = "Line length"
unused_imports = "Unused imports"
## nice to keep placeholder names etc aligned with actual titles but nothing breaks if we don't
LINE_CONTINUATION_MSG_TYPE = title2msg_type(line_continuation_title)
LINE_LENGTH_MSG_TYPE = title2msg_type(line_length_title)
UNUSED_IMPORT_MSG_TYPE = title2msg_type(unused_imports)

CONSOLIDATE_MSG_TYPE = {
    'E123': LINE_CONTINUATION_MSG_TYPE,
    'E124': LINE_CONTINUATION_MSG_TYPE,
    'E125': LINE_CONTINUATION_MSG_TYPE,
    'E126': LINE_CONTINUATION_MSG_TYPE,
    'E127': LINE_CONTINUATION_MSG_TYPE,
    'E128': LINE_CONTINUATION_MSG_TYPE,
    'E129': LINE_CONTINUATION_MSG_TYPE,
    'E131': LINE_CONTINUATION_MSG_TYPE,
    'E501': LINE_LENGTH_MSG_TYPE,
    'F401': UNUSED_IMPORT_MSG_TYPE,
}
LintMsgs = namedtuple('LintMsgs', 'brief, main, extra, replacement')
CUSTOM_LINT_MSGS = {
    LINE_CONTINUATION_MSG_TYPE: LintMsgs(
        layout(f"""

            #### {line_continuation_title}

            The linter has raised questions about line continuation. There are
            at least two styles of line continuation. Whichever you follow be
            consistent.
        """),
        (
            layout(f"""\

                #### {line_continuation_title}

                The linter has raised questions about line continuation. There
                are at least two styles of line continuation:

                1) Visual line continuation e.g. note how parameter_3 lines up
                with the opening parenthesis

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

                * every time you rename a function you have to realign
                parameters

                * code will generally not align tidily with multiples of
                standard indentation

                * room for parameters squeezed

                * you have to look to the right to make sense of the function

                2) Leftwards alignment with multiples of standard indentation
                e.g.

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

                * readability is enhanced because the main content of the code
                is as leftward as possible

                * beautiful alignment across entire module

                Cons:

                * you may need to change your IDE's default indenting behaviour

                Whichever of the two style you follow, be consistent.
                """)
            ),
        layout("""\

            See <https://rhodesmill.org/brandon/slides/2012-11-pyconca/#id183>
            for some thought-provoking ideas on code style and much more.

            """),
        True),
    LINE_LENGTH_MSG_TYPE: LintMsgs(
        layout(f"""\

            #### {line_length_title}

            One or more lines are longer than the recommended 79 characters.
            This is not necessarily a problem but long lines should be an
            exception to the rule.

            """),
        layout(f"""\

            #### {line_length_title}

            One or more lines are longer than the recommended 79 characters.
            This is not necessarily a problem given that we have wider monitors
            than when the guidelines were formulated. But long lines should be
            an exception to the rule. All being equal, short lines are easier to
            read and understand than long lines. There are multiple strategies
            for shortening lines but the overall goal has to be readability.
            Sometimes we have to live with broken "rules". And that's official.
            Read PEP 8 - the official Python style guide - especially the
            section "A Foolish Consistency is the Hobgoblin of Little Minds".

            """),
        '',
        True),
    UNUSED_IMPORT_MSG_TYPE: LintMsgs(
        layout(f"""\

            #### {unused_imports}

            One or more imports not used in snippet.

            """),
        layout(f"""\

            #### {unused_imports}

            One or more imports not used in snippet. If the snippet was
            extracted from a larger piece of code and the imports are used in
            that code then there is no problem.

            """),
        '',
        False
        )
}
