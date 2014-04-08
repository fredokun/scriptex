
import tangolib.optparse as optparse

class MarkupError(Exception):
    pass

class AbstractMarkup:
    def __init__(self, doc, start_pos, end_pos):
        self.doc = doc
        self.start_pos = start_pos
        self.end_pos = end_pos
        
    def toxml(self, indent_level=0, indent_string=""):
        raise NotImplementedError("Abstract method")

    def pos_toxml(self, pos_name, pos):
        if pos is None:
            return ""
        return '{}="{}"'.format(pos_name, str(pos))

    def is_markup(self):
        return False

    def positions_toxml(self):
        return '{} {}'.format(self.pos_toxml("start_pos", self.start_pos), self.pos_toxml("end_pos", self.end_pos))

class Markup(AbstractMarkup):
    def __init__(self, doc, markup_type, start_pos, end_pos):
        super().__init__(doc, start_pos, end_pos)
        self.markup_type = markup_type

        self.content = []

    def content_toxml(self, indent_level=0, indent_string="  "):
        #return "".join((element.toxml(indent_level + 1, indent_string) if isinstance(element,AbstractMarkup) else str(element) for element in self.content))
        return "".join((element.toxml(indent_level + 1, indent_string) for element in self.content))


    def append(self, element):
        self.content.append(element)

    def is_markup(self):
        return True

class Document(Markup):
    def __init__(self, filename, lex):
        super().__init__(None, "document", lex.pos, None)
        self.filename = filename
        self.lex = lex
        self.def_commands_ = dict() # dictionary for defined commands
        self.def_environments_ = dict() # dictionary for defined environments

    def register_def_command(self, def_cmd_name, def_cmd):
        self.def_commands_[def_cmd_name] = def_cmd

    def known_def_commands(self):
        return self.def_commands_.keys()

    def fetch_def_command(self, def_cmd_name):
        return self.def_commands_[def_cmd_name]

    def register_def_environment(self, def_env_name, def_env):
        self.def_environments_[def_env_name] = def_env

    def known_def_environments(self):
        return self.def_environments_.keys()

    def fetch_def_environment(self, def_env_name):
        return self.def_environments_[def_env_name]

    def __repr__(self):
        return "Document(content={})".format(repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<document filename="{}" {}>\n'.format(self.filename, self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + '</document>\n'
        return ret

class ChildDocument(Document):
    def __init__(self, parent_doc,  filename, sublex):
        super().__init__(filename, sublex)
        self.doc = parent_doc

    def register_def_command(self, def_cmd_name, def_cmd):
        # delegate to main document
        self.doc.register_def_command(def_cmd_name, def_cmd)

    def known_def_commands(self):
        return self.doc.known_def_commands()

    def fetch_def_command(self, def_cmd_name):
        return self.doc.fetch_def_command(def_cmd_name)

    def register_def_environment(self, def_env_name, def_env):
        # delegate to main document
        self.doc.register_def_environment(def_env_name, def_env)

    def known_def_environments(self):
        return self.doc.known_def_environments()

    def fetch_def_environment(self, def_env_name):
        return self.doc.fetch_def_environment(def_env_name)
    
class SubDocument(ChildDocument):
    def __init__(self, parent_doc, filename, start_pos, sublex):
        super().__init__(parent_doc, filename, sublex)
        self.markup_type = "subdoc"
        self.start_pos = start_pos
        self.sublex = sublex

    def __repr__(self):
        return "SubDocument(content={})".format(repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<subdoc filename="{}" {}>\n'.format(self.filename, self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + '</subdoc>\n'
        return ret

class MacroCommandDocument(ChildDocument):
    def __init__(self, parent_doc, filename, start_pos, end_pos, sublex):
        super().__init__(parent_doc, filename, sublex)
        self.markup_type = "macrocmddoc"
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.sublex = sublex

    def __repr__(self):
        return "MacroCmdDocument(content={})".format(repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<subdoc filename="{}" {}>\n'.format(self.filename, self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + '</subdoc>\n'
        return ret

class Command(Markup):
    def __init__(self, doc, cmd_name, cmd_opts, header_start_pos, header_end_pos, preformated=False):
        super().__init__(doc, "command", header_start_pos, header_end_pos)

        self.cmd_name = cmd_name

        if not cmd_opts:
            cmd_opts = ""
            
        if isinstance(cmd_opts,str):
            self.cmd_opts = optparse.parse_options(cmd_opts)
        else:
            try:
                ks = cmd_opts.keys()
                self.cmd_opts = cmd_opts
            except:
                raise MarkupError("Command options is not a string of mapping type: {}".cmd_opts)


        self.header_end_pos = header_end_pos
        self.preformated = preformated
        self.arguments = []

    def add_argument(self, arg):
        self.append(arg) # for standard content traversal
        self.arguments.append(arg) # for indexed acccess to arguments

    def __repr__(self):
        return "Command(cmd_name={}, cmd_opts={}, preformated={}, content={})".format(self.cmd_name, self.cmd_opts, self.preformated, repr(self.content))

    def opts_toxml(self):
        return '"{}"'.format(self.cmd_opts)

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<command name="{}" opts={} preformated="{}" {} >\n'.format(self.cmd_name, self.opts_toxml(), str(self.preformated), self.positions_toxml())
        if self.preformated:
            ret += "".join(((indent_string * (indent_level + 1)) + line + "\n" for line in self.content.splitlines()))
        else:
            ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</command>\n"
        return ret

class CommandArg(Markup):
    def __init__(self, doc, cmd, start_pos):
        super().__init__(doc, "command_arg", start_pos, start_pos)
        self.cmd = cmd

    def __repr__(self):
        return "CommandArg(cmd_name={}, content={})".format(self.cmd.cmd_name, repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<command_arg {} >\n'.format(self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</command_arg>\n"
        return ret


class Environment(Markup):
    def __init__(self, doc, env_name, env_opts, header_start_pos, header_end_pos):
        super().__init__(doc, "environment", header_start_pos, None)
        self.env_name = env_name

        if not env_opts:
            env_opts = ""
            
        if isinstance(env_opts,str):
            self.env_opts = optparse.parse_options(env_opts)
        else:
            try:
                ks = env_opts.keys()
                self.env_opts = env_opts
            except:
                raise MarkupError("Environment options is not a string of mapping type: {}".env_opts)
                
        self.header_end_pos = header_end_pos
        self.arguments = []

    def add_argument(self, arg):
        self.arguments.append(arg) # for indexed acccess to arguments

    def __repr__(self):
        return "Environment(env_name={},env_opts={},content={})".format(self.env_name, self.env_opts, repr(self.content))

    def opts_toxml(self):
        return '"{}"'.format(self.env_opts)

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<environment name="{}" opts={} {} >\n'.format(self.env_name, self.opts_toxml(), self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</environment>\n"
        return ret

class EnvArg(Markup):
    def __init__(self, doc, env, start_pos):
        super().__init__(doc, "env_arg", start_pos, start_pos)
        self.env = env

    def __repr__(self):
        return "EnvArg(env_name={}, content={})".format(self.env.env_name, repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<env_arg {} >\n'.format(self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</env_arg>\n"
        return ret

class MacroEnvDocument(ChildDocument):
    def __init__(self, parent_doc, filename, start_pos, end_pos, sublex):
        super().__init__(parent_doc, filename, sublex)
        self.markup_type = "macroenvdoc"
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.sublex = sublex

    def __repr__(self):
        return "MacroEnvDocument(content={})".format(repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<subdoc filename="{}" {}>\n'.format(self.filename, self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + '</subdoc>\n'
        return ret

class MacroEnvFooterDocument(ChildDocument):
    def __init__(self, parent_doc, filename, start_pos, end_pos, sublex):
        super().__init__(parent_doc, filename, sublex)
        self.markup_type = "macroenvfooterdoc"
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.sublex = sublex

    def __repr__(self):
        return "MacroEnvFooterDocument(content={})".format(repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<subdoc filename="{}" {}>\n'.format(self.filename, self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + '</subdoc>\n'
        return ret

class Section(Markup):
    def __init__(self, doc, section_title, section_name, section_depth, header_start_pos, header_end_pos):
        super().__init__(doc, "section", header_start_pos, None)
        self.section_title = section_title
        self.section_name = section_name
        self.section_depth = section_depth
        self.header_end_pos = header_end_pos

    def __repr__(self):
        return "Section(section_title={},section_name={},section_depth={},content={})".format(self.section_title, self.section_name, self.section_depth, repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<section title="{}" name="{}" depth="{}" {} >\n'.format(self.section_title, self.section_name, str(self.section_depth), self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</environment>\n"
        return ret


class Text(AbstractMarkup):
    def __init__(self, doc, text, start_pos, end_pos):
        super().__init__(doc, start_pos, end_pos)
        self.text = text
        self.markup_type = "text"

    def __repr__(self):
        return 'Text("{}")'.format(self.text)

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<text {}>{}</text>\n'.format(self.positions_toxml(), self.text)
        return ret


class Preformated(AbstractMarkup):
    def __init__(self, doc, text, lang, start_pos, end_pos):
        super().__init__(doc, start_pos, end_pos)
        self.text = text
        self.lang = lang

        self.markup_type = "preformated"

    def __repr__(self):
        return 'Preformated("{}")'.format(self.text)
    
    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<preformated lang="{}" {} >\n'.format(self.cmd_name, self.positions_toxml())
        ret += "".join(((indent_string * (indent_level + 1)) + line + "\n" for line in self.text.splitlines()))
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</preformated>\n"
        return ret

class Newlines(AbstractMarkup):
    def __init__(self, doc, newlines, start_pos, end_pos):
        super().__init__(doc, start_pos, end_pos)
        self.newlines = newlines

        self.markup_type = "newlines"

    def __repr__(self):
        return "Newlines({})".format(len(self.newlines))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<newline count="{}" {} />\n'.format(len(self.newlines), self.positions_toxml())
        return ret


class Spaces(AbstractMarkup):
    def __init__(self, doc, spaces, start_pos, end_pos):
        super().__init__(doc, start_pos, end_pos)
        self.spaces = spaces
        self.markup_type = "spaces"

    def __repr__(self):
        return "Spaces({})".format(len(self.spaces))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<space count="{}" {} />\n'.format(len(self.spaces), self.positions_toxml())
        return ret

class SkipMarkup(AbstractMarkup):
    def __init__(self, doc, start_pos, end_pos):
        super().__init__(doc, start_pos, end_pos)
        self.markup_type = "skip"

    def __repr__(self):
        return "SkipMarkup()"

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<skip {} />\n'.format(self.positions_toxml())
        return ret


def search_content_by_types(content, search_types):
    for element in content:
        if element.markup_type in search_types:
            return element
        else:
            try:
                if element.content:
                    found = search_content_by_types(element.content, search_types)
                    if found:
                        return found
            except:
                pass

    return None

def search_content_by_type(content, search_type):
    return search_content_by_types(content, {search_type})
