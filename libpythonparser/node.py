class Node:
    def __init__(self, node_type, name, location, span):
        self.type = node_type
        self.name = name
        self.location = location
        self.span = span

    def set_name(self, name):
        self.name = name
