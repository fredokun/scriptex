'''
The ScripTex parser
'''

from collections import OrderedDict

if __name__ == "__main__":
    import sys
    sys.path.append("../")

import scriptex.lexer as lexer
from scriptex.parselib \
   import AbstractParser, Choice, Repeat, Tuple, \
          Optional, ListOf, Literal, ParsingAlgo
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
        self._register_recognizer(lexer.Char("open_curly", '{'))
        self._register_recognizer(lexer.Char("close_curly", '}'))
        self._register_recognizer(lexer.Char("open_square", '['))
        self._register_recognizer(lexer.Char("close_square", ']'))
        self._register_recognizer(lexer.Char("comma", ','))

        ident_re = r"[a-zA-Z_][a-zA-Z_0-9]*"
        
        cmd_ident = lexer.Regexp("command_ident", r"\\" + ident_re)
        cmd_ident.excludes = { r"\begin", r"\end" }
        self._register_recognizer(cmd_ident)

        self._register_recognizer(lexer.Regexp("keyval", "(" + ident_re + r")(=[^,\]=]+)?"))

        # the text recognizer comes last
        self._register_recognizer(lexer.Regexp("text", r"[^ \n\r\t\f\v\\{}\[\]\(\)]+"))

        
    def _register_parser(self, name, parser):
        self.parsers[name] = parser


    class _RefParser(AbstractParser):
        def __init__(self, parser, name):
            super().__init__()
            self.parser = parser
            self.name = name

        @property
        def describe(self):
            return "<{}>".format(self.name)

        def do_parse(self, parser):
            if self.name not in self.parser.parsers:
                raise ValueError("No such parser: {}".format(self.name))

            return self.parser.parsers[self.name].parse(parser)
        

    def ref(self, name):
        if name in self.parsers:
            return self.parsers[name]
        
        parser =  ScripTexParser._RefParser(self, name)
        self.parsers[name] = parser
        return parser
        

    def build_parsers(self):
        line_comment = Literal("line_comment")
        line_comment.on_parse = lambda _,tok : markup.LineComment(tok.value.group(0)[1:], tok.start_pos, tok.end_pos)
        newline = Literal("end_of_line")
        newline.skip = True
        spaces = Literal("spaces")
        spaces.skip = True

        # a command has the general form
        #  \cmd
        #  \cmd[ley1=val1,...,keyN=valN]
        #  \cmd{<body>}
        #  \cmd[key1=val1,...,keyN=valN]{<body>}

        cmdhead = Literal("command_ident")
        keyval = Literal("keyval")
        
        cmdargs = Optional(ListOf(keyval,open_=Literal("open_square"),sep=Literal("comma"), close=Literal("close_square")))
        cmdbody = Optional(Tuple(Literal("open_curly"), self.ref("elements"), Literal("close_curly")))

        cmd = Tuple(cmdhead, cmdargs, cmdbody)
        cmd.on_parse = lambda _,tok : command_on_parse(tok)

        text = Literal("text")
        text.on_parse = lambda _,tok: markup.Text(tok.value.group(0), tok.start_pos, tok.end_pos)
        
        element = Choice(cmd,
                         line_comment,
                         newline,
                         spaces,
                         text)

        elements = Repeat(element)

        self._register_parser("elements", elements)
        
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
        

def command_on_parse(parsed):
    cmd = parsed[0].value.group(0)
    keyvals = [ tok for tok in parsed[1] if tok.type == "keyval"]
    body = parsed[2][1]
    return markup.Command(cmd, keyvals, body, parsed[0].start_pos, parsed[2][2].end_pos)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
