from ..advisors import any_block_advisor, type_block_advisor

from ..ast_funcs import get_assigned_name
from .. import conf
from ..utils import layout_comment

def _get_has_sorting_or_reversing(code_str):
    sort_or_reverse_patterns = ['.sort(', 'sorted(', 'reversed(']
    has_sorting_or_reversing = False
    for pattern in sort_or_reverse_patterns:
        if pattern in code_str:
            has_sorting_or_reversing = True
            break
    return has_sorting_or_reversing

@any_block_advisor()
def sorting_reversing_overview(block_dets):
    code_str = block_dets.block_code_str
    has_sorting_or_reversing = _get_has_sorting_or_reversing(code_str)
    if not has_sorting_or_reversing:
        return None
    message = {
        conf.BRIEF: layout_comment("""\
            #### Sorting / reversing

            This block of code has sorting or reversing. Sorting and, to a
            lesser extent, reversing are very common needs in programming. Two
            key points:

            1) reversing is not the same as sorting with reverse=True

            2) the list sort method e.g. my_list.sort() returns None, not the sorted list
            """),
        conf.MAIN: (
            layout_comment("""\
                #### Sorting / reversing

                This block of code has sorting or reversing. Sorting and, to a
                lesser extent, reversing are very common needs in programming. Two
                key points:
    
                1) reversing is not the same as sorting with reverse=True

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

                2) the list sort method e.g. my_list.sort() returns None, not the sorted list

                sorted(my_list) returns a sorted list but my_list.sort() is an
                in-place process. It mutates something rather than returning a
                separate thing.

                To illustrate:

                i) sorted() returning a result and leaving its input unchanged

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

                ii) .sort() returning None and changing its input in-place

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

@type_block_advisor(element_type=conf.ATTRIBUTE_ELEMENT_TYPE,
    xml_root='body/Assign/value/Call/func', warning=True)
def list_sort_as_value(block_dets):
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
