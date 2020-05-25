
def val_dets_3_7(val_el):
    """
    val_el is the element under value e.g. Constant (3.8+) or Str, Num (<3.8)
    """
    raw_val = val_el.get('s')
    if raw_val:
        val = raw_val
        needs_quoting = True
    else:
        raw_val = val_el.get('n')
        if raw_val:
            val = float(raw_val)  ## 1 and 1.0 are the same val when a key in a dict
            needs_quoting = False
        else:
            return None
    return val, needs_quoting

def val_dets_3_8(val_el):
    """
    As per 3_7 version
    """
    const_type = val_el.get('type')
    if not const_type:
        return None
    raw_val = val_el.get('value')
    if const_type == 'int':
        val = int(raw_val)
        needs_quoting = False
    elif const_type == 'float':
        val = float(raw_val)
        needs_quoting = False
    elif const_type == 'str':
        val = raw_val
        needs_quoting = True
    else:
        return None
    return val, needs_quoting

## nums ******************************

def assigned_num_els_from_block_3_7(block_el):
    num_els = block_el.xpath('descendant-or-self::Assign/value/Num')
    return num_els

def assigned_num_els_from_block_3_8(block_el):
    val_els = block_el.xpath('descendant-or-self::Assign/value')
    num_els = []
    for val_el in val_els:
        constant_els = val_el.xpath('Constant')
        if len(constant_els) != 1:
            continue
        constant_el = constant_els[0]
        if constant_el.get('type') in ('int', 'float'):
            num_els.append(constant_el)
    return num_els

def num_str_from_val_3_7(val_el):
    """
    As for 3_8 version but Num / Str instead of Constant etc.
    """
    positive_num_els = val_el.xpath('Num')
    if len(positive_num_els) == 1:
        num = positive_num_els[0].get('n')
    else:
        sub_els = val_el.xpath('UnaryOp/op/USub')
        if not sub_els:
            return None
        negative_num_els = val_el.xpath('UnaryOp/operand/Num')
        if len(negative_num_els) != 1:
            return None
        pos_num = negative_num_els[0].get('n')
        num = f'-{pos_num}'
    return num

def num_str_from_val_3_8(val_el):
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
    positive_num_els = val_el.xpath('Constant')
    if len(positive_num_els) == 1:
        positive_num_el = positive_num_els[0]
        val = positive_num_el.get('value')
        if positive_num_el.get('type') not in ('int', 'float'):
            return None
        num = val
    else:
        sub_els = val_el.xpath('UnaryOp/op/USub')
        if not sub_els:
            return None
        negative_num_els = val_el.xpath('UnaryOp/operand/Constant')
        if len(negative_num_els) != 1:
            return None
        negative_num_el = negative_num_els[0]
        val = negative_num_el.get('value')
        if negative_num_el.get('type') not in ('int', 'float'):
            return None
        num = f'-{val}'
    return num

def num_str_from_el_3_7(comparison_el):
    num = comparison_el.get('n')
    if not num:
        return None
    return num

def num_str_from_el_3_8(comparison_el):
    val = comparison_el.get('value')
    if comparison_el.get('type') in ('int', 'float'):
        num = val
    else:
        num = None
    return num

## strs ******************************

def str_from_el_3_7(el):
    string = el.get('s')
    if not string:
        return None
    return string

def str_from_el_3_8(el):
    val = el.get('value')
    if el.get('type') == 'str':
        string = val
    else:
        string = None
    return string

def assigned_str_els_from_block_3_7(block_el):
    str_els = block_el.xpath('descendant-or-self::Assign/value/Str')
    return str_els

def assigned_str_els_from_block_3_8(block_el):
    assign_val_els = block_el.xpath('descendant-or-self::Assign/value')
    str_els = []
    for assign_val_el in assign_val_els:
        assign_str_els = assign_val_el.xpath('Constant')
        if len(assign_str_els) != 1:
            continue
        assign_str_el = assign_str_els[0]
        if assign_str_el.get('type') == 'str':
            str_els.append(assign_str_el)
    return str_els

def str_els_from_block_3_7(block_el):
    str_els = block_el.xpath('descendant-or-self::Str')
    return str_els

def str_els_from_block_3_8(block_el):
    constant_els = block_el.xpath('descendant-or-self::Constant')
    str_els = [constant_el for constant_el in constant_els
        if constant_el.get('type') == 'str']
    return str_els

## dict keys ******************************

def dict_key_from_subscript_3_7(subscript_el):
    key_els = subscript_el.xpath(
        'slice/Index/value/Num | slice/Index/value/Str')
    if len(key_els) != 1:
        return None
    key_el = key_els[0]
    return val_dets_3_7(val_el=key_el)

def dict_key_from_subscript_3_8(subscript_el):
    key_els = subscript_el.xpath('slice/Index/value/Constant')
    if len(key_els) != 1:
        return None
    key_el = key_els[0]
    return val_dets_3_8(val_el=key_el)

## other ******************************

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
    """
    As for 3_8 version but Num / Str vs Constant etc.
    """
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
    """
    e.g. i if i += 1

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
    """
    e.g. i if i = i + 1

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
    """
    As for 3_7 version but Constant instead of Num / Str etc.
    """
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

def get_danger_status_3_7(child_el):
    if (child_el.tag == 'NameConstant'
            and child_el.get('value') in ['True', 'False']):
        danger_status = 'Boolean'
    elif child_el.tag == 'Num' and child_el.get('n'):
        danger_status = 'Number'
    else:
        danger_status = None
    return danger_status

def get_danger_status_3_8(child_el):
    if child_el.tag == 'Constant':
        val = child_el.get('value')
        if val in ['True', 'False']:
            danger_status = 'Boolean'
        else:
            try:
                float(val)
            except TypeError:
                danger_status = None
            else:
                danger_status = 'Number'
    else:
        danger_status = None
    return danger_status

def get_docstring_from_value_3_7(first_value_el):
    if first_value_el.tag != 'Str':
        docstring = None
    else:
        docstring = first_value_el.get('s')
    return docstring

def get_docstring_from_value_3_8(first_value_el):
    if first_value_el.tag != 'Constant':
        docstring = None
    elif first_value_el.get('type') != 'str':
        docstring = None
    else:
        docstring = first_value_el.get('value')
    return docstring

def get_slice_dets_3_7(assign_subscript_el):
    """
    Get slice dets e.g. '[2]', '[-1]' or '["NZ"]'. Only interested in numbers or
    strings. If the person is doing something funky they'll miss out on learning
    about names and values.
    """
    val_els = assign_subscript_el.xpath('slice/Index/value')
    if len(val_els) != 1:
        return None
    val_el = val_els[0]
    num_str = num_str_from_val_3_7(val_el)
    if num_str:
        slice_dets = slice_dets = f'[{num_str}]'
    else:
        slice_str_els = assign_subscript_el.xpath('slice/Index/value/Str')
        if slice_str_els:
            slice_str = slice_str_els[0].get('s')
            slice_dets = f'["{slice_str}"]'
        else:
            raise Exception("Unable to get slice_dets")
    return slice_dets

def get_slice_dets_3_8(assign_subscript_el):
    """
    As for get_slice_dets_3_7.
    """
    val_els = assign_subscript_el.xpath('slice/Index/value')
    if len(val_els) != 1:
        return None
    val_el = val_els[0]
    num_str = num_str_from_val_3_8(val_el)
    if num_str:
        slice_dets = slice_dets = f'[{num_str}]'
    else:
        val_constant_els = val_el.xpath('Constant')
        if len(val_constant_els) != 1:
            raise Exception("Unable to get slice_dets")
        val_constant_el = val_constant_els[0]
        val_type = val_constant_el.get('type')
        if val_type == 'str':
            slice_str = val_constant_el.get('value')
            slice_dets = f'["{slice_str}"]'
        else:
            raise Exception("Unable to get slice_dets")
    return slice_dets

def _get_nt_lbl_flds_any(assign_block_el, tag='Constant', id_attr='value'):
    """
    Either two strs
      e.g. 'DataDets', 'a, b, c'
    OR a Constant/Str and list of n Constant/Strs
      e.g. 'DataDets', ['a', 'b', 'c']
    OR a Constant/Str and a tuple of n Constants/Strs
      e.g. 'DataDets', ('a', 'b', 'c')
    """
    args_els = assign_block_el.xpath('value/Call/args')
    if len(args_els) != 1:
        raise Exception("Expected only one args el for named tuple")
    args_el = args_els[0]
    label_el, fields_el = args_el.getchildren()
    label = label_el.get(id_attr)
    field_el_type = fields_el.tag
    if field_el_type == tag:
        fields_str = fields_el.get(id_attr)
        fields_list = [field.strip() for field in fields_str.split(',')]
    elif field_el_type in ('Tuple', 'List'):
        field_els = fields_el.xpath(f'elts/{tag}')
        fields_list = [el.get(id_attr) for el in field_els]
    return label, fields_list

def get_nt_lbl_flds_3_7(assign_block_el):
    return _get_nt_lbl_flds_any(assign_block_el, tag='Str', id_attr='s')

def get_nt_lbl_flds_3_8(assign_block_el):
    return _get_nt_lbl_flds_any(
        assign_block_el, tag='Constant', id_attr='value')

def get_slice_n_3_7(assign_el):
    slice_n = assign_el.xpath(
        'value/Subscript/slice/Index/value/Num')[0].get('n')
    return slice_n

def get_slice_n_3_8(assign_el):
    val_els = assign_el.xpath('value/Subscript/slice/Index/value/Constant')
    val_el = val_els[0]
    if val_el.get('type') in ('int', 'float'):
        slice_n = val_el.get('value')
    else:
        raise TypeError("slice index value not an int or a float - actual type "
            f"'{val_el.get('type')}'")
    return slice_n

def get_str_els_being_combined_3_7(block_el):
    str_els_being_combined = block_el.xpath(
        'descendant-or-self::BinOp/left/Str')
    return str_els_being_combined

def get_str_els_being_combined_3_8(block_el):
    left_str_els = block_el.xpath('descendant-or-self::BinOp/left/Constant')
    str_els_being_combined = []
    for left_str_el in left_str_els:
        if left_str_el.get('type') == 'str':
            str_els_being_combined.append(left_str_el)
    return str_els_being_combined
