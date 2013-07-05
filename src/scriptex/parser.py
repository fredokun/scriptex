'''
The ScripTex parser
'''

from collections import OrderedDict

if __name__ == "__main__":
    import sys
    sys.path.append("../")

import scriptex.lexer as lexer
from scriptex.parselib import Choice, Repeat, Literal, ParsingAlgo
import scriptex.markup as markup

class ScripTexParser:
    def __init__(self):
        self.recognizers = OrderedDict()
        self.parsers = OrderedDict()
        
        self.build_lexers()
        self.build_parsers()

    def _register_recognizer(self,rec):
        self.recognizers[rec.token_type] = rec

    def build_lexers(self):
        self._register_recognizer(lexer.Regexp("line_comment", r"%(.)*$"))
        self._register_recognizer(lexer.Regexp("end_of_line", r'[\n\r]'))
        self._register_recognizer(lexer.Regexp("space", r'[ \t\f\v]'))
        self._register_recognizer(lexer.Regexp("spaces", r'[ \t\f\v]+'))

        self._register_recognizer(lexer.Regexp("escaped", r"\\[^ \t\r\n\f\v]+"))

    def _register_parser(self, name, parser):
        self.parsers[name] = parser

    def build_parsers(self):
        line_comment = Literal("line_comment")
        line_comment.on_parse = lambda _,tok : markup.LineComment(tok.value.group(0)[1:], tok.start_pos, tok.end_pos)
        newline = Literal("end_of_line")
        newline.skip = True
        spaces = Literal("spaces")
        spaces.skip = True

        element = Choice(line_comment,
                         newline,
                         spaces)
        
        self.main_parser = Repeat(element) 

    def parse_from_string(self, input):
        tokens = lexer.Tokenizer(lexer.StringTokenizer(input))
        recs = [rec for _,rec in self.recognizers.items()]
        # print("recs = {}".format([str(r) for r in recs]))
        lex = lexer.Lexer(tokens, *recs)
        parser = ParsingAlgo(lex)
        parser.parser = self.main_parser

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #

        return parser.parse()

    def parse_from_file(self, filename):
        pass
        

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
