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

    file_location = Location(
        atok.tree.first_token.start, atok.tree.last_token.end)
    visitor = MyNodeVisitor(atok, File(filepath, file_location))
    visitor.visit(atok.tree)


def read_source(filepath):
    try:
        with io.open(filepath, "r", encoding="utf8") as file:
            return file.read()
    except:
        logger.exception("Unable to read contents from file '%s'", filepath)
        return None


class MyNodeVisitor(ast.NodeVisitor):

    def __init__(self, atok, file):
        self._atok = atok
        self._file = file
        self._current_container = None

    def visit_Module(self, node):
        print("Module!")
        self.print(node)
        self._current_container = Container(
            'module', self.get_range(node), (0, -1), (0, -1))
        self._file.add_child(self._current_container)

        self.generic_visit(node)
        self._current_container = None

    def get_range(self, node):
        return Location((node.lineno, node.col_offset), (0, -1))

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
            'module', self.get_range(node), (0, -1), (0, -1))
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
