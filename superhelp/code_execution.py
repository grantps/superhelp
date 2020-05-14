import logging

from . import ast_funcs, conf
from .utils import get_nice_str_list, layout_comment as layout

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

def get_collections_dets(named_els, block_dets, *,
        collection_plural, truncated_items_func):
    """
    Get information on collections - names with associated items, plus a string
    message (empty str if no oversized items) which can be assembled as part of
    a full advisor message. If an item cannot be evaluated, it is set to None.

    :return: names_items: list of (name, items) tuples, and oversized_msg (str)
    :rtype: tuple
    """
    names_items = []
    oversized_names = []
    for named_el in named_els:
        names_dets = ast_funcs.get_assigned_names(named_el)
        for name_dets in names_dets:
            try:
                items = get_val(
                    block_dets.pre_block_code_str, block_dets.block_code_str,
                    name_dets.name_type, name_dets.name_details,
                    name_dets.name_str)
            except KeyError:
                items = None
            else:
                if len(items) > conf.MAX_ITEMS_EVALUATED:
                    items = truncated_items_func(items)
                    oversized_names.append(name_dets.name_str)
            names_items.append((name_dets.name_str, items))
    if oversized_names:
        multi_oversized = len(oversized_names) > 1
        if multi_oversized:
            nice_names = get_nice_str_list(oversized_names, quoter='`')
            oversized_msg = layout(f"""\

            Because the following {collection_plural} were large SuperHELP has
            only examined the first {conf.MAX_ITEMS_EVALUATED} items:
            {nice_names}
            """)
        else:
            oversized_msg = layout(f"""\

            Because `{name_dets.name_str}` is large SuperHELP has only examined
            the first {conf.MAX_ITEMS_EVALUATED} items.
            """)
    else:
        oversized_msg = ''
    return names_items, oversized_msg
