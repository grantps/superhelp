from superhelp.helpers import indiv_block_help
from superhelp import conf, name_utils
from superhelp.gen_utils import get_nice_str_list, layout_comment as layout
from superhelp.messages import MessageLevelStrs

def _get_sorting_or_reversing_comment(block_spec):
    """
    Get a comment on any sorting or reversing identified.

    :return: string describing type of reversing/sorting or None
    :rtype: str
    """
    element = block_spec.element
    comment = None
    func_attr_els = element.xpath('descendant-or-self::Call/func/Attribute')
    sort_els = [func_attr_el for func_attr_el in func_attr_els
        if func_attr_el.get('attr') == 'sort']
    func_name_els = element.xpath('descendant-or-self::Call/func/Name')
    sorted_els = [func_name_el for func_name_el in func_name_els
        if func_name_el.get('id') == 'sorted']
    reversed_els = [func_name_el for func_name_el in func_name_els
        if func_name_el.get('id') == 'reversed']
    if sort_els:
        comment = "has list sorting (`.sort()`)"
    if comment and (sorted_els or reversed_els):
        comment = ' and ' + comment
    if sorted_els and reversed_els:
        comment = "uses both the `sorted` and `reversed` functions"
    elif sorted_els:
        comment = "uses the `sorted` function"
    elif reversed_els:
        comment = "uses the `reversed` function"
    return comment

@indiv_block_help()
def sorting_reversing_overview(block_spec, *, repeat=False, **_kwargs) -> MessageLevelStrs | None:
    """
    Provide an overview of sorting and/or reversing. Advise on common
    confusions.
    """
    sorting_or_reversing_comment = _get_sorting_or_reversing_comment(block_spec)
    if not sorting_or_reversing_comment:
        return None

    title = layout("""\
    ### Sorting / reversing
    """)
    if not repeat:
        summary = layout(f"""\

        This block of code {sorting_or_reversing_comment}.

        Sorting and, to a lesser extent, reversing are very common needs in
        programming. Two key points:

        1) reversing is not the same as sorting with `reverse=True`

        2) the list sort method e.g. my_list.`sort()` returns `None`, not the
        sorted list
        """)
        details = (
            layout(f"""\

            Sorting and, to a lesser extent, reversing are very common needs in
            programming. Two key points:

            1) reversing is not the same as sorting with `reverse=True`

            To illustrate:
            """)
            +
            layout("""\
            word = 'cat'
            word_reversed = reversed(word)
            ## >>> word_reversed
            ## >>> 'tac'
            word_reverse_sorted = sorted(word, reverse=True)
            ## >>> word_reverse_sorted
            ## >>> 'tca'
            ## >>> word_reversed == word_reverse_sorted
            ## >>> False
            """, is_code=True)
            +
            layout("""\

            Using the reversed function does not apply any sorting to the
            sequence being reversed - it merely flips the (possibly) unordered
            sequence the other way.

            2) the list sort method e.g. `my_list.sort()` returns `None`, not
            the sorted list

            `sorted(my_list)` returns a sorted list but `my_list.sort()` is an
            in-place process. It mutates something rather than returning a
            separate thing.

            To illustrate:

            i) `sorted()` returning a result and leaving its input unchanged

            """)
            +
            layout("""\
            fruit = ['banana', 'apple', 'cranberry']
            fruit_sorted = sorted(fruit)
            ## >>> fruit_sorted
            ## >>> ['apple', 'banana', 'cranberry']
            ## fruit itself has not been changed
            ## >>> fruit
            ## >>> ['banana', 'apple', 'cranberry']
            """, is_code=True)
            +
            layout("""\
            ii) `.sort()` returning `None` and changing its input in-place
            """)
            +
            layout("""\
            result_of_fruit_sort = fruit.sort()
            ## >>> result_of_fruit_sort
            ## >>> None
            ## fruit has been changed by the in-place sort method
            ## >>> fruit
            ## >>> ['apple', 'banana', 'cranberry']
            """, is_code=True)
            )
    else:
        summary = layout(f"""\
        This block of code {sorting_or_reversing_comment}.
        """)
        details = summary
    brief = title + summary
    main = title + details
    message_level_strs = MessageLevelStrs(brief, main)
    return message_level_strs

ASSIGN_FUNC_ATTRIBUTE_XPATH = 'descendant-or-self::Assign/value/Call/func/Attribute'

@indiv_block_help(xpath=ASSIGN_FUNC_ATTRIBUTE_XPATH, warning=True)
def list_sort_as_value(block_spec, *, repeat=False, **_kwargs) -> MessageLevelStrs | None:
    """
    Warn about assigning a name to the result using .sort() on a list.
    """
    func_attr_els = block_spec.element.xpath(ASSIGN_FUNC_ATTRIBUTE_XPATH)
    names_assigned_to_sort = []
    for func_attr_el in func_attr_els:
        is_sort = (func_attr_el.get('attr') == 'sort')
        if is_sort:
            try:
                name_dets = name_utils.get_assigned_name(func_attr_el)
            except Exception:
                continue
            names_assigned_to_sort.append(name_dets.name_str)
    if not names_assigned_to_sort:
        return None

    title = layout("""\
    ### Assignment of `None` result from in-place `.sort()` on list
    """)
    if not repeat:
        multiple = len(names_assigned_to_sort) > 1
        if multiple:
            nice_str_list = get_nice_str_list(
                names_assigned_to_sort, quoter='`')
            details = layout(f"""\

            {nice_str_list} are assigned to the results of in-place sort
            operations. This is almost certainly a mistake as the intention is
            probably not to set them each to `None` (the return value of the
            `.sort()` method).
            """)
        else:
            name = names_assigned_to_sort[0]
            details = layout(f"""\

            `{name}` is assigned to the result of an in-place sort operation.
            This is almost certainly a mistake as the intention is probably not
            to set `{name}` to `None` (the return value of the `.sort()`
            method).
            """)
    else:
        details = ''
    brief = title + details
    main = title + details
    message_level_strs = MessageLevelStrs(brief, main)
    return message_level_strs
