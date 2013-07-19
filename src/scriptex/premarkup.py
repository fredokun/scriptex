
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
        self.depth = 0  # document has minimal depth

class PreCommand(PreMarkup):
    def __init__(self, cmd_name, cmd_opts, header_start_pos, header_end_pos):
        super().__init__("command", header_start_pos, header_end_pos)
        self.cmd_name = cmd_name
        self.cmd_opts = cmd_opts
        self.header_end_pos = header_end_pos

class PreEnvironment(PreMarkup):
    def __init__(self, env_name, env_opts, header_start_pos, header_end_pos):
        super().__init__("environment", header_start_pos, None)
        self.env_name = env_name
        self.env_opts = env_opts
        self.header_end_pos = header_end_pos

class PreSection(PreMarkup):
    def __init__(self, section_title, section_depth, header_start_pos, header_end_pos):
        super().__init__("section", header_start_pos, None)
        self.section_title = section_title
        self.section_depth = section_depth
        self.header_end_pos = header_end_pos


