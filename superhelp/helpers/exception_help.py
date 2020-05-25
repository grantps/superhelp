from ..helpers import all_blocks_help
from .. import conf
from ..gen_utils import get_nice_str_list, int2nice, layout_comment as layout

UNSPECIFIC_EXCEPTION = 'Exception'

def get_exception_blocks(blocks_dets):
    """
    There can be multiple try-except statements in a snippet so we have to
    handle each of them.
    """
    exception_blocks = []
    for block_dets in blocks_dets:
        block_exception_types = []
        except_handler_els = block_dets.element.xpath(
            'descendant-or-self::handlers/ExceptHandler')
        for except_handler_el in except_handler_els:
            exception_type_els = except_handler_el.xpath(
                'type/Name | type/Tuple/elts/Name')
            exception_handler_types = [
                exception_type_el.get('id')
                for exception_type_el in exception_type_els]
            block_exception_types.extend(exception_handler_types)
        if block_exception_types:
            exception_blocks.append(block_exception_types)
    return exception_blocks

@all_blocks_help()
def exception_overview(blocks_dets, *, repeat=False, **_kwargs):
    """
    Provide overview of exception handling.
    """
    exception_blocks = get_exception_blocks(blocks_dets)
    if not exception_blocks:
        return None
    if repeat:
        return None

    title = layout("""\
    ### Exception handling
    """)
    block_comment_bits = []
    for n, exception_block in enumerate(exception_blocks, 1):
        counter = '' if len(exception_blocks) == 1 else f" {int2nice(n)}"
        handlers = get_nice_str_list(exception_block, quoter='`')
        block_comment_bits.append(layout(f"""\
        #### `try`-`except` block{counter}

        The following exception handlers were detected: {handlers}
        """))
    block_comments = ''.join(block_comment_bits)

    message = {
        conf.BRIEF: title + block_comments,
    }
    return message

@all_blocks_help(warning=True)
def unspecific_exception(blocks_dets, *, repeat=False, **_kwargs):
    """
    Look for unspecific exceptions.
    """
    exception_blocks = get_exception_blocks(blocks_dets)
    if not exception_blocks:
        return None
    unspecific_block_ns = []
    for n, exception_block in enumerate(exception_blocks, 1):
        only_unspecific = (len(exception_block) == 1
            and exception_block[0] == UNSPECIFIC_EXCEPTION)
        if not only_unspecific:
            continue
        unspecific_block_ns.append(n)
    if not unspecific_block_ns:
        return None

    title = layout("""\
    #### Un-specific `Exception` only in `try`-`except` block(s)
    """)
    if not repeat:
        n_unspecific = len(unspecific_block_ns)
        if n_unspecific == 1:
            block_n_specific_text = ' has'
        else:
            unspecific_nice_block_ns = [
                int2nice(unspecific_block_n)
                for unspecific_block_n in unspecific_block_ns]
            blocks_ns = get_nice_str_list(unspecific_nice_block_ns, quoter='')
            block_n_specific_text = f"s {blocks_ns} have"
        unspecific_warning = layout(f"""\

        `try`-`except` block{block_n_specific_text} an un-specific Exception
        only.

        Using the un-specific exception type `Exception` is often completely
        appropriate. But if you are looking for specific exceptions you should
        handle those separately.
        """)
        unspecific_demo = (
            layout("""\
            For example:
            """)
            +
            layout("""\

            try:
                spec_dicts[idx][spec_type]
            except IndexError:
                print(f"Unable to access requested spec_dict (idx {idx})")
            except KeyError:
                print(f"Unable to access '{spec_type}' for "
                    f"requested spec_dict (idx {idx})")
            except Exception as e:
                print(f"Unexpected exception - details: {e}")
            """, is_code=True)
            )
    else:
        unspecific_warning = ''
        unspecific_demo = ''

    message = {
        conf.BRIEF: title + unspecific_warning,
        conf.MAIN: title + unspecific_warning + unspecific_demo,
    }
    return message
