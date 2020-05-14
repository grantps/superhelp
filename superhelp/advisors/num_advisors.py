from collections import defaultdict

from ..advisors import filt_block_advisor
from ..ast_funcs import get_assigned_name, assigned_num_els_from_block
from .. import code_execution, conf
from ..utils import get_nice_str_list, layout_comment as layout

ASSIGN_VAL_XPATH = 'descendant-or-self::Assign/value'

@filt_block_advisor(xpath=ASSIGN_VAL_XPATH)
def num_overview(block_dets, *, repeat=False):
    """
    Get general advice about assigned numbers e.g. var = 123
    """
    num_els = assigned_num_els_from_block(block_dets.element)
    val_types = defaultdict(list)
    has_num = False
    type_firsts = {}
    for num_el in num_els:
        name_dets = get_assigned_name(num_el)
        try:
            val = code_execution.get_val(
                block_dets.pre_block_code_str, block_dets.block_code_str,
                name_dets.name_type, name_dets.name_details, name_dets.name_str)
        except KeyError:
            continue
        else:
            val_type = type(val).__name__
            val_types[val_type].append(name_dets.name_str)
            if not type_firsts.get(val_type):
                type_firsts[val_type] = val
            has_num = True
    if not has_num:
        return None

    title = layout("""\
    ### Number details
    """)
    names_msg_bits = []
    for val_type, names in val_types.items():
        names_text = get_nice_str_list(names, quoter='`')
        if len(names) == 1:
            names_msg_bits.append(layout(f"""\

            {names_text} is a number - specific type `{val_type}`.
            """))
        else:
            names_msg_bits.append(layout(f"""\

            {names_text} are numbers - specific type `{val_type}`.
            """))
    names_msg = ''.join(names_msg_bits)
    if not repeat:
        specifics_bits = []
        for val_type, names in val_types.items():
            first_name = names[0]
            val = type_firsts[val_type]
            specific_comment = None
            if val_type == conf.INT_TYPE:
                specific_comment = layout(f"""\

                Integers are counting numbers and include 0 and negative numbers
                e.g. -2

                If you need a float instead of an integer use the float
                function.

                e.g. float({first_name}) which returns {float(val)}
                """)
            elif val_type == conf.FLOAT_TYPE:
                specific_comment = layout(f"""\

                Floats are used when decimal places are required.

                If you need an integer instead of a float use the int function.

                e.g. int({first_name}) which returns {int(val)}
                """)
            if specific_comment:
                specifics_bits.append(specific_comment)
        specifics = ''.join(specifics_bits)
        if conf.FLOAT_TYPE in val_types:
            floats = layout(f"""\

            Floats, or floating point numbers, are stored in computers as binary
            fractions. "Unfortunately, most decimal fractions cannot be
            represented exactly as binary fractions. A consequence is that, in
            general, the decimal floating-point numbers you enter are only
            approximated by the binary floating-point numbers actually stored in
            the machine." For more information, read the rest of
            <https://docs.python.org/3/tutorial/floatingpoint.html>. It is
            really interesting - honest!
            """)
        else:
            floats = ''
    else:
        specifics = ''
        floats = ''

    message = {
        conf.BRIEF: title + names_msg + specifics,
        conf.EXTRA: floats,
    }
    return message
