from ..advisors import shared, filt_block_advisor
from ..ast_funcs import get_assign_name
from .. import code_execution, conf, utils
from ..utils import layout_comment

ASSIGN_LISTCOMP_XPATH = 'descendant-or-self::Assign/value/ListComp'

@filt_block_advisor(xpath=ASSIGN_LISTCOMP_XPATH)
def listcomp_overview(block_dets):
    """
    Provide advice on list comprehensions and explain other types of
    comprehension available in Python.
    """
    listcomp_els = block_dets.element.xpath(ASSIGN_LISTCOMP_XPATH)
    brief_comment = ''
    plural = 's' if len(listcomp_els) > 1 else ''
    for i, dict_el in enumerate(listcomp_els):
        first = (i == 0)
        name = get_assign_name(dict_el)
        items = code_execution.get_val(
            block_dets.pre_block_code_str, block_dets.block_code_str, name)
        if first:
            title = layout_comment(f"""\

                #### List comprehension{plural} used

                """)
            brief_comment += title
        brief_comment += layout_comment(f"""

            `{name}` is a list comprehension returning a list
            with {utils.int2nice(len(items))} items: {items}
            """)
    message = {
        conf.BRIEF: brief_comment,
        conf.EXTRA: (
            layout_comment(f"""\
                #### Other "comprehensions"

                """)
            + shared.GENERAL_COMPREHENSION_COMMENT
            + layout_comment("""\

                List comprehensions aren't the only type of comprehension you can
                make. Python also lets you write Dictionary and Set Comprehensions:

                """)
            + shared.DICT_COMPREHENSION_COMMENT
            + '\n\n'
            + shared.SET_COMPREHENSION_COMMENT
            + '\n\n'
            + layout_comment("""\
                Pro tip: don't make comprehension *in*comprehensions ;-). If it is
                hard to read it is probably better written as a looping structure.
                """)
        ),
    }
    return message
