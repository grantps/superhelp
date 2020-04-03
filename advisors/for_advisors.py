from textwrap import dedent

from advisors import advisor, GENERAL_COMPREHENSION_COMMENT, \
    LIST_COMPREHENSION_COMMENT, DICT_COMPREHENSION_COMMENT, \
    SET_COMPREHENSION_COMMENT
import conf

@advisor(element_type=conf.FOR_ELEMENT_TYPE, xml_root=conf.XML_ROOT_BODY)
def for_overview(element, pre_line_code_str, line_code_str):  #@UnusedVariable (Ctrl 1 to identify what to suppress)
    """
    Don't try to properly understand the for loop or make a built comprehension.
    It is enough to detect whether a loop is simple enough to consider making a
    comprehension or not. And to see whether appending, key setting, or adding
    is happening and suggesting the right comprehension accordingly.
    """
    loop_lines = line_code_str.split('\n')
    short_enough = len(loop_lines) < 3
    if not short_enough:
        return None
    comp_type = None
    comp_comment = ''
    if 'append' in line_code_str:
        comp_type = 'List Comprehension'
        comp_comment = LIST_COMPREHENSION_COMMENT
    elif len(element.cssselect('Subscript')):  ## Seems a reasonable indicator
        comp_type = 'Dictionary Comprehension'
        comp_comment = DICT_COMPREHENSION_COMMENT
    elif 'set' in line_code_str:
        comp_type = 'Set Comprehension'
        comp_comment = SET_COMPREHENSION_COMMENT
    message = {
        conf.BRIEF: dedent(f"""\
            Simple for loops can sometimes be replaced with comprehensions.
            In this case a simple reading of the code suggests a {comp_type}
            might be possible.

            Of course, only use a comprehension if it makes your code easier to
            understand.
            """),
        conf.MAIN: (
            dedent(f"""\
            Simple for loops can sometimes be replaced with comprehensions.
            In this case a simple reading of the code suggests a {comp_type}
            might be possible. Of course, only use a comprehension if it makes
            your code easier to understand.
            """)
            +
            GENERAL_COMPREHENSION_COMMENT + '\n\n' + comp_comment),
    }
    return message
