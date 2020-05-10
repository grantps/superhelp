from collections import defaultdict

from ..advisors import get_unpacking_msg, all_blocks_advisor, \
    filt_block_advisor
from .. import conf, utils
from ..utils import get_python_version, layout_comment as layout

def get_slice_n_3_7(assign_el):
    slice_n = assign_el.xpath(
        'value/Subscript/slice/Index/value/Num')[0].get('n')
    return slice_n

def get_slice_n_3_8(assign_el):
    val_els = assign_el.xpath('value/Subscript/slice/Index/value/Constant')
    val_el = val_els[0]
    if val_el.get('type') in ('int', 'float'):
        slice_n = val_el.get('value')
    else:
        raise TypeError("slice index value not an int or a float - actual type "
            f"'{val_el.get('type')}'")
    return slice_n

python_version = get_python_version()
if python_version in (conf.PY3_6, conf.PY3_7):
    get_slice_n = get_slice_n_3_7
elif python_version == conf.PY3_8:
    get_slice_n = get_slice_n_3_8
else:
    raise Exception(f"Unexpected Python version {python_version}")

ASSIGN_UNPACKING_XPATH = 'descendant-or-self::Assign/targets/Tuple'

@filt_block_advisor(xpath=ASSIGN_UNPACKING_XPATH)
def unpacking(block_dets, *, repeat=False):
    """
    Identify name unpacking e.g. x, y = coord
    """
    unpacked_els = block_dets.element.xpath(ASSIGN_UNPACKING_XPATH)

    title = layout("""\
    ### Name uppacking
    """)
    summary_bits = []
    for unpacked_el in unpacked_els:
        unpacked_names = [
            name_el.get('id') for name_el in unpacked_el.xpath('elts/Name')]
        if not unpacked_names:
            continue
        nice_str_list = utils.get_nice_str_list(unpacked_names, quoter='`')
        summary_bits.append(layout(f"""\

        Your code uses unpacking to assign names {nice_str_list}
        """))
    summary = ''.join(summary_bits)
    if not repeat:
        unpacking_msg = get_unpacking_msg()
    else:
        unpacking_msg = ''

    message = {
        conf.BRIEF: title + summary,
        conf.EXTRA: unpacking_msg,
    }
    return message

@all_blocks_advisor()
def unpacking_opportunity(blocks_dets):
    """
    Look for opportunities to unpack values into multiple names instead of
    repeated and un-pythonic extraction using indexes.

    Signs of an unpacking opportunity - something is repeatedly sliced with
    different slice numbers e.g.

    x, y = coord
    vs
    x = coord[0]
    y = coord[1]
    """
    source_slices = defaultdict(set)
    for block_dets in blocks_dets:
        assign_els = block_dets.element.xpath('descendant-or-self::Assign')
        for assign_el in assign_els:
            try:
                slice_source = assign_el.xpath(
                    'value/Subscript/value/Name')[0].get('id')
                slice_n = get_slice_n(assign_el)
            except IndexError:
                continue
            else:
                source_slices[slice_source].add(slice_n)
    sources2unpack = [source
        for source, slice_ns in source_slices.items()
        if len(slice_ns) > 1]
    if not sources2unpack:
        return None

    title = layout("""\
    ### Unpacking opportunity
    """)
    multiple_items = len(sources2unpack) > 1
    if multiple_items:
        nice_sources_list = utils.get_nice_str_list(sources2unpack, quoter='`')
        unpackable = layout(f"""\

        {nice_sources_list} have multiple items extracted by indexing so might
        be suitable candidates for unpacking.
        """)
    else:
        unpackable = layout(f"""\

        Name (variable) `{sources2unpack[0]}` has multiple items extracted by
        indexing so might be a suitable candidate for unpacking.
        """)

    message = {
        conf.BRIEF: title + unpackable,
        conf.EXTRA: get_unpacking_msg(),
    }
    return message
