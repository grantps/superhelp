from textwrap import dedent

from advisors import advisor, get_name, get_val
import conf

@advisor(conf.STR_ELEMENT_TYPE)
def str_overview(element, safe_imports, code_str):
    name = get_name(element)
    if not name:
        return None
    val = get_val(safe_imports, code_str, name)
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

# To add more advice, just declare more advisor functions with the @advisor decorator!
