class File:
    def __init__(self, name, location):
        self.type = 'file'
        self.name = name
        self.location = location
        self.footer_span = [0, -1]
        self.children = []
        self.parsing_errors_detected = []

    def add_child(self, child):
        self.children.append(child)

    def add_parsing_error(self, error):
        self.parsing_errors_detected.append(error)
