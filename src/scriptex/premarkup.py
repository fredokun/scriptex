
class PreMarkup:
    def __init__(self, markup_type, start_pos, end_pos):
        self.markup_type = markup_type
        self.start_pos = start_pos
        self.end_pos = end_pos

        self.content = []

    def append(self, element):
        self.content.append(element)

class PreDocument(PreMarkup):
    def __init__(self, start_pos):
        super().__init__("document", start_pos, None)

class PreCommand(PreMarkup):
    pass

class PreEnvironment(PreMarkup):
    def __init__(self, env_name, env_opts, header_start_pos, header_end_pos):
        super().__init__(self, "environment", header_start_pos, None)
        self.env_name = env_name
        self.header_end_pos = header_end_pos

class PreSection(PreMarkup):
    pass



