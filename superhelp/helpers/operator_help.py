from .. import ast_funcs, conf
from ..gen_utils import layout_comment as layout
from . import any_block_help

op_name2symbol = {
    'Add': '+',
    'Sub': '-',
    'Mult': '*',
    'Div': '/',
    'Mod': '%',
    'FloorDiv': '//',
    'Pow': '**',
    'BitAnd': '&',
    'BitOr': '|',
    'BitXor': '^',
    'RShift': '>>',
    'LShift': '<<',
}

@any_block_help()
def compound_operator_possible(block_dets, *, repeat=False, **_kwargs):
    """
    Look for code like x = x + 1 and suggest the compound operator option.
    """
    block_el = block_dets.element
    assign_els = block_el.xpath('descendant-or-self::Assign')
    if not assign_els:
        return None
    missing_compound = False
    for assign_el in assign_els:
        target_name_els = assign_el.xpath('targets/Name')
        if len(target_name_els) != 1:
            continue
        target_name_el = target_name_els[0]
        target_name = target_name_el.get('id')
        next_name_els = assign_el.xpath('value/BinOp/left/Name')
        if len(next_name_els) != 1:
            continue
        next_name = next_name_els[0].get('id')
        same_name = (target_name == next_name)
        if not same_name:
            continue
        else:
            op_els = assign_el.xpath('value/BinOp/op')
            if len(op_els) != 1:
                raise Exception("Binop didn't have exactly one op")
            op_el = op_els[0]
            op_name = op_el.getchildren()[0].tag
            try:
                op_symbol = op_name2symbol[op_name]
            except KeyError:
                continue
            right_els = assign_el.xpath('value/BinOp/right')
            if len(right_els) != 1:
                raise Exception("BinOp didn't have exactly one value  "
                    "even though a BinOp")
            right_el = right_els[0]
            value_els = right_el.getchildren()  ## might be Constant
            if len(value_els) != 1:
                raise Exception("right didn't have exactly one value even "
                    "though a BinOp")
            val_el = value_els[0]
            result = ast_funcs.val_dets(val_el)
            if result is None:
                raise Exception("Unable to get value from right side of BinOp")
            val, needs_quoting = result

            missing_compound = True
            break
    if not missing_compound:
        return None

    title = layout("""\
    ### Compound operator possible
    """)
    val2go = f'"{val}"' if needs_quoting else val
    brief_msg = layout(f"""\

    `{target_name} = {target_name} {op_symbol} {val2go}` could be replaced
    by `{target_name} {op_symbol}= {val2go}`.
    """)
    if not repeat:
        compound_operators = (
            layout("""\
            Python supports the use of compound operators so the following pairs
            are all equivalent:
            """)
            +
            layout("""\
            x = x + 1
            x += 1

            x = x - 1
            x -= 1

            x = x * 5
            x *= 5
            """, is_code=True)
            + layout("""\
            See more details here:
            <https://www.programiz.com/python-programming/operators>

            `+=` and `-+` are probably the most readable but other compound
            operators become more useful when names used are longer. For example
            the compound versions of the following are arguably cleaner:
            """)
            +
            layout("""\
            eisen_value = eisen_value * 5
            eisen_value *= 5

            eisen_value = eisen_value ** 2
            eisen_value **= 2

            eisen_value = eisen_value \ 10
            eisen_value \= 10
            """, is_code=True)
        )
    else:
        compound_operators = ''

    message = {
        conf.BRIEF: title + brief_msg,
        conf.MAIN: title + brief_msg + compound_operators,
    }
    return message
