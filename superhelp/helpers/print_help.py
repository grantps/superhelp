
from ..helpers import all_blocks_help
from .. import conf
from ..gen_utils import layout_comment as layout

def _includes_print(block_el):
    """
    print('Hi') is Call/func/Name id = 'print'
    p = print is Assign/value/Name id = 'print'
    """
    func_name_els = block_el.xpath('descendant-or-self::Call/func/Name')
    print_els = [func_name_el for func_name_el in func_name_els
        if func_name_el.get('id') == 'print']
    if print_els:
        return True
    assigned_name_els = block_el.xpath('descendant-or-self::Assign/value/Name')
    print_assigned_els = [
        assigned_name_el for assigned_name_el in assigned_name_els
        if assigned_name_el.get('id') == 'print']
    if print_assigned_els:
        return True
    return False

@all_blocks_help()
def print_overview(blocks_dets, *, repeat=False, **_kwargs):
    """
    Show some of the surprise features of the humble print function.
    """
    has_print = False
    for block_dets in blocks_dets:
        if _includes_print(block_dets.element):
            has_print = True
            break
    if not has_print:
        return None

    title = layout("""\
    ### `print` function used
    """)
    if not repeat:
        brief_details = layout("""\
        `print` may seem like a very basic function but it has some extra
        parameters providing extra functionality. More information can be found
        in the official on-line documentation for `print`.
        """)
        main_details = (
            layout("""\

            `print` may seem like a very basic function but it has some extra
            features worth knowing about. Here is an example using the `end` and
            `flush` parameters. Dots should appear one by one in the same line.
            If `flush` were `False` then they would only appear at the end all
            at once. If `end` were the default new line character '\\n' they
            would have appeared on separate lines.
            """)
            +
            layout("""\
            from time import sleep
            print('.', end='', flush=True)
            sleep(0.25)
            """, is_code=True)
            +
            layout("""\

            More information can be found in `print`'s official on-line
            documentation.
            """)
        )
    else:
        brief_details = ''
        main_details = ''

    message = {
        conf.BRIEF: title + brief_details,
        conf.MAIN: title + main_details,
    }
    return message
