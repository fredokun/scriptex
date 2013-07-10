'''
The parser framework
'''

if __name__ == "__main__":
    import sys
    sys.path.append("../")

import scriptex.lexer as lexer

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
    
    def next_token(self, token_type):
        return self.lexer.next_token(token_type)

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
        self.on_parse = lambda parser, content: content
        self.on_error = lambda parser, err: err

        # by default the parser is *not* skip
        self.skip = False

    def describe(self):
        raise NotImplementedError("Abstract method")

    def do_parse(self, parser):
        raise NotImplementedError("Abstract method")

    def parse(self, parser):
        result = self.do_parse(parser)
        if is_parse_error(result):
            return self.on_error(parser, result)
        else:
            return self.on_parse(parser, result)

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
            
        token = parser.next_token(self.token_type)
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

        if self.skip:
            return None
        else:
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
        # BREAKPOINT >>> #  import pdb; pdb.set_trace()  # <<< BREAKPOINT #

        res = []
        for p in self.parsers:
            parsed = p.parse(parser)
            if is_parse_error(parsed):
                return parsed  # stop in case of a parse error
            if parsed is not None:
                res.append(parsed)
        return res

class Repeat(AbstractParser):
    r"""Parser for a repetition of a subparser.

    >>> input = lexer.Lexer(lexer.make_string_tokenizer("hellohellohello"),lexer.Literal("hello_lit", "hello"),lexer.Literal("world_lit","world"),lexer.Char("backslash", '\\'),lexer.CharIn("bracket",'{','}'))

    >>> parser = ParsingAlgo(input)
    >>> parser.parser = Repeat(Literal(token_type="hello_lit"))

    >>> [tok.value for tok in parser.parse()]
    ['hello', 'hello', 'hello']

    """
    def __init__(self, parser, min_count=0, max_count=-1):
        super().__init__()
        self.parser = parser
        self.description = None
        assert (min_count >= 0)
        assert (max_count == -1) or (min_count < max_count)
        self.min_count = min_count
        assert (max_count >= -1)
        self.max_count = max_count

    @property
    def describe(self):
        if self.description is None:
            rept_lbl = ""
            if self.max_count == 0:
                if self.min_count == 0:
                    rept_lbl = "*"
                elif self.min_count == 1:
                    rept_lbl = "+"
                else:
                    rept_lbl = "[{}...]".format(self.min_count)
            else:
                rept_lbl = "[{}..{}]".format(self.min_count, self.max_count)
                
            self.description = self.parser.describe + rept_lbl

        return self.description

    def do_parse(self, parser):
        res = []
        count = 0
        while True:
            
            parsed = self.parser.parse(parser)
            if is_parse_error(parsed):
                if count < self.min_count:
                    return parsed
                else:
                    return res
                
            # not a parse error
            if parsed is not None:
                res.append(parsed)
                count += 1
                if count == self.max_count:
                    return res

class Optional(Repeat):
    def __init__(self, parser):
        super().__init__(parser, min_count=0, max_count=1)

    @property
    def describe(self):
        if self.description is None:
            self.description = self.parser.describe + "?"

        return self.description
    

class ListOf(AbstractParser):
    r"""Parser for a repetition of a subparser with open, close and separator parsers.

    >>> input = lexer.Lexer(lexer.make_string_tokenizer("{hello,hello,hello}"),lexer.Literal("hello_lit", "hello"),lexer.Char("open_curly",'{'),lexer.Char("close_curly", '}'),lexer.Char("comma",','))

    >>> parser = ParsingAlgo(input)
    >>> parser.parser = ListOf(Literal(token_type="hello_lit"), open_=Literal(token_type="open_curly"), close=Literal(token_type="close_curly"), sep=Literal(token_type="comma"))

    >>> [tok.value for tok in parser.parse()]
    ['hello', 'hello', 'hello']

    """
    def __init__(self, parser, sep=None, open_=None, close=None, min_count=0, max_count=-1):
        super().__init__()
        self.parser = parser
        self.description = None
        self.open = open_
        self.close = close
        self.sep = sep
        self.min_count = min_count
        self.max_count = max_count

    @property
    def describe(self):
        if self.description is None:
            sep_lbl = ""
            if self.sep is not None:
                sep_lbl = self.sep.describe 
            open_lbl = ""
            if self.open is not None:
                open_lbl = self.open.describe 
            close_lbl = ""
            if self.close is not None:
                close_lbl = self.close.describe 
            self.description = "ListOf({}{}{}{})".format(self.parser.describe,sep_lbl,open_lbl,close_lbl)

        return self.description

    def do_parse(self, parser):
        res = []

        # parse open
        if self.open is not None:
            parsed = self.open.parse(parser)
            if is_parse_error(parsed):
                return parsed
            if parsed is not None:
                res.append(parsed)

        # parse elements
         
        count = 0
        while True:
            
            parsed = self.parser.parse(parser)
            if is_parse_error(parsed):
                if count < self.min_count:
                    return parsed
                else:
                    break # exit from loop
                
            # not a parse error
            if parsed is not None:
                res.append(parsed)
                count += 1
                if count == self.max_count:
                    break # exit from loop

            # parse separator
            if self.sep is not None:
                parsed = self.sep.parse(parser)
                if is_parse_error(parsed):
                    if count < self.min_count:
                        return parsed
                    else:
                        break # exit from loop

        # end of while

        # parse close
        if self.close is not None:
            parsed = self.close.parse(parser)
            if is_parse_error(parsed):
                return parsed
            else:
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
