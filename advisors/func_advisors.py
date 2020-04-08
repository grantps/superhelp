from textwrap import dedent

from advisors import type_advisor, code_indent
import code_execution, conf, utils
from pydoc import doc

def get_func_name(element):
    """
    :return: None if no name
    :rtype: str
    """
    name = element.get('name')
    return name

def _get_arg_comment(line_dets):
    args = line_dets.element.xpath('args/arguments/args')
    kwonlyargs = line_dets.element.xpath('args/arguments/kwonlyargs')
    all_args_n = len(args + kwonlyargs)
    if all_args_n:
        nice_n_args = utils.int2nice(all_args_n)
        arg_comment = (f"It receives {nice_n_args} argument")
        if all_args_n > 1:
            arg_comment += 's'
    else:
        arg_comment = "It doesn't take any arguments"
    return arg_comment

def _get_returns_comment(line_dets, name):
    return_elements = line_dets.element.xpath('descendant-or-self::Return')
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
        returns_comment = (f"`{name}` does not explicitly return anything. "
            "In which case it implicitly returns None")
    else:
        returns_comment = (f"`{name}` exits via an explicit returns statement "
            f"{utils.int2nice(keyword_returns_n)} time")
        if keyword_returns_n > 1:
            returns_comment += ("s. Some people prefer functions to have one, "
                "and only one exit point for clarity. Others disagree e.g. "
                "using early returns to short-circuit functions if initial "
                "validation of some sort makes it possible to avoid the bulk "
                "of the function. Whatever approach you take make sure your "
                "function is easy to reason about in terms of what it returns "
                "and where it exits")
    return returns_comment

@type_advisor(element_type=conf.FUNC_DEF_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY)
def func_overview(line_dets):
    name = get_func_name(line_dets.element)
    arg_comment = _get_arg_comment(line_dets)
    returns_comment = _get_returns_comment(line_dets, name)
    message = {
        conf.BRIEF: dedent(f"""\
            The function is named `{name}`. {arg_comment}. {returns_comment}.
            """),
        conf.EXTRA: dedent(f"""\
            There is often confusion about the difference between arguments and
            parameters. Functions define parameters but receive arguments. You
            can think of parameters as being like car parks and arguments as the
            cars that fill them. You supply arguments to a function depending on
            its parameters.
            """)
    }
    return message

@type_advisor(element_type=conf.FUNC_DEF_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY, warning=True)
def func_len_check(line_dets):
    name = get_func_name(line_dets.element)
    crude_loc = len(line_dets.line_code_str.split('\n'))
    
    if crude_loc <= 3: #conf.MAX_BRIEF_FUNC_LOC:
        return None
    
    print("reset crude_loc to conf.MAX_BRIEF_FUNC_LOC")
    
    message = {
        conf.BRIEF: dedent(f"""\
            #### Function possibly too long

            `{name}` has {utils.int2nice(crude_loc)} lines of code
            (including comments). Sometimes it is OK for a function to be that
            long but you should consider refactoring the code into smaller
            units.
            """)
    }
    return message

def get_n_args(line_dets):
    arg_els = line_dets.element.xpath('args/arguments/args')
    kwonlyarg_els = line_dets.element.xpath('args/arguments/kwonlyargs')
    n_args = len(arg_els + kwonlyarg_els)
    return n_args

@type_advisor(element_type=conf.FUNC_DEF_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY, warning=True)
def func_excess_parameters(line_dets):
    name = get_func_name(line_dets.element)
    n_args = get_n_args(line_dets)
    if n_args <= 2:  #conf.MAX_BRIEF_FUNC_ARGS:
        return None
    
    print("reset n_args to conf.MAX_BRIEF_FUNC_ARGS")

    message = {
        conf.BRIEF: dedent(f"""\
            #### Possibly too many function parameters

            `{name}` has {n_args:,} parameters. Sometimes it is OK for a
            function to have that many but you should consider refactoring the
            code or collecting related parameters into single parameters e.g.
            instead of receiving image size arguments separately perhaps you
            could receive a dictionary of image size argument details.
            """),
        conf.MAIN: dedent(f"""\
            #### Possibly too many function parameters

            `{name}` has {n_args:,} parameters. Sometimes it is OK for a
            function to have that many but you should consider refactoring the
            code or collecting related parameters into single parameters e.g.
            instead of receiving image size arguments separately perhaps you
            could receive a dictionary of image size argument details.
            """),
    }
    return message

@type_advisor(element_type=conf.FUNC_DEF_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY, warning=True)
def positional_boolean(line_dets):
    """
    Defaults apply from the rightmost backwards (within their group - either
    defaults or kw_defaults (related to kwonlyargs)).
    """
    name = get_func_name(line_dets.element)
    arg_els = line_dets.element.xpath('args/arguments/args')  ## not kwonlyargs so potentially supplied positionally only
    arg_names = [arg_el.get('arg') for arg_el in arg_els]
    arg_default_els = line_dets.element.xpath('args/arguments/defaults')
    danger_statuses = []
    for arg_default_el in arg_default_els:
        if arg_default_el.get('value') in ['True', 'False']:
            danger_status = 'Boolean'
        elif arg_default_el.get('n'):
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
        if danger_status is None]
    if not danger_args:
        return None
    danger_args = '; '.join([
        f"{arg} - {danger_status}"
        for arg, danger_status in args_and_danger_statuses])
    brief_message = (
        dedent(f"""\
            #### Risky positional arguments expected

            Functions which expect numbers or booleans (True/False) without
            requiring keywords are risky.
            They are risky when if the function is changed later to have
            different parameters.
            For example, greeting(formal=True) is more intelligible than
            greeting(True).
            And intelligible code is safer to alter / maintain over time than
            mysterious code.

            A partial analysis of `{name}` found the following risky non-keyword
            (positional) parameters: {danger_args}.

            Using an asterisk as a pseudo-parameter forces all paramaters to the
            right to be keywords e.g.

            """)
        +
        code_indent(dedent(f"""\
            def greeting(name, *, formal=False):
                ...
            """)
        )
        +
        dedent(f"""\

            In this example you couldn't now call the function
            greeting('Jo', True) - it would need to be
            greeting('Jo', formal=True)
            """)
    )
    message = {
        conf.BRIEF: brief_message,
        conf.EXTRA: dedent(f"""\
            Putting an asterisk in the parameters has the effect of forcing all
            parameters to the right to be keyword parameters because the
            asterisk mops up any remaining positional arguments supplied
            (if any) when the function is called.
            There can't be any other positional arguments, because they have all
            been handled already, so only keyword parameters are allowed
            thereafter.
            """),
    }
    return message

@type_advisor(element_type=conf.FUNC_DEF_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY, warning=True)
def docstring_issues(line_dets):
    """
    No doc string, not enough lines to cover params, return etc.
    """
    name = get_func_name(line_dets.element)
    docstring = code_execution.get_docstring(line_dets.line_code_str, name)
    example_docstring = code_indent(dedent(f'''\
        def greet(name, *, formal=False):
            """
            Get a greeting for the supplied person with the appropriate
            formality.

            :param str name: person being greeted
            :param bool formal: set the formality of the greeting
            :return: a greeting to the person
            :rtype: str
            """
            if formal:
                greeting = f"Hi {{name}}"
            else:
                greeting = f"Hello {{name}}"
            return greeting
        '''))
    if docstring is None:
        comment = (
            dedent(f"""\
                #### Function missing doc string

                `{name}` lacks a doc string - you should probably add one.
                Here is an example using one of several valid formats:

                """)
            +
            example_docstring
        )
    else:
        n_args = get_n_args(line_dets)
        n_doc_lines = len(docstring.split('\n'))
        too_short = n_doc_lines < (conf.MIN_BRIEF_DOCSTRING + n_args)
        if too_short:
            comment = (
                dedent("""\
                    #### Function doc string too brief?

                    Your doc string seems a little short given the number
                    of parameters. You might want to rework it.
                    Here is an example using one of several valid formats:

                """)
                +
                example_docstring
            )
        else:
            return None
    message = {
        conf.BRIEF: comment,
    }
    return message
