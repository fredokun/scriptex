'''
The ScripTex parser
'''

import lexer
import ast

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    def next_token(self):
        return next(self.lexer)

    def putback_token(self, token):
        self.lexer.putback(token)

    @property
    def pos(self):
        return self.lexer.pos


class ParseError:
    def __init__(self, msg, start_pos, end_pos=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.msg = msg

def is_parse_error(value):
    return isinstance(value, ParseError)
    
class AbstractParser:
    def __init__(self):
        # by default the parsed content is not transformed
        self.xform = lambda parser, content: content

    def describe(self):
        raise NotImplementedError("Abstract method")

    def do_parse(self, parser):
        raise NotImplementedError("Abstract method")

    def parse(self, parser):
        return self.xform(parser, self.do_parse(parser))

class Literal(AbstractParser):
    def __init__(self, literal, token_type=None):
        super().__init__()
        self.literal = literal
        self.token_type = token_type

    @property
    def describe(self):
        return "'{}'".format(self.literal)

    def do_parse(self, parser):
        token = parser.next_token()
        if token is None:
            parser.putback_token(token)
            return ParseError("Cannot parse literal '{}': no token".format(self.describe), parser.pos) 
        if (self.token_type is not None) and (token.type != self.token_type):
            parser.putback_token(token)
            return ParseError("Cannot parse literal '{0}': "
                              + "expect token type '{1}', got '{2}'".format(self.describe,
                                                                            self.token_type,
                                                                            token.type),
                              token.start_pos, token.end_pos)

        return token

class Tuple(AbstractParser):
    def __init__(self, *parsers):
        self.parsers = parsers
        self.description = None

    @property
    def describe(self):
        if self.description is None:
            self.description = " ".join(p.describe for p in self.parsers)
        return self.description

    def do_parse(self, parser):
        res = []
        for p in self.parsers:
            parsed = p.parse(parser)
            if is_parse_error(parsed):
                return parsed  # stop in case of a parse error
            if parsed is not None:
                res.append(parsed)
        return res

