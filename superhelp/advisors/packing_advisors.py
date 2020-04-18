from collections import defaultdict
from textwrap import dedent

from ..advisors import shared, snippet_advisor, filt_block_advisor
from .. import conf, utils
from ..utils import layout_comment

ASSIGN_UNPACKING_XPATH = 'descendant-or-self::Assign/targets/Tuple'

@filt_block_advisor(xpath=ASSIGN_UNPACKING_XPATH)
def unpacking(block_dets):
    """
    Identify name unpacking e.g. x, y = coord
    """
    unpacked_els = block_dets.element.xpath(ASSIGN_UNPACKING_XPATH)
    brief_comment = ''
    for unpacked_el in unpacked_els:
        unpacked_names = [
            name_el.get('id') for name_el in unpacked_el.xpath('elts/Name')]
        nice_str_list = utils.get_nice_str_list(unpacked_names, quoter='`')
        unpacked_comment = layout_comment(f"""\

            Your code uses unpacking to assign names {nice_str_list}
            """)
        brief_comment += unpacked_comment
    message = {
        conf.BRIEF: brief_comment,
        conf.EXTRA: shared.UNPACKING_COMMENT,
    }
    return message

@snippet_advisor()
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
                slice_n = assign_el.xpath(
                    'value/Subscript/slice/Index/value/Num')[0].get('n')
            except IndexError:
                continue
            else:
                source_slices[slice_source].add(slice_n)
    sources2unpack = [source
        for source, slice_ns in source_slices.items()
        if len(slice_ns) > 1]
    if not sources2unpack:
        return None
    multiple_items = len(sources2unpack) > 1
    if multiple_items:
        nice_sources_list = utils.get_nice_str_list(sources2unpack, quoter='`')
        brief_comment = layout_comment(f"""\
            {nice_sources_list} have multiple items extracted by
            indexing so might be suitable candidates for unpacking.
            """)
    else:
        brief_comment = layout_comment(f"""\
            Name (variable) `{sources2unpack[0]}` has multiple items extracted
            by indexing so might be a suitable candidate for unpacking.
            """)
    message = {
        conf.BRIEF: brief_comment,
        conf.EXTRA: shared.UNPACKING_COMMENT,
    }
    return message
