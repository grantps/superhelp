from superhelp.ast_funcs import versioned_nums as nums
from superhelp.utils import inspect_el

def val_dets(val_el):
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

## strs ******************************

def str_from_el(el):
    val = el.get('value')
    if el.get('type') == 'str':
        string = val
    else:
        string = None
    return string

def assigned_str_els_from_block(block_el):
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

def str_els_from_block(block_el):
    constant_els = block_el.xpath('descendant-or-self::Constant')
    str_els = [constant_el for constant_el in constant_els
        if constant_el.get('type') == 'str']
    return str_els

## dict keys ******************************

def dict_key_from_subscript(subscript_el):
    key_els = subscript_el.xpath('slice/Constant')
    if len(key_els) != 1:
        return None
    key_el = key_els[0]
    return val_dets(val_el=key_el)

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

def _get_var_plus_equalled(el):
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

def _get_var_equal_plussed(el):
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

def get_danger_status(child_el):
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

def get_docstring_from_value(first_value_el):
    if first_value_el.tag != 'Constant':
        docstring = None
    elif first_value_el.get('type') != 'str':
        docstring = None
    else:
        docstring = first_value_el.get('value')
    return docstring

def get_slice_dets(assign_subscript_el):
    val_els = assign_subscript_el.xpath('slice/Index/value')
    if len(val_els) != 1:
        return None
    val_el = val_els[0]
    num_str = nums.num_str_from_parent_el(val_el)
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

def get_nt_lbl_flds(assign_block_el):
    return _get_nt_lbl_flds_any(
        assign_block_el, tag='Constant', id_attr='value')

def get_slice_n(assign_el):
    # inspect_el(assign_el)
    val_els = assign_el.xpath('value/Subscript/slice/Constant')
    val_el = val_els[0]
    if val_el.get('type') in ('int', 'float'):
        slice_n = val_el.get('value')
    else:
        raise TypeError("slice index value not an int or a float - actual type "
            f"'{val_el.get('type')}'")
    return slice_n

def get_str_els_being_combined(block_el):
    left_str_els = block_el.xpath('descendant-or-self::BinOp/left/Constant')
    str_els_being_combined = []
    for left_str_el in left_str_els:
        if left_str_el.get('type') == 'str':
            str_els_being_combined.append(left_str_el)
    return str_els_being_combined
