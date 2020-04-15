from ..advisors import snippet_advisor
from .. import conf
from ..utils import get_nice_str_list, int2nice, layout_comment

UNSPECIFIC_EXCEPTION = 'Exception'

def _get_exception_block_comment(exception_block):
    handlers = get_nice_str_list(exception_block, quoter='`')
    comment = f"The following exception handlers were detected: {handlers}"
    return comment

def get_exception_blocks(blocks_dets):
    """
    There can be multiple try-except statements in a snippet so we have to
    handle each of them.
    """
    exception_blocks = []
    for block_dets in blocks_dets:
        block_exception_types = []
        except_handler_els = block_dets.element.xpath('handlers/ExceptHandler')
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

@snippet_advisor()
def exception_overview(blocks_dets):
    """
    Provide overview of exception handling.
    """
    exception_blocks = get_exception_blocks(blocks_dets)
    if not exception_blocks:
        return None
    brief_comment = ''
    for n, exception_block in enumerate(exception_blocks, 1):
        counter = '' if len(exception_blocks) == 1 else f" {int2nice(n)}"
        brief_comment += f"""\

            ##### `try`-`except` block{counter}

            """
        brief_comment += _get_exception_block_comment(exception_block)
    message = {
        conf.BRIEF: layout_comment(brief_comment),
    }
    return message

@snippet_advisor(warning=True)
def unspecific_exception(blocks_dets):
    """
    Look for unspecific exceptions.
    """
    exception_blocks = get_exception_blocks(blocks_dets)
    if not exception_blocks:
        return None
    brief_comment = ''
    for n, exception_block in enumerate(exception_blocks, 1):
        only_unspecific = (len(exception_block) == 1
            and exception_block[0] == UNSPECIFIC_EXCEPTION)
        if not only_unspecific:
            continue
        counter = '' if len(exception_blocks) == 1 else f" {int2nice(n)}"
        brief_comment += f"""\

            ##### Un-specific `Exception` only in `try`-`except` block{counter}

            """
        brief_comment += (f"""\

            Using the un-specific exception type `Exception` is often completely
            appropriate. But if you are looking for specific exceptions you
            should handle those separately.

            For example:
            """)
    if not brief_comment:
        return None
    message = {
        conf.BRIEF: layout_comment(brief_comment),
        conf.MAIN: (
            layout_comment(brief_comment)
            +
            layout_comment("""\

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
        ),
    }
    return message
