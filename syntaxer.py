import ast
from collections import namedtuple

NAME = 'name'
LIST = 'list'

LIST_ONLY = 'list_only'

PatternDets = namedtuple('PatternDets', 'pattern_type, objs')


class Analyser(ast.NodeVisitor):
    """
    To specially handle items visited add visit_X methods where X is what type
    of node is being visited.

    Node types are listed here:
    https://greentreesnakes.readthedocs.io/en/latest/nodes.html
    """

    def __init__(self, *, debug=False):
        self.debug = debug
        self.pattern_parts = []
        self.objs = []

    def visit_Name(self, node):
        """
        Pick up variables being created.
        """
        self.pattern_parts.append(NAME)
        if self.debug: print(f"Name: {node.id}")
        self.objs.append(node)

    def visit_List(self, node):
        """
        Lists have elts (elements). Elements can have different types
        """
        self.pattern_parts.append(LIST)
        if self.debug: print(f"List: {[elt for elt in node.elts]}")
        self.objs.append(node)
        
    def get_patterns(self):
        if self.pattern_parts == [NAME, LIST]:
            return PatternDets(LIST_ONLY, self.objs)
        else:
            raise Exception("Unsupported pattern")
