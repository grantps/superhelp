import logging

from . import ast_funcs, conf
from .utils import get_nice_str_list, layout_comment as layout


def get_val(pre_block_code_str, block_code_str, name):
    """
    Executing supplied code from end users - nope - nothing to see here from a
    security point of view ;-) Needs addressing if this code is ever used as a
    service for other users.

    Note - can be the source of mysterious output in stdout (e.g. exec a print
    function).

    Raises KeyError if unable to get value.
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
        raise KeyError(
            f"Unable to find name '{name}' in code_str\n{block_code_str}")
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
        name = ast_funcs.get_assign_name(named_el)
        try:
            items = get_val(
                block_dets.pre_block_code_str, block_dets.block_code_str, name)
        except KeyError:
            items = None
        else:
            if len(items) > conf.MAX_ITEMS_EVALUATED:
                items = truncated_items_func(items)
                oversized_names.append(name)
        names_items.append((name, items))
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

            Because `{name}` is large SuperHELP has only examined the first
            {conf.MAX_ITEMS_EVALUATED} items.
            """)
    else:
        oversized_msg = ''
    return names_items, oversized_msg
