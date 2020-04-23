from ..advisors import filt_block_advisor
from .. import conf
from ..utils import get_nice_str_list, layout_comment

decorator_xpath = (
    'descendant-or-self::decorator_list/Name '
    '| '
    'descendant-or-self::decorator_list/Call/func/Name'
    ' | '
    'descendant-or-self::decorator_list/Call/func/Attribute/value/Name'
)

@filt_block_advisor(xpath=decorator_xpath)
def decorator_overview(block_dets, *, repeated_message=False):
    """
    Look for decorators and explain some options for improving them.
    """
    decorator_els = block_dets.element.xpath(decorator_xpath)
    if not decorator_els:
        return None
    decorator_names = []
    for decorator_el in decorator_els:
        name = decorator_el.get('id')
        dec_list_el = decorator_el.xpath('ancestor::decorator_list')[0]
        attrib_els = dec_list_el.xpath('Call/func/Attribute')
        if len(attrib_els) == 1:
            namespace = attrib_els[0].get('attr')
            if namespace:
                name = f"{namespace}.{name}"
        decorator_names.append(name)
    dec_name_list = get_nice_str_list(decorator_names, quoter='`')
    plural = 's' if len(decorator_names) > 1 else ''
    brief_comment = layout_comment(f"""\
            #### Decorator{plural} used

            The code uses the decorator{plural}: {dec_name_list}.
            """)
    main_comment = brief_comment
    if not repeated_message:
        main_comment += (
            layout_comment("""\

                Decorators are a common and handy feature of Python. Using them
                is beginner-level Python and making them is intermediate-level
                Python. One tip - use functools.wraps to make the decorated
                function look like the original function e.g. have the same doc
                string.

                Decorators are well-documented elsewhere so there is no real
                advice to give here apart from recommending their use when
                appropriate.

                Here's an example of a simple decorator (`route`) making it easy
                to set up a web end point:

                """)
            +
            layout_comment("""\

                from bottle import route

                @route('/hello')
                def hello():
                    return "Hello World!"
                """, is_code=True)
            +
            layout_comment("""\

                and here is an example of a simple, no argument decorator being
                created with `functool.wraps` applied:

                """)
            +
            layout_comment('''\
                from functools import wraps

                def tweet(func):
                    """
                    Fake tweet original message after saying the message as
                    before
                    """
                    @wraps(func)
                    def wrapper(message):
                        func(message)
                        print(f"I'm tweeting the message {message}")
                    return wrapper

                @tweet
                def say(message):
                    """
                    Print supplied message
                    """
                    print(message)

                say("sausage!")
                ''', is_code=True)
        )
    message = {
        conf.BRIEF: brief_comment,
        conf.MAIN: main_comment,
    }
    return message
