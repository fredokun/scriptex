from tangolib.generator import DocumentGenerator, CommandGenerator, EnvironmentGenerator, SectionGenerator
from tangolib.generator import TextGenerator, PreformatedGenerator, SpacesGenerator, NewlinesGenerator

class XmlOutput:
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
        self.output.append((None, self.output_line, "<!-- -->"))    #CN:modified
        self.newline(None)
        self.output.append((orig_pos, self.output_line, "<!-- Tango Line: {} -->".format(orig_pos)))    #CN:modified
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

class XmlDocumentGenerator(DocumentGenerator):
    def __init__(self,document):
        super().__init__(document)
        
    
    def generate(self):
        self.output = XmlOutput()
        self.output.append(None,"<!-- Beginning of the xml document -->\n")    #CN:modified
        self.output.append(None,self.document.toxml())
        self.output.append(None,"<!-- End of the document -->\n")    #CN:modified
