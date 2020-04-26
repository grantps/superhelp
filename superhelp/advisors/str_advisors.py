from ..advisors import any_block_advisor, filt_block_advisor
from .. import code_execution, conf
from ..utils import get_python_version, layout_comment as layout

F_STR = 'f-string'
STR_FORMAT_FUNC = 'str_format'
SPRINTF = 'sprintf'
STR_ADDITION = 'string addition'

ASSIGN_VALUE_XPATH = 'descendant-or-self::Assign/value'
FUNC_ATTR_XPATH = 'descendant-or-self::value/Call/func/Attribute'
JOINED_STR_XPATH = 'descendant-or-self::Assign/value/JoinedStr'
SPRINTF_XPATH = 'descendant-or-self::value/BinOp/op/Mod'
STR_ADDITION_XPATH = 'descendant-or-self::BinOp/left/Str'  ## each left has a right as well so only need to look at one to get at binop and assign ancestors etc

F_STR_REMINDER = False

def get_str_els_3_7(block_el):
    str_els = block_el.xpath('descendant-or-self::Assign/value/Str')
    return str_els

def get_str_els_3_8(block_el):
    assign_val_els = block_el.xpath(ASSIGN_VALUE_XPATH)
    str_els = []
    for assign_val_el in assign_val_els:
        assign_str_els = assign_val_el.xpath('Constant')
        if len(assign_str_els) != 1:
            continue
        assign_str_el = assign_str_els[0]
        if assign_str_el.get('type') == 'str':
            str_els.append(assign_str_el)
    return str_els

def get_str_els_being_combined_3_7(block_el):
    str_els_being_combined = block_el.xpath(
        'descendant-or-self::BinOp/left/Str')
    return str_els_being_combined

def get_str_els_being_combined_3_8(block_el):
    left_str_els = block_el.xpath('descendant-or-self::BinOp/left/Constant')
    str_els_being_combined = []
    for left_str_el in left_str_els:
        if left_str_el.get('type') == 'str':
            str_els_being_combined.append(left_str_el)
    return str_els_being_combined

python_version = get_python_version()
if python_version in (conf.PY3_6, conf.PY3_7):
    get_str_els = get_str_els_3_7
    get_str_els_being_combined = get_str_els_being_combined_3_7
elif python_version == conf.PY3_8:
    get_str_els = get_str_els_3_8
    get_str_els_being_combined = get_str_els_being_combined_3_8
else:
    raise Exception(f"Unexpected Python version {python_version}")

@filt_block_advisor(xpath=ASSIGN_VALUE_XPATH)
def assigned_str_overview(block_dets, *, repeated_message=False):
    """
    Provide overview of assigned strings e.g. name = 'Hamish'.
    """
    brief_comment = ''
    str_els = get_str_els(block_dets.element)
    if not str_els:
        return None
    first_name = None
    first_val = None
    for i, str_el in enumerate(str_els):
        assign_el = str_el.xpath('ancestor::Assign')[0]
        first = (i == 0)
        name = assign_el.xpath('targets/Name')[0].get('id')
        val = code_execution.get_val(
            block_dets.pre_block_code_str, block_dets.block_code_str, name)
        if first:
            first_name = name
            first_val = val
            brief_comment += layout("""\

                #### String Overview

                """)
        brief_comment += layout(f"""\
            `{name}` is a string.

            """)
    if repeated_message:
        main_comment = brief_comment
        extra_comment = ''
    else:
        brief_comment += layout(f"""\
            Python makes it easy to do lots of cool things with strings.

            """)
        if first_val:
            name2use = first_name
            val2use = first_val
        else:
            name2use = 'address'
            val2use = 'Waiuku, New Zealand'
            brief_comment += layout(f"""\
                For illustration, imagine we have string '{val2use}' assigned to
                `{name2use}`:

                """)
        main_comment = brief_comment  ## after this brief and main diverge
        brief_comment += layout(f"""\
            {name2use}.upper() returns {val2use.upper()}.

            """)
        black_heart = "\N{BLACK HEART}"
        main_comment += layout(f"""\
            Examples:

            {name2use}.upper() returns {val2use.upper()}.

            {name2use}.center(70, '=') returns {val2use.center(70, '=')}

            {name2use}.endswith('chicken') returns {val2use.endswith('chicken')}

            {name2use} + ' is a string' returns {val2use + ' is a string'}

            {name2use} + ' ' + '{{\\NBLACK HEART}}' + ' Python' returns
            {val2use + ' ' + black_heart + ' Python'}

            len({name2use}) returns {len(val2use)} because that is how many
            characters are in the {name2use} string (remember to count spaces -
            they are characters too)

            sorted({name2use}) returns {sorted(val2use)}
            """)
        extra_comment = layout("""\
            .upper(), .center() etc are abilities available with all Python
            strings. Technically they are methods of string objects. They start
            with a dot and are on the end of the object.

            To see the full list of string methods enter dir(str) into a Python
            command line.

            len() is a function which can be used on lots of things - not just
            string objects. It is not a method of the string object. Other
            functions that are not string-specific but are commonly used with
            strings include sorted() and print().
            """)
    message = {
        conf.BRIEF: brief_comment,
        conf.MAIN: main_comment,
        conf.EXTRA: extra_comment,
    }
    return message

def str_combination(combination_type, str_els, *, repeated_message=False):
    global F_STR_REMINDER
    brief_comment = ''
    title = None
    for str_el in str_els:
        try:
            assign_el = str_el.xpath('ancestor::Assign')[-1]
        except IndexError:
            name = "An unnamed string"
        else:
            raw_name = assign_el.xpath('targets/Name')[0].get('id')
            name = f"`{raw_name}`"
        combination_type2comment = {
            F_STR: "f-string interpolation",
            STR_FORMAT_FUNC: "the format function",
            SPRINTF: "sprintf string interpolation",
            STR_ADDITION: "string addition (e.g. animal = 'jelly' + 'fish')",
        }
        combination_comment = combination_type2comment[combination_type]
        if not title:
            title = layout(f"""\

            ### Strings created by combining or interpolating strings
            """)
            brief_comment += title
        brief_comment += layout(f"""\

            {name} is created using {combination_comment}.
            """)
    message = {
        conf.BRIEF: brief_comment,
        conf.MAIN: brief_comment,
    }
    if combination_type != F_STR and not repeated_message:
        if not F_STR_REMINDER:
            F_STR_REMINDER = True
            message[conf.BRIEF] += layout("""\
    
                Your snippet uses a non-f-string approach to constructing a
                string.

                Have you considered using an f-string approach to constructing
                your string?
                """)
            message[conf.MAIN] += (
                layout("""\

                    Have you considered using an f-string approach to
                    constructing your string?

                    f-strings let you reference variables from earlier in your
                    code and allow very readable string construction. All the
                    usual tricks of the .format() approach also work. For
                    example, comma separating thousands in numbers:

                    """)
                +
                layout("""\
                    cost = 10_550
                    print(f"Cost is ${cost:,}")
                    # >>> 'Cost is $10,550'
                    """, is_code=True)
                +
                layout(f"""\

                    Or making small in-line calculations:

                    """)
                +
                layout("""\
                    people = ['Bart', 'Lisa']
                    print(f"There are {len(people)} people")
                    # >>> 'There are 2 people'
                    """, is_code=True)
                +
                layout(f"""\

                    Or zero-padding numbers:

                    """)
                +
                layout("""\
                    num = 525
                    print(f"{num:0>4}")
                    # >>> '0525'
                    """, is_code=True)
            )
    return message

@filt_block_advisor(xpath=JOINED_STR_XPATH)
def f_str_interpolation(block_dets, *, repeated_message=False):
    """
    Examine f-string interpolation.
    """
    joined_els = block_dets.element.xpath(JOINED_STR_XPATH)
    return str_combination(F_STR,
        joined_els, repeated_message=repeated_message)

@filt_block_advisor(xpath=FUNC_ATTR_XPATH)
def format_str_interpolation(block_dets, repeated_message=False):
    """
    Look at use of .format() to interpolate into strings.
    """
    func_attr_els = block_dets.element.xpath(FUNC_ATTR_XPATH)
    format_funcs = []
    for func_attr_el in func_attr_els:
        is_format_func = func_attr_el.get('attr') == 'format'
        if is_format_func:
            format_funcs.append(func_attr_el)
    if not format_funcs:
        return None
    return str_combination(STR_FORMAT_FUNC,
        format_funcs, repeated_message=repeated_message)

@any_block_advisor()
def sprintf(block_dets, *, repeated_message=False):
    """
    Look at use of sprintf for string interpolation e.g. greeting = "Hi %s" %
    name
    """
    sprintf_els = block_dets.element.xpath(SPRINTF_XPATH)
    has_sprintf = bool(sprintf_els)
    if not has_sprintf:
        return None
    return str_combination(SPRINTF,
        sprintf_els, repeated_message=repeated_message)

@any_block_advisor()
def string_addition(block_dets, *, repeated_message=False):
    """
    Advise on string combination using +. Explain how f-string alternative
    works.
    """
    str_els_being_combined = get_str_els_being_combined(block_dets.element)
    has_string_addition = False
    str_addition_els = []
    for str_el in str_els_being_combined:
        ## Does their immediate ancestor BinOp have op of Add?
        ## Don't know if there any alternatives but let's be sure
        ## Ordered set of nodes, from parent to ancestor? https://stackoverflow.com/a/15645846
        bin_op_el = str_el.xpath('ancestor-or-self::BinOp')[-1]
        ## was it an Add op
        has_add = bool(bin_op_el.xpath('op/Add'))
        if has_add:
            str_addition_els.append(str_el)
            has_string_addition = True
    if not has_string_addition:
        return None
    addition_message = str_combination(STR_ADDITION,
        str_addition_els, repeated_message=repeated_message)
    return addition_message
