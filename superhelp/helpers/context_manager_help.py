from ..helpers import filt_block_help, get_aop_msg
from .. import conf
from ..gen_utils import layout_comment as layout

def get_open_cm_msg():
    return (
        layout("""\

        For example, every time we open a file we need to make sure it is closed
        when we are finished. It is not that hard to handle that yourself in
        simple cases but can become much harder - perhaps the code exits in
        multiple places (perhaps as a result of an `exception`). You have to
        remember to handle the tidy-up in every place an exit might occur.
        Either you will forget one of them or you'll be repeating code all over
        the place violating the DRY principle - namely:

        > "Don't Repeat Yourself" (The Pragmatic Programmer)

        WET presumably stands for "Write Every Time", "Write Everything Twice",
        "We Enjoy Typing" or "Waste Everyone's Time" ;-)

        If you don't use a context manager, problems can emerge as a snippet
        gradually evolves. And it usually all starts so innocently :-). Here's
        one example of the problem unfolding:
        """)
        +
        layout("""\
        ## 1) Not using context manager (with) not really a problem
        f = open(fname)
        text = f.read()
        f.close()  # <------------------ First one (I hope this is the only one)

        ## 2) Maybe we need to handle empty files
        f = open(fname)
        text = f.read()
        if not text:
            raise Exception(f"{fname} is empty")  # <------ errr ... is the file
        f.close()                                 # handle going to get closed?

        ## 3) We remember to close the file handle if an exception
        f = open(fname)
        text = f.read()
        if not text:
            f.close()  # <---------------------------- Rats! I need a second one
            raise Exception(f"{fname} is empty")
        f.close()

        ## 4) We want the index of TAG for some reason
        f = open(fname)
        text = f.read()
        if not text:
            f.close()
            raise Exception(f"{fname} is empty")
        idx = text.index(TAG) # <--------------- Hmmm - will raise ValueError if
        f.close()             #                 TAG not in text? File left open?

        ## 5) We remember to handle the exception
        f = open(fname)
        text = f.read()
        if not text:
            f.close()
            raise Exception(f"{fname} is empty")
        try:
            idx = text.index(TAG)
        except ValueError:
            f.close()  # <----------------- Three already! I'm lucky it's only a
            raise      #                    one-liner each time.
        f.close()
        """, is_code=True)
        +
        layout("""\

        The code is much cleaner and robust using a simple context manager :-)
        """)
        +
        layout("""\
        with open(fname) as f:
            text = f.read()
            if not text:
                raise Exception(f"{fname} is empty")
            idx = text.index(TAG)
        ## If my code gets here, i.e. past the indented block inside the context
        ## manager,  we are guaranteed to have freed up the file - nice!
        """, is_code=True)
    )

WITH_XPATH = 'descendant-or-self::With'

def with_is_using_open(with_el):
    func_name_els = with_el.xpath(
        'descendant::items/withitem/context_expr/Call/func/Name')
    if len(func_name_els) != 1:
        return False
    func_name_el = func_name_els[0]
    func_name = func_name_el.get('id')
    return func_name == 'open'

@filt_block_help(xpath=WITH_XPATH)
def content_manager_overview(block_dets, *, repeat=False, **_kwargs):
    """
    Explain context managers.
    """
    with_els = block_dets.element.xpath(WITH_XPATH)
    if not with_els:
        return None
    using_open_cm = any([with_is_using_open(with_el) for with_el in with_els])

    title = layout("""\
    ### Context manager(s) used
    """)
    if using_open_cm:
        summary = layout("""\

        Your code includes the commonly used file opening context manager.
        """)
    else:
        summary = layout("""\

        Your code uses a context manager.
        """)
    brief_usage = layout("""\

        Context managers take care of anything required when we enter a block of
        code or exit it.
        """)
    if not repeat:
        brief_example = layout("""\

        For example, every time we open a file we need to make sure it is closed
        when we are finished. Or when we finish with database connections and
        cursors we need to clean up after ourselves. There may be some things we
        need to do when we start a code block as well.
        """)
        long_example = get_open_cm_msg()
        aop = get_aop_msg()
    else:
        brief_example = ''
        long_example = ''
        aop = ''

    message = {
        conf.BRIEF: title + summary + brief_usage + brief_example,
        conf.MAIN: title + summary + brief_usage + long_example,
        conf.EXTRA: aop,
    }
    return message

def has_with_ancestor(open_el):
    with_els = open_el.xpath('ancestor::With')
    if not with_els:
        return False
    with_el = with_els[-1]
    func_name_els = with_el.xpath('items/withitem/context_expr/Call/func/Name')
    if len(func_name_els) != 1:
        return False
    func_name_el_under_with = func_name_els[0]
    return open_el == func_name_el_under_with

FUNC_NAME_XPATH = 'descendant-or-self::Call/func/Name'

@filt_block_help(xpath=FUNC_NAME_XPATH, warning=True)
def file_cm_needed(block_dets, *, repeat=False, **_kwargs):
    """
    Look for opening of file without a context managers - recommend use of the
    "with open" context manager.
    """
    func_name_els = block_dets.element.xpath(FUNC_NAME_XPATH)
    if not func_name_els:
        return None
    open_els = []
    for func_name_el in func_name_els:
        func_name = func_name_el.get('id')
        if func_name == 'open':
            open_els.append(func_name_el)
    if not open_els:
        return None
    missing_cm = not all([has_with_ancestor(open_el) for open_el in open_els])
    if not missing_cm:
        return None

    title = layout("""\
    ### File opened without context manager
    """)
    summary = layout("""
    Your code opens a file without using a context manager.
    """)
    if not repeat:
        reasons = layout("""\

        Using a context manager is easy (actually, writing them isn't even that
        hard) but using the standard ones has big advantages.
        """)
        long_example = get_open_cm_msg()
        aop = get_aop_msg()
    else:
        reasons = ''
        long_example = ''
        aop = ''

    message = {
        conf.BRIEF: title + summary,
        conf.MAIN: title + summary + reasons + long_example,
        conf.EXTRA: aop,
    }
    return message
