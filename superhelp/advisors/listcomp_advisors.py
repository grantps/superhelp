from ..advisors import  DICT_COMPREHENSION_COMMENT, \
    GENERAL_COMPREHENSION_COMMENT, SET_COMPREHENSION_COMMENT, \
    filt_block_advisor
from ..ast_funcs import get_assign_name
from .. import code_execution, conf, utils
from ..utils import layout_comment as layout

ASSIGN_LISTCOMP_XPATH = 'descendant-or-self::Assign/value/ListComp'

@filt_block_advisor(xpath=ASSIGN_LISTCOMP_XPATH)
def listcomp_overview(block_dets, *, repeat=False):
    """
    Provide advice on list comprehensions and explain other types of
    comprehension available in Python.
    """
    listcomp_els = block_dets.element.xpath(ASSIGN_LISTCOMP_XPATH)
    listcomp_dets = []
    for listcomp_el in listcomp_els:
        name = get_assign_name(listcomp_el)
        items = code_execution.get_val(
            block_dets.pre_block_code_str, block_dets.block_code_str, name)
        listcomp_dets.append((name, items))
    if not listcomp_dets:
        return None

    plural = 's' if len(listcomp_dets) > 1 else ''
    title = layout(f"""\

        ### List comprehension{plural} used

        """)
    summary_bits = []
    for name, items in listcomp_dets:
        summary_bits.append(layout(f"""

        `{name}` is a list comprehension returning a list
        with {utils.int2nice(len(items))} items: {items}
        """))
    summary = ''.join(summary_bits)
    if not repeat:
        other_comprehensions = (
            layout(f"""\
                ### Other "comprehensions"

                """)
            + GENERAL_COMPREHENSION_COMMENT
            + layout("""\

                List comprehensions aren't the only type of comprehension you
                can make. Python also lets you write Dictionary and Set
                Comprehensions:

                """)
            + DICT_COMPREHENSION_COMMENT
            + '\n\n'
            + SET_COMPREHENSION_COMMENT
            + '\n\n'
            + layout("""\
                Pro tip: don't make comprehension *in*comprehensions ;-). If it
                is hard to read it is probably better written as a looping
                structure.
                """)
        )
    else:
        other_comprehensions = ''

    message = {
        conf.BRIEF: title + summary,
        conf.EXTRA: other_comprehensions,
    }
    return message
