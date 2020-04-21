
def get_assign_name(element):
    """
    Get name assignment associated with the element. The element might be the
    value or the target or something but we just want to identify the closest
    Assign ancestor and get its Name.

    If Assign appears more than once in the ancestral chain e.g.
    body-Assign-spam-eggs-Assign-targets-Name then we get a list like this:
    [body-Assign, body-Assign-spam-eggs-Assign] and we want the closest one to
    the element i.e. assign_els[-1]

    Ordered set of nodes, from parent to ancestor?
    https://stackoverflow.com/a/15645846
    """
    assign_els = element.xpath('ancestor::Assign')
    assign_el = assign_els[-1]
    name_els = assign_el.xpath('targets/Name')
    if len(name_els) == 1:
        name = name_els[0].get('id')
    else:
        name = None
    return name

def get_el_lines_dets(el):
    """
    Keeping it simple - don't traverse the tree - just grab everything and take
    it from there. Other approaches worked except when they didn't ;-).
    <tempting_fate>This can't fail</tempting_fate>.
    """
    line_no_strs = set(el.xpath('descendant-or-self::*[@lineno]/@lineno'))
    line_nos = [int(line_no_str) for line_no_str in line_no_strs]
    try:
        first_line_no = min(line_nos)
        last_line_no = max(line_nos)
        el_lines_n = last_line_no - first_line_no + 1
    except ValueError:
        first_line_no, last_line_no, el_lines_n = None, None, None
    return first_line_no, last_line_no, el_lines_n
