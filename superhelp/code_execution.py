
def get_val(pre_block_code_str, block_code_str, name):
    """
    Executing supplied code from end users - nope - nothing to see here from a
    security point of view ;-) Needs addressing if this code is ever used as a
    service for other users.

    Note - can be the source of mysterious output in stdout (e.g. exec a print
    function).
    """
    exp_dets = {}
    exec(pre_block_code_str + block_code_str, exp_dets)
    try:
        val = exp_dets[name]
    except KeyError:
        val = None
#         raise KeyError(
#             f"Unable to find name '{name}' in code_str\n{block_code_str}")
    return val
