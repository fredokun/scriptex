'''
The ScripTeX lexer
'''


class ParsePosition:
    '''
    Representation of parse positions (immutable structure).
    A parse position is a line position, a character position
    and an absolute offset
    '''
    def __init__(self, lpos, cpos, offset):
        self.lpos = lpos
        self.cpos = cpos
        self.offset = offset

    def __repr__(self):
        return "ParsePosition(lpos={0}, cpos={1}, offset={2})"\
            .format(self.lpos, self.cpos, self.offset)

    def __str__(self):
        return "{0}:{1}".format(self.lpos, self.cpos)


class Token:
    '''
    Representation of lexer tokens.
    '''
    def __init__(self, token_type, token_value, start_pos, end_pos):
        self.type = token_type
        self.value = token_value
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __repr__(self):
        return "Token({0}, {1}, start_pos={2}, end_pos={3})"\
            .format(self.type, self.value,
                    self.start_pos, self.end_pos)

class Recognizer:
    def __init__(self, token_type):
        self.token_type = token_type
        
    def recognize(self, tokenizer):
        raise NotImplementedError("Abstract method")

class Char(Recognizer):
    def __init__(self, char, token_type='Char'):
        super.__init__(token_type)
        self.char = char

    def recognize(self, tokenizer):
        start_pos = tokenizer.pos
        char = tokenizer.peek_char
        if char == self.char:
            tokenizer.next_char
            return Token(self.token_type, char, start_pos, tokenizer.pos)
        else:
            return None

        def __repr__(self):
            return "'{0}'".format(self.char)

class CharIn(Recognizer):
    def __init__(self, token_type='Char', *args):
        super.__init__(token_type)
        self.charset = {ch for ch in args}
        
    def recognize(self, tokenizer):
        start_pos = tokenizer.pos
        char = tokenizer.peek_char
        if char in self.charset:
            tokenizer.next_char
            return Token(self.token_type, char, start_pos, tokenizer.pos)
        else:
            return None

    def __repr__(self):
        return 'CharIn{0}'.repr(self.charset)

class CharNotIn(Recognizer):
    def __init__(self, token_type='Char', *args):
        super.__init__(token_type)
        self.charset = {ch for ch in args}

    def recognize(self, tokenizer):
        start_pos = tokenizer.pos
        char = tokenizer.peek_char
        if char not in self.charset:
            tokenizer.next_char
            return Token(self.token_type, char, start_pos, tokenizer.pos)
        else:
            return None

    def __repr__(self):
        return 'CharNotIn{0}'.repr(self.charset)

class Regexp(Recognizer):
    def __init__(self, regexp, re_flags=0, token_type='Regexp'):
        super.__init__(token_type)
        self.regexp = re.compile(regexp, re_flags)

    def recognize(self, tokenizer):
        start_pos = tokenizer.pos
        line = tokenizer.peek_line
        match = self.regexp.match(line)
        if match is not None:
            tokenizer.advance(len(match.group(0)))
            return Token(self.token_type, match, start_pos, tokenizer.pos)
        else:
            return None

class AnyOf(Recognizer):
    def __init__(self, token_type=None, *args):
        self.recognizers = args

    def recognize(self, tokenizer):
        start_pos = tokenizer.pos
        for recognizer in self.recognizers:
            token = recognizer.recognize(tokenizer)
            if token is not None:
                return token
            tokenizer.set_pos(start_pos)
        # nothing recognized
        return None

    def __repr__(self):
        return "AnyOf{0}".format(repr(self.recognizers))

class Repeat(Recognizer):
    def __init__(self, recognizer, minimum=0, token_type=None):
        self.recognizer = recognizer
        self.minimum = minimum
        
    def recognizer(self, tokenizer):
        nb_rec = 0
        tokens = []
        start_pos = tokenizer.pos
        while True:
            token = self.recognizer.recognize(tokenizer)
            if token is not None:
                nb_rec += 1
                tokens.append(token)
            else:
                if nb_rec < self.minimum:
                    tokenizer.set_pos(start_pos)
                    return None
                else:
                    return tokens

    def __repr__(self):
        return "Repeat({0}, minimum={1})".format(repr(self.recognizer),
                                                     self.minimum)
class Tokenizer:
    '''
    The main tokenizer class.
    A tokenizer backend must be provided.
    '''
    def Tokenizer(self, tokenizer_backend):
        self.tokenizer_backend = tokenizer_backend

    @property
    def pos(self):
        return self.tokenizer_backend.pos

    def set_pos(self, pos):
        self.tokenizer_backend.move_to(pos.offset)

    @property
    def peek_char(self):
        return self.tokenizer_backend.peek_char

    def next_char(self):
        self.advance(1)

    def advance(self, nb_chars):
        self.tokenizer_backend.advance(nb_chars) 

    def peek_chars(self, nb_chars):
        return self.tokenizer_backend.peek_chars(nb_chars)

class TokenError(Exception):
    def __init__(self, msg):
        super.__init__(msg)

class TokenizerBackend:
    @property
    def pos(self):
        raise NotImplementedError("Abstract method")

    @property
    def peek_char(self):
        raise NotImplementedError("Abstract method")


class StringTokenizer(TokenizerBackend):
    """A tokenizer backend for string inputs.

    >>> tokens = StringTokenizer("hello crazy\\nworld")
    >>> tokens.peek_char()
    'h'
    >>> tokens.at_eof()
    False
    >>> tokens.pos()
    ParsePosition(lpos=1, cpos=1, offset=0)
    >>> tokens.forward(5)
    'hello'
    >>> tokens.pos()
    ParsePosition(lpos=1, cpos=6, offset=5)
    
    
    """
    def __init__(self, input_string):
        self.offset = 0
        self.lpos = 1
        self.cpos = 1
        self.eol_set = set()
        self.input_string = input_string
        self.input_length = len(input_string)

    def pos(self):
        return ParsePosition(self.lpos, self.cpos, self.offset)

    def at_eof(self):
        return self.offset == self.input_length

    def peek_char(self):
        if self.at_eof():
            raise TokenError("Cannot peek char at end of in input")
        return self.input_string[self.offset]

    def next_char(self):
        ch = self.peek_char()
        if ch == r'\n':
            self.eol_set.add(self.offset)
            self.lpos += 1
            self.cpos = 0
        # in any case
        self.cpos += 1
        self.offset += 1
        return ch
    
    def forward(self, nb_chars):
        ret = ""
        for i in range(nb_chars):
            ret += self.next_char()
        return ret
    
    

def make_string_tokenizer(input_string):
    return Tokenizer(StringTokenizer(input_string))


class FileTokenizer(TokenizerBackend):
    pass


def make_file_tokenizer(filename):
    pass

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
