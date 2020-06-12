from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false  # @UnusedImport @UnresolvedImport

from superhelp import ast_funcs  # @Reimport

from tests import get_actual_result

def test_num_str_from_parent_el():
    simple = "a = 10"
    neg = "a = -6"
    zero = "a = 0"
    non_num = "a = 'chicken'"
    simple2num_key = "a[1] = 100"
    simple2str_key = "a['chicken'] = 100"
    simple2obj_attr = "a.chicken = 100"
    neg2num_key = "a[1] = -100"
    neg2str_key = "a['chicken'] = -100"
    neg2obj_attr = "a.chicken = -100"
    xpath = 'descendant::Assign/value'
    tests = [
        (simple, '10'),
        (neg, '-6'),
        (zero, '0'),
        (non_num, None),
        (simple2num_key, '100'),
        (simple2str_key, '100'),
        (simple2obj_attr, '100'),
        (neg2num_key, '-100'),
        (neg2str_key, '-100'),
        (neg2obj_attr, '-100'),
    ]
    for snippet, expected_res in tests:
        actual_res = get_actual_result(
            snippet, xpath, ast_funcs.num_str_from_parent_el)
        assert_equal(actual_res, expected_res)

# test_num_str_from_parent_el()
