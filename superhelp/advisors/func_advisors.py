from ..advisors import filt_block_advisor
from ..ast_funcs import get_el_lines_dets
from .. import conf, utils
from ..utils import layout_comment

FUNC_DEFN_XPATH = 'descendant-or-self::FunctionDef'

def _get_arg_comment(func_el, *, repeated_message=False):
    """
    Must cope with positional arguments, keyword arguments, keyword-only
    arguments, packed positional arguments, and packed keyword arguments.
    Trivial really ;-).

    Comment should end without a full stop because calling code adds that to
    make the sentence structure more explicit.
    """
    args = func_el.xpath('args/arguments/args/arg')
    vararg = func_el.xpath('args/arguments/vararg/arg')
    kwarg = func_el.xpath('args/arguments/kwarg/arg')
    kwonlyargs = func_el.xpath('args/arguments/kwonlyargs/arg')
    has_packing = (vararg or kwarg)
    if has_packing:
        arg_comment = 'receives a variable number of arguments'
        if repeated_message:
            arg_comment += '.'
        else:
            if vararg:
                vararg_name = vararg[0].get('arg')
                arg_comment += (". All positional arguments received are packed"
                    f" together into a list called {vararg_name} using "
                    f"the &ast;{vararg_name} syntax. If there is no better name"
                    " in a particular case the Python convention is to call "
                    "that list 'args'")
            if kwarg:
                kwarg_name = kwarg[0].get('arg')
                arg_comment += (". All keyword arguments received are packed "
                    f"together into a dictionary called {kwarg_name} "
                    f"using the &ast;&ast;{kwarg_name} syntax. If there is no "
                    "better name in a particular case the Python convention is "
                    "to call that dictionary 'kwargs'")
    else:
        all_args_n = len(args + kwonlyargs)
        if all_args_n:
            nice_n_args = utils.int2nice(all_args_n)
            arg_comment = (f"receives {nice_n_args} argument")
            if all_args_n > 1:
                arg_comment += 's'
        else:
            arg_comment = "doesn't take any arguments"
    return arg_comment

def _get_return_comment(return_elements, *, repeated_message=False):
    implicit_return_els = [return_element for return_element in return_elements
        if not return_element.getchildren()]
    implicit_returns_n = len(implicit_return_els)
    explicit_return_els = [return_element for return_element in return_elements
        if return_element.xpath('value')]
    none_returns_n = 0
    val_returns_n = 0
    for el in explicit_return_els:
        val_children = el.getchildren()
        for val_child in val_children:
            if (val_child.tag == 'NameConstant'
                    and val_child.get('value') is None):
                none_returns_n += 1
            else:
                val_returns_n += 1
    keyword_returns_n = none_returns_n + val_returns_n + implicit_returns_n
    if not keyword_returns_n:
        returns_comment = "The function does not explicitly return anything."
        if not repeated_message:
            returns_comment += (
                " In which case, in Python, it implicitly returns None")
    else:
        returns_comment = (
            "The function exits via an explicit `return` statement "
            f"{utils.int2nice(keyword_returns_n)} time")
        if repeated_message:
            returns_comment += '.'
        else:
            if keyword_returns_n > 1:
                returns_comment += (
                    "s. Some people prefer functions to have one, "
                    "and only one exit point for clarity. Others disagree e.g. "
                    "using early returns to short-circuit functions if initial "
                    "validation of some sort makes it possible to avoid the "
                    "bulk of the function. Whatever approach you take make sure"
                    " your function is easy to reason about in terms of what it"
                    " returns and where it exits")
            else:
                returns_comment += '.'
    return returns_comment

def _get_exit_comment(func_el, *, repeated_message=False):
    """
    Look for 'return' and 'yield'.
    """
    return_elements = func_el.xpath('descendant-or-self::Return')
    yield_elements = func_el.xpath('descendant-or-self::Yield')
    if yield_elements:
        if return_elements:
            exit_comment = ("It has both `return` and `yield`. "
                "That probably doesn't make any sense.")
        else:
            exit_comment = "It is a generator function."
    else:
        exit_comment = _get_return_comment(
            return_elements, repeated_message=repeated_message)
    return exit_comment

@filt_block_advisor(xpath=FUNC_DEFN_XPATH)
def func_overview(block_dets, *, repeated_message=False):
    """
    Advise on function definition statements. e.g. def greeting(): ...
    """
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    brief_comment = layout_comment("""\
        #### Function Details
        """)
    for func_el in func_els:
        name = func_el.get('name')
        arg_comment = _get_arg_comment(
            func_el, repeated_message=repeated_message)
        exit_comment = _get_exit_comment(
            func_el, repeated_message=repeated_message)
        brief_comment += layout_comment(f"""\

            The function named `{name}` {arg_comment}. {exit_comment}.
            """)
    if repeated_message:
        extra_comment = ''
    else:
        extra_comment = layout_comment("""\
            There is often confusion about the difference between arguments and
            parameters. Functions define parameters but receive arguments. You
            can think of parameters as being like car parks and arguments as the
            cars that fill them. You supply arguments to a function depending on
            its parameters.
            """)
    message = {
        conf.BRIEF: brief_comment,
        conf.EXTRA: extra_comment,
    }
    return message

@filt_block_advisor(xpath=FUNC_DEFN_XPATH, warning=True)
def func_len_check(block_dets, *, repeated_message=False):
    """
    Warn about functions that might be too long.
    """
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    brief_comment = ''
    has_short_comment = False
    for func_el in func_els:
        name = func_el.get('name')
        first_line_no, last_line_no, _func_lines_n = get_el_lines_dets(
            func_el, ignore_trailing_lines=True)
        block_lines = block_dets.block_code_str.split('\n')
        func_lines = block_lines[first_line_no - 1: last_line_no]
        func_non_empty_lines = [line for line in func_lines if line]
        func_lines_n = len(func_non_empty_lines)
        if func_lines_n <= conf.MAX_BRIEF_FUNC_LOC:
            continue
        else:
            if not has_short_comment:
                brief_comment += layout_comment("""\
                    #### Function possibly too long

                    """)
                has_short_comment = True
            brief_comment += layout_comment(f"""\

            `{name}` has {utils.int2nice(func_lines_n)} lines of code
            (including comments but with empty lines ignored).
            """)
            if not repeated_message:
                brief_comment += (" Sometimes it is OK for a function to be "
                    "that long but you should consider refactoring the code "
                    "into smaller units.")
    if not brief_comment:
        return None
    message = {
        conf.BRIEF: brief_comment,
    }
    return message

def get_n_args(func_el):
    arg_els = func_el.xpath('args/arguments/args/arg')
    kwonlyarg_els = func_el.xpath('args/arguments/kwonlyargs/arg')
    n_args = len(arg_els + kwonlyarg_els)
    return n_args

@filt_block_advisor(xpath=FUNC_DEFN_XPATH, warning=True)
def func_excess_parameters(block_dets, *, repeated_message=False):
    """
    Warn about functions that might have too many parameters.
    """
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    brief_comment = ''
    has_high = False
    for func_el in func_els:
        name = func_el.get('name')
        n_args = get_n_args(func_el)
        high_args = n_args > conf.MAX_BRIEF_FUNC_ARGS
        if high_args:
            brief_comment += layout_comment("""\
                #### Possibly too many function parameters

                """)
            brief_comment += layout_comment(f"""\

            `{name}` has {n_args:,} parameters.

            """)
            if not (has_high or repeated_message):
                brief_comment += layout_comment("""\
                    Sometimes it is OK for a function to have that many but you
                    should consider refactoring the code or collecting related
                    parameters into single parameters e.g. instead of receiving
                    image size arguments separately perhaps you could receive a
                    dictionary of image size argument details.
                    """)
            has_high = True
    if not has_high:
        return None
    message = {
        conf.BRIEF: brief_comment,
    }
    return message

def get_danger_args(func_el):
    arg_els = func_el.xpath('args/arguments/args/arg')  ## not kwonlyargs so potentially supplied positionally only
    arg_names = [arg_el.get('arg') for arg_el in arg_els]
    arg_default_els = func_el.xpath('args/arguments/defaults')
    danger_statuses = []
    for arg_default_el in arg_default_els:
        for child_el in arg_default_el.getchildren():
            if (child_el.tag == 'NameConstant'
                    and child_el.get('value') in ['True', 'False']):
                danger_status = 'Boolean'
            elif child_el.tag == 'Num' and child_el.get('n'):
                danger_status = 'Number'
            else:
                danger_status = None
            danger_statuses.append(danger_status)
    ## reversed because defaults are filled in rightwards e.g. a, b=1, c=2
    ## args = a,b,c and defaults=1,2 -> reversed c,b,a and 2,1 -> c: 2, b: 1
    arg_names_reversed = reversed(arg_names)
    danger_statuses_reversed = reversed(danger_statuses)
    args_and_danger_statuses = zip(arg_names_reversed, danger_statuses_reversed)
    danger_args = [(arg, danger_status)
        for arg, danger_status in args_and_danger_statuses
        if danger_status is not None]
    return danger_args

@filt_block_advisor(xpath=FUNC_DEFN_XPATH, warning=True)
def positional_boolean(block_dets, *, repeated_message=False):
    """
    Look for any obvious candidates for forced keyword use e.g. where a
    parameter is a boolean or a number.

    Defaults apply from the rightmost backwards (within their group - either
    defaults or kw_defaults (related to kwonlyargs)).
    """
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    brief_comment = ''
    has_positional_comment = False
    for func_el in func_els:
        name = func_el.get('name')
        danger_args = get_danger_args(func_el)
        if danger_args:
            if not has_positional_comment:
                brief_comment += layout_comment("""\

                    #### Function expects risky positional arguments
                    """)
                if not repeated_message:
                    brief_comment += layout_comment("""\

                    Functions which expect numbers or booleans (True/False)
                    without requiring keywords are risky. They are risky when if
                    the function is changed later to have different parameters.
                    For example, greeting(formal=True) is more intelligible than
                    greeting(True). And intelligible code is safer to alter /
                    maintain over time than mysterious code.
                    """)
            brief_comment += layout_comment(f"""\
                A partial analysis of `{name}` found the following risky non-
                keyword (positional) parameters: {danger_args}.
                """)
            if not (has_positional_comment) or repeated_message:
                brief_comment += (
                    layout_comment("""\

                        Using an asterisk as a pseudo-parameter forces all
                        parameters to the right to be keywords e.g.
                        """)
                    +
                    layout_comment(f"""\
                        def greeting(name, *, formal=False):
                            ...
                        """, is_code=True)
                    +
                    layout_comment(f"""\

                        In this example you couldn't now call the function
                        greeting('Jo', True) - it would need to be
                        greeting('Jo', formal=True)
                        """)
                )
            has_positional_comment = True
    if not has_positional_comment:
        return None
    if repeated_message:
        extra_comment = ''
    else:
        extra_comment = layout_comment(f"""\
            Putting an asterisk in the parameters has the effect of forcing all
            parameters to the right to be keyword parameters because the
            asterisk mops up any remaining positional arguments supplied (if
            any) when the function is called. There can't be any other
            positional arguments, because they have all been handled already, so
            only keyword parameters are allowed thereafter.
            """)
    message = {
        conf.BRIEF: brief_comment,
        conf.EXTRA: extra_comment,
    }
    return message

def get_func_name_docstring(func_el):
    func_body_el = func_el.xpath('body')[0]
    func_name = func_el.get('name')
    ## first item in body MUST be Expr and the first value must be a Str
    body_els = func_body_el.getchildren()
    if not body_els:
        docstring = None
    else:
        first_body_el = body_els[0]
        if first_body_el.tag != 'Expr':
            docstring = None
        else:
            expr_els = first_body_el.getchildren()
            if not expr_els:
                docstring = None
            else:
                first_expr_el = expr_els[0]
                if first_expr_el.tag != 'value':
                    docstring = None
                else:
                    value_els = first_expr_el.getchildren()
                    if not value_els:
                        docstring = None
                    else:
                        first_value_el = value_els[0]
                        if first_value_el.tag != 'Str':
                            docstring = None
                        else:
                            docstring = first_value_el.get('s')
    return func_name, docstring

def get_funcs_dets_and_docstring(func_els):
    funcs_dets_and_docstring = []
    for func_el in func_els:
        func_name, docstring = get_func_name_docstring(func_el)
        func_dets_and_docstring = (func_el, func_name, docstring)
        funcs_dets_and_docstring.append(func_dets_and_docstring)
    return funcs_dets_and_docstring

@filt_block_advisor(xpath=FUNC_DEFN_XPATH, warning=True)
def docstring_issues(block_dets, *, repeated_message=False):
    """
    Check over function doc strings. Missing doc string, not enough lines to
    cover params, return etc.
    """
    WRAPPING_NEWLINE_N = 2
    example_docstring = layout_comment(f'''\
        def greet(name, greet_word='Hi'):
            """
            Get a greeting for the supplied person.

            :param str name: person being greeted
            :param str greet_word: the word to start the greeting
            :return: a greeting message to the person
            :rtype: str
            """
            greeting = f"{{greet_word}} {{name}} - how are you?"
            return greeting
        ''', is_code=True)
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    funcs_dets_and_docstring = get_funcs_dets_and_docstring(func_els)
    brief_comment = ''
    missing_commented = False
    inadequate_commented = False
    for func_el, func_name, docstring in funcs_dets_and_docstring:
        if docstring is None:
            if not (missing_commented or repeated_message):
                brief_comment += (
                    layout_comment(f"""\
                        #### Function missing doc string

                        `{func_name}` lacks a doc string - you should probably
                        add one.

                        Note - # comments at the top of the function do not work
                        as doc strings. Python completely ignores them. If you
                        add a proper doc string, however, it can be accessed by
                        running help({func_name}) or {func_name}.\_\_doc\_\_.
                        Which is useful when using this function in bigger
                        projects e.g. in an IDE (Integrated Development
                        Environment).

                        Here is an example doc string using one of several valid
                        formats:

                        """)
                    +
                    example_docstring
                )
                missing_commented = True
            else:
                brief_comment += layout_comment(f"""\
                    `{func_name}` lacks a doc string - you should probably add
                    one.
                    """)
        else:
            n_args = get_n_args(func_el)
            n_doc_lines = len(docstring.split('\n')) - WRAPPING_NEWLINE_N
            too_short = n_doc_lines < (conf.MIN_BRIEF_DOCSTRING + n_args)
            param_str = ' given the number of parameters' if n_args > 1 else ''
            if too_short:
                if not (inadequate_commented or repeated_message):
                    brief_comment += (
                        layout_comment(f"""\
                            #### Function doc string too brief?

                            The doc string for {func_name} seems a little
                            short{param_str}. You might want to rework it. Here
                            is an example using one of several valid formats:

                            """)
                        +
                        example_docstring
                    )
                    inadequate_commented = True
                else:
                    brief_comment += layout_comment(f"""\
                        The doc string for {func_name} seems a little short.
                        """)
    if not (missing_commented or inadequate_commented):
        return None
    message = {
        conf.BRIEF: brief_comment,
    }
    return message
