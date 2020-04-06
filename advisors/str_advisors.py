from textwrap import dedent

from advisors import advisor, get_name, get_val
import conf

@advisor(element_type=conf.STR_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def str_overview(element, pre_line_code_str, line_code_str):
    name = get_name(element)
    if not name:
        return None
    val = get_val(pre_line_code_str, line_code_str, name)
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

def str_combination(val, element):
    print(val)
    print(element)
    combination = ''
    
    return combination

def str_interpolation(element, pre_line_code_str, line_code_str):
    name = get_name(element)
    if not name:
        return None
    val = get_val(pre_line_code_str, line_code_str, name)
    if not str_combination(val, element):
        return None
    message = {
        conf.BRIEF: dedent(f"""\
        
        """)
    }
    return message

@advisor(element_type=conf.JOINED_STR_ELEMENT_TYPE,
    xml_root='body/Assign/value')
def f_str_interpolation(element, pre_line_code_str, line_code_str):
    return str_interpolation(element, pre_line_code_str, line_code_str)

@advisor(element_type=conf.FUNC_ELEMENT_TYPE,
    xml_root='body/Assign/value/Call')
def format_str_interpolation(element, pre_line_code_str, line_code_str):
    if element.xpath('Attribute')[0].get('attr') != 'format':
        return None
    return str_interpolation(element, pre_line_code_str, line_code_str)
