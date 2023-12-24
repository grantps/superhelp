from dataclasses import dataclass

from superhelp.conf import Level
from superhelp.helpers import multi_block_help, shared_messages
from superhelp import ast_funcs
from superhelp.gen_utils import layout_comment as layout
from superhelp.messages import MessageLevelStrs

@dataclass
class NTDets:
    name: str
    label: str
    fields_str: str
    fields_list: list[str]

def get_named_tuple_dets(named_tuple_el):
    """
    Get name, label, fields.
    """
    assign_block_el = named_tuple_el.xpath('ancestor-or-self::Assign')[-1]
    name = assign_block_el.xpath('targets/Name')[0].get('id')
    label, fields_list = ast_funcs.get_nt_lbl_flds(assign_block_el)
    fields_str = ', '.join(fields_list)
    named_tuple_dets = NTDets(name, label, fields_str, fields_list)
    return named_tuple_dets

def get_named_tuples_dets(block_specs):
    all_named_tuples_dets = []
    for block_spec in block_specs:
        func_name_els = block_spec.element.xpath(
            'descendant-or-self::value/Call/func/Name')
        if not func_name_els:
            continue
        named_tuple_els = [func_name_el for func_name_el in func_name_els
            if func_name_el.get('id') == 'namedtuple']
        named_tuples_dets = [
            get_named_tuple_dets(named_tuple_el)
            for named_tuple_el in named_tuple_els]
        all_named_tuples_dets.extend(named_tuples_dets)
    return all_named_tuples_dets

@multi_block_help()
def named_tuple_overview(block_specs, *, repeat=False, **_kwargs) -> MessageLevelStrs | None:
    """
    Look for named tuples and explain how they can be enhanced.
    """
    if repeat:
        return None
    named_tuples_dets = get_named_tuples_dets(block_specs)
    if not named_tuples_dets:
        return None

    example_dets = named_tuples_dets[0]
    fields = '\n                '.join(f"{field_str}: str" for field_str in example_dets.fields_list)
    replacement = (
            layout("""\
            ### Replacing Named Tuples with Dataclasses

            Named tuples might be the correct answer in this case
            but you should probably be using a dataclass instead
            (see https://whenof.python.nz/blog/classy-data-with-dataclasses.html)

            For example:
            """)
            +
            layout(f"""\
            from dataclasses import dataclass

            @dataclass
            class {example_dets.name.title()}:
                {fields}
            """, is_code=True)
        )
    brief = replacement
    main = replacement + shared_messages.get_dataclass_msg(level=Level.MAIN, in_named_tuple_context=True)
    extra = shared_messages.get_dataclass_msg(level=Level.EXTRA, in_named_tuple_context=True)
    message_level_strs = MessageLevelStrs(brief, main, extra)
    return message_level_strs
