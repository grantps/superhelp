from collections import defaultdict
from textwrap import dedent

from ..advisors import shared, snippet_advisor, filt_block_advisor
from .. import conf, utils

@filt_block_advisor(xpath='body/Assign/targets/Tuple')
def unpacking(block_dets):
    """
    Identify name unpacking e.g. x, y = coord
    """
    unpacked_items = block_dets.element.xpath('targets/Tuple/elts/Name')
    unpacked_names = [
        unpacked_item.get('id') for unpacked_item in unpacked_items]
    nice_str_list = utils.get_nice_str_list(unpacked_names, quoter='`')
    message = {
        conf.BRIEF: dedent(f"""\
            Your code uses unpacking to assign names {nice_str_list}
            """),
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
        el = block_dets.element
        try:
            slice_source = el.xpath('value/Subscript/value/Name')[0].get('id')
            slice_n = el.xpath(
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
        comment = (f"{nice_sources_list} have multiple items extracted by "
            "indexing so might be suitable candidates for unpacking. ")
    else:
        comment = (f"Name (variable) `{sources2unpack[0]}` has multiple items "
            "extracted by indexing so might be a suitable candidate for "
            "unpacking. ")
    message = {
        conf.BRIEF: dedent(f"""\
            {comment}
            """),
        conf.EXTRA: shared.UNPACKING_COMMENT,
    }
    return message
