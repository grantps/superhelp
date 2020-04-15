from ..advisors import any_block_advisor, filt_block_advisor

from ..ast_funcs import get_assigned_name
from .. import conf
from ..utils import layout_comment

def _get_sorting_or_reversing_comment(block_dets):
    """
    Get a comment on any sorting or reversing identified.

    :return: string describing type of reversing/sorting or None
    :rtype: str
    """
    element = block_dets.element
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

@any_block_advisor()
def sorting_reversing_overview(block_dets):
    """
    Provide an overview of sorting and/or reversing. Advise on common
    confusions.
    """
    sorting_or_reversing_comment = _get_sorting_or_reversing_comment(block_dets)
    if not sorting_or_reversing_comment:
        return None
    message = {
        conf.BRIEF: layout_comment(f"""\
            #### Sorting / reversing

            This block of code {sorting_or_reversing_comment}. Sorting and, to a
            lesser extent, reversing are very common needs in programming. Two
            key points:

            1) reversing is not the same as sorting with `reverse=True`

            2) the list sort method e.g. my_list.`sort()` returns `None`, not the sorted list
            """),
        conf.MAIN: (
            layout_comment(f"""\
                #### Sorting / reversing

                This block of code {sorting_or_reversing_comment}. Sorting and,
                to a lesser extent, reversing are very common needs in
                programming. Two key points:
    
                1) reversing is not the same as sorting with `reverse=True`

                To illustrate:

                """)
            +
            layout_comment("""\
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
            layout_comment("""\
                Using the reversed function does not apply any sorting to the
                sequence being reversed - it merely flips the (possibly)
                unordered sequence the other way.

                2) the list sort method e.g. `my_list.sort()` returns `None`, not the sorted list

                `sorted(my_list)` returns a sorted list but `my_list.sort()` is
                an in-place process. It mutates something rather than returning
                a separate thing.

                To illustrate:

                i) `sorted()` returning a result and leaving its input unchanged

                """)
            +
            layout_comment("""\
                fruit = ['banana', 'apple', 'cranberry']
                fruit_sorted = sorted(fruit)
                ## >>> fruit_sorted
                ## >>> ['apple', 'banana', 'cranberry']
                ## fruit itself has not been changed
                ## >>> fruit
                ## >>> ['banana', 'apple', 'cranberry']
                """, is_code=True)
            +
            layout_comment("""\

                ii) `.sort()` returning `None` and changing its input in-place

                """)
            +
            layout_comment("""\

                result_of_fruit_sort = fruit.sort()
                ## >>> result_of_fruit_sort
                ## >>> None
                ## fruit has been changed by the in-place sort method
                ## >>> fruit
                ## >>> ['apple', 'banana', 'cranberry']
                """, is_code=True)
            ),
    }
    return message

@filt_block_advisor(xpath='body/Assign/value/Call/func/Attribute', warning=True)
def list_sort_as_value(block_dets):
    """
    Warn about assigning a name to the result using .sort() on a list.
    """
    element = block_dets.element
    func_attr_els = element.xpath('value/Call/func/Attribute')
    name = get_assigned_name(element)
    if not name:
        return None
    sort_els = [func_attr_el for func_attr_el in func_attr_els
        if func_attr_el.get('attr') == 'sort']
    if not sort_els:
        return None
    message = {
        conf.BRIEF: layout_comment(f"""\
            #### Assignment of None result from in-place .sort() on list

            `{name}` is assigned to the result of an in-place sort operation.
            This is probably a mistake as the intention is probably not to set
            `{name}` to None.
            """),
    }
    return message
