
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
