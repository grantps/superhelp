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

@filt_block_advisor(xpath=NESTING_XPATH, warning=True)
def bloated_nested_block(block_dets, *, repeated_message=False):
    """
    Look for long indented blocks under conditionals, inside loops etc that are
    candidates for separating into functions to simplify the narrative of the
    main code.
    """
    bloated_outer_types = set()
    for lbl, outer_xpath in OUTER_XPATHS.items():
        if has_long_block(block_dets.element, outer_xpath):
            bloated_outer_types.add(lbl)
    if not bloated_outer_types:
        return None
    brief_msg = layout("""\
        
        ### Possible option of replacing long nested block with function call

        """)
    for bloated_outer_type in bloated_outer_types:
        brief_msg += layout(f"""\
            The code has at least one long nested block under
            `{bloated_outer_type}:`
            """)
    if repeated_message:
        main_msg = brief_msg
        extra_msg = ''
    else:  ## Hypocrisy alert LOL - I complain here about excessive nested blocks
        brief_msg += layout("""\

            It may be possible to pull most of the nested code block into a
            function which can be called instead.
            """)
        main_msg = brief_msg
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

                you could possibly write:

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
