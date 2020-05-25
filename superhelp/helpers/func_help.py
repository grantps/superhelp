"""
Covers functions and methods.
"""
from ..helpers import filt_block_help
from ..ast_funcs import get_danger_status, get_docstring_from_value, \
    get_el_lines_dets
from .. import conf
from .. import gen_utils
from ..gen_utils import get_nice_pairs, layout_comment as layout

FUNC_DEFN_XPATH = 'descendant-or-self::FunctionDef'

def get_mutable_status(default_el):
    """
    KISS - Only look for List, Dict, and Set. Python 3.6 as well as 3.8
    compatible.
    """
    if default_el.tag in ['List', 'Dict', 'Set']:
        mutable_status = default_el.tag
    else:
        mutable_status = None
    return mutable_status

def get_is_method(func_el):
    class_els = func_el.xpath('ancestor::ClassDef')
    if not class_els:
        return False
    class_el = class_els[-1]
    ## check is a direct member of a class and not just a function defined somewhere internally
    method_els = class_el.xpath('body/FunctionDef')
    return func_el in method_els

def get_func_type_lbl(func_el):
    func_type_lbl = (
        conf.METHOD_LBL if get_is_method(func_el) else conf.FUNCTION_LBL)
    return func_type_lbl

def get_overall_func_type_lbl(func_els):
    if not func_els:
        return None
    includes_plain_function = False
    for func_el in func_els:
        func_type_lbl = get_func_type_lbl(func_el)
        if func_type_lbl == conf.FUNCTION_LBL:
            includes_plain_function = True
    overall_func_type_lbl = (
        conf.FUNCTION_LBL if includes_plain_function else conf.METHOD_LBL)
    return overall_func_type_lbl

def count_args(func_el):
    """
    Have to handle positional-only, keyword-only, and standard arguments. Not
    counting any unpacked args (vararg and kwarg).
    """
    posonlyargs = func_el.xpath('args/arguments/posonlyargs/arg')  ## python 3.8+
    args = func_el.xpath('args/arguments/args/arg')
    kwonlyargs = func_el.xpath('args/arguments/kwonlyargs/arg')
    all_args_n = len(posonlyargs + args + kwonlyargs)
    return all_args_n

def _get_arg_comment(func_el, *, repeat=False):
    """
    Must cope with positional-only arguments, positional arguments, keyword
    arguments, keyword-only arguments, packed positional arguments, and packed
    keyword arguments. Trivial really ;-).

    Comment should end without a full stop because calling code adds that to
    make the sentence structure more explicit.
    """
    vararg = func_el.xpath('args/arguments/vararg/arg')
    kwarg = func_el.xpath('args/arguments/kwarg/arg')
    has_packing = (vararg or kwarg)
    if has_packing:
        arg_comment = 'receives a variable number of arguments'
        if repeat:
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
        all_args_n = count_args(func_el)
        if all_args_n:
            nice_n_args = gen_utils.int2nice(all_args_n)
            arg_comment = (f"receives {nice_n_args} argument")
            if all_args_n > 1:
                arg_comment += 's'
        else:
            arg_comment = "doesn't take any arguments"
    return arg_comment

def _get_return_comment(func_type_lbl, return_elements, *,
        repeat=False):
    """
    Comment should end without a full stop because calling code adds that to
    make the sentence structure more explicit.
    """
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
        returns_comment = (
            f"The {func_type_lbl} does not explicitly return anything")
        if not repeat:
            returns_comment += (
                ". In which case, in Python, it implicitly returns `None`")
    else:
        returns_comment = (
            f"The {func_type_lbl} exits via an explicit `return` statement "
            f"{gen_utils.int2nice(keyword_returns_n)} time")
        if not repeat:
            if keyword_returns_n > 1:
                returns_comment += (
                f"s. Some people prefer {func_type_lbl}s to have one, and only "
                "one exit point for clarity. Others disagree e.g. using early "
                f"returns to short-circuit {func_type_lbl}s if initial "
                "validation of some sort makes it possible to avoid the bulk of"
                f" the {func_type_lbl}. Whatever approach you take make sure "
                f"your {func_type_lbl} is easy to reason about in terms of what"
                " it returns and where it exits")
    return returns_comment

def _get_exit_comment(func_el, func_type_lbl, *, repeat=False):
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
        exit_comment = _get_return_comment(func_type_lbl,
            return_elements, repeat=repeat)
    return exit_comment

@filt_block_help(xpath=FUNC_DEFN_XPATH)
def func_overview(block_dets, *, repeat=False, **_kwargs):
    """
    Advise on function (or method) definition statements.
    e.g. def greeting(): ...
    """
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    if not func_els:
        return None
    overall_func_type_lbl = get_overall_func_type_lbl(func_els)

    title = layout(f"""\

        ### {overall_func_type_lbl.title()} Details
        """)
    detail_bits = []
    for func_el in func_els:
        func_type_lbl = get_func_type_lbl(func_el)
        name = func_el.get('name')
        arg_comment = _get_arg_comment(
            func_el, repeat=repeat)
        exit_comment = _get_exit_comment(
            func_el, func_type_lbl, repeat=repeat)
        detail_bits.append(layout(f"""\

            The {func_type_lbl} named `{name}` {arg_comment}. {exit_comment}.
            """))
    details = ''.join(detail_bits)
    if not repeat:
        args_vs_params = layout(f"""\

        There is often confusion about the difference between arguments and
        parameters. {overall_func_type_lbl.title()}s define parameters but
        receive arguments. You can think of parameters as being like car parks
        and arguments as the cars that fill them. You supply arguments to a
        {overall_func_type_lbl} depending on its parameters.
        """)
        if func_type_lbl == conf.METHOD_LBL:
            methods = layout("""\

            Methods are functions that sit directly inside a class definition.
            Unless they are defined as static methods e.g. using the
            `@staticmethod` decorator, they take the instance of the class as
            the first parameter - almost always named `self`. But they are
            basically functions.
                """)
        else:
            methods = ''
    else:
        args_vs_params = ''
        methods = ''

    message = {
        conf.BRIEF: title + details,
        conf.MAIN: title + details + methods,
        conf.EXTRA: args_vs_params,
    }
    return message

@filt_block_help(xpath=FUNC_DEFN_XPATH, warning=True)
def func_len_check(block_dets, *, repeat=False, **_kwargs):
    """
    Warn about functions that might be too long.
    """
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    if not func_els:
        return None
    overall_func_type_lbl = get_overall_func_type_lbl(func_els)
    long_func_dets = []
    for func_el in func_els:
        func_type_lbl = get_func_type_lbl(func_el)
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
            long_func_dets.append((name, func_lines_n))
    if not long_func_dets:
        return None

    title = layout(f"""\
    ### {overall_func_type_lbl.title()} possibly too long
    """)
    summary_bits = []
    for name, func_lines_n in long_func_dets:
        summary_bits.append(layout(f"""\

        `{name}` has {gen_utils.int2nice(func_lines_n)} lines of code (including
        comments but with empty lines ignored).
        """))
    summary = ''.join(summary_bits)
    if not repeat:
        sometimes_ok = (
            f" Sometimes it is OK for a {func_type_lbl} to be "
            "that long but you should consider refactoring the code "
            "into smaller units.")
    else:
        sometimes_ok = ''

    message = {
        conf.BRIEF: title + summary + sometimes_ok,
    }
    return message

def get_n_args(func_el):
    arg_els = func_el.xpath('args/arguments/args/arg')
    posonlyarg_els = func_el.xpath('args/arguments/posonlyargs/arg')
    kwonlyarg_els = func_el.xpath('args/arguments/kwonlyargs/arg')
    n_args = len(arg_els + posonlyarg_els + kwonlyarg_els)
    return n_args

@filt_block_help(xpath=FUNC_DEFN_XPATH, warning=True)
def func_excess_parameters(block_dets, *, repeat=False, **_kwargs):
    """
    Warn about functions that might have too many parameters.
    """
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    if not func_els:
        return None
    overall_func_type_lbl = get_overall_func_type_lbl(func_els)
    excess_param_dets = []
    for func_el in func_els:
        func_type_lbl = get_func_type_lbl(func_el)
        name = func_el.get('name')
        n_args = get_n_args(func_el)
        high_args = n_args > conf.MAX_BRIEF_FUNC_ARGS
        if high_args:
            excess_param_dets.append((name, n_args, func_type_lbl))
    if not excess_param_dets:
        return None

    title = layout(f"""\
    ### Possibly too many {overall_func_type_lbl} parameters
    """)
    summary_bits = []
    for i, (name, n_args, func_type_lbl) in enumerate(excess_param_dets):
        first = (i == 0)
        summary_bits.append(layout(f"""\

        `{name}` has {n_args:,} parameters.
        """))
        if first and not repeat:
            summary_bits.append(layout(f"""\

            Sometimes it is OK for a {func_type_lbl} to have that many but you
            should consider refactoring the code or collecting related
            parameters into single parameters e.g. instead of receiving image
            size arguments separately perhaps you could receive a dictionary of
            image size argument details.
            """))
    summary = ''.join(summary_bits)

    message = {
        conf.BRIEF: title + summary,
    }
    return message

def get_arg_default_issues(func_el, *, get_issue_status_func, include_kw=True):
    """
    Look at this function's arguments. Any issues?
    """
    posonly_arg_els = func_el.xpath('args/arguments/posonlyargs/arg')
    arg_els = func_el.xpath('args/arguments/args/arg')
    all_arg_els = posonly_arg_els + arg_els  ## order matters
    if include_kw:
        kwonly_arg_els = func_el.xpath('args/arguments/kwonlyargs/arg')
        all_arg_els +=  kwonly_arg_els
    arg_names = [arg_el.get('arg') for arg_el in all_arg_els]
    arg_default_els = func_el.xpath('args/arguments/defaults')
    default_els = arg_default_els  ## order matters
    if include_kw:
        kw_default_els = func_el.xpath('args/arguments/kw_defaults')
        default_els += kw_default_els
    issue_statuses = []
    for default_el in default_els:
        for child_el in default_el.getchildren():
            issue_status = get_issue_status_func(child_el)
            issue_statuses.append(issue_status)
    ## reversed because defaults are filled in rightwards e.g. a, b=1, c=2
    ## args = a,b,c and defaults=1,2 -> reversed c,b,a and 2,1 -> c: 2, b: 1
    arg_names_reversed = reversed(arg_names)
    issue_statuses_reversed = reversed(issue_statuses)
    args_and_issue_statuses = reversed(list(
        zip(arg_names_reversed, issue_statuses_reversed)))  ## back to left-to-right order
    args_with_issues = [(arg, issue_status)
        for arg, issue_status in args_and_issue_statuses
        if issue_status]
    return args_with_issues

def _get_mutable_default_args(func_el):
    """
    Interested in all args, not just non-keyword ones as when looking for danger
    arguments. We are also interested in all defaults as well.
    """
    return get_arg_default_issues(
        func_el, get_issue_status_func=get_mutable_status, include_kw=True)

@filt_block_help(xpath=FUNC_DEFN_XPATH, warning=True)
def mutable_default(block_dets, *, repeat=False, **_kwargs):
    """
    Look for use of mutable defaults and warn against use except in rare cases.
    """
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    if not func_els:
        return None
    overall_func_type_lbl = get_overall_func_type_lbl(func_els)
    mutable_defaults_dets = []
    for func_el in func_els:
        func_type_lbl = get_func_type_lbl(func_el)
        name = func_el.get('name')
        mutable_default_args = _get_mutable_default_args(func_el)
        if mutable_default_args:
            mutable_defaults_dets.append(
                (name, func_type_lbl, mutable_default_args))
    if not mutable_defaults_dets:
        return None

    title = layout(f"""\
    ### {overall_func_type_lbl.title()} has mutable default arguments
    """)
    brief_summary_bits = []
    main_summary_bits = []
    for i, mutable_default_dets in enumerate(mutable_defaults_dets):
        name, func_type_lbl, mutable_default_args = mutable_default_dets
        first = (i == 0)
        nice_pairs = get_nice_pairs(
            mutable_default_args, pair_glue=' defaults to a ')
        issue = layout(f"""\

        `{name}` has the following parameters with mutable defaults:
        {nice_pairs}.
        """)
        brief_summary_bits.append(issue)
        main_summary_bits.append(issue)
        if first and not repeat:  ## explaining once is enough ;-)
            main_summary_bits.append(layout(f"""\

            Mutable default arguments are a well-known "gotcha" in Python. They
            do not behave as most people would expect them to. It is better to
            have `None` as the default, and inside the function set the name to
            the desired mutable if it is `None`.
            """)
            +
            layout("""\
            ## BAD (mutable default)
            def communicate(person, msg, people=[]):
                people.append(person)
                for person in people:
                    print(f"Emailed {person} with message: '{msg}'")

            ## GOOD (no mutable defaults)
            def communicate(person, msg, people=None):
                if people is None:
                    people = []
                people.append(person)
                for person in people:
                    print(f"Emailed {person} with message: '{msg}'")
            """, is_code=True)
            )
    brief_summary = ''.join(brief_summary_bits)
    main_summary = ''.join(main_summary_bits)
    if not repeat:
        defaults_explained = (
            layout(f"""\

            {overall_func_type_lbl.title()}s are stored in memory when they are
            defined, and that includes any default arguments that belong to
            them. So every time the {overall_func_type_lbl} is called it is from
            the same piece of memory and the default argument is the same.
            Calling a {overall_func_type_lbl} multiple times will mean starting
            from the mutable default as it was left by the previous call - which
            makes sense because it is one and the same thing.

            Let's use our BAD version of the `communicate` function to see what
            happens:
            """)
            +
            layout("""\
            ## BAD (people list will persist across multiple calls)
            def communicate(person, msg, people=[]):
                people.append(person)
                for person in people:
                    print(f"Emailed {person} with message: '{msg}'")

            communicate('Jack', 'Apples are on special')
            ## people is empty, so only Jack is emailed
            # >>> Emailed Jack with message: 'Apples are on special'

            communicate('Jill', 'Tennis this Saturday')
            ## people started with Jack in it so both Jack AND Jill get emailed!
            # >>> Emailed Jack with message: 'Tennis this Saturday'  # <---oops!
            # >>> Emailed Jill with message: 'Tennis this Saturday'
            """, is_code=True)
        )
    else:
        defaults_explained = ''

    message = {
        conf.BRIEF: title + brief_summary,
        conf.MAIN: title + main_summary + defaults_explained,
    }
    return message

def _get_positional_danger_args(func_el):
    """
    Interested in non-keyword args only. So posonly_args and args respectively.
    As for defaults, defaults only (ignoring kw_defaults - the only other option
    - there is no separate posonly_defaults)
    """
    return get_arg_default_issues(
        func_el, get_issue_status_func=get_danger_status, include_kw=False)

@filt_block_help(xpath=FUNC_DEFN_XPATH, warning=True)
def positional_boolean(block_dets, *, repeat=False, **_kwargs):
    """
    Look for any obvious candidates for forced keyword use e.g. where a
    parameter is a boolean or a number.

    Defaults apply from the rightmost backwards (within their group - either
    defaults or kw_defaults (related to kwonlyargs)).
    """
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    if not func_els:
        return None
    overall_func_type_lbl = get_overall_func_type_lbl(func_els)
    positional_dets = []
    for func_el in func_els:
        func_type_lbl = get_func_type_lbl(func_el)
        name = func_el.get('name')
        danger_args = _get_positional_danger_args(func_el)
        if danger_args:
            positional_dets.append((name, func_type_lbl, danger_args))
    if not positional_dets:
        return None

    title = layout(f"""\
    ### {overall_func_type_lbl.title()} expects risky positional arguments
    """)
    summary_bits = []
    for i, (name, func_type_lbl, danger_args) in enumerate(positional_dets):
        first = (i == 0)
        summary_bits.append(layout(f"""\

        A partial analysis of `{name}` found the following risky non-keyword
        (positional) parameters: {get_nice_pairs(danger_args, left_quoter='')}.
        """))
        if first and not repeat:  ## explaining once is enough ;-)
            summary_bits.append(layout(f"""\

            {func_type_lbl.title}s which expect numbers or booleans
            (`True`/`False`) without requiring keywords are risky. They are
            risky when if the {func_type_lbl} is changed later to have different
            parameters. For example, `greeting(formal=True)` is more
            intelligible than `greeting(True)`. And intelligible code is safer
            to alter / maintain over time than mysterious code.
            """))
    summary = ''.join(summary_bits)
    if not repeat:
        asterisk_demo = (
            layout("""\

            Using an asterisk as a pseudo-parameter forces all parameters to the
            right to be keywords e.g.
            """)
            +
            layout("""\
            def greeting(name, *, formal=False):
                ...
            """, is_code=True)
            +
            layout("""\

            In this example you couldn't now call the function `greeting('Jo',
            True)` - it would need to be `greeting('Jo', formal=True)`
            """)
        )
        asterisk_explained = layout(f"""\

        Putting an asterisk in the parameters has the effect of forcing all
        parameters to the right to be keyword parameters because the asterisk
        mops up any remaining positional arguments supplied (if any) when the
        {func_type_lbl} is called. There can't be any other positional
        arguments, because they have all been handled already, so only keyword
        parameters are allowed thereafter.
        """)
    else:
        asterisk_demo = ''
        asterisk_explained = ''

    message = {
        conf.BRIEF: title + summary + asterisk_demo,
        conf.EXTRA: asterisk_explained,
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
                        docstring = get_docstring_from_value(first_value_el)
    return func_name, docstring

def get_funcs_dets_and_docstring(func_els):
    funcs_dets_and_docstring = []
    for func_el in func_els:
        func_name, docstring = get_func_name_docstring(func_el)
        func_dets_and_docstring = (func_el, func_name, docstring)
        funcs_dets_and_docstring.append(func_dets_and_docstring)
    return funcs_dets_and_docstring

@filt_block_help(xpath=FUNC_DEFN_XPATH, warning=True)
def docstring_issues(block_dets, *, repeat=False, **_kwargs):
    """
    Check over function doc strings. Missing doc string, not enough lines to
    cover params, return etc.
    """
    WRAPPING_NEWLINE_N = 2
    MISSING_DOCSTRING = 'missing_docstring'
    DOCSTRING_TOO_SHORT = 'docstring_too_short'
    func_els = block_dets.element.xpath(FUNC_DEFN_XPATH)
    if not func_els:
        return None
    funcs_dets_and_docstring = get_funcs_dets_and_docstring(func_els)
    docstring_issues = []
    for func_el, func_name, docstring in funcs_dets_and_docstring:
        func_type_lbl = get_func_type_lbl(func_el)
        if docstring is None:
            docstring_issues.append(
                (func_name, func_type_lbl, MISSING_DOCSTRING))
        else:
            n_args = get_n_args(func_el)
            n_doc_lines = len(docstring.split('\n')) - WRAPPING_NEWLINE_N
            too_short = n_doc_lines < (conf.MIN_BRIEF_DOCSTRING + n_args)
            param_str = ' given the number of parameters' if n_args > 1 else ''
            if too_short:
                docstring_issues.append(
                (func_name, func_type_lbl, DOCSTRING_TOO_SHORT))
    if not docstring_issues:
        return None

    title = layout("""\
    ### Function / Method missing doc string
    """)
    example_docstring = layout(f'''\
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
    summary_bits = []
    for i, (func_name, func_type_lbl, problem) in enumerate(docstring_issues):
        first = (i == 0)
        if problem == MISSING_DOCSTRING:
            if first and not repeat:  ## only want to say it once ;-)
                summary_bits.append((
                    layout(f"""\

                    #### {func_type_lbl.title()} missing doc string

                    `{func_name}` lacks a doc string - you should probably add
                    one.

                    Note - # comments at the top of the {func_type_lbl} do not
                    work as doc strings. Python completely ignores them. If you
                    add a proper doc string, however, it can be accessed by
                    running `help({func_name})` or `{func_name}.`\_\_doc\_\_.
                    Which is useful when using this {func_type_lbl} in bigger
                    projects e.g. in an IDE (Integrated Development
                    Environment).

                    Here is an example doc string for a simple function using
                    one of several valid formats:
                    """)
                    +
                    example_docstring
                ))
            else:
                summary_bits.append(layout(f"""\
                #### `{func_name}` lacks a doc string

                You should probably add a doc string to `{func_name}`
                """))
        elif problem == DOCSTRING_TOO_SHORT:
            if first and not repeat:
                summary_bits.append((layout(f"""\
                #### Function doc string too brief?

                The doc string for `{func_name}` seems a little
                short{param_str}. You might want to rework it. Here is an
                example using one of several valid formats:
                """)
                +
                example_docstring
                ))
            else:
                summary_bits.append(layout(f"""\
                #### Function doc string too brief?

                The doc string for `{func_name}` seems a little short.
                """))
    summary = ''.join(summary_bits)

    message = {
        conf.BRIEF: title + summary,
    }
    return message
