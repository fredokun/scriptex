"""Base for HTML generation.
"""
from tangolib.generator import DocumentGenerator, CommandGenerator, EnvironmentGenerator, SectionGenerator
from tangolib.generator import TextGenerator, PreformatedGenerator, SpacesGenerator, NewlinesGenerator
from tangolib.markup import Markup, Text, Preformated, Spaces, Newlines, SkipMarkup

import json
from os import path

class HTMLTemplateError(Exception):
    pass


class HTMLTemplate:
    
    def __init__(self,data):
        self.data=data

    def getValue(self,aType,key):
        if key in self.data[aType]:
            return self.data[aType][key]
        elif "default" in self.data[aType]:
            return self.data[aType]["default"]
        else:
            raise HTMLTemplateError("Key and default value are undefined")

class HTMLTemplateFactory:

    @staticmethod
    def createBasicTemplate():
        filePath = path.realpath("../src/tangolib/generators/html/template/basic.template")
        with open(filePath) as content_file:
            content=content_file.read()

        return HTMLTemplate(json.loads(content))


class HTMLOutput:
    def __init__(self):
        self.output = []
        self.output_line = 1
        self.pos_map = dict()
        self.last_pos = 1

        self.ident_level = 4
        self.isNewLine = False

    def addIdentLevel(self):
        self.ident_level += 4

    def retrieveIdentLevel(self):
        self.ident_level -= 4

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

        if self.isNewLine :
            indent_text = []
            for i in range(self.ident_level):
                indent_text.append(" ")
            indent_text.append(text)
        else:
            indent_text=text

        self.output.append((orig_pos, self.output_line, ''.join(indent_text)))
        if self.output_line not in self.pos_map:
            self.pos_map[self.output_line] = orig_pos

        self.isNewLine=False

    def newline(self, orig_pos):
        self.isNewLine=True
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

        self.HTML_config = HTML_config


        self.default_command_generator = DefaultHTMLCommandGenerator()
        self.default_environment_generator = DefaultHTMLEnvironmentGenerator()
        self.default_section_generator = DefaultHTMLSectionGenerator()
        self.text_generator = HTMLTextGenerator()
        self.preformated_generator = HTMLPreformatedGenerator()
        self.spaces_generator = HTMLSpacesGenerator()
        self.newlines_generator = HTMLNewlinesGenerator()
        self.template = HTMLTemplateFactory.createBasicTemplate()
      
        
    def straighten_configuration(self):
        if not self.HTML_config.document_class:
            self.HTML_config.document_class = guess_document_class(self.document)



    def generateHTML(self):
        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        
        self.markup_stack = [(self.document, 0)]
        self.environment_stack = []
        self.command_stack = []
        self.section_stack = []
        self.onItem = None

        while self.markup_stack:
            self.markup, self.content_index = self.markup_stack.pop()
            if self.content_index == -1: # command/env not generated
                if self.markup.markup_type == "command":
                    if self.markup.cmd_name in self.cmd_generators:
                        if self.markup.cmd_name == "item" or self.markup.cmd_name == "enumerate" :
                            self.onItem=self.markup
                        self.cmd_generators[self.markup.cmd_name].enter_command(self, self.markup)
                    elif self.default_command_generator is not None:
                        if self.markup.cmd_name == "item" or self.markup.cmd_name == "enumerate" :
                            self.onItem=self.markup
                        self.default_command_generator.enter_command(self, self.markup)
                    if self.markup.preformated:
                        if self.markup.cmd_name in self.cmd_generators:
                            self.cmd_generators[self.markup.cmd_name].exit_command(self, self.markup)
                        elif self.default_command_generator is not None:
                            self.default_command_generator.exit_command(self, self.markup)
                    else:
                        self.command_stack.append(self.markup)
                elif self.markup.markup_type == "environment":
                    if self.markup.env_name in self.env_generators:
                        self.env_generators[self.markup.env_name].enter_environment(self, self.markup)
                    elif self.default_environment_generator is not None:
                        self.default_environment_generator.enter_environment(self, self.markup)
                    self.environment_stack.append(self.markup)
                elif self.markup.markup_type == "section":
                    if 0 in self.sec_generators:
                        self.sec_generators[0].enter_section(self, self.markup)
                    elif self.markup.section_depth in self.sec_generators:
                        self.sec_generators[self.markup.section_depth].enter_section(self, self.markup)
                    elif self.default_section_generator is not None:
                        self.default_section_generator.enter_section(self, self.markup)
                    self.section_stack.append(self.markup)
                if self.markup.markup_type != "command" or not self.markup.preformated:
                    # push back in queue but next time generate content at index 0 (first child)
                    self.markup_stack.append((self.markup, 0))
            else: # generating of markup already started
                if self.content_index == len(self.markup.content):
                    # done generating content
                    if self.markup.markup_type == "command" and self.markup.cmd_name != "item":
                        check_cmd = self.command_stack.pop()
                        assert check_cmd == self.markup,  "invalid command stack (please report)"
                        if self.markup.cmd_name in self.cmd_generators:
                            self.cmd_generators[self.markup.cmd_name].exit_command(self, self.markup)
                        elif self.default_command_generator is not None:
                            self.default_command_generator.exit_command(self, self.markup)
                    elif self.markup.markup_type == "environment":
                        check_env = self.environment_stack.pop()
                        assert check_env == self.markup,  "invalid environment stack (please report)"
                        if self.markup.env_name in self.env_generators:
                            self.env_generators[self.markup.env_name].exit_environment(self, self.markup)
                        elif self.default_environment_generator is not None:
                            self.default_environment_generator.exit_environment(self, self.markup)
                    elif self.markup.markup_type == "section":
                        check_sec = self.section_stack.pop()
                        assert check_sec == self.markup, "Invalid section stack (please report)"
                        if 0 in self.sec_generators:
                            self.sec_generators[0].exit_section(self, self.markup)
                        elif self.markup.section_depth in self.sec_generators:
                           self.sec_generators[self.markup.section_depth].exit_section(self, self.markup)
                        elif self.default_section_generator is not None:
                            self.default_section_generator.exit_section(self, self.markup)
                else: # generate a child
                    child = self.markup.content[self.content_index]
                    self.markup_stack.append((self.markup, self.content_index+1))
                    if isinstance(child, Markup):
                        self.markup_stack.append((child, -1))
                    elif isinstance(child, Text):
                        if self.text_generator is not None:
                            self.text_generator.on_text(self, child)
                    elif isinstance(child, Preformated):
                        if self.preformated_generator is not None:
                            self.preformated_generator.on_preformated(self, child)
                    elif isinstance(child, Spaces):
                        if self.spaces_generator is not None:
                            self.spaces_generator.on_spaces(self, child)
                    elif isinstance(child, Newlines):
                        if self.onItem is not None:
                            if self.onItem in self.cmd_generators:
                                self.cmd_generators[self.onItem.cmd_name].exit_command(self, self.onItem)
                            elif self.default_command_generator is not None:
                                self.default_command_generator.exit_command(self, self.onItem)
                            self.onItem=None
                            
                        if self.newlines_generator is not None:
                            self.newlines_generator.on_newlines(self, child)
                    elif isinstance(child, SkipMarkup):
                        pass # skip markup
                    else:
                        raise GenerateError("Wrong child type: {} (please report)".format(repr(child)))
                        

        # done generating




    def generate(self):
        #import pdb; pdb.set_trace()

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

        self.output.newline(None)
        self.generateHTML()

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


class DefaultHTMLCommandGenerator(CommandGenerator):
    def __init__(self):
        pass
    
    def enter_command(self, generator, cmd):
        opts_str = "" if cmd.cmd_opts is None else "{}".format(cmd.cmd_opts)
        open_str = "" if not cmd.content else ""


        tag = generator.template.getValue("commands",cmd.cmd_name)


        generator.output.append(cmd.start_pos.lpos, """<{} class="command" name="{}" options="{}" open="{}">""".format(tag,cmd.cmd_name, opts_str, open_str))            
        
        generator.output.newline(None)
        generator.output.append(cmd.start_pos.lpos, """<!-- {} -->""".format(str(cmd.content)))
        generator.output.newline(None)

        '''
        if cmd.cmd_name == "item":
            generator.output.append(cmd.start_pos.lpos, """<li class="command" name="{}" options="{}" open="{}">""".format(cmd.cmd_name, opts_str, open_str))
        elif cmd.cmd_name == "url":
            generator.output.append(cmd.start_pos.lpos, """<a class="command" name="{}" options="{}" open="{}" href="{}">""".format(cmd.cmd_name, opts_str, open_str,cmd.arguments[0].content[0].text))
        else :
           generator.output.append(cmd.start_pos.lpos, """<span class="command" name="{}" options="{}" open="{}">""".format(cmd.cmd_name, opts_str, open_str))
        #generator.output.append(cmd.start_pos.lpos, """<!-- {} -->\n""".format(str(cmd.content)))
        '''

    def exit_command(self, generator, cmd):

        tag = generator.template.getValue("commands",cmd.cmd_name)

        if cmd.content:
            if cmd.end_pos.lpos != cmd.start_pos.lpos:
                generator.output.append(cmd.end_pos.lpos,"</{}>".format(tag))
            else:
                generator.output.append(None,"</{}>".format(tag))
        else:
            generator.output.append(None,"</{}>".format(tag))

        '''
        if cmd.cmd_name == "item":
            generator.output.append(None,"</li>")
        elif cmd.cmd_name == "url":
            generator.output.append(None,"</a>")
            

        if cmd.content:
            if cmd.end_pos.lpos != cmd.start_pos.lpos:
                generator.output.append(cmd.end_pos.lpos, "</span>")
            else:
                generator.output.append(None, "</span>")
        '''


class DefaultHTMLEnvironmentGenerator(EnvironmentGenerator):
    def __init__(self):
        pass
    
    def enter_environment(self, generator, env):
        opts_str = "" if env.env_opts is None else "{}".format(env.env_opts)


        tag = generator.template.getValue("environments",env.env_name)

        
        generator.output.append(env.start_pos.lpos, """<{} class="environnement" name="{}" options="{}">""".format(tag,env.env_name,opts_str,env.env_name))
        

        generator.output.addIdentLevel()
        generator.output.newline(None)

        if (env.env_name!="abstract") and (env.env_name != "itemize") and (env.env_name!="enumerate"):
            tag = generator.template.getValue("others","text")
            generator.output.append(env.start_pos.lpos, """<{} class="environnementTitle">{}</{}>""".format(tag,env.env_name,tag))


        

        '''
        if env.env_name == "abstract":
            generator.output.append(env.start_pos.lpos, """<div class="environnement" name="{}" options="{}">""".format(env.env_name,opts_str,env.env_name))
        elif env.env_name == "itemize":
            generator.output.append(env.start_pos.lpos, """<ul class="environnement" name="{}" options="{}">""".format(env.env_name,opts_str,env.env_name))            
        elif env.env_name=="enumerate":
            generator.output.append(env.start_pos.lpos, """<ol class="environnement" name="{}" options="{}">""".format(env.env_name,opts_str,env.env_name))            

        else :
            generator.output.append(env.start_pos.lpos, """<div class="environnement" name="{}" options="{}"><span class="environnementTitle">{}</span>""".format(env.env_name,opts_str,env.env_name))
        '''
        #generator.output.newline(None)<
        #generator.output.append(env.start_pos.lpos, '<p>\n')

    def exit_environment(self, generator, env):
        tag = generator.template.getValue("environments",env.env_name)

        
        generator.output.retrieveIdentLevel()
        generator.output.newline(None)

        generator.output.append(env.end_pos.lpos,"</{}>".format(tag))
        generator.output.newline(None)

        '''
            if env.env_name == "itemize" :
                generator.output.append(env.end_pos.lpos, "</ul>")
            elif env.env_name=="enumerate" :
                generator.output.append(env.end_pos.lpos, "</ol>")
        #generator.output.append(env.end_pos.lpos, "</p>\n")
        #generator.output.newline(None)
            else:
                generator.output.append(env.end_pos.lpos, "</div>")

        #generator.output.append(env.end_pos.lpos, "</p>\n")
        #generator.output.newline(None)
        '''

# Finir la suite

class DefaultHTMLSectionGenerator(SectionGenerator):
    def __init__(self):
        pass
    
    def enter_section(self, generator, sec):

        tag = generator.template.getValue("sections",sec.section_name)

        generator.output.append(sec.start_pos.lpos,  """<{} class="section" name="{}" title="{}">""".format(tag,sec.section_name, sec.section_title))


        generator.output.addIdentLevel()
        generator.output.newline(None)


        tag = generator.template.getValue("others","text")
        generator.output.append(sec.start_pos.lpos,  """<{} class="sectionTitle">{}</{}>""".format(tag,sec.section_title,tag))


        #generator.output.newline(None)
        #generator.output.append(env.start_pos.lpos, '<p>\n')

    def exit_section(self, generator, sec):
        #generator.output.append(env.end_pos.lpos, "</p>\n")
        #generator.output.newline(None)

        generator.output.retrieveIdentLevel()
        generator.output.newline(None)


        tag = generator.template.getValue("sections",sec.section_name)
        generator.output.append(sec.end_pos.lpos, "</{}>".format(tag))

        generator.output.newline(None)
        #generator.output.append(sec.end_pos.lpos, "</div>\n")


class HTMLTextGenerator(TextGenerator):
    def __init__(self):
        pass
        
    def on_text(self, generator, text):
        tag = generator.template.getValue("others","text")
        generator.output.append(text.start_pos.lpos,"""<{} class="text">{}</{}>""".format(tag,text.text,tag))


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
        tag = generator.template.getValue("others","space")
        generator.output.append(None, "{}".format(tag))


class HTMLNewlinesGenerator(NewlinesGenerator):
    def __init__(self):
        pass

    def on_newlines(self, generator, newlines):
        lpos = newlines.start_pos.lpos
        tag = generator.template.getValue("others","newline")
        for _ in newlines.newlines:
            generator.output.newline(None)
            generator.output.append(None,"<{}/>".format(tag))
            lpos += 1
