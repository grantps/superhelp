from textwrap import dedent

from ..advisors import filt_block_advisor
from .. import ast_funcs, code_execution, conf

def int_message(name, val):
    message = {
        conf.BRIEF: dedent(f"""\
            Integers are counting numbers and include 0 and negative numbers
            e.g. -2

            If you need a float instead of an integer use the float function

            e.g. float({name}) which returns {float(val)}""")
    }
    return message

def float_message(name, val):
    message = {
        conf.BRIEF: dedent(f"""\
            Floats are used when decimal places are required.

            If you need an integer instead of a float use the int function

            e.g. int({name}) which returns {int(val)}"""),
        conf.EXTRA: dedent(f"""\
            Floats, or floating point numbers, are stored in computers as binary
            fractions. "Unfortunately, most decimal fractions cannot be
            represented exactly as binary fractions. A consequence is that, in
            general, the decimal floating-point numbers you enter are only
            approximated by the binary floating-point numbers actually stored
            in the machine." For more information, read the rest of
            https://docs.python.org/3/tutorial/floatingpoint.html. It is really
            interesting - honest!
            """)
    }
    return message

TYPE2FUNC = {
    conf.INT_TYPE: int_message,
    conf.FLOAT_TYPE: float_message,
}

@filt_block_advisor(xpath='body/Assign/value/Num')
def num_overview(block_dets):
    """
    Get general advice about assigned numbers e.g. var = 123
    """
    name = ast_funcs.get_assigned_name(block_dets.element)
    if not name:
        return None
    val = code_execution.get_val(
        block_dets.pre_block_code_str, block_dets.block_code_str, name)
    val_type = type(val).__name__
    message_func = TYPE2FUNC[val_type]
    message = message_func(name, val)
    return message
