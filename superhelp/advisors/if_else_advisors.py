from textwrap import dedent

from ..advisors import any_block_advisor, type_block_advisor
from .. import ast_funcs, code_execution, conf, utils

@type_block_advisor(element_type=conf.STR_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def str_overview(block_dets):
    name = ast_funcs.get_assigned_name(block_dets.element)
    return None

## TODO: if-elif-else (always else - even if to raise an exception)
