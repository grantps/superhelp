
from superhelp.helpers import multi_block_help
from superhelp import conf
from superhelp.gen_utils import layout_comment as layout
from superhelp.messages import MessageLevelStrs

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

@multi_block_help()
def print_overview(block_specs, *, repeat=False, **_kwargs) -> MessageLevelStrs | None:
    """
    Show some of the surprise features of the humble print function.
    """
    has_print = False
    for block_spec in block_specs:
        if _includes_print(block_spec.element):
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
            for i in range(10):
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
    brief = title + brief_details
    main = title + main_details
    message_level_strs = MessageLevelStrs(brief, main)
    return message_level_strs
