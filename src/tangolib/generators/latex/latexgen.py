"""Base for latex generation.
"""

from tangolib.generator import DocumentGenerator, CommandGenerator, EnvironmentGenerator, SectionGenerator
from tangolib.generator import TextGenerator, PreformatedGenerator, SpacesGenerator, NewlinesGenerator

class LatexOutput:
    def __init__(self):
        self.output = []
        self.output_line = 1
        self.pos_map = dict()
        self.last_pos = 1

    def register_orig_pos(self, orig_pos):
        if orig_pos is None:
            return self.last_pos
        elif orig_pos == self.last_pos:
            return self.last_pos
        # original position given
        self.output.append((None, self.output_line, "%%%"))
        self.newline(None)
        self.output.append((orig_pos, self.output_line, "%%% Tango Line: {}".format(orig_pos)))
        self.newline(None)
        self.last_pos = orig_pos
        return orig_pos
        
    def append(self, orig_pos, text):
        orig_pos = self.register_orig_pos(orig_pos)
        self.output.append((orig_pos, self.output_line, text))
        if self.output_line not in self.pos_map:
            self.pos_map[self.output_line] = orig_pos

    def newline(self, orig_pos):
        orig_pos = self.register_orig_pos(orig_pos)
        self.output.append((orig_pos, self.output_line, "\n"))
        if self.output_line not in self.pos_map:
            self.pos_map[self.output_line] = orig_pos
        self.output_line += 1
        
    def __str__(self):
        return "" if not self.output else "".join([str_ for (_,__,str_) in self.output])
        
class LatexGenerator(DocumentGenerator):
    def __init__(self, document):
        super().__init__(document)
        self.default_command_generator = DefaultLatexCommandGenerator()
        self.default_environment_generator = DefaultLatexEnvironmentGenerator()
        self.default_section_generator = DefaultLatexSectionGenerator()
        self.text_generator = LatexTextGenerator()
        self.preformated_generator = LatexPreformatedGenerator()
        self.spaces_generator = LatexSpacesGenerator()
        self.newlines_generator = LatexNewlinesGenerator()
        
    def generate(self):
        self.output = LatexOutput()
        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        super().generate()


class DefaultLatexCommandGenerator(CommandGenerator):
    def __init__(self):
        pass
    
    def enter_command(self, generator, cmd):
        opts_str = "" if cmd.cmd_opts is None else "[{}]".format(cmd.cmd_opts)
        open_str = "" if not cmd.content else "{"
        generator.output.append(cmd.start_pos.lpos, "\\{}".format(cmd.cmd_name) + opts_str + open_str)

    def exit_command(self, generator, cmd):
        if cmd.content:
            if cmd.end_pos.lpos != cmd.start_pos.lpos:
                generator.output.append(cmd.end_pos.lpos, "}")
            else:
                generator.output.append(None, "}")

class DefaultLatexEnvironmentGenerator(EnvironmentGenerator):
    def __init__(self):
        pass
    
    def enter_environment(self, generator, env):
        opts_str = "" if env.env_opts is None else "[{}]".format(env.env_opts)
        generator.output.append(env.start_pos.lpos, "\\begin{{{}}}".format(env.env_name) + opts_str)

    def exit_environment(self, generator, env):
        generator.output.append(env.end_pos.lpos, "\\end{{{}}}".format(env.env_name))

class DefaultLatexSectionGenerator(SectionGenerator):
    def __init__(self):
        pass
    
    def enter_section(self, generator, sec):
        generator.output.append(sec.start_pos.lpos, "\\{}{{{}}}".format(sec.section_name, sec.section_title))

    def exit_section(self, generator, sec):
        pass

class LatexTextGenerator(TextGenerator):
    def __init__(self):
        pass

    def on_text(self, generator, text):
        generator.output.append(text.start_pos.lpos, text.text)
        # TODO:  escape strings for latex output

class LatexPreformatedGenerator(PreformatedGenerator):
    def __init__(self):
        pass

    def on_text(self, generator, text):
        generator.output.append(text.start_pos.lpos, text.text)
        # TODO:  escape strings for latex output
        
class LatexSpacesGenerator(SpacesGenerator):
    def __init__(self):
        pass

    def on_spaces(self, generator, spaces):
        generator.output.append(None, spaces.spaces)


class LatexNewlinesGenerator(NewlinesGenerator):
    def __init__(self):
        pass

    def on_newlines(self, generator, newlines):
        lpos = newlines.start_pos.lpos
        for _ in newlines.newlines:
            generator.output.newline(None)
            lpos += 1




