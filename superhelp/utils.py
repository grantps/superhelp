from textwrap import dedent

from . import conf

def get_nice_str_list(items, *, quoter='`'):
    """
    Get a nice English phrase listing the items.

    :param sequence items: individual items to put into a phrase.
    :param str quoter: default is backtick because it is expected that the most
     common items will be names (variables).
    :return: nice phrase
    :rtype: str
    """
    nice_str_list = ', '.join(
        [f"{quoter}{item}{quoter}" for item in items[:-1]])
    if nice_str_list:
        nice_str_list += " and "
    nice_str_list += f"{quoter}{items[-1]}{quoter}"
    return nice_str_list

def int2nice(num):
    """
    :return: nicer version of number ready for use in sentences
    :rtype: str
    """
    nice = {
        0: 'no',
        1: 'one',
        2: 'two',
        3: 'three',
        4: 'four',
        5: 'five',
        6: 'six',
        7: 'seven',
        8: 'eight',
        9: 'nine',
        10: 'ten',
        11: 'twelve',
        12: 'twelve',
    }
    return nice.get(num, num)

def layout_comment(raw_comment, *, is_code=False):
    if is_code:
        lines = (
            [conf.PYTHON_CODE_START]
            + dedent(raw_comment).split('\n')
            + [conf.PYTHON_CODE_END]
        )
        indented_lines = [f"{' ' * 4}{line}" for line in lines]
        comment = f'\n'.join(indented_lines) + '\n'  ## new line at end needed otherwise content of next str (if any) becomes part of code highlighting
    else:
        comment = dedent(raw_comment)
    return comment
