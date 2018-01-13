import io
import logging
import sys
import ast
import asttokens

from .file import File
from .container import Container
from .location import Location
from .node import Node

logger = logging.getLogger(__name__)


def main(args):
    if len(args) != 1:
        sys.exit(1)

    filepath = args[0]
    logger.info("Parsing file '%s'", filepath)

    source = read_source(filepath)
    if source is None:
        sys.exit(1)

    try:
        atok = asttokens.ASTTokens(source, parse=True)
    except Exception as ex:
        logger.exception("Unable to parse file '%s'", filepath, exc_info=ex)
        sys.exit(1)

    if atok is None:
        logger.info("Parsing returned an empty tree.")
        sys.exit(1)

    visitor = MyNodeVisitor(atok, File(filepath, get_node_location(atok.tree)))
    visitor.visit(atok.tree)


def read_source(filepath):
    try:
        with io.open(filepath, "r", encoding="utf8") as file:
            return file.read()
    except:
        logger.exception("Unable to read contents from file '%s'", filepath)
        return None


def get_node_location(node):
    return Location(node.first_token.start, node.last_token.end)


class MyNodeVisitor(ast.NodeVisitor):

    def __init__(self, atok, file):
        self._atok = atok
        self._containers = [file]

    def add_new_container(self, node, node_type):
        container = Container(node_type, node.name, get_node_location(node))
        self._containers[-1].add_child(container)
        self._containers.append(container)
        return container

    def remove_last_container(self):
        self._containers.pop()

    def add_new_node(self, node, node_type):
        result = Node(
            node_type,
            node.name,
            get_node_location(node),
            self._atok.get_text_range(node))
        self._containers[-1].add_child(result)

    def visit_Module(self, node):
        module = self.add_new_container(node, 'module')
        module.set_header(None)
        module.set_footer(None)

        self.generic_visit(node)
        self.remove_last_container()

    def visit_Import(self, node):
        self.add_new_node(node, 'import')

    def visit_ImportFrom(self, node):
        self.add_new_node(node, 'import')

    def visit_FunctionDef(self, node):
        self.add_new_node(node, 'function')

    def visit_AsyncFunctionDef(self, node):
        self.add_new_node(node, 'function')

    def visit_ClassDef(self, node):
        module = self.add_new_container(node, 'class')
        module.set_header(None)
        module.set_footer(None)

        self.generic_visit(node)
        self.remove_last_container()
