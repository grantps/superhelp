from textwrap import dedent

from ..advisors import shared, filt_block_advisor
from .. import ast_funcs, code_execution, conf, utils

@filt_block_advisor(xpath='body/Assign/value/ListComp')
def listcomp_overview(block_dets):
    """
    Provide advice on list comprehensions and explain other types of
    comprehension available in Python.
    """
    name = ast_funcs.get_assigned_name(block_dets.element)
    items = code_execution.get_val(
        block_dets.pre_block_code_str, block_dets.block_code_str, name)
    message = {
        conf.BRIEF: dedent(f"""
            `{name}` is a list comprehension returning a list
            with {utils.int2nice(len(items))} items: {items}
        """),
        conf.EXTRA: (
            dedent(f"""\
            #### Other "comprehensions"

            """)
            + shared.GENERAL_COMPREHENSION_COMMENT
            + dedent("""\


            List comprehensions aren't the only type of comprehension you can
            make. Python also lets you write Dictionary and Set Comprehensions:

            """)
            + shared.DICT_COMPREHENSION_COMMENT
            + '\n\n'
            + shared.SET_COMPREHENSION_COMMENT
            + '\n\n'
            + dedent("""\
            Pro tip: don't make comprehension *in*comprehensions ;-). If it is
            hard to read it is probably better written as a looping structure.
            """)
        ),
    }
    return message
