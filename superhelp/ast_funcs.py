import logging

from . import conf
from . import ast_versioned_funcs as avf
from . import gen_utils

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

def store_ast_output(xml):
    fname = conf.AST_OUTPUT_XML_FNAME
    with gen_utils.make_open_tmp_file(fname, mode='w') as tmp_dets:
        _superhelp_tmpdir, _tmp_ast_fh, tmp_ast_output_xml_fpath = tmp_dets
        xml.getroottree().write(
            str(tmp_ast_output_xml_fpath), pretty_print=True)
    logging.info("\n\n\n\n\nUpdating AST\n\n\n\n\n")

def get_standardised_el_dict(el):
    """
    If we want to see if a value is the same we need to strip out items that
    only vary by position within the script e.g. lineno or col_offset.

    :param Element el: element we want to standardise e.g. a Constant
    :return: standardised dictionary of element attributes
    :rtype: dict
    """
    std_el_dict = {key: value for key, value in el.items()
        if key not in conf.NON_STD_EL_KEYS}
    return std_el_dict

## when backward compatibility with 3.6 can be dropped use def __getattr__(name):
## https://stackoverflow.com/questions/2447353/getattr-on-a-module
python_version = gen_utils.get_python_version()

if python_version in (conf.PY3_6, conf.PY3_7):

    val_dets = avf.val_dets_3_7

    assigned_num_els_from_block = avf.assigned_num_els_from_block_3_7
    num_str_from_val = avf.num_str_from_val_3_7
    num_str_from_el = avf.num_str_from_el_3_7

    assigned_str_els_from_block = avf.assigned_str_els_from_block_3_7
    str_from_el = avf.str_from_el_3_7
    str_els_from_block = avf.str_els_from_block_3_7

    dict_key_from_subscript = avf.dict_key_from_subscript_3_7

    _get_var_plus_equalled = avf._get_var_plus_equalled_3_7
    _get_var_equal_plussed = avf._get_var_equal_plussed_3_7
    get_danger_status = avf.get_danger_status_3_7

    get_docstring_from_value = avf.get_docstring_from_value_3_7
    get_slice_dets = avf.get_slice_dets_3_7
    get_nt_lbl_flds = avf.get_nt_lbl_flds_3_7
    get_slice_n = avf.get_slice_n_3_7
    get_str_els_being_combined = avf.get_str_els_being_combined_3_7

elif python_version == conf.PY3_8:

    val_dets = avf.val_dets_3_8

    assigned_num_els_from_block = avf.assigned_num_els_from_block_3_8
    num_str_from_val = avf.num_str_from_val_3_8
    num_str_from_el = avf.num_str_from_el_3_8

    assigned_str_els_from_block = avf.assigned_str_els_from_block_3_8
    str_from_el = avf.str_from_el_3_8
    str_els_from_block = avf.str_els_from_block_3_8

    dict_key_from_subscript = avf.dict_key_from_subscript_3_8

    _get_var_plus_equalled = avf._get_var_plus_equalled_3_8
    _get_var_equal_plussed = avf._get_var_equal_plussed_3_8
    get_danger_status = avf.get_danger_status_3_8
    get_docstring_from_value = avf.get_docstring_from_value_3_8
    get_slice_dets = avf.get_slice_dets_3_8
    get_nt_lbl_flds = avf.get_nt_lbl_flds_3_8
    get_slice_n = avf.get_slice_n_3_8
    get_str_els_being_combined = avf.get_str_els_being_combined_3_8

else:
    raise Exception(f"Unexpected Python version {python_version}")
