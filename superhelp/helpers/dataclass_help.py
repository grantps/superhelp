from superhelp.helpers import indiv_block_help
from superhelp import utils
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

@indiv_block_help(xpath=DATACLASS_XPATH)
def dataclass_overview(block_spec, *, xml: str, repeat=False, **_kwargs) -> MessageLevelStrs | None:
    """
    Provide advice on dataclasses and explain key features.
    """
    if repeat:
        return None
    named_tuples_in_snippet = has_named_tuples_in_snippet(xml)
    print(f"{named_tuples_in_snippet = }")
    dataclass_els = block_spec.element.xpath(DATACLASS_XPATH)
    title = layout("""\

        ### Dataclass Details
        """)
    detail_bits = []
    for dataclass_el in dataclass_els:
        utils.inspect_el(dataclass_el)
        # detail_bits.append(layout(f"""\
        #
        #     The {func_type_lbl} named `{name}` {arg_comment}. {exit_comment}.
        #     """))
    details = ''.join(detail_bits)
    brief = title + details
    main = title + details
    extra = ''
    message_level_strs = MessageLevelStrs(brief, main, extra)
    return message_level_strs
