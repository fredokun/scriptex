
'''
The basic ScripTex markup language
'''

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
    def __init__(self, markup_type):
        self.markup_type = markup_type

class AbstractElement(AbstractMarkup):
    """The base abstract class for element markups.

    Element markup objects cannot nest.
    """
    def __init__(self, markup_type):
        super().__init__(markup_type)

class AbstractStructure(AbstractMarkup):
    """The base abstract class for structure markups.

    Structure markup objects can (and most often do) nest.
    """
    def __init__(self, markup_type):
        super().__init__(markup_type)

#------------------------------------------------------------------------------#
#   Documents                                                                  #
#------------------------------------------------------------------------------#

def BASE_DOCUMENT_TOKENIZERS():
    tks = [ lexer.CharIn("space-or-newline", ' ', '\t', '\r', '\n'),
            lexer.CharIn("space-not-newline", ' ', '\t'),
            lexer.CharIn("newline-only", '\n')
            ]

class BaseDocument(AbstractStructure):
    def __init__(self):
        super().__init__("document")
        self.tokenizers = BASE_DOCUMENT_TOKENIZERS()
        
#------------------------------------------------------------------------------#
#   Comments                                                                   #
#------------------------------------------------------------------------------#

class LineComment(AbstractElement):
    def __init__(self):
        super().__init__("line_comment")
        self.tokenizers = [ lexer.Regexp('line-comment', '%.*') ]
        self.parser = parser.Literal(token_type='line-comment')    

    def on_parse(self, translator, parsed):
        pass

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
    def __init__(self, start_pos, end_pos, name, level, title):
        AbstractSection.__init__(self, start_pos, end_pos)
        self._name = name
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
    def __init__(self, start_pos, end_pos, title):
        Section.__init__(self, start_pos, end_pos, "paragraph", 0, title)
        
#------------------------------------------------------------------------------#
#   Text elements                                                              #
#------------------------------------------------------------------------------#

class Text(AbstractElement):
    """Representation of a textual element: character, word, etc.
    In ScripTex the content of a textual element must be encoded in UTF-8.
    """
    def __init__(self, start_pos, end_pos, content):
        super().__init__(start_pos, end_pos)
        self._content = content

    @property
    def content(self):
        return self._content

    def __repr__(self):
        return "Text({})".format(self.content)

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

