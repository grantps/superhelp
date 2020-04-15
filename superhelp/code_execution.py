import logging

def get_val(pre_block_code_str, block_code_str, name):
    """
    Executing supplied code from end users - nope - nothing to see here from a
    security point of view ;-) Needs addressing if this code is ever used as a
    service for other users.

    Note - can be the source of mysterious output in stdout (e.g. exec a print
    function).
    """
    exp_dets = {}
    try:
        exec(pre_block_code_str + block_code_str, exp_dets)
    except ImportError as e:
        logging.debug(
            f"Import problem running {__file__} (specifically {__name__}): {e}")
        raise ImportError("SuperHELP only has modules from the Python standard "
            "library installed - it looks like your snippet relies on a module "
            "from outside the standard library.")
    try:
        val = exp_dets[name]
    except KeyError:
        val = None
#         raise KeyError(
#             f"Unable to find name '{name}' in code_str\n{block_code_str}")
    return val
