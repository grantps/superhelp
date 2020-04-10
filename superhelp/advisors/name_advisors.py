from textwrap import dedent

from advisors import any_block_advisor
import conf, utils

def _get_shamed_names_comment(shamed_names):
    multiple_shamed_names = len(shamed_names) > 1
    if multiple_shamed_names:
        names_listed = utils.get_nice_str_list(shamed_names, quoter='`')
        names_listed += f" and `{shamed_names[-1]}`"
        shamed_names_comment = f"{names_listed} are un-pythonic."
    else:
        shamed_names_comment = f"`{shamed_names[0]}` is un-pythonic."
    return shamed_names_comment

def _get_shamed_names_title(bad_names, dubious_names):
    if not (bad_names or dubious_names):
        raise Exception(f"No shamed names supplied to {__name__}")
    n_bad_names = len(bad_names)
    n_dubious_names = len(dubious_names)
    if bad_names:
        if n_bad_names == 1:
            if n_dubious_names < 1:
                title = 'Un-pythonic name'
            else:
                title = 'Un-pythonic name(s)'
        else:
            title = 'Un-pythonic names'
    else:
        if n_dubious_names == 1:
            title = 'Possibly un-pythonic name'
        else:
            title = 'Possibly un-pythonic names'
    return title

@any_block_advisor(warning=True)
def name_style_check(block_dets):
    assigned_name_elements = block_dets.element.xpath(
        'descendant-or-self::Assign/targets/Name')
    assigned_names = [name_el.get('id') for name_el in assigned_name_elements]
    def_func_elements = block_dets.element.xpath(
        'descendant-or-self::FunctionDef')
    def_func_names = [name_el.get('name') for name_el in def_func_elements]
    names = assigned_names + def_func_names
    bad_names = []
    dubious_names = []
    for name in names:
        all_lower_case = (name.lower() == name)
        all_upper_case = (name.upper() == name)
        bad_name = not (all_lower_case or all_upper_case)
        if bad_name:
            bad_names.append(name)
        elif all_upper_case:
            dubious_names.append(name)
    if not bad_names or dubious_names:
        return None
    title = _get_shamed_names_title(bad_names, dubious_names)
    comment = dedent(f"""\
        #### {title}
        """)
    if bad_names:
        bad_names_comment = _get_shamed_names_comment(bad_names)
        comment += dedent(f"""\

        {bad_names_comment}

        Generally speaking Python variables should be snake case -
        that is lower case, with multiple words joined by underscores
        e.g. `high_scores` (not `highScores` or `HighScores`)
        """)
    if dubious_names:
        dubious_names_comment = _get_shamed_names_comment(dubious_names)
        comment += dedent(f"""\

        {dubious_names_comment}

        Generally speaking Python variables should be snake case -
        that is lower case, with multiple words joined by underscores
        e.g. `high_scores` (not `highScores` or `HighScores`)
        """)
    message = {
        conf.BRIEF: comment,
        conf.MAIN: (
            comment
            + '\n\n'
            + dedent("""\
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
