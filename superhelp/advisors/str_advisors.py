from ..advisors import any_block_advisor, filt_block_advisor
from .. import ast_funcs, code_execution, conf
from ..utils import layout_comment

F_STR = 'f-string'
STR_FORMAT_FUNC = 'str_format'
SPRINTF = 'sprintf'
STR_ADDITION = 'string addition'

@filt_block_advisor(xpath='body/Assign/value/Str')
def str_overview(block_dets):
    """
    Provide overview of assigned strings e.g. name = 'Hamish'.
    """
    name = ast_funcs.get_assigned_name(block_dets.element)
    if not name:
        return None
    val = code_execution.get_val(
        block_dets.pre_block_code_str, block_dets.block_code_str, name)
    black_heart = "\N{BLACK HEART}"
    message = {
        conf.BRIEF: layout_comment(f"""\
            ##### String Overview

            `{name}` is a string.
            Python makes it easy to do lots of cool things with strings.
            E.g. {name}.upper() returns {val.upper()}.
            """),
        conf.MAIN: layout_comment(f"""\
            ##### String Overview

            `{name}` is a string.
            Python makes it easy to do lots of cool things with strings.\n\n
            Examples:\n\n
            {name}.upper() returns {val.upper()}.

            {name}.center(70, '=') returns {val.center(70, '=')}

            {name}.endswith('chicken') returns {val.endswith('chicken')}

            {name} + ' is a string' returns {val + ' is a string'}

            {name} + ' ' + '{{\\NBLACK HEART}}' + ' Python' returns
            {val + ' ' + black_heart + ' Python'}

            len({name}) returns {len(val)} because that is how many characters
            are in the {name} string
            (remember to count spaces - they are characters too)

            sorted({name}) returns {sorted(val)}
            """),
        conf.EXTRA: layout_comment("""\
            .upper(), .center() etc
            are abilities available with all Python strings.
            Technically they are methods of string objects.
            They start with a dot and are on the end of the object.

            To see the full list of string methods enter dir(str)
            into a Python command line.

            len() is a function which can be used on lots of things - not just
            string objects. It is not a method of the string object.
            Other functions that are not string-specific but are
            commonly used with strings include sorted() and print().
            """),
    }
    return message

def str_combination(combination_type, block_dets):
    name = ast_funcs.get_assigned_name(block_dets.element)
    if not name:
        return None
    combination_type2comment = {
        F_STR: "f-string interpolation",
        STR_FORMAT_FUNC: "the format function",
        SPRINTF: "sprintf string interpolation",
        STR_ADDITION: "string addition (e.g. animal = 'jelly' + 'fish')",
    }
    combination_comment = combination_type2comment[combination_type]
    message = {
        conf.BRIEF: layout_comment(f"""\
            `{name}` is created using {combination_comment}.
            """),
        conf.MAIN: layout_comment(f"""\
            `{name}` is created using {combination_comment}.
            """),
    }
    if combination_type != F_STR:
        message[conf.BRIEF] += layout_comment(f"""\

            Have you considered using an f-string approach to constructing
            your `{name}`?
            """)
        message[conf.MAIN] += (
            layout_comment(f"""\

                Have you considered using an f-string approach to constructing
                your `{name}`?

                f-strings let you reference variables from earlier in your code and
                allow very readable string construction. All the usual tricks of the
                .format() approach also work. For example, comma separating
                thousands in numbers:

                """)
            +
            layout_comment("""\
                cost = 10_550
                print(f"Cost is ${cost:,}")
                # >>> 'Cost is $10,550'
                """, is_code=True)
            +
            layout_comment(f"""\

                Or making small in-line calculations:

                """)
            +
            layout_comment("""\
                people = ['Bart', 'Lisa']
                print(f"There are {len(people)} people")
                # >>> 'There are 2 people'
                """, is_code=True)
            +
            layout_comment(f"""\

                Or zero-padding numbers:

                """)
            +
            layout_comment("""\
                num = 525
                print(f"{num:0>4}")
                # >>> '0525'
                """, is_code=True)
        )
    return message

@filt_block_advisor(xpath='body/Assign/value/JoinedStr')
def f_str_interpolation(block_dets):
    """
    Examine f-string interpolation.
    """
    return str_combination(F_STR, block_dets)

@filt_block_advisor(xpath='body/Assign/value/Call/func')
def format_str_interpolation(block_dets):
    """
    Look at use of .format() to interpolate into strings.
    """
    try:
        was_a_format_func = (
            block_dets.element.xpath('value/Call/func/Attribute')[0]
            .get('attr') == 'format')
    except IndexError:
        was_a_format_func = False
    if not was_a_format_func:
        return None
    return str_combination(STR_FORMAT_FUNC, block_dets)

def _get_has_sprintf_format_specifiers(block_dets):
    block_code_str = block_dets.block_code_str
    conversion_types = ['d', 'i', 'o', 'u', 'x', 'X', 'e', 'E', 'f', 'F',
        'g', 'G', 'c', 'r', 's', 'a', '%']  ## https://docs.python.org/3/library/stdtypes.html#old-string-formatting
    format_specifiers = [
        f"%{conversion_type}" for conversion_type in conversion_types ]
    has_sprintf_format_specifiers = any(
        [format_specifier in block_code_str
         for format_specifier in format_specifiers])
    return has_sprintf_format_specifiers

@any_block_advisor()
def sprintf(block_dets):
    """
    Look at use of sprintf for string interpolation e.g. greeting = "Hi %s" %
    name
    """
    has_str_modification = bool(block_dets.element.xpath('value/BinOp/op/Mod'))
    has_sprintf_format_specifiers = _get_has_sprintf_format_specifiers(
        block_dets)
    has_sprintf = has_str_modification and has_sprintf_format_specifiers
    if not has_sprintf:
        return None
    return str_combination(SPRINTF, block_dets)

@any_block_advisor()
def string_addition(block_dets):
    """
    Advise on string combination using +. Explain how f-string alternative
    works.
    """
    element = block_dets.element
    left_strs = 'descendant-or-self::BinOp/left/Str'
    right_strs = 'descendant-or-self::BinOp/right/Str'
    str_elements_being_combined = element.xpath(f'{left_strs} | {right_strs}')
    has_string_addition = False
    for str_el in str_elements_being_combined:
        ## Does their immediate ancestor BinOp have op of Add?
        ## Don't know if there any alternatives but let's be sure
        ## Ordered set of nodes, from parent to ancestor? https://stackoverflow.com/a/15645846
        bin_op_el = str_el.xpath('ancestor-or-self::BinOp')[-1]
        ## was it an Add op
        has_add = bool(bin_op_el.xpath('op/Add'))
        if has_add:
            has_string_addition = True
            break
    if not has_string_addition:
        return None
    return str_combination(STR_ADDITION, block_dets)
