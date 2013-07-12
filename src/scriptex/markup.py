
'''
The basic ScripTex markup language
'''

if __name__ == "__main__":
    import sys
    sys.path.append("../")


class AbstractMarkup:
    """Abstract representation of markup objects.
        
    A markup object is roughly like a function that takes
    a text to parse, detects a given markup in the input,
    and produces some output and/or effects based on the parsed
    information.  The most common result of a markup detection is
    to return an abstract syntax tree built from the parsed input.

    Note that markup objects can be nested.
    
    Internally, a markup embeds a parser and an abstract syntax
    tree builder.
    """
    def __init__(self, markup_type, start_pos, end_pos):
        self.markup_type = markup_type
        self.start_pos = start_pos
        self.end_pos = end_pos

class AbstractElement(AbstractMarkup):
    """The base abstract class for element markups.
    
    Element markup objects cannot nest.
    """
    def __init__(self, markup_type, start_pos, end_pos):
        super().__init__(markup_type, start_pos, end_pos)

class AbstractStructure(AbstractMarkup):
    """The base abstract class for structure markups.

    Structure markup objects can (and most often do) nest.
    """
    def __init__(self, markup_type, start_pos, end_pos):
        super().__init__(markup_type, start_pos, end_pos)

#------------------------------------------------------------------------------#
#   Documents                                                                  #
#------------------------------------------------------------------------------#

class Document(AbstractStructure):
    def __init__(self, body, start_pos, end_pos):
        super().__init__("document", start_pos, end_pos)
        self.body = body

    def __str__(self):
        return "Document({})".format(self.body)

    def __repr__(self):
        return str(self)
        
#------------------------------------------------------------------------------#
#   Comments                                                                   #
#------------------------------------------------------------------------------#

class LineComment(AbstractElement):
    def __init__(self, comment, start_pos, end_pos):
        super().__init__("line_comment", start_pos, end_pos)
        self.comment = comment
        
    def __str__(self):
        return "LineComment({},start={},end={})".format(self.comment, self.start_pos, self.end_pos)

    def __repr__(self):
        return str(self)
    

class NestComment(AbstractStructure):
    """Representation of nested comments.
    A nested comment can be introduced with the syntax
    %{   ... content ... %}
    or in the latex style :
    \begin{comment} ... \end{comment}
    The interior of the comment will be parsed as usual,
     however the processing will be disabled (or not ?).
    """
    def __init__(self):
        AbstractStructure.__init__(self, start_pos, end_pos)


#------------------------------------------------------------------------------#
#   Paragraphs and sections                                                    #
#------------------------------------------------------------------------------#

class Section(AbstractStructure):
    """Representation of sections: chapter, section, etc.
    Each section has a level with the following constraints:
    - a paragraph has level 0 and cannot contain any sub-section but
      can be put at any level.
    - a section of level N can only have subsections of level N+1 (or paragraphs).

    The first syntax to introduce a paragraph is to start with a blank line,
    and finish with another blank line  (that can serve as a delimiter for the next paragraph).
    A paragraph can also start with \paragraph{title}  to give it a title (as in latex).
    The third syntax is  \begin{paragraph}[options]  ... contents .... \end{paragraph}.

    For sections of level >= N the first syntax is :
    -  '= title =' for a section of level 1
    -  '== title =='  for a section of level 2
    -  '=== title ==='  for a section of level 3
    - etc.

    The second syntax is  \begin{section}[level=N]  \end{section}.
    User commands can be provided for default sectionning, e.g. as in latex

    The thid syntax is latex-inspired :   \chapter{title},  \section{title}, etc.
    """
    def __init__(self, name, level, title, start_pos, end_pos):
        super().__init__(name,start_pos, end_pos)
        self._level = level
        self._title = title

    @property
    def name(self):
        return self._name

    @property
    def level(self):
        return self._level

    @property
    def title(self):
        return self._title

class Paragraph(Section):
    """Representation of paragraphs, a specific kind of section.
    """
    def __init__(self, title, elements, start_pos, end_pos):
        Section.__init__(self, "paragraph", 0, title, start_pos, end_pos)
        self.elements = elements

    def __repr__(self):
        return "Paragraph(elements={})".format(repr(self.elements))
        
#------------------------------------------------------------------------------#
#   Text elements                                                              #
#------------------------------------------------------------------------------#

class Text(AbstractElement):
    """Representation of a textual element: character, word, etc.
    In ScripTex the content of a textual element must be encoded in UTF-8.
    """
    def __init__(self, content, start_pos, end_pos):
        super().__init__("text", start_pos, end_pos)
        self._content = content

    @property
    def content(self):
        return self._content

    def __repr__(self):
        return "Text({})".format(self.content)


#------------------------------------------------------------------------------#
#   (unprocessed) Commands                                                     #
#------------------------------------------------------------------------------#

class Command(AbstractElement):
    """Representation of commands.
    """
    def __init__(self, cmd, args, body, start_pos, end_pos):
        super().__init__("command", start_pos, end_pos)
        self.cmd = cmd
        self.args = {}
        for arg in args:
            key = arg.value.group(1)
            val = arg.value.group(2)
            self.args[key] = Command.Arg(self, key,val, arg.start_pos, arg.end_pos)
        self.body = body
        
    class Arg:
        def __init__(self, cmd, key, val, start_pos, end_pos):
            self.cmd = cmd
            self.key = key
            self.val = val
            self.start_pos = start_pos
            self.end_pos = end_pos

        def __str__(self):
            return "{}={}".format(self.key, self.val)

        def __repr__(self):
            return str(self)

    def __repr__(self):
        return "Command(cmd={},args=[{}],body={})".format(self.cmd, [ str(self.args[key]) for key in self.args], self.body)
        
#------------------------------------------------------------------------------#
#   (unprocessed) Environments                                                 #
#------------------------------------------------------------------------------#

class Environment(AbstractStructure):
    """Representation of environments.
    """
    def __init__(self, env_name, args, components, start_pos, end_pos):
        super().__init__("environment", start_pos, end_pos)
        self.env_name = env_name
        self.args = {}
        for arg in args:
            key = arg.value.group(1)
            val = arg.value.group(2)
            self.args[key] = Command.Arg(self, key,val, arg.start_pos, arg.end_pos)
        self.components = components
        
    def __repr__(self):
        return "Environment(env_name=\"{}\",args={},components={})".format(self.env_name, self.args, self.components)

#------------------------------------------------------------------------------#
#   Math elements                                                              #
#------------------------------------------------------------------------------#

class Math(AbstractStructure):
    """Reprensentation of math formulas.
    A math formula can be either of style:
    - inline using the notation $ ... formula ... $   or \( ... formula ... \)
      or   \math{ ... formula ... }
    - offline using the notation $$ ... formula ... $$  or \[ ... formula ... \]
      or   \begin{math} ... formula ... \end{math}
    """
    def __init__(self, start_pos, end_pos, style='inline'):
        AbstractSection.__init__(self, start_pos, end_pos)
        self._style = style

    @property
    def style(self):
        return self._style

