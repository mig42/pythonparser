import sys
import io
import logging
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
        self._file = file
        self._current_container = None

    def visit_Module(self, node):
        print("Module!")
        self.print(node)
        self._current_container = Container(
            'module',
            get_node_location(node),
            (0, -1),
            (0, -1))
        self._file.add_child(self._current_container)

        self.generic_visit(node)
        self._current_container = None

    def visit_Import(self, node):
        print("Import!")
        self.print(node)

    def visit_ImportFrom(self, node):
        print("Import from!")
        self.print(node)

    def visit_FunctionDef(self, node):
        print("Function!")
        self.print(node)

    def visit_AsyncFunctionDef(self, node):
        print("AsyncFunction!")
        self.print(node)

    def visit_ClassDef(self, node):
        print("Class!")
        print("lineno: {}; col_offset: {};".format(node.lineno, node.col_offset))
        print("name: {}".format(node.name))
        self.print(node)

        self._current_container = Container(
            'class', get_node_location(node), (0, -1), (0, -1))
        self._file.add_child(self._current_container)

        self.generic_visit(node)
        self._current_container = None

    def print(self, node):
        print(type(node))
        print(self._atok.get_text_range(node))
        print(self._atok.get_text(node))
        print("###")
        print()
        print()
