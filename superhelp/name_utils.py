from collections import namedtuple

from . import conf

AssignedNameDets = namedtuple('AssignedNameDets',
    'name_type, name_details, name_str, unpacking_idx')

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
    from . import ast_funcs  ## avoid circular import
    dict_name_els = subscript_el.xpath('value/Name')
    if len(dict_name_els) != 1:
        return None
    dict_name_el = dict_name_els[0]
    dict_name = dict_name_el.get('id')
    dict_key, needs_quoting = ast_funcs.dict_key_from_subscript(subscript_el)
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
