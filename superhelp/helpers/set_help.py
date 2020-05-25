from ..helpers import filt_block_help
from .. import ast_funcs, conf
from ..gen_utils import layout_comment as layout
from .. import gen_utils

def truncate_set(items):
    return set(list(items)[: conf.MAX_ITEMS_EVALUATED])

ASSIGN_SET_XPATH = (
    'descendant-or-self::Assign/value/Call/func/Name '
    '| descendant-or-self::Assign/value/Set')

def get_set_els(block_el):
    set_els = [el for el in block_el.xpath(ASSIGN_SET_XPATH)
        if el.tag == 'Set' or el.get('id') == 'set']
    return set_els

@filt_block_help(xpath=ASSIGN_SET_XPATH)
def set_overview(block_dets, *, repeat=False, execute_code=True, **_kwargs):
    """
    Look for sets and provide general advice on using them and finding out more.

    Need to handle both:
    a = set([1, 2, 3])
    a = {1, 2, 3}

    If any items are conf.UNKNOWN_ITEM we cannot comment on true length of set
    so have to say its contents couldn't be evaluated.

    E.g. {dt, dt, dt, 4} -> {conf.UNKNOWN_ITEM, 4} i.e. 2 items when it should
    be 4.
    """
    set_els = [el for el in block_dets.element.xpath(ASSIGN_SET_XPATH)
        if el.tag == 'Set' or el.get('id') == 'set']
    if not set_els:
        return None
    names_items, oversized_msg = gen_utils.get_collections_dets(
        set_els, block_dets,
        collection_plural='sets', truncated_items_func=truncate_set,
        execute_code=execute_code)
    if not names_items:
        return None

    title = layout("""\
    ### Set details
    """)
    summary_bits = []
    for name, items in names_items:
        unknowns = (items == conf.UNKNOWN_ITEMS or conf.UNKNOWN_ITEM in items)
        if unknowns:
            if not repeat:
                summary_bits.append(layout(f"""\
                Unable to evaluate all contents of set `{name}` but still able
                to make some general comments.
                """))
            else:
                summary_bits.append(layout(f"""\
                `{name}` is a set but unable to evaluate contents.
                """))
        elif len(items) == 0:  ## no unknowns, just empty
            summary_bits.append(layout(f"""\
            `{name}` is an empty set.
            """))
        else:
            members = str(sorted(items)).strip('[').strip(']')
            plural = 's' if len(members) > 1 else ''
            summary_bits.append(layout(f"""\

            `{name}` is a set with {gen_utils.int2nice(len(items))}
            member{plural}: {members}
            """))
    summary = ''.join(summary_bits)
    if not repeat:
        sets_rock = (
            layout("""\

            Python sets are brilliant. There are often cases in programming
            where you need some sort of set operation e.g. you need everything
            in one set that is not in another. In Python you can express that
            idea directly and semantically with set concepts instead of having
            to build the operations yourself in code which needs explaining and
            testing.

            For example:
            """)
            +
            layout("""\
            people = set(['Sam', 'Avi', 'Terri', 'Noor', 'Hyeji'])
            no_email = set(['Sam', 'Terri'])
            people2email = people - no_email
            ## >>> {'Noor', 'Hyeji', 'Avi'}
            """, is_code=True)
        )
        no_duplicates_demo = ''
        for name, items in names_items:
            unknown_set = conf.UNKNOWN_ITEM in items
            empty_set = len(items) == 0
            if not (empty_set or unknown_set):
                members = str(sorted(items)).strip('[').strip(']')
                existing_set_item = list(items)[0]
                no_duplicates_demo = (
                    layout("""\
                    For example:
                    """)
                    +
                    layout(f"""\
                    {name}.add({existing_set_item})
                    ## >>> {items}
                    """, is_code=True)
                )
                break
        set_dets = (
            layout(f"""\

            Being a set, all members are unique by definition so if you add
            something to a set that is already a member the set doesn't change.
            """)
            +
            no_duplicates_demo
            +
            layout("""\

            This is unlike a list which grows each time you append an item - the
            list simply repeats the item. For example:
            """)
            +
            layout("""\
            my_list = [1, 2, 3]
            my_list.append(4)
            my_list.append(4)
            my_list.append(4)
            ## >>> [1, 2, 3, 4, 4, 4]
            my_set = {1, 2, 3}
            my_set.add(4)
            my_set.add(4)
            my_set.add(4)
            ## >>> {1, 2, 3, 4}
            """, is_code=True)
        )
        set_extras = (
            layout("""\

            Set operations can be expressed with operators such as `-` (minus)
            or with methods such as .difference().

            Sets are well explained in the official documentation so it will
            suffice to show a simple example.

            Note - the operator corresponding to the `.union()` method is the
            pipe `|` not `+`.
            """)
            +
            layout("""\
            badminton_players = set(['Grant', 'Charlotte', 'Aravind'])
            tennis_players = set(['Giles', 'Grant'])
            squash_players = set(['Grzegorz'])
            racquet_players = badminton_players | tennis_players | squash_players
            ## >>> {'Grzegorz', 'Giles', 'Grant', 'Aravind', 'Charlotte'}
            """, is_code=True)
        )
    else:
        sets_rock = ''
        set_dets = ''
        set_extras = ''

    message = {
        conf.BRIEF: title + oversized_msg + summary + sets_rock,
        conf.MAIN: title + oversized_msg + summary + sets_rock + set_dets,
        conf.EXTRA: set_extras,
    }
    return message

## Raise exceptions when something happens that apparently shouldn't

def _checking_non_membership(compare_el):
    """
    See if checking membership status (specifically non-membership status).
    """
    ops_els = compare_el.xpath('ops')
    if len(ops_els) != 1:
        raise Exception("Should only be one ops item in a Compare")
    ops_el = ops_els[0]
    ops_type_els = ops_el.getchildren()
    if len(ops_type_els) != 1:
        raise Exception("Should only be one ops child")
    ops_type = ops_type_els[0].tag
    checking_non_membership = (ops_type == 'NotIn')
    return checking_non_membership

def _append_after_check(call_el):
    func_attribute_els = call_el.xpath('func/Attribute')
    if len(func_attribute_els) != 1:
        return False
    func_attribute_el = func_attribute_els[0]
    if func_attribute_el.get('attr') != 'append':
        return False
    return True

def _get_test_item_dict(compare_el):
    left_els = compare_el.xpath('left')
    if len(left_els) != 1:
        raise Exception("Should only be one left item in a Compare")
    left_el = left_els[0]
    left_val_els = left_el.getchildren()
    if len(left_val_els) != 1:
        raise Exception("Should only be one value item in a Compare/left")
    left_val_el = left_val_els[0]
    test_item_dict = ast_funcs.get_standardised_el_dict(left_val_el)
    return test_item_dict

def _get_append_item_dict(call_el):
    args_els = call_el.xpath('args')
    if len(args_els) != 1:
        return None
    args_el = args_els[0]
    args_children_els = args_el.getchildren()
    if len(args_children_els) != 1:
        return None
    args_child_el = args_children_els[0]
    append_item_dict = ast_funcs.get_standardised_el_dict(args_child_el)
    return append_item_dict

def _get_test_collection_dict(compare_el):
    comparator_name_els = compare_el.xpath('comparators/Name')
    if len(comparator_name_els) != 1:
        return None
    comparator_name_el = comparator_name_els[0]
    test_collection_dict = ast_funcs.get_standardised_el_dict(
        comparator_name_el)
    return test_collection_dict

def _get_append_collection_dict(call_el):
    appended_name_els = call_el.xpath('func/Attribute/value/Name')
    if len(appended_name_els) != 1:
        return None
    appended_name_el = appended_name_els[0]
    append_collection_dict = ast_funcs.get_standardised_el_dict(
        appended_name_el)
    return append_collection_dict

def _get_inappropriate_list(if_el):
    """
    Look for a test item being identified as not being in a collection and then
    being appended to that collection.
    """
    test_el = if_el.xpath('test')[0]

    compare_els = test_el.xpath('Compare')
    if len(compare_els) != 1:
        return None
    compare_el = compare_els[0]

    checking_non_membership = _checking_non_membership(compare_el)
    if not checking_non_membership:
        return None

    body_el = if_el.xpath('body')[0]
    call_els = body_el.xpath('Expr/value/Call')
    if len(call_els) != 1:
        return None
    call_el = call_els[0]

    if not _append_after_check(call_el):
        return None

    test_item_dict = _get_test_item_dict(compare_el)
    append_item_dict = _get_append_item_dict(call_el)
    if append_item_dict is None:
        return None
    same_item_checked_and_appended = (test_item_dict == append_item_dict)
    if not same_item_checked_and_appended:
        return None

    test_collection_dict = _get_test_collection_dict(compare_el)
    if test_collection_dict is None:
        return None
    append_collection_dict = _get_append_collection_dict(call_el)
    if append_collection_dict is None:
        return None
    same_collection_in_membership_test_and_append = (
        test_collection_dict == append_collection_dict)
    if not same_collection_in_membership_test_and_append:
        return None

    inappropriate_list = test_collection_dict.get('id')
    return inappropriate_list

XPATH_COMPARE = 'descendant-or-self::If/test/Compare'

@filt_block_help(xpath=XPATH_COMPARE, warning=True)
def set_better_than_list(block_dets, *, repeat=False, **_kwargs):
    """
    Look for cases where the code checks list membership before adding.
    Candidate for a set?
    """
    if_els = block_dets.element.xpath('descendant-or-self::If')
    if not if_els:
        return None
    inappropriate_lists = []
    for if_el in if_els:
        inappropriate_list = _get_inappropriate_list(if_el)
        if inappropriate_list is not None:
            inappropriate_lists.append(inappropriate_list)
    if not inappropriate_lists:
        return None

    title = layout("""\
    ### Using a `set` with the `add` method probably a better option
    """)
    first_list = inappropriate_lists[0]
    multiple = len(inappropriate_lists) > 1
    if multiple:
        dubious_lists_msg = gen_utils.get_nice_str_list(
            inappropriate_lists, quoter='`')
        summary = layout(f"""\

        It looks like the following collections are built by checking potential
        new values for non-membership and appending to them if not already
        present: {dubious_lists_msg}. Using a `set` could result in a more
        semantic option.
        """)
    else:
        summary = layout(f"""\

        It looks like `{first_list}` is built by checking potential new values
        for non-membership and appending if not already present. Using a `set`
        could result in a more semantic option.
        """)
    if not repeat:
        alternative = (layout("""\
            For example, the following:
            """)
            +
            layout(f"""\
            {first_list} = [value, ...]
            if value not in {first_list}:
                {first_list}.append(value)
            """, is_code=True)
            +
            layout("""\
            could be replaced with the simpler and more semantic:
            """)
            +
            layout(f"""\
            {first_list} = {{value, ...}}
            {first_list}.add(value)
            """, is_code=True)
            + layout("""\

            Adding is a no-op if a value is already a member of a `set`.

            The curly braces indicate a `set` if it contains individual items
            and a `dict` if it contains key: value pairs.
            """)
        )
    else:
        alternative = ''

    message = {
        conf.BRIEF: title + summary,
        conf.MAIN: title + summary + alternative,
    }
    return message
