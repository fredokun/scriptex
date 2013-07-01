'''
The ScripTex parser
'''

import lexer
import parser
import markup


class ScripTexParser:
    def __init__(self):
        self.build_lexers()
        self.build_parsers()


    def build_lexers(self)
        self.lex_block_comment = lexer.Enclosing("%{","%}")
        self.lex_line_comment = lexer.Regexp(r"%(\.)*$")

        self.lex_command = lexer.Regexp(r"\[a-zA-Z_]+[a-zA-Z_0-9]*")

    def build_parsers(self):
        pass
        


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
