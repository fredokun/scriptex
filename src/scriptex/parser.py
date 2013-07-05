'''
The ScripTex parser
'''

from collections import OrderedDict

if __name__ == "__main__":
    import sys
    sys.path.append("../")

import scriptex.lexer as lexer
from scriptex.parselib import AbstractParser, Choice, Repeat, Literal, ParsingAlgo
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

        ident_re = "[a-zA-Z_][a-zA-Z_0-9]*"
        
        cmd_ident = lexer.Regexp("command_ident", "\\" + ident_re)
        cmd_ident.excludes = { r"\begin", r"\end" }
        self._register_recognizer(cmd_ident)

        self._register_recognizer(lexer.Regexp("keyval", ident_re + r"(=[^,\]]+)?"))
        
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
            if self.name not in self.parsers:
                raise ValueError("No such parser: {}".format(self.name))

            return self.parsers[self.name].parse(parser)
        

    def ref(self, name):
        self.parsers[name] = ScripTexParser._RefParser(self, name)

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
        
        cmdargs = Optional(ListOf(Literal("keyval"),sep=Literal("comma")))
        cmdbody = Optional(Tuple(Literal("open_curly"), ref("elements"), Literal("close_curly")))

        cmd = Tuple(cmdhead, cmdargs, cmdbody)
        
        element = Choice(cmd,
                         line_comment,
                         newline,
                         spaces)

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
        

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
