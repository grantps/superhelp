from textwrap import dedent

import advisors
from advisors import gen_advisor, type_advisor
import conf

F_STR = 'f-string'
STR_FORMAT_FUNC = 'str_format'
SPRINTF = 'sprintf'
STR_ADDITION = 'string addition'

@type_advisor(element_type=conf.STR_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def str_overview(line_dets):
    name = advisors.get_assigned_name(line_dets.element)
    if not name:
        return None
    val = advisors.get_val(
        line_dets.pre_line_code_str, line_dets.line_code_str, name)
    black_heart = "\N{BLACK HEART}"
    message = {
        conf.BRIEF: dedent(f"""\
            `{name}` is a string.
            Python makes it easy to do lots of cool things with strings.
            E.g. {name}.upper() returns {val.upper()}.
        """),
        conf.MAIN: dedent(f"""\
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
        conf.EXTRA: dedent("""\
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

def str_combination(combination_type, line_dets):
    name = advisors.get_assigned_name(line_dets.element)
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
        conf.BRIEF: dedent(f"""\
            `{name}` is created using {combination_comment}.
            """),
        conf.MAIN: dedent(f"""\
            `{name}` is created using {combination_comment}.
            """),
    }
    if combination_type != F_STR:
        message[conf.BRIEF] += dedent(f"""\

            Have you considered using an f-string approach to constructing
            your `{name}`?
            """)
        message[conf.MAIN] += (
            dedent(f"""\

                Have you considered using an f-string approach to constructing
                your `{name}`?

                f-strings let you reference variables from earlier in your code and
                allow very readable string construction. All the usual tricks of the
                .format() approach also work. For example, comma separating
                thousands in numbers:

                """)
            +
            advisors.code_indent(dedent("""\
                cost = 10_550
                print(f"Cost is ${cost:,}")
                # >>> 'Cost is $10,550'
                """))
            +
            dedent(f"""\

                Or making small in-line calculations:

                """)
            +
            advisors.code_indent(dedent("""\
                people = ['Bart', 'Lisa']
                print(f"There are {len(people)} people")
                # >>> 'There are 2 people'
                """))
            +
            dedent(f"""\

                Or zero-padding numbers:

                """)
            +
            advisors.code_indent(dedent("""\
                num = 525
                print(f"{num:0>4}")
                # >>> '0525'
                """))
        )
    return message

@type_advisor(element_type=conf.JOINED_STR_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def f_str_interpolation(line_dets):
    return str_combination(F_STR, line_dets)

@type_advisor(element_type=conf.FUNC_ELEMENT_TYPE,
    xml_root='body/Assign/value/Call')
def format_str_interpolation(line_dets):
    was_a_format_func = (
        line_dets.element.xpath('//Attribute')[0].get('attr') == 'format')
    if not was_a_format_func:
        return None
    return str_combination(STR_FORMAT_FUNC, line_dets)

@gen_advisor()
def sprintf(line_dets):
    code_str = line_dets.line_code_str
    conversion_types = ['d', 'i', 'o', 'u', 'x', 'X', 'e', 'E', 'f', 'F',
        'g', 'G', 'c', 'r', 's', 'a', '%']  ## https://docs.python.org/3/library/stdtypes.html#old-string-formatting
    format_specifiers = [
        f"%{conversion_type}" for conversion_type in conversion_types ]
    has_sprintf = any(
        [format_specifier in code_str
         for format_specifier in format_specifiers])
    if not has_sprintf:
        return None
    return str_combination(SPRINTF, line_dets)

@gen_advisor()
def string_addition(line_dets):
    """
    Look inside for any (possibly nested) BinOp with op = Add and either a left
    being a Str or right being a Str.
    """
    element = line_dets.element
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
    return str_combination(STR_ADDITION, line_dets)
