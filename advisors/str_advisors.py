from advisors import advisor, get_name, get_val

import conf

@advisor(conf.STR_ELEMENT_TYPE)
def str_overview(element, code_str):
    name = get_name(element)
    if not name:
        return None
    val = get_val(code_str, name)
    black_heart = "\N{BLACK HEART}"
    message = {
        conf.BRIEF: f"""\
            #### Info on *{name}*\n
            *{name}* is a string.
            Python makes it easy to do lots of cool things with strings.
            E.g.
                {name}.upper()
            returns {val.upper()}.
        """,
        conf.MAIN: f"""\
            #### Info on *{name}*\n
            *{name}* is a string.
            Python makes it easy to do lots of cool things with strings.\n\n
            Examples:\n\n
            {name}.upper() returns {val.upper()}.\n\n
            {name}.center(70, '=') returns {val.center(70, '=')}\n\n
            {name}.endswith('chicken') returns {val.endswith('chicken')}\n\n
            {name} + ' is a string' returns {val + ' is a string'}\n\n
            {name} + ' ' + '{{\\NBLACK HEART}}' + ' Python' returns
            {val + ' ' + black_heart + ' Python'}\n\n
            len({name}) returns {len(val)} because that is how many characters
            are in the {name} string
            (remember to count spaces - they are characters too)\n\n
            sorted({name}) returns {sorted(val)}
        """,
        conf.EXTRA: """\
            .upper(), .center() etc
            are abilities available with all Python strings.
            Technically they are methods of string objects.
            They start with a dot and are on the end of the object.\n\n
            To see the full list of string methods enter dir(str)
            into a Python command line.\n\n
            len() is a function which can be used on lots of things - not just
            string objects. It is not a method of the string object.
            Other functions that are not string-specific but are
            commonly used with strings include sorted() and print().
        """,
    }
    return message

# To add more advice, just declare more advisor functions with the @advisor decorator!
