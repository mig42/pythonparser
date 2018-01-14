class Container:
    def __init__(self, container_type, name, location):
        self.type = container_type
        self.name = name
        self.location = location
        self.header_span = (0, -1)
        self.footer_span = (0, -1)
        self.children = []

    def add_child(self, child):
        self.children.append(child)
