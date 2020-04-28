from ..advisors import filt_block_advisor
from .. import ast_funcs, conf
from ..utils import layout_comment as layout

FOR_XPATH = 'descendant-or-self::For'
WHILE_XPATH = 'descendant-or-self::While'
IF_XPATH = 'descendant-or-self::If'  ## includes elif
OUTER_XPATHS = {
    'for': FOR_XPATH,
    'while': WHILE_XPATH,
    'if': IF_XPATH,
}
NESTING_XPATH = ' | '.join(OUTER_XPATHS.values())

def _long_nested_block(outer_el):
    _first_line_no, _last_line_no, el_lines_n = ast_funcs.get_el_lines_dets(
        outer_el, ignore_trailing_lines=True)
    nested_block_line_len = el_lines_n - 1  ## ignore the actual outer el e.g. for:
    too_long = nested_block_line_len > conf.MAX_BRIEF_NESTED_BLOCK
    return too_long

def has_long_block(block_el, xpath):
    long_block = False
    outer_els = block_el.xpath(xpath)
    for outer_el in outer_els:
        too_long = _long_nested_block(outer_el)
        if too_long:
            long_block = True
            break
    return long_block

def get_short_circuit_alt_msgs(brief_msg, main_msg):
    """
    Messages exploring option of unnesting indented block by exiting early if
    the conditional in the if expression is not met.
    """
    brief_msg += layout("""\

        #### Short-circuit and exit early

        It may be possible to unnest the indented code block by exiting early if
        the condition in the `if` expression is not met.
        """)
    main_msg += brief_msg
    main_msg += (
        layout("""

            For example, instead of:

            """)
        +
        layout("""\
            if tall_enough:
                ## add to basketball team
                line 1
                line 2
                line 3
                ...
                line 30
            logging.info("Finished!")
            """, is_code=True)
        +
        layout("""\

            we could possibly write:

            """)
        +
        layout('''\
            if not tall_enough:
                return
            ## add to basketball team
            line 1
            line 2
            line 3
            ...
            line 30
            logging.info("Finished!")
            ''', is_code=True)
    )
    return brief_msg, main_msg

def get_func_alt_msgs(brief_msg, main_msg):
    """
    Messages exploring option of replacing nested block with a function call.
    """
    move_to_func_msg = layout("""\

        #### Shift to function

        It may be possible to pull most of the nested code block into a function
        which can be called instead.
        """)
    brief_msg += move_to_func_msg
    main_msg += move_to_func_msg
    main_msg += (
        layout("""

            For example, instead of:

            """)
        +
        layout("""\
            for name in names:
                ## contact name
                line 1
                line 2
                line 3
                ...
                line 30
            logging.info("Finished!")
            """, is_code=True)
        +
        layout("""\

            we could possibly write:

            """)
        +
        layout('''\
            def contact(name):
                """
                Contact person ...
                """
                line 1
                line 2
                line 3
                ...
                line 30

            for name in names:
                contact(name)
            logging.info("Finished!")
            ''', is_code=True)
    )
    return brief_msg, main_msg

@filt_block_advisor(xpath=NESTING_XPATH, warning=True)
def bloated_nested_block(block_dets, *, repeated_message=False):
    """
    Look for long indented blocks under conditionals, inside loops etc that are
    candidates for separating into functions to simplify the narrative of the
    main code.
    """
    bloated_outer_types = set()
    included_if = False
    for lbl, outer_xpath in OUTER_XPATHS.items():
        if has_long_block(block_dets.element, outer_xpath):
            bloated_outer_types.add(lbl)
            if lbl == 'if':
                included_if = True
    if not bloated_outer_types:
        return None
    brief_msg = layout("""\
        
        ### Possibility of avoiding excessively long nested blocks

        """)
    for bloated_outer_type in bloated_outer_types:
        brief_msg += layout(f"""\
            The code has at least one long nested block under
            `{bloated_outer_type}:`
            """)
    if repeated_message:
        main_msg = brief_msg
        extra_msg = ''
    else:
        brief_msg += layout("""\
            You might want to consider applying a strategy for avoiding
            excessively long indented blocks:
            """)
        main_msg = ''
        if included_if:
            brief_msg, main_msg = get_short_circuit_alt_msgs(
                brief_msg, main_msg)
        brief_msg, main_msg = get_func_alt_msgs(brief_msg, main_msg)
        extra_msg = layout("""\
            Computers can handle lots of nesting without malfunctioning. Human
            brains are not so fortunate. As it says in The Zen of Python:

            > "Flat is better than nested."
            """)
    message = {
        conf.BRIEF: brief_msg,
        conf.MAIN: main_msg,
        conf.EXTRA: extra_msg,
    }
    return message
