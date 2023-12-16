from superhelp.helpers import indiv_block_help
from superhelp import conf
from superhelp import gen_utils
from superhelp.gen_utils import layout_comment as layout

DATACLASS_XPATH = "descendant-or-self::ClassDef[decorator_list/Name[@id='dataclass']]"

@indiv_block_help(xpath=DATACLASS_XPATH)
def dataclass_overview(block_spec, *,
        repeat=False, execute_code=True, **_kwargs):
    """
    Provide advice on list comprehensions and explain other types of
    comprehension available in Python.
    """
    dataclass_els = block_spec.element.xpath(DATACLASS_XPATH)

    return None



    names_items, oversized_msg = 1, 2
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
            + layout("""\

            List comprehensions aren't the only type of comprehension you can
            make. Python also lets you write Dictionary and Set Comprehensions:
            """)
            + '\n\n'
            + layout("""\

            Pro tip: don't make comprehension *in*comprehensions ;-). If it is
            hard to read it is probably better written as a looping structure.
            """)
        )
    else:
        other_comprehensions = ''

    message = {
        conf.Level.BRIEF: title + oversized_msg + brief_summary,
        conf.Level.MAIN: title + oversized_msg + main_summary,
        conf.Level.EXTRA: other_comprehensions,
    }
    return message
