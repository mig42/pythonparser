import io
import logging
import json
import os
import sys

import ast
import asttokens

from .file import File
from .container import Container
from .location import Location
from .node import Node

LOGGER = logging.getLogger(__name__)


def main(args):
    if len(args) != 1:
        sys.exit(1)

    filepath = args[0]
    LOGGER.info("Parsing file '%s'", filepath)

    source = read_source(filepath)
    if source is None:
        sys.exit(1)

    try:
        atok = asttokens.ASTTokens(source, parse=True)
    except Exception as ex:
        LOGGER.exception("Unable to parse file '%s'", filepath, exc_info=ex)
        sys.exit(1)

    if atok is None:
        LOGGER.info("Parsing returned an empty tree.")
        sys.exit(1)

    source_file = File(os.path.basename(filepath), get_node_location(atok.tree))
    visitor = MyNodeVisitor(atok, source_file)
    visitor.visit(atok.tree)

    print(json.dumps(source_file, default=lambda x: x.__dict__))


def read_source(filepath):
    try:
        with io.open(filepath, "r", encoding="utf8") as file:
            return file.read()
    except:
        LOGGER.exception("Unable to read contents from file '%s'", filepath)
        return None


def get_node_location(node):
    return Location(node.first_token.start, node.last_token.end)


class MyNodeVisitor(ast.NodeVisitor):

    def __init__(self, atok, file):
        self._atok = atok
        self._containers = [file]

    def add_new_container(self, node, node_type):
        container = Container(
            node_type,
            self.get_node_name(node),
            get_node_location(node))
        self._containers[-1].add_child(container)
        self._containers.append(container)
        return container

    def get_node_name(self, node):
        if (hasattr(node, 'name')):
            return node.name
        return self.get_module_name()

    def get_module_name(self):
        filename = self._containers[0].name
        return os.path.splitext(filename)[0]

    def remove_last_container(self):
        self._containers.pop()

    def add_new_node(self, node, node_type):
        result = Node(
            node_type,
            self.get_node_name(node),
            get_node_location(node),
            self._atok.get_text_range(node))
        self._containers[-1].add_child(result)

    def visit_Module(self, node):
        module = self.add_new_container(node, 'module')
        module.set_header((0, -1))
        module.set_footer((0, -1))

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
        module.set_header((node.first_token.startpos, node.first_token.endpos))
        module.set_footer((0, -1))

        self.generic_visit(node)
        self.remove_last_container()
