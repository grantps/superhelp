"""
Specialised functions for working with the AST. Copes with different ASTs
created prior to Python 3.8. Handles odd things like positive numbers being
under value but negative being under value/UnaryOp/operand/Constant etc.

When backward compatibility with 3.6 can be dropped use def __getattr__(name):
https://stackoverflow.com/questions/2447353/getattr-on-a-module
"""
from .. import conf, gen_utils
from . import versioned_gen as gen, versioned_nums as nums

python_version = gen_utils.get_python_version()

if python_version in (conf.PY3_6, conf.PY3_7):

    val_dets = gen.val_dets_3_7

    assigned_num_els_from_block = nums.assigned_num_els_from_block_3_7
    num_str_from_parent_el = nums.num_str_from_parent_el_3_7
    num_str_from_el = nums.num_str_from_el_3_7

    assigned_str_els_from_block = gen.assigned_str_els_from_block_3_7
    str_from_el = gen.str_from_el_3_7
    str_els_from_block = gen.str_els_from_block_3_7

    dict_key_from_subscript = gen.dict_key_from_subscript_3_7

    _get_var_plus_equalled = gen._get_var_plus_equalled_3_7
    _get_var_equal_plussed = gen._get_var_equal_plussed_3_7
    get_danger_status = gen.get_danger_status_3_7

    get_docstring_from_value = gen.get_docstring_from_value_3_7
    get_slice_dets = gen.get_slice_dets_3_7
    get_nt_lbl_flds = gen.get_nt_lbl_flds_3_7
    get_slice_n = gen.get_slice_n_3_7
    get_str_els_being_combined = gen.get_str_els_being_combined_3_7

elif python_version == conf.PY3_8:

    val_dets = gen.val_dets_3_8

    assigned_num_els_from_block = nums.assigned_num_els_from_block_3_8
    num_str_from_parent_el = nums.num_str_from_parent_el_3_8
    num_str_from_el = nums.num_str_from_el_3_8

    assigned_str_els_from_block = gen.assigned_str_els_from_block_3_8
    str_from_el = gen.str_from_el_3_8
    str_els_from_block = gen.str_els_from_block_3_8

    dict_key_from_subscript = gen.dict_key_from_subscript_3_8

    _get_var_plus_equalled = gen._get_var_plus_equalled_3_8
    _get_var_equal_plussed = gen._get_var_equal_plussed_3_8
    get_danger_status = gen.get_danger_status_3_8
    get_docstring_from_value = gen.get_docstring_from_value_3_8
    get_slice_dets = gen.get_slice_dets_3_8
    get_nt_lbl_flds = gen.get_nt_lbl_flds_3_8
    get_slice_n = gen.get_slice_n_3_8
    get_str_els_being_combined = gen.get_str_els_being_combined_3_8

else:
    raise Exception(f"Unexpected Python version {python_version}")
