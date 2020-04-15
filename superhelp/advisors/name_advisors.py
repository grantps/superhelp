from ..advisors import any_block_advisor
from .. import conf, utils
from .shared import is_reserved_name
from ..utils import layout_comment

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
    return title

def _get_shamed_names_comment(shamed_names):
    multiple_shamed_names = len(shamed_names) > 1
    if multiple_shamed_names:
        shamed_names_listed = utils.get_nice_str_list(shamed_names, quoter='`')
        shamed_names_comment = f"{shamed_names_listed} are un-pythonic."
    else:
        shamed_names_comment = f"`{shamed_names[0]}` is un-pythonic."
    return shamed_names_comment

def get_relevant_assigned_names(block_dets):
    """
    Ignore named tuple names. Classes are already excluded because I haven't
    explicitly included them. They are stored differently e.g.
    <ClassDef ... name="ActuallyGoodName">
    """
    assigned_name_els = block_dets.element.xpath(
        'descendant-or-self::Assign/targets/Name')
    assigned_names = []
    for name_el in assigned_name_els:
        assign_el = name_el.xpath('ancestor::Assign')[0]
        func_name_els = assign_el.xpath('value/Call/func/Name')
        if func_name_els:
            func_names = [
                func_name_el.get('id') for func_name_el in func_name_els]
            if 'namedtuple' in func_names:
                continue  ## skip named tuples - they are allowed "un-Pythonic" names
        name = name_el.get('id')
        assigned_names.append(name)
    return assigned_names

def get_unpacked_names(block_dets):
    unpacked_name_els = block_dets.element.xpath(
        'descendant-or-self::Assign/targets/Tuple/elts/Name')
    unpacked_names = [unpacked_name_el.get('id')
        for unpacked_name_el in unpacked_name_els]
    return unpacked_names

@any_block_advisor(warning=True)
def name_style_check(block_dets):
    """
    Check names used for use of reserved words and camel case.
    """
    assigned_names = get_relevant_assigned_names(block_dets)
    unpacked_names = get_unpacked_names(block_dets)
    def_func_elements = block_dets.element.xpath(
        'descendant-or-self::FunctionDef')
    def_func_names = [name_el.get('name') for name_el in def_func_elements]
    names = assigned_names + unpacked_names + def_func_names
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
    title = _get_shamed_names_title(reserved_names, bad_names, dubious_names)
    brief_comment = layout_comment(f"""\
        #### {title}

        """)
    if reserved_names:
        reserved_names_listed = utils.get_nice_str_list(
            reserved_names, quoter='`')
        brief_comment += layout_comment(f"""\
            Reserved name(s): {reserved_names_listed}
            """)
    if bad_names:
        bad_names_listed = utils.get_nice_str_list(bad_names, quoter='`')
        brief_comment += layout_comment(f"""\
            Un-pythonic name(s): {bad_names_listed}
            """)
    if dubious_names:
        dubious_names_listed = utils.get_nice_str_list(
            dubious_names, quoter='`')
        brief_comment += layout_comment(f"""\
            Possibly un-pythonic name(s): {dubious_names_listed}
            """)
    brief_comment += layout_comment("""\

        Python variables should not named using reserved words e.g.
        `collections` or `sorted`.

        Generally speaking Python variables should be snake case - that is lower
        case, with multiple words joined by underscores e.g. `high_scores` (not
        `highScores` or `HighScores`)
        """)
    message = {
        conf.BRIEF: brief_comment,
        conf.MAIN: (
            brief_comment
            +
            layout_comment("""\
                In Python class names and named tuples are expected to be in
                Pascal Case (also known as upper camel case) rather than the
                usual snake case. E.g. `collections.ChainMap`

                Exceptions can also be made when a higher priority is
                consistency with other code e.g. a library the Python is ported
                from, or the non-Python code that Python is wrapping.
                """)
        ),
    }
    return message
