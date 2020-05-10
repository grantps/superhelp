import logging

from ..advisors import all_blocks_advisor
from .. import conf
from ..utils import get_python_version, layout_comment as layout

def _get_num_3_7(value_el):
    positive_num_els = value_el.xpath('Num')
    if len(positive_num_els) == 1:
        num = positive_num_els[0].get('n')
        if num not in ['0', '1']:
            return None
    else:
        sub_els = value_el.xpath('UnaryOp/op/USub')
        if not sub_els:
            return None
        negative_num_els = value_el.xpath('UnaryOp/operand/Num')
        if len(negative_num_els) != 1:
            return None
        pos_num = negative_num_els[0].get('n')
        if pos_num != '1':
            return None
        num = f'-{pos_num}'
    return num

def _get_num_3_8(value_el):
    positive_num_els = value_el.xpath('Constant')
    if len(positive_num_els) == 1:
        positive_num_el = positive_num_els[0]
        val = positive_num_el.get('value')
        if positive_num_el.get('type') not in ('int', 'float'):
            return None
        if val not in ['0', '1']:
            return None
        num = val
    else:
        sub_els = value_el.xpath('UnaryOp/op/USub')
        if not sub_els:
            return None
        negative_num_els = value_el.xpath('UnaryOp/operand/Constant')
        if len(negative_num_els) != 1:
            return None
        negative_num_el = negative_num_els[0]
        val = negative_num_el.get('value')
        if negative_num_el.get('type') not in ('int', 'float'):
            return None
        if val != '1':
            return None
        num = f'-{val}'
    return num

def _get_var_plus_equalled_all(el):
    plus_equalled_els = el.xpath('descendant-or-self::AugAssign')
    if len(plus_equalled_els) != 1:
        return None
    plus_equalled_el = plus_equalled_els[0]
    target_els = plus_equalled_el.xpath('target/Name')
    if len(target_els) != 1:
        return None
    target = target_els[0].get('id')  ## e.g. 'i' or 'counter' etc
    add_sub_els = plus_equalled_el.xpath('op/Add | op/Sub')  ## only interested in Add / Sub
    if len(add_sub_els) != 1:
        return None
    return target, plus_equalled_el

def _get_var_plus_equalled_3_7(el):
    ok_num = '1'
    res = _get_var_plus_equalled_all(el)
    if res is None:
        return None
    target, plus_equalled_el = res
    num_els = plus_equalled_el.xpath('value/Num')
    if len(num_els) != 1:
        return None
    num = num_els[0].get('n')
    if num != ok_num:
        return None
    var_plus_equalled = target
    return var_plus_equalled

def _get_var_plus_equalled_3_8(el):
    ok_num = '1'
    res = _get_var_plus_equalled_all(el)
    if res is None:
        return None
    target, plus_equalled_el = res
    num_els = plus_equalled_el.xpath('value/Constant')
    if len(num_els) != 1:
        return None
    num_el = num_els[0]
    val = num_el.get('value')
    if num_el.get('type') not in ('int', 'float'):
        return None
    if val != ok_num:
        return None
    var_plus_equalled = target
    return var_plus_equalled

def _get_var_equal_plussed_all(el):
    assign_els = el.xpath('descendant-or-self::Assign')
    if len(assign_els) != 1:
        return None
    assign_el = assign_els[0]
    target_name_els = assign_el.xpath('targets/Name')
    if len(target_name_els) != 1:
        return None
    var_name = target_name_els[0].get('id')
    binop_els = assign_el.xpath('value/BinOp')
    if len(binop_els) != 1:
        return None
    bin_op_el = binop_els[0]
    left_val_els = bin_op_el.xpath('left/Name')
    if len(left_val_els) != 1:
        return None
    left_val = left_val_els[0].get('id')
    if left_val != var_name:  ## we want i = i ... + 1
        return None
    add_els = bin_op_el.xpath('op/Add')
    if len(add_els) != 1:
        return None
    return var_name, bin_op_el

def _get_var_equal_plussed_3_7(el):
    ok_val = '1'
    res = _get_var_equal_plussed_all(el)
    if res is None:
        return None
    var_name, bin_op_el = res
    right_els = bin_op_el.xpath('right/Num')
    if len(right_els) != 1:
        return None
    right_val = right_els[0].get('n')  ## ... + 1
    if right_val != ok_val:
        return None
    var_equal_plussed = var_name
    return var_equal_plussed

def _get_var_equal_plussed_3_8(el):
    ok_val = '1'
    res = _get_var_equal_plussed_all(el)
    if res is None:
        return None
    var_name, bin_op_el = res
    right_els = bin_op_el.xpath('right/Constant')
    if len(right_els) != 1:
        return None
    right_el = right_els[0]
    right_val = right_el.get('value')  ## ... + 1
    if right_el.get('type') not in ('int', 'float'):
        return None
    if right_val != ok_val:
        return None
    var_equal_plussed = var_name
    return var_equal_plussed

python_version = get_python_version()
if python_version in (conf.PY3_6, conf.PY3_7):
    _get_num = _get_num_3_7
    _get_var_plus_equalled = _get_var_plus_equalled_3_7
    _get_var_equal_plussed = _get_var_equal_plussed_3_7
elif python_version == conf.PY3_8:
    _get_num = _get_num_3_8
    _get_var_plus_equalled = _get_var_plus_equalled_3_8
    _get_var_equal_plussed = _get_var_equal_plussed_3_8
else:
    raise Exception(f"Unexpected Python version {python_version}")

def get_num(value_el):
    """
    ## a positive number
    <Assign lineno="1" col_offset="0">
      ...
      <value>
        <Constant lineno="1" col_offset="4" type="int" value="0"/>
      </value>
    </Assign>
    
    ## a negative number
    <Assign lineno="1" col_offset="0">
      ...
      <value>
        <UnaryOp lineno="1" col_offset="4">
          <op>
            <USub/>
          </op>
          <operand>
            <Constant lineno="1" col_offset="5" type="int" value="1"/>
          </operand>
        </UnaryOp>
      </value>
    </Assign>
    """
    return _get_num(value_el)

def get_var_initialised(el):
    """
    e.g. i = 0 or i = -1 or i = 1

    ## example where a positive number
    <Assign lineno="1" col_offset="0">
      <targets>
        <Name lineno="1" col_offset="0" type="str" id="counter">
          <ctx>
            <Store/>
          </ctx>
        </Name>
      </targets>
      <value>
        <Constant lineno="1" col_offset="10" type="int" value="0"/>
      </value>
    </Assign>
    """
    assign_els = el.xpath('descendant-or-self::Assign')
    if not assign_els:
        return None
    has_var_init = False
    for assign_el in assign_els:
        value_els = assign_el.xpath('value')
        if len(value_els) != 1:
            continue
        num = get_num(value_els[0])
        if num is None:
            continue
        name_els = assign_el.xpath('targets/Name')
        if not name_els:
            continue
        name = name_els[0].get('id')
        has_var_init = True
        break
    var_initialised = name if has_var_init else None
    return var_initialised

def get_var_plus_equalled(el):
    """
    e.g. i += 1

    <AugAssign lineno="2" col_offset="0">
      <target>
        <Name lineno="2" col_offset="0" id="counter">
          <ctx>
            <Store/>
          </ctx>
        </Name>
      </target>
      <op>
        <Add/>
      </op>
      <value>
        <Constant lineno="2" col_offset="11" value="1"/>
      </value>
    </AugAssign>
    """
    return _get_var_plus_equalled(el)

def get_var_equal_plussed(el):
    """
    e.g. i = i + 1

    <Assign lineno="4" col_offset="0">
      <targets>
        <Name lineno="4" col_offset="0" id="counter">
          <ctx>
            <Store/>
          </ctx>
        </Name>
      </targets>
      <value>
        <BinOp lineno="4" col_offset="10">
          <left>
            <Name lineno="4" col_offset="10" id="counter">
              <ctx>
                <Load/>
              </ctx>
            </Name>
          </left>
          <op>
            <Add/>
          </op>
          <right>
            <Num lineno="4" col_offset="20" n="1"/>
          </right>
        </BinOp>
      </value>
    </Assign>
    """
    return _get_var_equal_plussed(el)

def get_var_incremented(el):
    """
    e.g. i += 1 or i = i + 1
    """
    var_incremented = get_var_plus_equalled(el)
    if not var_incremented:
        var_incremented = get_var_equal_plussed(el)
    return var_incremented

def process_el(el, vars_initialised, vars_incremented):
    """
    Look for either init or incrementing.

    Update vars_init set and, if var already in init set, in
    vars_incremented set. Once anything in vars_incremented set, return
    because we only need one. If neither, get children and process down each
    path. Then return.
    """
    var_initialised = get_var_initialised(el)
    if var_initialised:
        vars_initialised.add(var_initialised)
    var_incremented = get_var_incremented(el)
    if var_incremented:
        if var_incremented in vars_initialised:
            vars_incremented.add(var_incremented)
            return
    for child_el in el.getchildren():
        process_el(child_el, vars_initialised, vars_incremented)
    return

def get_incrementing_var(block_dets, vars_initialised, vars_incremented):
    """
    Iterate through lines in AST (depth first). Look for var init and once
    found, then incrementing. On first init-incrementing pair found, halt and
    give message about enumerate using the var name in example.
    """
    process_el(block_dets.element, vars_initialised, vars_incremented)
    if not vars_incremented:
        incrementing_var = None
    else:
        incrementing_var = vars_incremented.pop()
    return incrementing_var

@all_blocks_advisor()
def manual_incrementing(blocks_dets):
    """
    Look for manual handling of incrementing inside loops.
    """
    vars_initialised = set()
    vars_incremented = set()
    has_incrementing = False
    for block_dets in blocks_dets:
        incrementing_var = get_incrementing_var(
            block_dets, vars_initialised, vars_incremented)
        logging.debug(f"vars_initialised: {vars_initialised}; "
            f"vars_incremented: {vars_incremented}")
        if incrementing_var:
            has_incrementing = True
            break
    if not has_incrementing:
        return None

    summary = layout(f"""\
    ### Possible option of using `enumerate()`

    It looks like your code is manually incrementing `{incrementing_var}`. In
    Python you can use the `enumerate` function to handle this for you.
    """)
    demo = (
        layout("""\
        Here is an example of the manual approach:
        """)
        +
        layout("""\
        n = 1
        for image in images:
            if n % 10 == 0:
                print(f"Just processed image {{n}}")
            process_image(image)
            n += 1
        """, is_code=True)
        +
        layout("""\
        Here is how we can use `enumerate()` instead:
        """)
        +
        layout("""\
        for n, image in enumerate(images, 1):
            if n % 10 == 0:
                print(f"Just processed image {{n}}")
            process_image(image)
        """, is_code=True)
        +
        layout("""\

        Often you want counting from 0 in which case you don't need to specify
        the start value (0 is the default):
        """)
        +
        layout("""\
        for i, image in enumerate(images):
            ...
        """, is_code=True)
        +
        layout("""\

        You can give the enumerated value any name that makes sense but reserve
        `i` for incrementing starting at 0 and prefer `n` when starting at 1.
        """)
    )

    message = {
        conf.BRIEF: summary,
        conf.MAIN: summary + demo,
    }
    return message
