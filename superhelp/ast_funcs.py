
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
    name = assign_el.xpath('targets/Name')[0].get('id')
    return name

def get_xml_element_first_line_no(element):
    element_line_nos = element.xpath(
        './ancestor-or-self::*[@lineno][1]/@lineno')
    if element_line_nos:
        first_line_no = int(element_line_nos[0])
    else:
        first_line_no = None
    return first_line_no

def _get_last_line_no(element, *, first_line_no):
    last_line_no = None
    ancestor = element
    while True:
        ## See if there are any following siblings at this level of the tree.
        next_siblings = ancestor.xpath('./following-sibling::*')
        ## Get the line no of the closest following sibling we can.
        for sibling in next_siblings:
            sibling_line_nos = sibling.xpath(
                './ancestor-or-self::*[@lineno][1]/@lineno')
            if len(sibling_line_nos):
                ## Subtract 1 from the next siblings line_no to get the
                ## last line_no of the element (unless that would be
                ## less than the first_line_no).
                last_line_no = max(
                    (int(sibling_line_nos[0]) - 1), first_line_no)
                break
        ## Continue searching for the next element by going up the tree to the next ancestor
        ancestor_ancestors = ancestor.xpath('./..')
        if len(ancestor_ancestors):
            ancestor = ancestor_ancestors[0]
        else:
            ## Break if we've run out of ancestors
            break
    return last_line_no

def get_xml_element_line_no_range(element):
    element_line_nos = element.xpath(
        './ancestor-or-self::*[@lineno][1]/@lineno')
    if element_line_nos:
        first_line_no = int(element_line_nos[0])
        last_line_no = _get_last_line_no(element, first_line_no=first_line_no)
    else:
        first_line_no, last_line_no = None, None
    return first_line_no, last_line_no
