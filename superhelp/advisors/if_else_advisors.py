from collections import namedtuple

from ..advisors import filt_block_advisor
from .. import conf
from ..utils import int2nice, layout_comment

IfDets = namedtuple('IfDetails',
    'multiple_conditions, missing_else, if_clauses')

ELIF = 'elif'
ELSE = 'else'

def add_if_details(if_element, if_clauses):
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
        if_clauses.append(ELIF)
        add_if_details(if_element_under_if, if_clauses)
    else:
        if_clauses.append(ELSE)
    return

def get_ifs_details(block_dets):
    """
    There can be multiple if statements in a snippet so we have to handle each
    of them.
    """
    ## skip when if __name__ == '__main__'
    if block_dets.block_code_str.startswith("if __name__ == "):
        return []
    if_elements = block_dets.element.xpath('If')
    ifs_details = []
    for if_element in if_elements:
        if_clauses = []
        add_if_details(if_element, if_clauses)
        multiple_conditions = bool(if_clauses)
        if multiple_conditions:
            last_sub_if = if_clauses[-1]
            missing_else = (last_sub_if != ELSE)
        else:
            missing_else = False
        ifs_details.append(IfDets(multiple_conditions, missing_else, if_clauses))
    return ifs_details

def _get_if_comment(ifs_details):
    """
    Have to cope with multiple if statements and make it nice (unnumbered) when
    only one.
    """
    brief_comment = ''
    for n, if_details in enumerate(ifs_details, 1):
        counter = '' if len(ifs_details) == 1 else f" {int2nice(n)}"
        if if_details.multiple_conditions:
            n_elifs = if_details.if_clauses.count(ELIF)
            brief_comment += (f"""\

                `if` statement{counter} has {int2nice(n_elifs)} `elif`
                clauses
                """)
            if if_details.missing_else:
                brief_comment += " and no `else` clause."
            else:
                brief_comment += " and an `else` clause."
        else:
            brief_comment += (f"""\

                `if` statement{counter} has no extra conditions.
                """)
    return brief_comment

@filt_block_advisor(xpath='//If')
def if_else_overview(block_dets):
    """
    Look at conditional statements using if (apart from if __name__ ==
    '__main__").
    """
    ## skip when if __name__ == '__main__'
    if block_dets.block_code_str.startswith("if __name__ == "):
        return None
    ifs_details = get_ifs_details(block_dets)
    brief_comment = _get_if_comment(ifs_details)
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

@filt_block_advisor(xpath='//If', warning=True)
def missing_else(block_dets):
    """
    Warn about benefits in many cases of adding else clause if missing.
    """
    ifs_details = get_ifs_details(block_dets)
    brief_comment = ''
    for n, if_details in enumerate(ifs_details, 1):
        counter = '' if len(ifs_details) == 1 else f" {int2nice(n)}"
        if if_details.missing_else:
            brief_comment += (f"`if` block{counter} has `elif` clauses but "
                "lacks an `else` clause. It is often best to include an "
                "`else` clause when there are `elif` clauses.")
    if not brief_comment:
        return None
    brief_comment = "#### Missing `else` clause\n\n" + brief_comment
    message = {
        conf.BRIEF: layout_comment(brief_comment),
        conf.MAIN: (
            layout_comment(brief_comment)
            +
            layout_comment("""\

                You may have left out the `else` because it is currently
                impossible that this branch will ever be called. You know that
                you can only receive the items currently handled by the `elif`s
                so `else` can logically never be called. And that it true -
                until it isn't later ;-) - for example, if the calling code
                starts supplying more types of whatever is being evaluated in
                the `elif`s. This problem happens surprisingly often and can
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
