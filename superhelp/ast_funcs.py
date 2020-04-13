import ast

from . import conf

def get_assigned_name(element):
    """
    :return: None if no name
    :rtype: str
    """
    ## Get the name of the element if we can.
    name_elements = element.xpath('targets/Name')
    if len(name_elements) == 1 and name_elements[0].get('id'):
        name_id = name_elements[0].get('id')
        name = name_id
    else:
        name = None
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


## https://www.mattlayman.com/blog/2018/decipher-python-ast/
class Analyser(ast.NodeVisitor):

    def __init__(self):
        self.std_imports = []

    def check_module(self, module):
        if module not in conf.STD_LIBS:
            raise Exception("Only modules from the Python standard library can "
                f"be imported. `{module}` is not in the current list of "
                "standard modules.")

    def visit_Import(self, node):
        for alias in node.names:
            module = alias.name
            self.check_module(module)
            self.std_imports.append(
                f"import {module} as {alias.asname or module}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.check_module(node.module)
            self.std_imports.append(f"from {node.module} "
                f"import {alias.name} as {alias.asname or alias.name}")
        self.generic_visit(node)


def check_tree(tree):
    analyser = Analyser()
    analyser.visit(tree)
