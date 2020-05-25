from ..helpers import (get_dict_comprehension_msg,
    get_general_comprehension_msg, get_set_comprehension_msg,
    filt_block_help)
from .. import conf
from .. import gen_utils
from ..gen_utils import layout_comment as layout

def truncate_list(items):
    return items[: conf.MAX_ITEMS_EVALUATED]

ASSIGN_LISTCOMP_XPATH = 'descendant-or-self::Assign/value/ListComp'

@filt_block_help(xpath=ASSIGN_LISTCOMP_XPATH)
def listcomp_overview(block_dets, *,
        repeat=False, execute_code=True, **_kwargs):
    """
    Provide advice on list comprehensions and explain other types of
    comprehension available in Python.
    """
    listcomp_els = block_dets.element.xpath(ASSIGN_LISTCOMP_XPATH)
    if not listcomp_els:
        return None
    names_items, oversized_msg = gen_utils.get_collections_dets(
        listcomp_els, block_dets,
        collection_plural='lists', truncated_items_func=truncate_list,
        execute_code=execute_code)
    plural = 's' if len(names_items) > 1 else ''
    title = layout(f"""\
    ### List comprehension{plural} used
    """)
    summary_bits = []
    for name, items in names_items:
        if items is None or items == conf.UNKNOWN_ITEMS:
            if not repeat:
                summary_bits.append(layout(f"""\
                Unable to evaluate all contents of list comprehension `{name}`
                but still able to make some general comments.
                """))
            else:
                summary_bits.append(layout(f"""\
                `{name}` is a list comprehension but unable to evaluate
                contents.
                """))
        elif len(items) == 0:
            summary_bits.append(layout(f"""\
            `{name}` is an empty list comprehension.
            """))
        else:
            summary_bits.append(layout(f"""

            `{name}` is a list comprehension returning a list with
            {gen_utils.int2nice(len(items))} items: {items}
            """))
    summary = ''.join(summary_bits)
    brief_summary = summary
    main_summary = summary
    if not repeat:
        other_comprehensions = (
            layout("""\
            ### Other "comprehensions"
            """)
            + get_general_comprehension_msg()
            + layout("""\

            List comprehensions aren't the only type of comprehension you can
            make. Python also lets you write Dictionary and Set Comprehensions:
            """)
            + get_dict_comprehension_msg()
            + '\n\n'
            + get_set_comprehension_msg()
            + '\n\n'
            + layout("""\

            Pro tip: don't make comprehension *in*comprehensions ;-). If it is
            hard to read it is probably better written as a looping structure.
            """)
        )
    else:
        other_comprehensions = ''

    message = {
        conf.BRIEF: title + oversized_msg + brief_summary,
        conf.MAIN: title + oversized_msg + main_summary,
        conf.EXTRA: other_comprehensions,
    }
    return message
