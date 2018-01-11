import sys
import io
import logging
import ast
import asttokens

logger = logging.getLogger(__name__)


def main(args):
    if len(args) != 1:
        sys.exit(1)

    filepath = args[0]
    logger.info("Parsing file '{0}'", filepath)

    source = read_source(filepath)
    if source is None:
        sys.exit(1)

    try:
        atok = asttokens.ASTTokens(source, parse=True)
    except Exception as ex:
        logger.exception("Unable to parse file '{0}'", filepath)
        sys.exit(1)

    if atok is None:
        logger.info("Parsing returned an empty tree.")
        sys.exit(1)

    visitor = MyNodeVisitor(atok)
    visitor.visit(atok.tree)


def read_source(filepath):
    try:
        with io.open(filepath, "r", encoding="utf8") as file:
            return file.read()
    except:
        logger.exception("Unable to read contents from file '{0}'", filepath)
        return None


class MyNodeVisitor(ast.NodeVisitor):

    def __init__(self, atok):
        self._atok = atok

    def visit_Module(self, node):
        print("Module!")
        self.print(node)
        self.generic_visit(node)

    def visit_Import(self, node):
        print("Import!")
        self.print(node)

    def visit_ImportFrom(self, node):
        print("Import from!")
        self.print(node)

    def visit_Expression(self, node):
        print("Expression!")
        self.print(node)

    def visit_Assign(self, node):
        print("Assign!")
        self.print(node)

    def visit_AugAssign(self, node):
        print("Assign!")
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
        self.generic_visit(node)

    def print(self, node):
        print(type(node))
        print(self._atok.get_text_range(node))
        print(self._atok.get_text(node))
        print("###")
        print()
        print()
