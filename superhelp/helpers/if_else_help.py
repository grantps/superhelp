from collections import defaultdict, namedtuple, Counter

from ..helpers import filt_block_help
from .. import ast_funcs, conf
from ..gen_utils import int2nice, layout_comment as layout

IfDets = namedtuple('IfDetails',
    'multiple_conditions, missing_else, if_clauses')

ELIF = 'elif'
ELSE = 'else'

STRING = 'string'
NUMBER = 'number'

IF_XPATH = 'descendant-or-self::If'

def add_if_details(if_element, if_clauses):
    """
    If under our <If>'s <orelse> we have another <If>, and it is the only child,
    store an 'elif' in if_details and send the <If> under <orelse> through
    again (the AST nests them even though they are siblings in the original code
    syntax); otherwise store an 'else' in if_details and return.

    <If>s have <orelse>s which either have sole <If>s or not. When there is not
    then we have reached else.
    """
    orelse_el = if_element.xpath('orelse')[0]  ## always has one
    orelse_children = orelse_el.getchildren()
    if not orelse_children:
        return  ## merely an If on its own without clauses
    ## else: if or elif: ?
    just_the_if_under_orelse = (
        len(orelse_children) == 1 and orelse_children[0].tag == 'If')
    has_elif = just_the_if_under_orelse
    if has_elif:
        if_clauses.append(ELIF)
        elif_el = orelse_children[0]
        add_if_details(elif_el, if_clauses)
    else:
        if_clauses.append(ELSE)
    return

def get_ifs_details(block_dets):
    """
    There can be multiple if statements in a snippet so we have to handle each
    of them.

    And in AST the following are very similar:

    if foo:
        ...
    else:
        if bar:
            ...

    if foo:
        ...
    elif bar:
        ...

    They both result in:
    <orelse>
        <If ...>

    So need to look under the 'orelse' for anything other than an 'If' to decide
    whether an 'else' or 'elif'.
    """
    ## skip when if __name__ == '__main__'
    if block_dets.block_code_str.startswith("if __name__ == "):
        return []
    raw_if_els = block_dets.element.xpath(IF_XPATH)
    if_elements = []
    for raw_if_el in raw_if_els:
        ## ignore if really an elif
        parent_el = raw_if_el.getparent()
        has_or_else_parent = (parent_el.tag == 'orelse')
        has_siblings = len(parent_el.getchildren()) > 1
        actually_elif = (has_or_else_parent and not has_siblings)
        if not actually_elif:
            if_elements.append(raw_if_el)
    ifs_details = []
    for if_element in if_elements:
        if_clauses = []
        add_if_details(if_element, if_clauses)
        multiple_conditions = bool(if_clauses)
        if multiple_conditions:
            last_sub_if = if_clauses[-1]
            missing_else = (last_sub_if != ELSE)
        else:
            missing_else = False
        ifs_details.append(
            IfDets(multiple_conditions, missing_else, if_clauses))
    return ifs_details

def _get_if_comment(block_dets):
    """
    Have to cope with multiple if statements and make it nice (unnumbered) when
    only one.
    """
    ifs_details = get_ifs_details(block_dets)
    if_comment = ''
    for n, if_details in enumerate(ifs_details, 1):
        counter = '' if len(ifs_details) == 1 else f" {int2nice(n)}"
        if if_details.multiple_conditions:
            n_elifs = if_details.if_clauses.count(ELIF)
            else_comment = (
                " and no `else` clause." if if_details.missing_else
                else " and an `else` clause.")
            elif_rules_comment = (
                " Note - `else` clauses with an `if`, and only an `if`, "
                "underneath count as `elif` clauses not `else` clauses.")
            if_comment += layout(f"""\

            `if` statement{counter} has {int2nice(n_elifs)} `elif` clauses
            {else_comment}{elif_rules_comment}
            """)
        else:
            if_comment += layout(f"""\

            `if` statement{counter} has no extra clauses e.g. `elif`s or an
            `else`.
            """)
    return if_comment

@filt_block_help(xpath=IF_XPATH)
def if_else_overview(block_dets, *, repeat=False, **_kwargs):
    """
    Look at conditional statements using if (apart from if __name__ ==
    '__main__").
    """
    if block_dets.block_code_str.startswith("if __name__ == "):
        return None

    title = layout("""
    ### Conditional statement detected
    """)
    if_comment = _get_if_comment(block_dets)
    if not repeat:
        demo = (
            layout("""\

            When using `if`, `elif`, or `else`, the item evaluated can either be
            an expression or a name (variable). Sometimes your code can be more
            readable if you make an intermediate variable and use that instead.
            Shorter, more readable, easier to check the parts. For example:
            """)
            +
            layout("""\
            if length_matters and len(phrase) > conf.MAX_SANE_LENGTH:
                phrase = chop(phrase)
            """, is_code=True)
            +
            layout("""\
            is shorter but more complex than:
            """)
            +
            layout("""\
            too_long = (
                length_matters
                and len(phrase) > conf.MAX_SANE_LENGTH
            )
            if too_long:
                phrase = chop(phrase)
            """, is_code=True)
        )
    else:
        demo = ''

    message = {
        conf.BRIEF: title + if_comment,
        conf.MAIN: title + if_comment + demo,
    }
    return message

@filt_block_help(xpath=IF_XPATH, warning=True)
def missing_else(block_dets, *, repeat=False, **_kwargs):
    """
    Warn about benefits in many cases of adding else clause if missing.
    """
    ifs_details = get_ifs_details(block_dets)
    ifs_dets_missing_else = [
        if_details for if_details in ifs_details if if_details.missing_else]
    if not ifs_dets_missing_else:
        return None

    title = layout("""\

        ### Possibly better with `else` clause

        """)
    summary_bits = []
    for i, if_details in enumerate(ifs_dets_missing_else):
        first = (i == 0)
        counter = (
            '' if len(ifs_dets_missing_else) == 1 else f" {int2nice(i + 1)}")
        summary_bits.append(layout(f"""\
        `if` block{counter} has `elif` clauses but lacks an `else` clause.
        """))
        if first and not repeat:
            summary_bits.append(layout(f"""\

            If your `elif` clauses are trying to handle all expected cases it is
            probably best to include an `else` clause as well just in case
            something unexpected happens.

            Note - `else` clauses with an `if` and only the `if` underneath
            count as `elif` clauses.
                """))
    summary = ''.join(summary_bits)
    dets = (
        layout("""\

        You may have left out the `else` because it is currently impossible that
        this branch will ever be called. You know that you can only receive the
        items currently handled by the `elif`s so `else` can logically never be
        called. And that it true - until it isn't later ;-) - for example, if
        the calling code starts supplying more types of whatever is being
        evaluated in the `elif`s. This problem happens surprisingly often and
        can create nasty bugs that are hard to trace. If you add an `else`
        clause that raises an exception you will instantly know if the expected
        conditions for your conditional are breached and exactly what to fix.

        For example:
        """)
        +
        layout("""\
        ## At the point this code is written we absolutely know
        ## there are only two user types: managers and staff

        if user == 'manager':
            create_alert()
            set_up_manager(user)
        elif user == 'staff':
            set_up_staff(user)
        else:
            ## This can logically never happen so
            ## we might be tempted to leave out the else clause
            pass
        """, is_code=True)
        +
        layout("""\

        But then a new user type is created (e.g. admin) and the logic of the
        entire program breaks all over the place with no clarity about the real
        source.

        It would be better to have an `else` clause as follows so you know
        exactly what violated the program's assumptions:
        """)
        +
        layout("""\
        else:
            raise Exception(f"Unexpected user: '{user}'")
        """, is_code=True)
        )

    message = {
        conf.BRIEF: title + summary,
        conf.MAIN: title + summary + dets,
    }
    return message

def get_split_membership_dets(if_el):
    """
    if x == 'a' or x == 'b' or x == 'c':
        print(x)

    If/test/BoolOp/values/Compare
                                 left/Name id 'x'
                                 comparators/Constant s 'a'
                                 comparators/Num n  etc

    Only provide message using content if all items are of the same type and are
    either numbers or strings.
    """
    compare_els = if_el.xpath('test/BoolOp/values/Compare')
    if not compare_els:
        return None
    left_name_comp_vals = defaultdict(list)
    basic_types = set()
    for compare_el in compare_els:
        left_name_els = compare_el.xpath('left/Name')
        if not left_name_els:
            continue
        left_name = left_name_els[0].get('id')
        if not left_name:
            continue
        comparators_els = compare_el.xpath('comparators')
        if not comparators_els:
            continue
        comparators_el = comparators_els[0]
        comparison_els = comparators_el.getchildren()  ## e.g. Strs, Nums, NameConstants etc
        if not comparison_els:
            continue
        comparison_el = comparison_els[0]  ## Str or Num etc
        comp_val = ast_funcs.str_from_el(comparison_el)
        if comp_val is not None:
            basic_types.add(STRING)
            if len(basic_types) > 1:
                return None
        else:
            comp_val = ast_funcs.num_str_from_el(comparison_el)
            if comp_val is not None:
                basic_types.add(NUMBER)
                if len(basic_types) > 1:
                    return None
            else:
                return None  ## Give up - something is not right
        left_name_comp_vals[left_name].append(comp_val)
    c = Counter(left_name_comp_vals.keys())
    comp_var = c.most_common(1)[0][0]
    comp_vals = left_name_comp_vals[comp_var]
    comp_val_strs = []
    basic_type = basic_types.pop()
    for comp_val in comp_vals:
        if basic_type == STRING:
            quoter = "'" if '"' in comp_val else "'"
            comp_val_strs.append(f"{quoter}{comp_val}{quoter}")
        elif basic_type == NUMBER:
            comp_val_strs.append(str(comp_val))
        else:
            raise ValueError(f"Unexpected basic type: '{basic_type}'")
    comp_vals_gp_str = '[' + ', '.join(comp_val_strs) + ']'
    return comp_var, comp_vals_gp_str

@filt_block_help(xpath=IF_XPATH)
def split_group_membership(block_dets, *, repeat=False, **_kwargs):
    """
    Explain how to use in group and not in group rather than multiple
    comparisons.

    if x == 'a' or x == 'b' or x == 'c':
        print(x)
    ==>
    if x in ['a', 'b', 'c']:
        print(x)
    """
    if_els = block_dets.element.xpath(IF_XPATH)
    if not if_els:
        return None
    has_split = False
    for if_el in if_els:
        try:
            comp_var, comp_vals_gp_str = get_split_membership_dets(if_el)
        except TypeError:
            continue
        else:
            has_split = True
            break
    if not has_split:
        return None

    summary = layout(f"""\
    ### Possible option of evaluating group membership

    It looks like `{comp_var}` has been in multiple separate comparisons. In
    Python it is possible to do a simple check of group membership instead.
    """)
    if not repeat:
        demo = (
            layout("""\
            For example:
            """)
            +
            layout(f"""\
            if {comp_var} in {comp_vals_gp_str}:
                ...
            """, is_code=True)
        )
        extra_demo = (
            layout("""\
            Or to check if a variable is NOT in a group:
            """)
            +
            layout(f"""\
            if {comp_var} not in {comp_vals_gp_str}:
                ...
            """, is_code=True)
        )
    else:
        demo = ''
        extra_demo = ''

    message = {
        conf.BRIEF: summary + demo,
        conf.MAIN: summary + demo + extra_demo,
    }
    return message

def get_has_explicit_count(if_el):
    compare_els = if_el.xpath('test/Compare')
    if not compare_els:
        return False
    compare_el = compare_els[0]
    func_name_els = compare_el.xpath('left/Call/func/Name')
    if not func_name_els:
        return False
    len_func = (func_name_els[0].get('id') == 'len')
    if not len_func:
        return False
    ops_els = compare_el.xpath('ops')
    if not ops_els:
        return False
    ops_el = ops_els[0]
    operator_els = ops_el.getchildren()
    if not operator_els:
        return False
    operator_type = operator_els[0].tag  ## e.g. Gt
    comparators_els = compare_el.xpath('comparators')
    if not comparators_els:
        return False
    comparator_el = comparators_els[0]
    comparison_els = comparator_el.getchildren()
    if not comparison_els:
        return False
    comparison_el = comparison_els[0]
    n = ast_funcs.num_str_from_el(comparison_el)
    if n is None:
        return False
    explicit_booleans = [
        ('Gt', '0'),
        ('GtE', '1'),
        ('Eq', '0'),
        ('LtE', '0'),
        ('Lt', '1'),
    ]
    has_explicit_boolean = ((operator_type, n) in explicit_booleans)
    return has_explicit_boolean

@filt_block_help(xpath=IF_XPATH)
def implicit_boolean_enough(block_dets, *, repeat=False, **_kwargs):
    """
    Look for cases where an implicit boolean comparison is enough.
    """
    if repeat:
        return None
    if_els = block_dets.element.xpath(IF_XPATH)
    if not if_els:
        return None
    implicit_boolean_possible = False
    for if_el in if_els:
        has_explicit_count = get_has_explicit_count(if_el)
        if has_explicit_count:
            implicit_boolean_possible = True
        else:
            continue
    if not implicit_boolean_possible:
        return None
    title = layout("""\
    ### Possible option of using an implicit boolean
    """)
    if not repeat:
        summary = (
            layout("""\

            There is often no need to check a non-zero length explicitly. In
            Python, "", 0, [], {}, (), `None` all evaluate to False when we ask
            if they are `True` or `False`. And they all evaluate to `True` if
            they contain something.

            So if we have a list `my_list` we can replace:
            """)
            +
            layout("""\
            if len(my_list) > 0:
                ...

            """, is_code=True)
            +
            layout("""\
            with:
            """)
            +
            layout("""\
            if my_list:  ## if empty, evaluates to False otherwise True
                ...

            """, is_code=True)
        )
    else:
        summary = layout("""\
        There is often no need to check a non-zero length explicitly.
        """)
    message = {
        conf.BRIEF: title + summary,
    }
    return message

def could_short_circuit(if_el):
    """
    Is there the potential to take advantage of Python's ability to short-
    circuit and collapse a nested IF into its parent as a single expression?

    The if_el must have an IF as its only child AND that nested IF must have an
    ORELSE as a child. But that ORELSE must have no children.

    :param element if_el: If element
    :return: True if the If has the potential to be short-circuited
    :rtype: bool
    """
    body_els = if_el.xpath('body')
    has_one_body = len(body_els) == 1
    if not has_one_body:
        return False
    body_el = body_els[0]
    body_children_els = body_el.getchildren()
    body_one_child = len(body_children_els) == 1
    if not body_one_child:
        return False
    body_child_el = body_children_els[0]
    sole_child_is_if = body_child_el.tag == 'If'
    if not sole_child_is_if:
        return False
    nested_if_el = body_child_el
    nested_if_orelse_els = nested_if_el.xpath('orelse')
    one_orelse = len(nested_if_orelse_els) == 1
    if not one_orelse:
        return False
    nested_if_orelse_el = nested_if_orelse_els[0]
    orelse_has_children = bool(nested_if_orelse_el.getchildren())
    if orelse_has_children:
        return False
    ## we have an IF with one child which is an IF and the nested IF's ORELSE has no children
    return True

@filt_block_help(xpath=IF_XPATH)
def short_circuit(block_dets, *, repeat=False, **_kwargs):
    """
    Look for cases where short-circuiting is possible.
    """
    if_els = block_dets.element.xpath(IF_XPATH)
    if not if_els:
        return None
    could_short_circuit_something = False
    for if_el in if_els:
        if could_short_circuit(if_el):
            could_short_circuit_something = True
            break
    if not could_short_circuit_something:
        return None

    summary = layout("""\
    ### Potential to collapse `if`s (possibly relying on short-circuiting)

    This code contains nested `if`s that could potentially be collapsed into one
    single conditional expression.
    """)
    if not repeat:
        how2short_circuit = layout("""\

        If the second `if` can only be run once the first `if` has been
        evaluated as True it is still possible to combine the two expressions -
        as long as the two expressions are combined with `and` AND the test to
        see if the nested expression can be run comes first. We can do this
        because Python supports "short-circuiting" :-).
        """)
        demo = (
            layout("""\
            For example, we can rewrite the following:
            """)
            +
            layout("""\
            if word is not None:
                ## the next expression would raise TypeError: object of type
                ## 'NoneType' has no len() if word was None and it got this far
                if len(word) > 20:
                    print(f"'{word}' is a long word")

            """, is_code=True)
            +
            layout("""\
            as:
            """)
            +
            layout("""\
            ## the second clause is only evaluated if the first evaluates as True
            ## i.e. we have relied on short-circuiting
            if word is not None and len(word) > 20:
                print(f"'{word}' is a long word")

            """, is_code=True)
        )
    else:
        how2short_circuit = ''
        demo = ''

    message = {
        conf.BRIEF: summary + how2short_circuit,
        conf.MAIN: summary + how2short_circuit + demo,
    }
    return message

def could_any_or_all(if_el):
    could_any = False
    could_all = False
    boolop_val_els = if_el.xpath('descendant::BoolOp/values')
    for boolop_val_el in boolop_val_els:
        n_items = len(boolop_val_el.getchildren())
        if n_items < conf.MIN4ANY_OR_ALL:  ## worth doing any or all
            continue
        boolop_el = boolop_val_el.getparent()
        op_els = boolop_el.xpath('op')
        op_el = op_els[0]
        op_type_el = op_el.getchildren()[0]
        if op_type_el.tag == 'Or':
            could_any = True
        elif op_type_el.tag == 'And':
            could_all = True
        if all([could_any, could_all]):
            break
    return could_any, could_all

@filt_block_help(xpath=IF_XPATH)
def any_all(block_dets, *, repeat=False, **_kwargs):
    """
    Look for cases where using built-in any or all functions makes sense.
    """
    if_els = block_dets.element.xpath(IF_XPATH)
    if not if_els:
        return None
    could_any_something = False
    could_all_something = False
    for if_el in if_els:
        could_any, could_all = could_any_or_all(if_el)
        if could_any:
            could_any_something = True
        if could_all:
            could_all_something = True
        if all([could_any_something, could_all_something]):  ## LOL - thought I might use 'all' given the context even though only two items
            break
    if not any([could_any_something, could_all_something]):
        return None

    if all([could_any_something, could_all_something]):
        title_content = "Consider using `any` and `all`"
    elif could_any_something:
        title_content = "Consider using `any`"
    elif could_all_something:
        title_content = "Consider using `all`"
    else:
        raise Exception("Unexpected situation with "
            f"could_any_something ({could_any_something}) "
            f"and could_all_something ({could_all_something})")
    title = layout(f"""\
    ### {title_content}
    """)
    if not repeat:
        summary = layout("""\

        Python has built-in `any` and `all` functions that make your code more
        readable when you're evaluating whether all or any of a group of items
        are True (or whether _not_ all or _not_ any are True). The argument has
        to be an iterable e.g. a list.
        """)
        demo = (
            layout("""\
            For example, instead of:
            """)
            +
            layout("""\
            if current or valid or safe or permitted:
                proceed()
            """, is_code=True)
            +
            layout("""\
            you could write the more semantic:
            """)
            +
            layout("""\
            if all([current, valid, safe, permitted]):
                proceed()
            """, is_code=True)
            +
            layout("""\
            or the equivalent, and, arguably, more readable:
            """)
            +
            layout("""\
            conditions = [current, valid, safe, permitted]
            if all(conditions):
                proceed()

            """, is_code=True)
            +
            layout("""\
            Or if you wanted the negation the syntax would be:
            """)
            +
            layout("""\
            if not all(conditions):
                exit()
            """, is_code=True)
            +
            layout("""\
            The `any` function works the same way
            """)
            +
            layout("""\
            flatmate_positives = [
                has_car, has_appliances, has_tv, great_cook, funny]
            if any(flatmate_positives):
                recruit_to_flat()

            """, is_code=True)
        )
        extra = (
            layout("""\

            It is easy to forget that an iterable has to be passed in as the
            argument rather than the individual items. So:
            """)
            +
            layout("""\
            if any(books, magazines, comics, games):  ## FAIL TypeError: any() takes exactly one argument (4 given)
                relax()

            if any([books, magazines, comics, games]):  ## SUCCESS
                relax()
            """, is_code=True)
        )
    else:
        summary = layout("""\

        Python has built-in `any` and `all` functions that can make your code
        more readable.
        """)
        demo = ''
        extra = ''

    message = {
        conf.BRIEF: title + summary,
        conf.MAIN: title + summary + demo,
        conf.EXTRA: extra,
    }
    return message
