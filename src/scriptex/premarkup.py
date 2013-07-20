
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
        self.section_depth = 0  # document has minimal depth

    def __repr__(self):
        return "PreDocument(content={})".format(repr(self.content))
        
class PreCommand(PreMarkup):
    def __init__(self, cmd_name, cmd_opts, header_start_pos, header_end_pos, preformated=False):
        super().__init__("command", header_start_pos, header_end_pos)
        self.cmd_name = cmd_name
        self.cmd_opts = cmd_opts
        self.header_end_pos = header_end_pos
        self.preformated = preformated

    def __repr__(self):
        return "PreCommand(cmd_name={}, cmd_opts={}, preformated={}, content={})".format(self.cmd_name, self.cmd_opts, self.preformated, repr(self.content))

class PreEnvironment(PreMarkup):
    def __init__(self, env_name, env_opts, header_start_pos, header_end_pos):
        super().__init__("environment", header_start_pos, None)
        self.env_name = env_name
        self.env_opts = env_opts
        self.header_end_pos = header_end_pos

    def __repr__(self):
        return "PreEnvironment(env_name={},env_opts={},content={})".format(self.env_name, self.env_opts, repr(self.content))

class PreSection(PreMarkup):
    def __init__(self, section_title, section_depth, header_start_pos, header_end_pos):
        super().__init__("section", header_start_pos, None)
        self.section_title = section_title
        self.section_depth = section_depth
        self.header_end_pos = header_end_pos

    def __repr__(self):
        return "PreSection(section_title={},section_depth={},content={})".format(self.section_title, self.section_depth, repr(self.content))




