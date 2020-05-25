from ..helpers import filt_block_help
from .. import conf
from .. import gen_utils
from ..gen_utils import get_collections_dets, layout_comment as layout

ASSIGN_LIST_XPATH = (
    'descendant-or-self::Assign/value/Call/func/Name '
    '| descendant-or-self::Assign/value/List')

DEFAULT_EXAMPLE_TYPE = conf.STR_TYPE

def get_list_els(block_el):
    list_els = [el for el in block_el.xpath(ASSIGN_LIST_XPATH)
        if el.tag == 'List' or el.get('id') == 'list']
    return list_els

def get_item_type_names(items):
    item_type_names = sorted(set(
        [type(item).__name__ for item in items]
    ))
    item_type_nice_names = [
        conf.TYPE2NAME.get(item_type, item_type)
        for item_type in item_type_names]
    return item_type_names, item_type_nice_names

def get_type_for_example(items):
    """
    If all else fails, just use strings for examples.
    """
    if not items:
        type4example = DEFAULT_EXAMPLE_TYPE
    else:
        usable_items = [item for item in items if item != conf.UNKNOWN_ITEM]
        item_type_names, _item_type_nice_names = get_item_type_names(
            usable_items)
        try:
            type4example = item_type_names[0]
        except IndexError:
            type4example = DEFAULT_EXAMPLE_TYPE
    return type4example

def _get_detailed_list_comment(first_name, first_items):
    type4example = get_type_for_example(first_items)
    try:
        example_items = conf.EXAMPLES_OF_TYPES[type4example]
    except KeyError:
        example_items = conf.EXAMPLES_OF_TYPES[DEFAULT_EXAMPLE_TYPE]
    example_item = example_items[0]
    needs_quoting = type4example in (
        conf.STR_TYPE, conf.DATETIME_TYPE, conf.DATE_TYPE)
    listable_example_item = (f"'{example_item}'" if needs_quoting
        else example_item)
    if first_items is None:
        appended_list = []
    else:
        appended_list = first_items.copy()
    appended_list.append(example_item)
    extended_list = appended_list.copy()
    items2extend = example_items[1:3]  ## don't repeat the appended item - might confuse the user at this stage
    extended_list.extend(items2extend)
    friends = ['Selma', 'Willy', 'Principal Skinner']
    family = ['Bart', 'Lisa', 'Marge', 'Homer']
    guests = friends + family
    detailed_list_comment = (
        layout("""\

        Lists, along with dictionaries, are the workhorses of Python data
        structures.

        Lists have an order, and can contain duplicate items and items of
        different types (usually not advisable).

        Extra items can be added to lists using the .append() method e.g.
        """)
        +
        layout(f"""\
        {first_name}.append({listable_example_item})
        """, is_code=True)
        +
        layout(f"""\
        which results in {appended_list}
        """)
        +
        layout("""\

        If you want to add multiple items at once, .extend() is useful.

        Note - we are extending the list which has already had an item appended,
        not the original list.
        """)
        +
        layout(f"""\
        {first_name}.extend({items2extend})
        """, is_code=True)
        +
        layout(f"""\
        which results in {extended_list}
        """)
        +
        layout("""\

        GOTCHA: if you are adding tuples to your list it is easy to forget the
        nested parentheses. E.g.
        """)
        +
        layout(f"""\
        coordinates.append((x, y))  ## Correct

        coordinates.append(x, y)  ## Oops - append only takes one item not two
        """, is_code=True)
        +
        layout("""\
        Lists can also be added together e.g.
        """)
        +
        layout(f"""\
        friends = {friends}
        family = {family}
        guests = friends + family
        """, is_code=True)
        +
        layout(f"""\
        resulting in {guests}

        GOTCHA: you can't add individual items to lists unless you put them in a
        list as well E.g.
        """)
        +
        layout(f"""\
        workmate = 'Carl'
        guests = {friends} + {family} + workmate  ## Oops - can only add lists
        guests = {friends} + {family} + [workmate]  ## That's better
        """, is_code=True)
        +
        layout(f"""\
        resulting in {guests + ['Carl']}
        """)
        )
    return detailed_list_comment

def truncate_list(items):
    return items[: conf.MAX_ITEMS_EVALUATED]

## only interested in lists when being assigned as a value
## (e.g. <body><Assign><value><List> so we're looking for List under value only)
@filt_block_help(xpath=ASSIGN_LIST_XPATH)
def list_overview(block_dets, *, repeat=False, execute_code=True, **_kwargs):
    """
    General overview of list taking content details into account.
    """
    list_els = get_list_els(block_dets.element)
    if not list_els:
        return None
    plural = 's' if len(list_els) > 1 else ''
    title = layout(f"""\
    ### List{plural} defined
    """)
    first_name = None
    first_items = None
    names_items, oversized_msg = get_collections_dets(list_els, block_dets,
        collection_plural='lists', truncated_items_func=truncate_list,
        execute_code=execute_code)
    summary_bits = []
    for name, items in names_items:
        unknowns = (items == conf.UNKNOWN_ITEMS or conf.UNKNOWN_ITEM in items)
        empty = len(items) == 0
        if unknowns:
            if not repeat:
                summary_bits.append(layout(f"""\
                Unable to evaluate all contents of list `{name}` but still able
                to make some general comments.
                """))
            else:
                summary_bits.append(layout(f"""\
                `{name}` is a list but unable to evaluate contents.
                """))
        elif empty:
            summary_bits.append(layout(f"""\
            `{name}` is an empty list.
            """))
        else:
            plural = 's' if len(items) > 1 else ''
            summary_bits.append(layout(f"""\

            `{name}` is a list with {gen_utils.int2nice(len(items))}
            item{plural}.
            """))
        if not first_name and not unknowns:
            first_name = name
            first_items = items
    summary = ''.join(summary_bits)
    if not first_name:
        first_name = 'demo_list'
        first_items = ['apple', 'banana', 'cherry', ]
    if not repeat:
        brief_overview = layout("""\

        Lists, along with dictionaries, are the workhorses of Python data
        structures.

        Lists have an order, and can contain duplicate items and items of
        different types (usually not advisable).
        """)
        detailed_list_comment = _get_detailed_list_comment(
            first_name, first_items)
    else:
        brief_overview = ''
        detailed_list_comment = ''

    message = {
        conf.BRIEF: title + oversized_msg + summary + brief_overview,
        conf.MAIN: title + oversized_msg + summary + detailed_list_comment,
    }
    return message

@filt_block_help(xpath=ASSIGN_LIST_XPATH, warning=True)
def mixed_list_types(block_dets, *, repeat=False, execute_code=True, **_kwargs):  # @UnusedVariable
    """
    Warns about lists containing a mix of data types.
    """
    list_els = get_list_els(block_dets.element)
    if not list_els:
        return None
    list_dets = []
    names_items, oversized_msg = get_collections_dets(list_els, block_dets,
        collection_plural='lists', truncated_items_func=truncate_list,
        execute_code=execute_code)
    has_mixed = False
    for name, items in names_items:
        if items is None:
            continue
        else:
            _item_type_names, item_type_nice_names = get_item_type_names(items)
            if len(item_type_nice_names) <= 1:
                ## No explanation needed if there aren't multiple types.
                continue
            has_mixed = True
            list_dets.append((name, item_type_nice_names))
    if not has_mixed:
        return None

    title = layout("""\
    ### List(s) with mix of different data types
    """)
    mixed_warning_bits = []
    for name, item_type_nice_names in list_dets:
        mixed_warning_bits.append(layout(f"""

        `{name}` contains more than one data type - which is probably a bad
        idea.
        """))
    mixed_warning = ''.join(mixed_warning_bits)
    mixed_dets = layout(f"""\

    The data types found were: {", ".join(item_type_nice_names)}.
    """)

    message = {
        conf.BRIEF: title + oversized_msg + mixed_warning,
        conf.MAIN: title + oversized_msg + mixed_warning + mixed_dets,
    }
    return message
