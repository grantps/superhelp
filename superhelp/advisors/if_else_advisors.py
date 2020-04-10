from ..advisors import type_block_advisor
from .. import conf
from ..utils import int2nice, layout_comment

ELIF = 'elif'
ELSE = 'else'

def add_if_details(if_element, if_details):
    """
    If under our <If>s <orelse> we have another <If> store an 'elif' in if_details
    and send the <If> under <orelse> through again; otherwise store an 'else'
    in if_details and return.

    <If>s have <orelse>s which either have <If>s or not. When there is not then
    we have reached else.
    """
    orelse_has_children = bool(if_element.xpath('orelse')[0].getchildren())  ## always has one but if merely an <If> has no children under orelse
    if not orelse_has_children:
        return
    try:
        if_element_under_if = if_element.xpath('orelse/If')[0]
        has_elif = True
    except IndexError:
        has_elif = False
    if has_elif:
        if_details.append(ELIF)
        add_if_details(if_element_under_if, if_details)
    else:
        if_details.append(ELSE)
    return

def get_if_details(block_dets):
    if_element = block_dets.element
    if_details = []
    add_if_details(if_element, if_details)
    multiple_conditions = bool(if_details)
    if multiple_conditions:
        last_sub_if = if_details[-1]
        missing_else = (last_sub_if != ELSE)
    else:
        missing_else = False
    return multiple_conditions, missing_else, if_details

@type_block_advisor(element_type=conf.IF_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY)
def if_else_overview(block_dets):
    multiple_conditions, missing_else, if_details = get_if_details(block_dets)
    if multiple_conditions:
        n_elifs = if_details.count(ELIF)
        brief_comment = (f"""\
            Detected an `If` statement with {int2nice(n_elifs)} `elif` clauses
            """)
        if missing_else:
            brief_comment += " and no `else` clause."
        else:
            brief_comment += " and an `else` clause."
    else:
        brief_comment = ("""\
            Simple `If` statement detected.
            """)
    message = {
        conf.BRIEF: (
            layout_comment(f"""\
                ##### Conditional statement detected

                """)
            +
            layout_comment(brief_comment)
        ),
        conf.MAIN: (
            layout_comment(f"""\
                ##### Conditional statement detected

                """)
            +
            layout_comment(brief_comment)
            +
            layout_comment("""\

                When using `if`, `elif`, or `else`, the item evaluated can
                either be an expression or a name (variable). Sometimes your
                code can be more readable if the expression is precalculated and
                a name is supplied instead. For example:

                """)
            +
            layout_comment("""\
                if length_matters and len(phrase) > conf.MAX_SANE_LENGTH:
                    phrase = chop(phrase)
                """, is_code=True)
            +
            layout_comment("""\

                vs

                """)
            +
            layout_comment("""\
                too_long = length_matters and len(phrase) > conf.MAX_SANE_LENGTH
                if too_long:
                    phrase = chop(phrase)
                """, is_code=True)
        ),
    }
    return message

@type_block_advisor(element_type=conf.IF_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY, warning=True)
def missing_else(block_dets):
    _multiple_conditions, missing_else, _if_details = get_if_details(block_dets)
    if not missing_else:
        return None
    message = {
        conf.BRIEF: layout_comment("""\
            #### Missing else clause

            It is almost best to include an else clause if there are elif
            clauses.
            """),
        conf.MAIN: (
            layout_comment("""\
                #### Missing else clause
    
                It is almost best to include an `else` clause if there are
                `elif` clauses. You may have left out the `else` because it is
                currently impossible that this branch will ever be called. You
                know that you can only receive the items currently handled by
                the `elif`s so `else` can logically never be called. And that it
                true - until it isn't later ;-) - for example, if the calling
                code starts supplying more types of whatever is being evaluated
                in the `elif`s. This problem happens surprisingly often and can
                create nasty bugs that are hard to trace. If you add an `else`
                clause that raises an exception you will instantly know if the
                expected conditions for your conditional are breached and
                exactly what to fix.
    
                For example:
    
                """)
            +
            layout_comment("""\
                ## At the point this code is written we absolutely know
                ## there are only two user types: managers and staff

                if user == 'manager':
                    create_alert()
                    set_up_manager(user)
                elif user == 'staff':
                    set_up_staff(user)
                else:
                    ## This can logically never happen so
                    ## we might be tempted to leave out the else clause
                    pass
                """, is_code=True)
            +
            layout_comment("""\

                But then a new user type is created (e.g. admin) and the logic
                of the entire program breaks all over the place with no clarity
                about the real source.

                It would be better to have an `else` clause as follows so you
                know exactly what violated the program's assumptions:

                """)
            +
            layout_comment("""\
                else:
                    raise Exception(f"Unexpected user: '{user}'")
                """, is_code=True)
        )
    }
    return message
