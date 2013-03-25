
#------------------------------------------------------------------------------#
#   Abstract blocks                                                            #
#------------------------------------------------------------------------------#

class AbstractBlock:
    '''Abstract representation of a document block.
    '''
    def __init__(self, start_pos, end_pos):
        self._start_pos = start_pos
        self._end_pos = end_pos

    @property
    def start_pos(self):
        return self._start_pos

    @property
    def end_pos(self):
        return self._end_pos

class AbstractElement(AbstractBlock):
    '''Common representation of non-sectionning blocks, or elements.
    '''
    def __init__(self, start_pos, end_pos):
        AbstractBlock.__init__(self, start_pos, end_pos)

class AbstractSection(AbstractBlock):
    '''Common representation of sectionning blocks.
    A section is simply a container block associated
    to a list of sub-blocks.
    '''
    def __init__(self, start_pos, end_pos):
        AbstractBlock.__init__(self, start_pos, end_pos)
        self._kind = self.__class__.__name__
        self._blocks = []

    @property
    def kind(self):
        return self._kind

    def __repr__(self):
        return "Section({0})\{{1}\}".format(self.kind, repr(self._blocks))

#------------------------------------------------------------------------------#
#   Comments                                                                   #
#------------------------------------------------------------------------------#
        
class LineComment(AbstractElement):
    """Representation of line comments.
    A line comment starts with a '%' character followed by at least a space,
    and terminates at the end of the line.
    A line comment can also be introduced with the \comment{...} command.
    In this case the formatting within the comment is preserved, however
    it is still a non-nesting comment.
    """
    def __init__(self, start_pos, end_pos, comment):
        AbstractElement.__init__(self, start_pos, end_pos)
        self.comment = comment

    def __repr__(self):
        return 'LineComment("{}")'.format(self.comment)
    
class NestComment(AbstractSection):
    """Representation of nested comments.
    A nested comment can be introduced with the syntax
    %{   ... content ... %}
    or in the latex style :
    \begin{comment} ... \end{comment}
    The interior of the comment will be parsed as usual,
     however the processing will be disabled.
    """
    def __init__(self, start_pos, end_pos):
        AbstractSection.__init__(self, start_pos, end_pos)

#------------------------------------------------------------------------------#
#   Paragraphs and sections                                                    #
#------------------------------------------------------------------------------#

class Section(AbstractSection):
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

class Math(AbstractSection):
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

