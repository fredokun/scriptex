"""Base for HTML generation.
"""


from tangolib.generator import DocumentGenerator, CommandGenerator, EnvironmentGenerator, SectionGenerator
from tangolib.generator import TextGenerator, PreformatedGenerator, SpacesGenerator, NewlinesGenerator

class HTMLOutput:
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
        # self.output.append((None, self.output_line, "<!-- -->"))
        self.newline(None)
        #self.output.append((orig_pos, self.output_line, "<!--  Tango Line: {} -->".format(orig_pos)))
        #self.newline(None)
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

class HTMLDocumentGenerator(DocumentGenerator):
    def __init__(self, document, HTML_config):
        super().__init__(document)
        # A verifier : config ?? c'est quoi ?        
        self.HTML_config = HTML_config


        self.default_command_generator = DefaultHTMLCommandGenerator()
        self.default_environment_generator = DefaultHTMLEnvironmentGenerator()
        self.default_section_generator = DefaultHTMLSectionGenerator()
        self.text_generator = HTMLTextGenerator()
        self.preformated_generator = HTMLPreformatedGenerator()
        self.spaces_generator = HTMLSpacesGenerator()
        self.newlines_generator = HTMLNewlinesGenerator()

        
    def straighten_configuration(self):
        if not self.HTML_config.document_class:
            self.HTML_config.document_class = guess_document_class(self.document)

    def generate(self):
        self.HTML_config.check_configuration()

        self.output = HTMLOutput()

        preamble = self.generate_preamble()
        self.output.append(None, preamble)

        self.output.append(None, \
"""
    <!-- Tango: Beginning of top-level document -->
    <!-- Tango: File = '{}' -->
    <body>
""".format(self.document.filename))

        super().generate()

        self.output.append(None, \
"""
    </body>
    <!-- Tango: End of top-level document -->
</html>
""")

    def generate_preamble(self):
        return \
"""\
<!-- Tango HTML preamble starts here -->

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>HTML generator</title>
    </head>
    <!-- Tango HTML preamble stops here -->
"""

################################################################
class DefaultHTMLCommandGenerator(CommandGenerator):
    def __init__(self):
        pass
    
    def enter_command(self, generator, cmd):
        opts_str = "" if cmd.cmd_opts is None else "{}".format(cmd.cmd_opts)
        open_str = "" if not cmd.content else ""
        if (cmd.cmd_name == "snip") :
            generator.output.append(cmd.start_pos.lpos,"<b>")
        else :
            generator.output.append(cmd.start_pos.lpos, """<div class="command" name="{}" options="{}" open="{}">""".format(cmd.cmd_name, opts_str, open_str))
            generator.output.append(cmd.start_pos.lpos, """\n<!-- {} -->\n""".format(str(cmd.content)))
            #exec(str(cmd.content).replace(">>>","")

    def exit_command(self, generator, cmd):
        if (cmd.cmd_name == "snip") :
            generator.output.append(cmd.start_pos.lpos,"</b>")
        else :
            if cmd.content:
                if cmd.end_pos.lpos != cmd.start_pos.lpos:
                    generator.output.append(cmd.end_pos.lpos, "</div>")
                else:
                    generator.output.append(None, "</div>")
##############################################################


class DefaultHTMLEnvironmentGenerator(EnvironmentGenerator):
    def __init__(self):
        pass
    
    def enter_environment(self, generator, env):
        opts_str = "" if env.env_opts is None else "{}".format(env.env_opts)
        generator.output.append(env.start_pos.lpos, """<div class="environnement" name="{}" options="{}">""".format(env.env_name,opts_str))
        #generator.output.newline(None)
        generator.output.append(env.start_pos.lpos, '<p>\n')

    def exit_environment(self, generator, env):
        generator.output.append(env.end_pos.lpos, "</p>\n")
        #generator.output.newline(None)
        generator.output.append(env.end_pos.lpos, "</div>")

# Finir la suite

class DefaultHTMLSectionGenerator(SectionGenerator):
    def __init__(self):
        pass
    
    def enter_section(self, generator, sec):
        generator.output.append(sec.start_pos.lpos,  """<div class="section" name="{}" title="{}">\n""".format(sec.section_name, sec.section_title))
        #generator.output.newline(None)
        generator.output.append(env.start_pos.lpos, '<p>\n')

    def exit_section(self, generator, sec):
        generator.output.append(env.end_pos.lpos, "</p>\n")
        #generator.output.newline(None)
        generator.output.append(env.end_pos.lpos, "</div>\n")


class HTMLTextGenerator(TextGenerator):
    def __init__(self):
        pass

    # def tohtml(self, indent_level=0, indent_string="  "):
        # s = self.text
        # edits = [('é', '&eacute;'), ('à', '&agrave;'), ('è', '&egrave;')] # etc.
        # for search, replace in edits:
            # s = s.replace(search, replace)
        # ret = indent_string * indent_level
        # ret += '<p {}>{}</p>\n'.format(self.positions_tohtml(), s)
        # return ret
        
    def on_text(self, generator, text):
        generator.output.append(text.start_pos.lpos,"""{}""".format(text.text))


class HTMLPreformatedGenerator(PreformatedGenerator):
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
        
class HTMLSpacesGenerator(SpacesGenerator):
    def __init__(self):
        pass

    def on_spaces(self, generator, spaces):
        generator.output.append(None, " ")


class HTMLNewlinesGenerator(NewlinesGenerator):
    def __init__(self):
        pass

    def on_newlines(self, generator, newlines):
        lpos = newlines.start_pos.lpos
        generator.output.append(None,"<br />")
        for _ in newlines.newlines:
            generator.output.newline(None)
            lpos += 1