import sys
import io
import logging
import ast

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
        syntax_tree = ast.parse(source, filename=filepath, mode="exec")
        ast.fix_missing_locations(syntax_tree)
    except Exception as ex:
        logger.exception("Unable to parse file '{0}'", filepath)

    if syntax_tree is None:
        logger.info("Tree was None.")
        sys.exit(1)

    for fieldname, value in ast.iter_fields(syntax_tree):
        print("{0}: {1}".format(fieldname, value))

    print_fields(syntax_tree)
    for node in ast.iter_child_nodes(syntax_tree):
        print_fields(node)


def read_source(filepath):
    try:
        with io.open(filepath, "r", encoding="utf8") as file:
            return file.read()
    except:
        logger.exception("Unable to read contents from file '{0}'", filepath)
        return None


def print_fields(node):
    print(type(node).__name__)
    if type(node) is not ast.Module:
        print("lineno: {0}; col: {1};".format(node.lineno, node.col_offset))
    for fieldname, value in ast.iter_fields(node):
        print("{0}: {1}".format(fieldname, value))
    print("---")
