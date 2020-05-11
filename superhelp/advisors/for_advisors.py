from ..advisors import get_dict_comprehension_msg, \
    get_general_comprehension_msg, get_set_comprehension_msg, filt_block_advisor
from ..ast_funcs import get_el_lines_dets
from .. import conf
from ..utils import layout_comment as layout

FOR_XPATH = 'descendant-or-self::For'

@filt_block_advisor(xpath=FOR_XPATH)
def comprehension_option(block_dets, *, repeat=False):
    """
    Provide overview of for loop to see if simple enough to be a possible
    candidate for a comprehension.

    Don't try to properly understand the for loop or make a built comprehension.
    It is enough to detect whether a loop is simple enough to consider making a
    comprehension or not. And to see whether appending, key setting, or adding
    is happening and suggesting the right comprehension accordingly.
    """
    for_els = block_dets.element.xpath(FOR_XPATH)
    any_short_enough = False
    for for_el in for_els:
        _first_line_no, _last_line_no, for_lines_n = get_el_lines_dets(
            for_el, ignore_trailing_lines=True)
        short_enough = for_lines_n < 3
        if short_enough:
            any_short_enough = True
            break
    if not any_short_enough:
        return None
    comp_type = None
    comp_comment = ''
    if 'append' in block_dets.block_code_str:
        comp_type = 'List Comprehension'
        comp_comment = get_dict_comprehension_msg()
    elif len(block_dets.element.cssselect('Subscript')):  ## Seems a reasonable indicator
        comp_type = 'Dictionary Comprehension'
        comp_comment = get_dict_comprehension_msg()
    elif 'set' in block_dets.block_code_str:
        comp_type = 'Set Comprehension'
        comp_comment = get_set_comprehension_msg()
    else:
        return None

    title = layout(f"""\
    ### Possible option of using a {comp_type}
    """)
    if not repeat:
        option = layout(f"""\

        Simple for loops can sometimes be replaced with comprehensions. In this
        case a simple reading of the code suggests a {comp_type} might be
        possible. Of course, only use a comprehension if it makes your code
        easier to understand.
        """)
    else:
        option = ''

    message = {
        conf.BRIEF: title + option,
        conf.MAIN: (title + option + get_general_comprehension_msg()
            + '\n\n' + comp_comment),
    }
    return message

def get_incremental_iteration_dets(for_el):
    """
    Look for the pattern:

    pets = ['cat', 'dog']
    for i in range(len(pets)):
        print(f"My {pets[i]}")

    For/target/Name id = i
        iter/Call/func/Name id = range
                  args/Call/func/Name id = len
                            args/Name id = pets

    ... Subscript/value/Name id = pets
                  slice/Index/value/Name = i
    """
    target_name_els = for_el.xpath('target/Name')
    if not target_name_els:
        return None
    index_name = target_name_els[0].get('id')  ## e.g. 'i'
    iterator_func_name_els = for_el.xpath('iter/Call/func/Name')
    if not iterator_func_name_els:
        return None
    range_iterator_func = iterator_func_name_els[0].get('id') == 'range'  ## range()
    if not range_iterator_func:
        return None
    iter_arg_func_name_els = for_el.xpath('iter/Call/args/Call/func/Name')
    if not iter_arg_func_name_els:
        return None
    len_inside = (iter_arg_func_name_els[0].get('id') == 'len')  ## range(len())
    if not len_inside:
        return None
    len_arg_name_els = for_el.xpath('iter/Call/args/Call/args/Name')
    if not len_arg_name_els:
        return None
    iterable_name = len_arg_name_els[0].get('id')  ## e.g. pets
    if not iterable_name:
        return None
    subscript_name_els = for_el.xpath(
        'descendant-or-self::Subscript/value/Name')
    if not subscript_name_els:
        return None
    subscript_name = subscript_name_els[0].get('id')  ## e.g. pets
    slicing_iterable = (iterable_name == subscript_name)
    if not slicing_iterable:
        return None
    slice_index_name_els = for_el.xpath(
        'descendant-or-self::Subscript/slice/Index/value/Name')
    if not slice_index_name_els:
        return None
    slice_index_name = slice_index_name_els[0].get('id')
    slicing_by_range_val = (slice_index_name == index_name)
    if not slicing_by_range_val:
        return None
    return index_name, iterable_name

@filt_block_advisor(xpath=FOR_XPATH)
def for_index_iteration(block_dets, *, repeat=False):
    """
    Look to see if an opportunity for simple iteration available as more
    pythonic alternative to incremental indexing.

    Look for the pattern:

    for i in range(len(foo)):
        foo[i] detected
    """
    for_els = block_dets.element.xpath(FOR_XPATH)
    any_incremental_iteration = False
    for for_el in for_els:
        try:
            index_name, iterable_name = get_incremental_iteration_dets(for_el)
        except TypeError:
            continue
        else:
            any_incremental_iteration = True
            break
    if not any_incremental_iteration:
        return None

    summary = layout(f"""\
    ### Possible option of using direct iteration

    It looks like your snippet iterates through `{iterable_name}` using indexes.
    In Python you can iterate directly which is much easier.
    """)
    if not repeat:
        examples = (
            layout("""\
            For example, instead of:
            """)
            +
            layout(f"""\
            for {index_name} in range(len({iterable_name})):
                print({iterable_name}[{index_name}])
            """, is_code=True)
            +
            layout("""\
            you can directly iterate as follows:
            """)
            +
            layout(f"""\
            for item in {iterable_name}:  ## item should be replaced with a more useful name
                print(item)

            """, is_code=True)
            +
            layout("""\
            which is considered more pythonic i.e. good.
            """)
        )
    else:
        examples = ''

    message = {
        conf.BRIEF: summary + examples,
    }
    return message

@filt_block_advisor(xpath=FOR_XPATH, warning=True)
def for_else(block_dets, *, repeat=False):
    """
    Look for the for-else construct and warn about its safe usage.
    """
    for_els = block_dets.element.xpath(FOR_XPATH)
    has_for_else = False
    for for_el in for_els:
        for_else_els = for_el.xpath('orelse')
        non_empty_for_else_els = [el for el in for_else_els if el.getchildren()]
        if non_empty_for_else_els:
            has_for_else = True
            break
    if not has_for_else:
        return None

    title = layout("""\
    ### Ambiguous `for-else` language feature used
    """)
    if not repeat:
        problem = (
            layout("""\

            `for`-`else` is a useful language feature but it is so widely
            misunderstood it is dangerous to use without special comment. For
            example, in the snippet below do we pass through `else` because we
            finished the looping or because we didn't?
            """)
            +
            layout("""\
            for i in range(size):
                if i > 100:
                    break
            else:
                pass
            """, is_code=True)
        )
        solution = (
            layout("""\

            The correct answer, which as many as a third of people will guess
            correctly ;-), is that we only follow the `else` path if we finished
            the for-looping without breaking. The thinking is that we loop
            through something to find something and exit the loop. `else`
            applies when that search fails. But it is very easy to get the logic
            confused. And given that programs are made to be read by humans we
            obviously need to do something. We can either avoid the feature
            altogether or we can add a brief comment each time (my preference).
            For example:
            """)
            +
            layout("""\
            for i in range(size):
                if i > 100:
                    break
            else:  # didn't break for-loop
                pass
            """, is_code=True)
        )
        extra_msg = layout("""\
        #### Interesting discussion on `for`-`else`

        <https://nedbatchelder.com/blog/201110/forelse.html>
        One comment noted that the construct violates the principle of Least
        Astonishment.
        """)
    else:
        problem = ''
        solution = ''
        extra_msg = ''

    message = {
        conf.BRIEF: title + problem,
        conf.MAIN: title + problem + solution,
        conf.EXTRA: extra_msg,
    }
    return message

@filt_block_advisor(xpath=FOR_XPATH)
def nested_fors(block_dets, *, repeat=False):
    """
    Look to see if an opportunity for using itertools.product instead of nested
    iteration.
    """
    for_els = block_dets.element.xpath(FOR_XPATH)
    nested_iteration = False
    for for_el in for_els:
        nested_for_els = for_el.xpath('descendant::For')
        if nested_for_els:
            nested_iteration = True
            break
    if not nested_iteration:
        return None

    summary = layout("""\
    ### Possible option of simplifying nested iteration

    Consider replacing nested iteration with `itertools.product`.
    """)
    if not repeat:
        demo = (
            layout("""\
            For example, you could replace:
            """)
            +
            layout("""\
            for person in persons:
                for pet in pets:
                    for year in years:
                        print(f"{person} might like a {pet} in {year}")
            """, is_code=True)
            +
            layout("""\
            with a version using `itertools.product`:
            """)
            +
            layout("""\
            from itertools import product
            for person, pet, year in product(persons, pets, years):
                print(f"{person} might like a {pet} in {year}")
            """, is_code=True)
        )
        pros = layout("""\

        Whether this is a good idea or not depends on your specific code but
        using `product` has the advantage of reducing indentation. It also
        semantically expresses the intention of the code - namely to look at
        every option in the cartesian product of the different collections of
        items.
        """)
    else:
        demo = ''
        pros = ''

    message = {
        conf.BRIEF: summary + demo,
        conf.MAIN: summary + demo + pros,
    }
    return message
