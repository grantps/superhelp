from collections import namedtuple

from . import conf
from .utils import get_python_version

AssignedNameDets = namedtuple('AssignedNameDets',
    'name_type, name_details, name_str, unpacking_idx')

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

def num_str_from_val_3_7(value_el):
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

def num_str_from_val_3_8(value_el):
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
    raw_val_els = key_el.get('s')
    if len(raw_val_els) == 1:
        key = raw_val_els[0]
        needs_quoting = True
    else:
        raw_val_els = key_el.get('n')
        if len(raw_val_els) == 1:
            key = float(raw_val_els[0])  ## 1 and 1.0 are the same key
            needs_quoting = False
        else:
            return None
    return key, needs_quoting

def dict_key_from_subscript_3_8(subscript_el):
    key_els = subscript_el.xpath('slice/Index/value/Constant')
    if len(key_els) != 1:
        return None
    key_el = key_els[0]
    const_type = key_el.get('type')
    raw_val = key_el.get('value')
    if const_type == 'int':
        key = int(raw_val)
        needs_quoting = False
    elif const_type == 'float':
        key = float(raw_val)
        needs_quoting = False
    elif const_type == 'str':
        key = raw_val
        needs_quoting = True
    else:
        return None
    return key, needs_quoting

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
    Get slice dets e.g. '[2]' or '["NZ"]'. Only interested in numbers or
    strings. If the person is doing something funky they'll miss out on learning
    about names and values.
    """
    slice_n_els = assign_subscript_el.xpath('slice/Index/value/Num')
    if slice_n_els:
        slice_n = slice_n_els[0].get('n')
        slice_dets = f'[{slice_n}]'
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
    val_els = assign_subscript_el.xpath('slice/Index/value/Constant')
    val_el = val_els[0]
    val_type = val_el.get('type')
    if val_type in ('int', 'float'):
        slice_n = val_el.get('value')
        slice_dets = f'[{slice_n}]'
    elif val_type == 'str':
        slice_str = val_el.get('value')
        slice_dets = f'["{slice_str}"]'
    return slice_dets

def get_lbl_flds_3_7(assign_block_el):
    label_el, fields_el = assign_block_el.xpath('value/Call/args/Str')
    label = label_el.get('s')
    fields_str = fields_el.get('s')
    return label, fields_str

def get_lbl_flds_3_8(assign_block_el):
    label_el, fields_el = assign_block_el.xpath('value/Call/args/Constant')
    label = label_el.get('value')
    fields_str = fields_el.get('value')
    return label, fields_str

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

## when backward compatibility with 3.6 can be dropped use def __getattr__(name):
## https://stackoverflow.com/questions/2447353/getattr-on-a-module
python_version = get_python_version()
if python_version in (conf.PY3_6, conf.PY3_7):

    assigned_num_els_from_block = assigned_num_els_from_block_3_7
    num_str_from_val = num_str_from_val_3_7
    num_str_from_el = num_str_from_el_3_7

    assigned_str_els_from_block = assigned_str_els_from_block_3_7
    str_from_el = str_from_el_3_7
    str_els_from_block = str_els_from_block_3_7

    dict_key_from_subscript = dict_key_from_subscript_3_7

    _get_var_plus_equalled = _get_var_plus_equalled_3_7
    _get_var_equal_plussed = _get_var_equal_plussed_3_7
    get_danger_status = get_danger_status_3_7

    get_docstring_from_value = get_docstring_from_value_3_7
    get_slice_dets = get_slice_dets_3_7
    get_lbl_flds = get_lbl_flds_3_7
    get_slice_n = get_slice_n_3_7
    get_str_els_being_combined = get_str_els_being_combined_3_7
elif python_version == conf.PY3_8:
    assigned_num_els_from_block = assigned_num_els_from_block_3_8
    num_str_from_val = num_str_from_val_3_8
    num_str_from_el = num_str_from_el_3_8

    assigned_str_els_from_block = assigned_str_els_from_block_3_8
    str_from_el = str_from_el_3_8
    str_els_from_block = str_els_from_block_3_8

    dict_key_from_subscript = dict_key_from_subscript_3_8

    _get_var_plus_equalled = _get_var_plus_equalled_3_8
    _get_var_equal_plussed = _get_var_equal_plussed_3_8
    get_danger_status = get_danger_status_3_8
    get_docstring_from_value = get_docstring_from_value_3_8
    get_slice_dets = get_slice_dets_3_8
    get_lbl_flds = get_lbl_flds_3_8
    get_slice_n = get_slice_n_3_8
    get_str_els_being_combined = get_str_els_being_combined_3_8
else:
    raise Exception(f"Unexpected Python version {python_version}")

## =============================================================================

def _std_name_dets_from_std_name_el(std_name_el, unpacking_idx=None):
    name_str = std_name_el.get('id')
    name_details = [name_str, ]
    name_type = conf.STD_NAME
    return AssignedNameDets(name_type, name_details, name_str, unpacking_idx)

def _std_name_dets_from_assign_el(assign_el):
    std_name_els = assign_el.xpath('targets/Name')
    if len(std_name_els) != 1:
        return None
    std_name_el = std_name_els[0]
    std_name_dets = _std_name_dets_from_std_name_el(std_name_el)
    return std_name_dets

def _obj_attr_name_dets_from_attribute_el(attribute_el, unpacking_idx=None):
    attribute_name = attribute_el.get('attr')
    obj_name_els = attribute_el.xpath('value/Name')
    if len(obj_name_els) != 1:
        return None
    obj_name_el = obj_name_els[0]
    obj_only_name = obj_name_el.get('id')
    name_str = f"{obj_only_name}.{attribute_name}"
    name_details = [obj_only_name, attribute_name]
    name_type = conf.OBJ_ATTR_NAME
    return AssignedNameDets(name_type, name_details, name_str, unpacking_idx)

def _obj_attr_name_dets_from_assign_el(assign_el):
    """
    The target name is the attribute of an object.
    """
    attribute_els = assign_el.xpath('targets/Attribute')
    if len(attribute_els) != 1:
        return None
    attribute_el = attribute_els[0]
    return _obj_attr_name_dets_from_attribute_el(attribute_el)

def _dict_key_name_dets_from_subscript_el(subscript_el, unpacking_idx=None):
    dict_name_els = subscript_el.xpath('value/Name')
    if len(dict_name_els) != 1:
        return None
    dict_name_el = dict_name_els[0]
    dict_name = dict_name_el.get('id')
    dict_key, needs_quoting = dict_key_from_subscript(subscript_el)
    quoter = '"' if needs_quoting else ''
    name_str = f"{dict_name}[{quoter}{dict_key}{quoter}]"
    name_details = [dict_name, dict_key]
    name_type = conf.DICT_KEY_NAME
    return AssignedNameDets(name_type, name_details, name_str, unpacking_idx)

def _dict_key_name_dets_from_assign_el(assign_el):
    """
    The target name is the key of a dictionary.
    """
    subscript_els = assign_el.xpath('targets/Subscript')
    if len(subscript_els) != 1:
        return None
    subscript_el = subscript_els[0]
    return _dict_key_name_dets_from_subscript_el(subscript_el)

def _tuple_names_dets_from_assign_el(assign_el):
    """
    The target names are in a tuple.
    """
    tuple_els = assign_el.xpath('targets/Tuple')
    if len(tuple_els) != 1:
        return None
    tuple_el = tuple_els[0]
    tuple_elts = tuple_el.getchildren()[0]
    tuple_item_els = tuple_elts.getchildren()
    tuple_names_dets = []
    for unpacking_idx, tuple_item_el in enumerate(tuple_item_els):
        if tuple_item_el.tag == 'Name':
            std_name_dets = _std_name_dets_from_std_name_el(
                std_name_el=tuple_item_el, unpacking_idx=unpacking_idx)
            tuple_names_dets.append(std_name_dets)
        elif tuple_item_el.tag == 'Attribute':
            obj_attr_name_dets = _obj_attr_name_dets_from_attribute_el(
                attribute_el=tuple_item_el, unpacking_idx=unpacking_idx)
            tuple_names_dets.append(obj_attr_name_dets)
        elif tuple_item_el.tag == 'Subscript':
            dict_key_name_dets = _dict_key_name_dets_from_subscript_el(
                subscript_el=tuple_item_el, unpacking_idx=unpacking_idx)
            tuple_names_dets.append(dict_key_name_dets)
    return tuple_names_dets

def get_assigned_names(element):
    """
    Get name assignment associated with the element. The element might be the
    value or the target or something but we just want to identify the closest
    Assign ancestor and get its Name.

    Raise Exception if not found.

    If Assign appears more than once in the ancestral chain e.g.
    body-Assign-spam-eggs-Assign-targets-Name then we get a list like this:
    [body-Assign, body-Assign-spam-eggs-Assign] and we want the closest one to
    the element i.e. assign_els[-1]

    Ordered set of nodes, from parent to ancestor?
    https://stackoverflow.com/a/15645846

    :return: name type (std, dict_key, obj_attr); list of name details; and name
     as single string. For name details, a list with one item in case of std,
     two otherwise.
    :rtype: tuple
    """
    assign_els = element.xpath('ancestor-or-self::Assign')
    try:
        assign_el = assign_els[-1]
    except IndexError:
        raise IndexError(  ## in theory, guaranteed to be one given how we got the name2name_els
            f"Unable to identify ancestor Assign for element: {element}")

    std_name_dets = _std_name_dets_from_assign_el(assign_el)
    if std_name_dets:
        names_dets = [std_name_dets, ]
        return names_dets

    obj_attr_name_dets = _obj_attr_name_dets_from_assign_el(assign_el)
    if obj_attr_name_dets:
        names_dets = [obj_attr_name_dets, ]
        return names_dets

    dict_key_name_dets = _dict_key_name_dets_from_assign_el(assign_el)
    if dict_key_name_dets:
        names_dets = [dict_key_name_dets, ]
        return names_dets

    tuple_names_dets = _tuple_names_dets_from_assign_el(assign_el)
    if tuple_names_dets:
        names_dets = tuple_names_dets
        return names_dets

    return [None, ]

def get_assigned_name(element):
    names_dets = get_assigned_names(element)
    n_names = len(names_dets)
    if n_names == 0:
        raise Exception("Tried to get name but got nothing")
    elif n_names > 1:
        raise Exception(f"Tried to get name but got multiple names ({n_names})")
    else:
        name_dets = names_dets[0]
        return name_dets

def get_el_lines_dets(el, *, ignore_trailing_lines=False):
    """
    How long is the snippet of code that completely wraps up this element? If
    there are no "trailing lines" it is simple because the AST includes line
    numbers. We just get the min and max line number values. But if there are,
    these trailing lines are not part of the AST (in the same way that comments
    are ignored). So:

    d = {
        1: 1}

    d = {
        1: 1,
    }

    are equivalent in the AST. And there are only lines 1-2 in the AST in both
    cases.

    If there are subsequent AST-relevant lines of code, we can find the first of
    those lines, subtract 1, and treat that as the end of our code. If client
    code is worried about trailing empty lines it can strip them off itself.
    Blank lines (or other non-code lines e.g. comments) won't have any effect on
    the execution of the code.

    They do affect our judgement of code length though e.g. to see if the
    snippet is too long or short so the ignore_trailing_lines option is
    provided.

    If there are no subsequent AST-relevant lines of code, we are in the dark
    about where exactly the actual code string (assuming we only have the AST to
    work from). In which case we simply add enough lines to cover all reasonable
    cases e.g. if different levels of nested parentheses/brackets are on
    separate lines. E.g.

    a = (
            (
                (
                    (
                        (
                            (
                                (
                                 ...
                                )
                            )
                        )
                    )
                )
            )
        )
    """
    SAFE_EXTRA_LINES = 10
    line_no_strs = set(el.xpath('descendant-or-self::*[@lineno]/@lineno'))
    line_nos = [int(line_no_str) for line_no_str in line_no_strs]
    if not line_nos:
        first_line_no, last_line_no, el_lines_n = None, None, None
    else:
        first_line_no = min(line_nos)
        last_ast_line_no = max(line_nos)
        if ignore_trailing_lines:
            last_line_no = last_ast_line_no
        else:
            module_el = el.xpath('//Module')[0]
            all_line_no_strs = set(
                module_el.xpath('descendant::*[@lineno]/@lineno'))
            all_line_nos = [
                int(line_no_str) for line_no_str in all_line_no_strs]
            subsequent_line_nos = [line_no for line_no in all_line_nos
                if line_no > last_ast_line_no]
            if not subsequent_line_nos:
                last_line_no = last_ast_line_no + SAFE_EXTRA_LINES
            else:
                last_line_no = min(subsequent_line_nos) - 1
        el_lines_n = last_line_no - first_line_no + 1
    return first_line_no, last_line_no, el_lines_n
