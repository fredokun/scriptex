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

def guess_document_class(document):
    """A relatively silly heuristics to guess the document class.
    """
    node = document
    nodes = []
    search_more = True
    while search_more:
        if node.is_markup() and node.markup_type == "section":
            if section_of_depth(section.depth) == "section":
                return "article"
            elif section_of_depth(section.depth) == "chapter":
                return "book"
            elif section_of_depth(section.depth) == "part":
                return "book"
            else:
                return None
        nodes = nodes.extend(node.content)
        if nodes:
            node = nodes.pop()
        else:
            search_more = False

    # by default use article
    return "article"

class LatexDocumentGenerator(DocumentGenerator):
    def __init__(self, document, latex_config):
        super().__init__(document)
        self.latex_config = latex_config

        self.default_command_generator = DefaultLatexCommandGenerator()
        self.default_environment_generator = DefaultLatexEnvironmentGenerator()
        self.default_section_generator = DefaultLatexSectionGenerator()
        self.text_generator = LatexTextGenerator()
        self.preformated_generator = LatexPreformatedGenerator()
        self.spaces_generator = LatexSpacesGenerator()
        self.newlines_generator = LatexNewlinesGenerator()
        
    def straighten_configuration(self):
        if not self.latex_config.document_class:
            self.latex_config.document_class = guess_document_class(self.document)

    def generate(self):
        self.latex_config.check_configuration()

        self.output = LatexOutput()

        preamble = self.generate_preamble()
        self.output.append(None, preamble)

        self.output.append(None, \
"""
%%% >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
%%% Tango: Beginning of top-level document
%%% Tango: File = '{}'
\\begin{{document}}
""".format(self.document.filename))

        super().generate()

        self.output.append(None, \
"""
%%% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
%%% Tango: End of top-level document
\\end{document}
""")

    def generate_preamble(self):
        return \
"""\
%%% >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
%%% Tango latex preamble starts here

\documentclass{class_options}{{{document_class}}}

%%% Tango only supports extended utf-8 encodings
\\usepackage{{ucs}}
\\usepackage[utf8x]{{inputenc}}

%%% <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
%%% Tango latex preamble stops here
""".format(class_options=("["+(",".join(self.latex_config.class_options))+"]") if self.latex_config.class_options else "",
           document_class=self.latex_config.document_class)

class DefaultLatexCommandGenerator(CommandGenerator):
    def __init__(self):
        pass
    
    def enter_command(self, generator, cmd):
        opts_str = "" if cmd.cmd_opts is None else "[{}]".format(cmd.cmd_opts if cmd.cmd_opts else "")
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
        self.verb_chars = [ '|', '!', '+', '-', '/', '<', '>' ] # TODO: a more systematic treatment ?

    def on_preformated(self, generator, preformated):
        if preformated.lang == "inline":
            for verb_char in self.verb_chars:
                if verb_char not in preformated.text:
                    generator.output.append(preformated.start_pos.lpos, r"\verb{0}{1}{0}".format(verb_char, preformated.text))
                    return # don't escape too much

                # no available verbatim character
                raise GenerateError("All verbatim characters used", preformated.start_pos, preformated.end_pos)

        else: # output as text (XXX: is this ok ?)
            generator.output.append(preformated.start_pos.lpos, preformated.text)
        
class LatexSpacesGenerator(SpacesGenerator):
    def __init__(self):
        pass

    def on_spaces(self, generator, spaces):
        generator.output.append(None, spaces.spaces)


class LatexNewlinesGenerator(NewlinesGenerator):
    def __init__(self):
        pass

    def on_newlines(self, generator, newlines):
        generator.output.newline(None)
        if len(newlines.newlines) >= 2:
            generator.output.newline(None)





