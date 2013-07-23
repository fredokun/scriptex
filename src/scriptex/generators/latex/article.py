"""Basic latex generator based on document class article.
"""

from scriptex.generator import DocumentGenerator, CommandGenerator, EnvironmentGenerator, SectionGenerator

class LatexOutput:
    def __init__(self):
        self.output = []
        self.output_line = 1
        self.pos_map = dict()

    def append(self, orig_pos, text):
        self.output.append((orig_pos, self.output_line, text))
        if self.output_line not in self.pos_map:
            self.pos_map[self.output_line] = orig_pos
        
    def newline(self, orig_pos):
        self.output.append((orig_pos, self.output_line, "\n"))
        if self.output_line not in self.pos_map:
            self.pos_map[self.output_line] = orig_pos
        self.output_line += 1
        
    def __str__(self):
        "".join((str_ for (_,__,str_) in self.output))
        
class LatexArticleGenerator(DocumentGenerator):
    def __init__(self, document):
        super().__init__(document)
        self.default_command_generator = DefaultLatexCommandGenerator()
        
    def generate(self):
        self.output = LatexOutput()
        super().generate()


class DefaultLatexCommandGenerator(CommandGenerator):
    def __init__(self):
        pass
    
    def enter_command(self, generator, cmd):
        opts_str = "" if cmd.cmd_opts is None else "[{}]".format(cmd.cmd_opts)
        open_str = "" if not cmd.content else "{{"
        generator.output.append(cmd.start_pos.lpos, "\\{}".format(cmd_name) + opts_str + open_str)

    def exit_command(self, generator, cmd):
        if cmd.content:
            generator.output.append(cmd.end_pos.lpos, "}")


