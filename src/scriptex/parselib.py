'''
The parser framework
'''

import lexer

class ParsingAlgo:
    def __init__(self, lexer):
        self.lexer = lexer
        self._parser = None

    @property
    def parser(self):
        return self._parser

    @parser.setter
    def parser(self, p):
        self._parser = p
    
    def next_token(self):
        return next(self.lexer)

    def putback_token(self, token):
        self.lexer.putback(token)

    @property
    def pos(self):
        return self.lexer.pos

    def parse(self):
        return self._parser.parse(self)


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
    r"""Parser for a literal token.

    >>> input = lexer.Lexer(lexer.make_string_tokenizer("\hello{world}"),lexer.Literal("hello_lit", "hello"),lexer.Char("backslash", '\\'),lexer.CharIn("bracket",'{','}'))

    >>> parser = ParsingAlgo(input)
    >>> parser.parser = Literal(token_type="backslash")
    >>> parser.parse().value
    '\\'

    >>> parser.parser = Literal(literal="hello")
    >>> parser.parse().value
    'hello'

    >>> parser.parse().msg
    "Cannot parse literal 'hello': expect value 'hello', got '{'"

    """
    def __init__(self, token_type=None, literal=None):
        super().__init__()
        self.literal = literal
        self.token_type = token_type

    @property
    def describe(self):
        ret = ""
        if self.token_type is not None:
            ret += "{{{}}}".format(self.token_type)
        if self.literal is not None:
            if self.token_type is not None:
                ret += ":"
            ret += "'{}'".format(self.literal)
        return ret

    def do_parse(self, parser):
        #import pdb ; pdb.set_trace()
        token = parser.next_token()
        if token is None:
            return ParseError("Cannot parse literal {}: no further token".format(self.describe), parser.pos) 
        if (self.token_type is not None) and (token.type != self.token_type):
            parser.putback_token(token)
            return ParseError("Cannot parse literal {0}: "\
                              "expect token type '{1}', got '{2}'".format(self.describe,
                                                                          self.token_type,
                                                                          token.type),
                              token.start_pos, token.end_pos)

        if (self.literal is not None) and (token.value != self.literal):
            parser.putback_token(token)
            return ParseError("Cannot parse literal {0}: "\
                              "expect value '{1}', got '{2}'".format(self.describe,
                                                                     self.literal,
                                                                     token.value),
                              token.start_pos, token.end_pos)            
        return token

class Tuple(AbstractParser):
    r"""Parser for a tuple of subparsers.

    >>> input = lexer.Lexer(lexer.make_string_tokenizer("\hello{world}"),lexer.Literal("hello_lit", "hello"),lexer.Literal("world_lit","world"),lexer.Char("backslash", '\\'),lexer.CharIn("bracket",'{','}'))

    >>> parser = ParsingAlgo(input)
    >>> parser.parser = Tuple(Literal(token_type="backslash"), Literal("hello_lit", "hello"), Literal(token_type="bracket"), Literal("world_lit", "world"), Literal(token_type="bracket"))

    >>> [(v.value,v.type) for v in parser.parse()]
    [('\\', 'backslash'), ('hello', 'hello_lit'), ('{', 'bracket'), ('world', 'world_lit'), ('}', 'bracket')]

    """
    def __init__(self, *parsers):
        super().__init__()
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

class Choice(AbstractParser):
    r"""Parser for a choice of subparsers.

    Note: there is no look-ahead and only right recursion is allowed.

    >>> input = lexer.Lexer(lexer.make_string_tokenizer("\hello{world}"),lexer.Literal("hello_lit", "hello"),lexer.Literal("world_lit","world"),lexer.Char("backslash", '\\'),lexer.CharIn("bracket",'{','}'))

    >>> parser = ParsingAlgo(input)
    >>> parser.parser = Choice(Literal(token_type="backslash"), Literal("hello_lit", "hello"), Literal(token_type="bracket"), Literal("world_lit", "world"), Literal(token_type="bracket"))

    >>> parser.parse().value
    '\\'

    >>> parser.parse().value
    'hello'

    >>> parser.parse().value
    '{'
    
    >>> parser.parse().value
    'world'

    >>> parser.parse().value
    '}'

    >>> parser.parse().msg
    "Cannot parse: {backslash} / {hello_lit}:'hello' / {bracket} / {world_lit}:'world' / {bracket}"

    """
    def __init__(self, *parsers):
        super().__init__()
        self.parsers = parsers
        self.description = None

    @property
    def describe(self):
        if self.description is None:
            self.description = " / ".join(p.describe for p in self.parsers)
        return self.description

    def do_parse(self,parser):
        start_pos = parser.pos
        parsed = None
        for p in self.parsers:
            parsed = p.parse(parser)
            if not is_parse_error(parsed):
                return parsed
        # everything failed
        return ParseError("Cannot parse: {}".format(self.describe), start_pos, parser.pos)

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
