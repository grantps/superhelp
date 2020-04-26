from collections import defaultdict

from ..advisors import filt_block_advisor
from ..ast_funcs import get_assign_name
from .. import code_execution, conf
from ..utils import get_nice_str_list, get_python_version,\
    layout_comment as layout

ASSIGN_VAL_XPATH = 'descendant-or-self::Assign/value'

def get_num_els_3_7(block_el):
    num_els = block_el.xpath('descendant-or-self::Assign/value/Num')
    return num_els

def get_num_els_3_8(block_el):
    val_els = block_el.xpath(ASSIGN_VAL_XPATH)
    num_els = []
    for val_el in val_els:
        constant_els = val_el.xpath('Constant') 
        if len(constant_els) != 1:
            continue
        constant_el = constant_els[0]
        if constant_el.get('type') in ('int', 'float'):
            num_els.append(constant_el)
    return num_els

python_version = get_python_version()
if python_version in (conf.PY3_6, conf.PY3_7):
    get_num_els = get_num_els_3_7
elif python_version == conf.PY3_8:
    get_num_els = get_num_els_3_8
else:
    raise Exception(f"Unexpected Python version {python_version}")

@filt_block_advisor(xpath=ASSIGN_VAL_XPATH)
def num_overview(block_dets, *, repeated_message=False):
    """
    Get general advice about assigned numbers e.g. var = 123
    """
    num_els = get_num_els(block_dets.element)
    val_types = defaultdict(list)
    has_num = False
    type_firsts = {}
    for num_el in num_els:
        name = get_assign_name(num_el)
        val = code_execution.get_val(
            block_dets.pre_block_code_str, block_dets.block_code_str, name)
        val_type = type(val).__name__
        val_types[val_type].append(name)
        if not type_firsts.get(val_type):
            type_firsts[val_type] = val
        has_num = True
    if not has_num:
        return None
    brief_comment = ''
    for val_type, names in val_types.items():
        names_text = get_nice_str_list(names, quoter='`')
        if len(names) == 1:
            names_msg = layout(f"""\

                {names_text} is a number - specific type `{val_type}`.
                """)
        else:
            names_msg = layout(f"""\

                {names_text} are numbers - specific type `{val_type}`.
                """)
        brief_comment += names_msg
    if not repeated_message:
        for val_type, names in val_types.items():
            first_name = names[0]
            val = type_firsts[val_type]
            specific_comment = None
            if val_type == conf.INT_TYPE:
                specific_comment = layout(f"""\

                    Integers are counting numbers and include 0 and negative
                    numbers e.g. -2

                    If you need a float instead of an integer use the float
                    function.

                    e.g. float({first_name}) which returns {float(val)}
                    """)
            elif val_type == conf.FLOAT_TYPE:
                specific_comment = layout(f"""\

                    Floats are used when decimal places are required.

                    If you need an integer instead of a float use the int
                    function.

                    e.g. int({name}) which returns {int(val)}
                    """)
            if specific_comment:
                brief_comment += specific_comment
    message = {
        conf.BRIEF: brief_comment,
    }
    if conf.FLOAT_TYPE in val_types and not repeated_message:
        message[conf.EXTRA] = layout(f"""\
            Floats, or floating point numbers, are stored in computers as binary
            fractions. "Unfortunately, most decimal fractions cannot be
            represented exactly as binary fractions. A consequence is that, in
            general, the decimal floating-point numbers you enter are only
            approximated by the binary floating-point numbers actually stored
            in the machine." For more information, read the rest of
            <https://docs.python.org/3/tutorial/floatingpoint.html>. It is
            really interesting - honest!
            """)
    return message
