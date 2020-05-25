import logging

from . import conf

def get_val(pre_block_code_str, block_code_str,
        name_type, name_details, name_str):
    """
    Executing supplied code from end users - nope - nothing to see here from a
    security point of view ;-) Needs addressing if this code is ever used as a
    service for other users.

    Note - can be the source of mysterious output in stdout (e.g. exec a print
    function).

    :param str name_type: e.g. conf.STD_NAME. Lets us know how to handle the
     parts of the name e.g. dict name and key name.
    :param list name_details: e.g. name; dict and key; obj and attr
    :param str name_str: name as string e.h. Family.pet or capitals['NZ']
    :return: value if possible. Raises KeyError if unable to get value.
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
    if name_type == conf.STD_NAME:
        val = exp_dets[name_details[0]]
    elif name_type == conf.OBJ_ATTR_NAME:
        obj_name, attr_name = name_details
        try:
            val = getattr(exp_dets[obj_name], attr_name)
        except AttributeError:
            raise KeyError(f"Unable to find name '{name_str}' "
                f"in code_str\n{block_code_str}")
    elif name_type == conf.DICT_KEY_NAME:
        dict_name, key_name = name_details
        try:
            val = exp_dets[dict_name][key_name]
        except NameError:
            raise KeyError(f"Unable to find name '{name_str}' "
                f"in code_str\n{block_code_str}")
    else:
        raise Exception(f"Unexpected name_type: '{name_type}'")
    return val

def execute_collection_dets(block_dets, name_dets):
    try:
        items = get_val(
            block_dets.pre_block_code_str, block_dets.block_code_str,
            name_dets.name_type, name_dets.name_details,
            name_dets.name_str)
    except Exception:
        items = conf.UNKNOWN_ITEMS
    else:
        if isinstance(items, dict):
            items = items.items()  ## we always want to return a list with no special cases
    return items
