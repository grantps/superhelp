from collections import defaultdict, namedtuple

from ..advisors import all_blocks_advisor, any_block_advisor, is_reserved_name
from .. import ast_funcs, conf, utils
from ..utils import (get_nice_str_list, int2first_etc, int2nice,
    layout_comment as layout)

PairDets = namedtuple('PairDets', 'name, name_value, unpacking_idx')
PairDets.name.__doc__ = (
    "Name assigned to the other name e.g. pet when pet = cat")
PairDets.name_value.__doc__ = ("Name acting as the value having the other name "
    "assigned to it e.g. cat when pet = cat")
PairDets.unpacking_idx.__doc__ = ("The unpacking index if applicable "
    "e.g if a, b = c and name is a then unpacking_idx is 0; for b it is 1")

ASSIGN_SUBSCRIPT_XPATH = 'descendant-or-self::Assign/value/Subscript'
ASSIGN_NAME_XPATH = 'descendant-or-self::Assign/value/Name'

def get_subscript_name_value(assign_subscript_el):
    """
    Looking for:
    people[0] (list)
    capitals['NZ'] (dict)
    """
    name_value_el = assign_subscript_el.xpath('value/Name')[0]
    name_value_name = name_value_el.get('id')
    slice_dets = ast_funcs.get_slice_dets(assign_subscript_el)
    name_value = f"{name_value_name}{slice_dets}"
    return name_value

def pairs_dets_from_el(name2name_el):
    """
    Get details of a name to name assignment. Note - might be multiple names
    assigned to the name_value e.g. a, b = var

    :return: list of tuples of name, name_value. name_value might be a standard
     Python name e.g. person, or a subscript of some sort e.g. people[0] or
     capitals['NZ']
    """
    ancestor_assign_els = name2name_el.xpath('ancestor::Assign')
    try:
        ancestor_assign_el = ancestor_assign_els[-1]
    except IndexError:
        raise IndexError(  ## in theory, guaranteed to be one given how we got the name2name_els
            "Unable to identify ancestor Assign for name-to-name assignment")
    try:
        names_dets = ast_funcs.get_assigned_names(name2name_el)
    except Exception as e:
        raise Exception("Unable to identify name for name-value assignment. "
            f"Orig error: {e}")

    assign_subscript_els = ancestor_assign_el.xpath(ASSIGN_SUBSCRIPT_XPATH)
    if assign_subscript_els:
        assign_subscript_el = assign_subscript_els[0]
        name_value = get_subscript_name_value(assign_subscript_el)
    else:
        assign_name_els = ancestor_assign_el.xpath(ASSIGN_NAME_XPATH)
        direct_assign_el = assign_name_els[0]
        name_value = direct_assign_el.get('id')
    if not name_value:
        raise Exception(
            "Unable to identify name_value even though there should be one")
    pairs_dets = [
        PairDets(name_dets.name_str, name_value, name_dets.unpacking_idx)
            for name_dets in names_dets]
    return pairs_dets

def pairs_dets_from_block(block_el):
    """
    Get details of name-to-name assignments.

    Examples of name to name assignment:

    animal = pet
    first_person = people[0]
    capital_nz = capitals['NZ']

    Obviously, being Python, the assignment is to the value under the name but
    it is a name nonetheless.
    """
    name2name_els = block_el.xpath(
        f"{ASSIGN_SUBSCRIPT_XPATH}|{ASSIGN_NAME_XPATH}")
    if not name2name_els:
        return None
    pairs_dets = []
    for el in name2name_els:
        el_pairs_dets = pairs_dets_from_el(el)
        pairs_dets.extend(el_pairs_dets)
    return pairs_dets

@all_blocks_advisor()
def names_and_values(blocks_dets):
    """
    Look for names assigned to other names and explain names and values in
    Python.
    """
    name2name_pairs_dets = []
    for block_dets in blocks_dets:
        block_el = block_dets.element
        block_name2name_pairs_dets = pairs_dets_from_block(block_el)
        if block_name2name_pairs_dets:
            name2name_pairs_dets.extend(block_name2name_pairs_dets)
    if not name2name_pairs_dets:
        return None

    name2name_pair_strs = []
    for pair_dets in name2name_pairs_dets:
        if pair_dets.unpacking_idx is not None:
            first_etc_str = int2first_etc(pair_dets.unpacking_idx + 1)
            name2name_pair_str = (
                f"`{pair_dets.name}` is assigned to the {first_etc_str} item of"
                f" `{pair_dets.name_value}` through value unpacking")
        else:
            name2name_pair_str = (
                f"`{pair_dets.name}` is assigned to `{pair_dets.name_value}`")
        name2name_pair_strs.append(name2name_pair_str)
    first_pair_dets = name2name_pairs_dets[0]
    if first_pair_dets.unpacking_idx is None:
        example = layout(f"""\

        So when your code assigned name `{first_pair_dets.name}` to another name
        `{first_pair_dets.name_value}`, for example, it was actually linking
        `{first_pair_dets.name}` to the **value** `{first_pair_dets.name_value}`
        was linked to. If you reassigned `{first_pair_dets.name_value}` to
        something else it would not affect `{first_pair_dets.name}`.
        """)
    else:
        first_etc_str = int2first_etc(first_pair_dets.unpacking_idx + 1)
        example = layout(f"""\

        So when your code assigned name `{first_pair_dets.name}` to the
        {first_etc_str} item in another name `{first_pair_dets.name_value}`, for
        example, it was actually linking `{first_pair_dets.name}` to the
        **value** of that item. If you replaced that item with something else it
        would not affect `{first_pair_dets.name}`.
        """)
    nice_name2name_pairs = get_nice_str_list(
        name2name_pair_strs, item_glue='; ', quoter='')

    title = layout("""
    ### Names assigned to names
    """)
    assignments = layout(f"""\

    Your code assigned names to other names as values: {nice_name2name_pairs}.
    """)
    brief_summary = layout("""\

    To get a better understanding of what that means in Python see / read
    <https://nedbatchelder.com/text/names1.html>. Or look at this advice at a
    higher level of detail e.g. 'Main'.
    """)
    main_summary = (
        layout(f"""\

        So what does that mean in Python? Having a firm grasp of how names and
        values work in Python means you can confidently reason about your code
        and pre-emptively avoid numerous bugs.

        #### How variables work in Python - names and values

        Assignment is linking names and values e.g. `fname = "Maggie"`

        Another way of expressing the same idea:

        > "Assignment: make this name refer to that value" Ned Batchelder

        Names are something you can assign to a value.

        Multiple names can refer to the same value. No name is the "real" name
        in Python - they are all just labels to a value.

        Names can take a variety of forms. For example:
        """)
        +
        layout("""\
        fname = value
        mydict['fruit'] = value
        family.pet = value
        """, is_code=True)
        +
        layout("""
        are all names.

        A wide variety of data structures can be values to which names are
        assigned. For example:
        """)
        +
        layout("""\
        name = 1066
        name = 'cheerful'
        name = [1, 2, 3, 4]
        name = {'width': 12.5, 'height': 23.75}

        etc
        """, is_code=True)
        +
        layout(f"""

        The key idea is that we are always linking names to values - NEVER names
        to other names. Python has references (names pointing to objects) but
        not pointers (names pointing to other names). When we assign one name to
        another we are actually linking to the underlying value of the second
        name.

        And be very clear - assignment never **copies** data. It just links
        names to values. There are no exceptions to this rule.

        So if `a = 'cat'` and `b = a` then both `a` and `b` are labels assigned
        to the string 'cat'. If we change what label `a` is attached to we don't
        affect `b`. It remains linked to 'cat'.

        {example}

        The names aren't necessarily independent though. If a mutable object
        like a list has multiple labels then any changes to the value, i.e. the
        list, are shared by all labels because they are all linked to the same
        value.

        For example:
        """)
        +
        layout("""\
        fruit = ['apple', 'banana']
        ingredients = fruit
        fruit.append('cherry')
        ## What is ingredients now? Try this code and find out. If you
        ## understand the ideas above you should be able to reason it out with
        ## confidence.
        """, is_code=True)
    )
    ned_talk = layout("""\
    The talk to watch / read on the topic is:
    <https://nedbatchelder.com/text/names1.html>

    <https://lerner.co.il/2019/06/18/understanding-python-assignment/> is also
    helpful.

    A note about using the verb 'assign'? I recommend saying that we assign
    names to values rather than the other way around because it better fits how
    Python actually works. The central reality in Python is the value not the
    name. The name is nothing substantial - it's not a container for a value
    or anything like that - it is merely a label.
    """)

    message = {
        conf.BRIEF: title + assignments + brief_summary,
        conf.MAIN: title + assignments + main_summary,
        conf.EXTRA: ned_talk,
    }
    return message

def _get_shamed_names_title(reserved_names, bad_names, dubious_names):
    if not (reserved_names or bad_names or dubious_names):
        raise Exception(f"No shamed names supplied to {__name__}")
    n_reserved_names = len(reserved_names)
    n_bad_names = len(bad_names)
    n_dubious_names = len(dubious_names)
    if reserved_names:
        if n_reserved_names == 1:
            title = "Bad naming - use of reserved name."
        else:
            title = "Bad naming - use of reserved names."
    else:
        title = ''
    if title:
        if bad_names:
            if n_bad_names == 1:
                if n_dubious_names < 1:
                    title += ' Also un-pythonic name'
                else:
                    title += ' Also un-pythonic name(s)'
            else:
                title += ' Also un-pythonic names'
        elif dubious_names:
            if n_dubious_names == 1:
                title += ' Also a possibly un-pythonic name'
            else:
                title += ' Also other possibly un-pythonic names'
    else:
        if bad_names:
            if n_bad_names == 1:
                if n_dubious_names < 1:
                    title = 'Un-pythonic name'
                else:
                    title = 'Un-pythonic name(s)'
            else:
                title = 'Un-pythonic names'
        elif dubious_names:
            if n_dubious_names == 1:
                title = 'Possibly an un-pythonic name'
            else:
                title = 'Possibly some un-pythonic names'
    return title

def get_standard_assigned_names(block_dets):
    """
    Only get names where we expect standard pythonic naming. So not named tuple
    or class names, for example. We have to explicitly ignore named tuple names.
    Classes are automatically excluded because I haven't explicitly included
    them. They are stored differently e.g. <ClassDef ...name="ActuallyGoodName">
    """
    assigned_name_els = block_dets.element.xpath(
        'descendant-or-self::targets/Name | descendant-or-self::target/Name')
    assigned_names = []
    for name_el in assigned_name_els:
        ## exclude if named tuple - they are allowed "un-Pythonic" names
        try:
            assign_el = name_el.xpath('ancestor::Assign')[0]
        except IndexError:
            ## cannot be a named tuple
            pass
        else:
            func_name_els = assign_el.xpath('value/Call/func/Name')
            if func_name_els:
                func_names = [
                    func_name_el.get('id') for func_name_el in func_name_els]
                if 'namedtuple' in func_names:
                    continue
        ## not a named tuple 
        name = name_el.get('id')
        assigned_names.append(name)
    return assigned_names

def get_class_names(block_dets):
    class_els = block_dets.element.xpath('ClassDef')
    class_names = [class_el.get('name') for class_el in class_els]
    return class_names

def get_named_tuple_names(block_dets):
    assigned_name_els = block_dets.element.xpath(
        'descendant-or-self::Assign/targets/Name')
    named_tuple_names = []
    for name_el in assigned_name_els:
        assign_el = name_el.xpath('ancestor::Assign')[0]
        func_name_els = assign_el.xpath('value/Call/func/Name')
        if func_name_els:
            func_names = [
                func_name_el.get('id') for func_name_el in func_name_els]
            if 'namedtuple' not in func_names:
                continue
        name = name_el.get('id')
        named_tuple_names.append(name)
    return named_tuple_names

def get_unpacked_names(block_dets):
    unpacked_name_els = block_dets.element.xpath(
        'descendant-or-self::targets/Tuple/elts/Name'
        ' | '
        'descendant-or-self::target/Tuple/elts/Name')
    unpacked_names = [unpacked_name_el.get('id')
        for unpacked_name_el in unpacked_name_els]
    return unpacked_names

def get_def_func_names(block_dets):
    def_func_elements = block_dets.element.xpath(
        'descendant-or-self::FunctionDef')
    def_func_names = [name_el.get('name') for name_el in def_func_elements]
    return def_func_names

def get_all_names(block_dets, *, include_non_standard=False):
    """
    :param bool include_non_standard: if True include variables that aren't
     expected to follow standard Python naming conventions e.g. class or named
     tuple names.
    """
    assigned_names = get_standard_assigned_names(block_dets)
    unpacked_names = get_unpacked_names(block_dets)
    def_func_names = get_def_func_names(block_dets)
    all_names = assigned_names + unpacked_names + def_func_names
    if include_non_standard:
        class_names = get_class_names(block_dets)
        named_tuple_names = get_named_tuple_names(block_dets)
        all_names = all_names + class_names + named_tuple_names
    return all_names

@any_block_advisor(warning=True)
def unpythonic_name_check(block_dets, *, repeat=False):
    """
    Check names used for use of reserved words and camel case.
    """
    names = get_all_names(block_dets, include_non_standard=False)
    reserved_names = []
    bad_names = []
    dubious_names = []
    for name in names:
        if is_reserved_name(name):
            reserved_names.append(name)
        all_lower_case = (name.lower() == name)
        all_upper_case = (name.upper() == name)
        bad_name = not (all_lower_case or all_upper_case)
        if bad_name:
            bad_names.append(name)
        elif all_upper_case:
            dubious_names.append(name)
    if not (reserved_names or bad_names or dubious_names):
        return None

    shamed_names_title = _get_shamed_names_title(
        reserved_names, bad_names, dubious_names)
    title = layout(f"""\
    ### {shamed_names_title}
    """)
    if reserved_names:
        reserved_names_listed = utils.get_nice_str_list(
            reserved_names, quoter='`')
        reserved_comment = layout(f"""\
        Reserved name(s): {reserved_names_listed}
        """)
    else:
        reserved_comment = ''
    if bad_names:
        bad_names_listed = utils.get_nice_str_list(bad_names, quoter='`')
        bad_comment = layout(f"""\
        Un-pythonic name(s): {bad_names_listed}
        """)
    else:
        bad_comment = ''
    if dubious_names:
        dubious_names_listed = utils.get_nice_str_list(
            dubious_names, quoter='`')
        dubious_comment = layout(f"""\
        Possibly un-pythonic name(s): {dubious_names_listed}
        """)
    else:
        dubious_comment = ''
    if not repeat:
        snake_case = layout("""\

        Python variables should not named using reserved words e.g.
        `collections` or `sorted`.

        Generally speaking Python variables should be snake case - that is lower
        case, with multiple words joined by underscores e.g. `high_scores` (not
        `highScores` or `HighScores`)
        """)
        pascal = layout("""\
        In Python class names and named tuples are expected to be in Pascal Case
        (also known as upper camel case) rather than the usual snake case. E.g.
        `collections.ChainMap`

        Exceptions can also be made when a higher priority is consistency with
        other code e.g. a library the Python is ported from, or the non-Python
        code that Python is wrapping.
        """)
    else:
        snake_case = ''
        pascal = ''

    message = {
        conf.BRIEF: (title + reserved_comment + bad_comment
            + dubious_comment + snake_case + pascal),
        conf.MAIN: (title + reserved_comment + bad_comment
            + dubious_comment + snake_case + pascal),
    }
    return message

@any_block_advisor(warning=True)
def short_name_check(block_dets, *, repeat=False):
    """
    Check for short variable names.
    """
    names = get_all_names(block_dets, include_non_standard=True)
    short_names = defaultdict(set)
    for name in names:
        if len(name) < conf.MIN_BRIEF_NAME:
            short_names[len(name)].add(name)
    if not short_names:
        return None

    title = layout("""
    ### Short variable name
    """)
    short_comment_bits = []
    for length, names in sorted(short_names.items()):
        freq = len(names)
        multiple = (freq > 1)
        plural = 's' if length > 1 else ''
        if multiple:
            nice_list = get_nice_str_list(list(names), quoter='`')
            short_comment_bits.append((
                f"{int2nice(freq)} variables have names "
                f"{int2nice(length)} character{plural} long: {nice_list}."))
        else:
            name = names.pop()
            short_comment_bits.append(f"`{name}` is short (only "
                f"{int2nice(length)} character{plural} long).")
    short_comment = '; '.join(short_comment_bits)
    sometimes_ok = layout(f"""\

    Sometimes, short variable names are appropriate - even conventional - but
    they should be avoided outside of a few special cases. In your code:

    {short_comment}
    """)
    if not repeat:
        idiomatic = (
            layout("""\

            In many programming languages it is idiomatic to use `i`, `j`, and
            even `k` as increment counters. It is best to reserve `i` for
            incrementing starting at 0 and prefer `n` when starting at 1. But
            longer names should be used when they aid readability (i.e. usually
            ;-)).

            `k` and `v` are idiomatic in Python when iterating through
            dictionary items e.g.
            """)
            +
            layout("""\
                for k, v in my_dict.items():
                    ...
            """, is_code=True)
            +
            layout("""\

            But even they should probably be replaced with something more
            descriptive.

            And there are other cases specific to certain contexts e.g. using r
            for the result of a request e.g.
            """)
            +
            layout("""\
            r = requests.get('https://pypi.org/project/superhelp/')
            """, is_code=True)
            +
            layout("""\

            The main goal is readability, readability, readability. That is what
            should drive variable naming above all else. Only a modest weight
            should be given to speed of typing in any code that is going to be
            used or worked on in the future as opposed to quick exploratory code
            in a terminal / notebook etc.

            In the words of the legendary Donald Knuth:

            > "Programs are meant to be read by humans and only incidentally for
            computers to execute."

            Note - excessively long variable names can be unreadable as well.
            They may also indicate the code needs to be reworked.
            """)
        )
    else:
        idiomatic = ''

    message = {
        conf.BRIEF: title + sometimes_ok,
        conf.MAIN: title + sometimes_ok + idiomatic,
    }
    return message
