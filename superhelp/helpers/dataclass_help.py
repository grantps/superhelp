from superhelp.conf import Level
from superhelp.helpers import multi_block_help, shared_messages
from superhelp.gen_utils import layout_comment as layout
from superhelp.messages import MessageLevelStrs

DATACLASS_XPATH = "descendant-or-self::ClassDef[decorator_list/Name[@id='dataclass']]"

def has_named_tuples_in_snippet(xml: str) -> bool:
    """
    We don't want to repeat the advice on dataclasses so if it is already going to be handled by the named tuple
    feedback we need to know so don't do it again here.
    """
    func_name_els = xml.xpath('descendant-or-self::value/Call/func/Name')
    if not func_name_els:
        return False
    named_tuple_els = [func_name_el for func_name_el in func_name_els if func_name_el.get('id') == 'namedtuple']
    return bool(named_tuple_els)

@multi_block_help()
def dataclass_overview(block_specs, xml: str, *, repeat=False, **_kwargs) -> MessageLevelStrs | None:
    """
    Provide advice on dataclasses and explain key features.
    """
    if repeat:
        return None
    named_tuples_in_snippet = has_named_tuples_in_snippet(xml)
    if named_tuples_in_snippet:
        return None
    dataclass_els = []
    for block_spec in block_specs:
        block_dataclass_els = block_spec.element.xpath(DATACLASS_XPATH)
        dataclass_els.extend(block_dataclass_els)
    n_dcs = len(dataclass_els)
    if not n_dcs:
        return None
    plural = 'es' if n_dcs > 1 else ''
    names = [dataclass_el.get('name') for dataclass_el in dataclass_els]
    names_str = ', '.join(names)
    title = layout(f"""\

        ### Dataclass Details

        Your code includes {n_dcs} dataclass{plural}: {names_str}
        """)
    brief = title + shared_messages.get_dataclass_msg(level=Level.BRIEF, in_named_tuple_context=False)
    main = title + shared_messages.get_dataclass_msg(level=Level.BRIEF, in_named_tuple_context=False)
    extra = shared_messages.get_dataclass_msg(level=Level.EXTRA, in_named_tuple_context=False)
    message_level_strs = MessageLevelStrs(brief, main, extra)
    return message_level_strs
