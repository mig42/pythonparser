import io
import logging
import json
import os
import sys
import token

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
        return result

    def visit_Module(self, node):
        the_module = self.add_new_container(node, 'module')

        self.generic_visit(node)

        if the_module.children:
            child_start = the_module.children[0].location.start
            if child_start != the_module.location.start:
                span_end = self._atok._line_numbers.line_to_offset(
                    child_start[0], child_start[1]) - 1
                the_module.header_span = (0, span_end)

        # Calculate footer here

        self.remove_last_container()


    def visit_Import(self, node):
        the_import = self.add_new_node(node, 'import')
        the_import.name = node.names[0].name
        self.fix_node_span_start(node, the_import)

    def visit_ImportFrom(self, node):
        the_import = self.add_new_node(node, 'import')
        the_import.name = '{0}.{1}'.format(node.module, node.names[0].name)
        self.fix_node_span_start(node, the_import)

    def visit_FunctionDef(self, node):
        self.process_function(node)

    def visit_AsyncFunctionDef(self, node):
        self.process_function(node)

    def visit_ClassDef(self, node):
        the_class = self.add_new_container(node, 'class')
        endpos = node.first_token.endpos
        startpos = node.first_token.startpos

        leading_newline = self.find_first_leading_newline(node)
        if leading_newline is not None:
            the_class.location.start = leading_newline.start
            startpos = leading_newline.startpos

        the_class.header_span = (startpos, endpos)

        self.generic_visit(node)
        self.remove_last_container()

    def process_function(self, node):
        function = self.add_new_node(node, 'function')
        self.fix_node_span_start(node, function)

    def fix_node_span_start(self, ast_node, api_node):
        leading_newline = self.find_first_leading_newline(ast_node)
        if leading_newline is None:
            return

        api_node.location.start = leading_newline.start
        api_node.span = (leading_newline.startpos, api_node.span[1])

    def find_first_leading_newline(self, node):
        result = None
        cur_token = self._atok.prev_token(node.first_token, include_extra=True)

        while self.is_leading_token(cur_token):
            result = cur_token
            cur_token = self._atok.prev_token(cur_token, include_extra=True)

        return result

    def is_leading_token(self, ast_token):
        tok_name = token.tok_name[ast_token.type]
        if tok_name == 'DEDENT' or tok_name == 'NL' or tok_name == 'COMMENT':
            return True
        if ast_token.string.startswith('"""'):
            return True
        return False
