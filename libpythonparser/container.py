class Container:
    def __init__(self, name, location, header, footer):
        self.type = 'file'
        self.name = name
        self.location = location
        self.header_span = header
        self.footer_span = footer
        self.children = []

    def add_child(self, child):
        self.children.append(child)
