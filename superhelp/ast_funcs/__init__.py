"""
In future this might be a useful place to handle different versions of ast funcs
according to Python version (3.9+).
"""
import sys

from superhelp.ast_funcs import versioned_gen as gen, versioned_nums as nums

major, minor = sys.version_info[:2]
ok_version = True
if int(major) < 3:
    ok_version = False
else:
    if int(minor) < 8:
        ok_version = False
if not ok_version:
    raise Exception("SuperHELP only supports Python 3.8+")

val_dets = gen.val_dets

assigned_num_els_from_block = nums.assigned_num_els_from_block
num_str_from_parent_el = nums.num_str_from_parent_el
num_str_from_el = nums.num_str_from_el

assigned_str_els_from_block = gen.assigned_str_els_from_block
str_from_el = gen.str_from_el
str_els_from_block = gen.str_els_from_block

dict_key_from_subscript = gen.dict_key_from_subscript

_get_var_plus_equalled = gen._get_var_plus_equalled
_get_var_equal_plussed = gen._get_var_equal_plussed
get_danger_status = gen.get_danger_status
get_docstring_from_value = gen.get_docstring_from_value
get_slice_dets = gen.get_slice_dets
get_nt_lbl_flds = gen.get_nt_lbl_flds
get_slice_n = gen.get_slice_n
get_str_els_being_combined = gen.get_str_els_being_combined
