from collections import defaultdict

from ..advisors import any_block_advisor, is_reserved_name
from .. import conf, utils
from ..utils import get_nice_str_list, int2nice, layout_comment as layout

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
