class Container:
    def __init__(self, name, location):
        self.type = 'file'
        self.name = name
        self.location = location
        self.children = []

    def set_header(self, header):
        self.header_span = header

    def set_footer(self, footer):
        self.footer_span = footer

    def add_child(self, child):
        self.children.append(child)
