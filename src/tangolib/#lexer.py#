'''
The Tango lexer
'''

class ParsePosition:
    '''
    Representation of parse positions.

    A parse position is a line position, a character position
    and an absolute offset into a character buffer.
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
        self.token_type = token_type
        self.value = token_value
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __str__(self):
        return "{}::{}".format(self.value, self.type)

    def __repr__(self):
        return "Token({0}, {1}, start_pos={2}, end_pos={3})"\
            .format(self.token_type, self.value,
                    self.start_pos, self.end_pos)

class Recognizer:
    def __init__(self, token_type):
        self.token_type = token_type
        
    def recognize(self, tokenizer):
        raise NotImplementedError("Abstract method")

class EndOfInput(Recognizer):
    def __init__(self, token_type="end_of_input"):
        super().__init__(token_type)

    def recognize(self, tokenizer):
        if tokenizer.at_eof():
            return Token(self.token_type, None, tokenizer.pos, tokenizer.pos)
        else:
            return None

        def __repr__(self):
            return "EndOfInput(token_type={})".format(self.token_type)

        def __str__(self):
            return "<EndOfInput>::{}".format(self.token_type)

class Char(Recognizer):
    def __init__(self, token_type, char):
        super().__init__(token_type)
        self.char = char

    def recognize(self, tokenizer):
        start_pos = tokenizer.pos
        char = tokenizer.peek_char
        if char is None:
            return None
        if char == self.char:
            tokenizer.next_char()
            return Token(self.token_type, char, start_pos, tokenizer.pos)
        else:
            return None

        def __repr__(self):
            return "Char(token_type={},char={})".format(self.token_type, repr(self.char))

        def __str__(self):
            return "'{}'::{}".format(self.char, self.token_type)


class CharIn(Recognizer):
    def __init__(self, token_type, *args):
        super().__init__(token_type)
        self.charset = {ch for ch in args}
        
    def recognize(self, tokenizer):
        start_pos = tokenizer.pos
        char = tokenizer.peek_char
        if char is None:
            return None
        if char in self.charset:
            tokenizer.next_char()
            return Token(self.token_type, char, start_pos, tokenizer.pos)
        else:
            return None

    def __str__(self):
        return "[{}]::{}".format("".join(self.charset),self.token_type)

    def __repr__(self):
        return "CharIn(token_type={},charset={})".format(self.token_type, repr(self.charset))

class CharNotIn(Recognizer):
    def __init__(self, token_type, *args):
        super().__init__(token_type)
        self.charset = {ch for ch in args}

    def recognize(self, tokenizer):
        start_pos = tokenizer.pos
        char = tokenizer.peek_char
        if char is None:
            return None
        if char not in self.charset:
            tokenizer.next_char()
            return Token(self.token_type, char, start_pos, tokenizer.pos)
        else:
            return None

    def __str__(self):
        return "[^{}]::{}".format("".join(self.charset),self.token_type)
        
    def __repr__(self):
        return "CharNotIn(token_type={},charset={})".format(self.token_type, repr(self.charset))

class Literal(Recognizer):
    def __init__(self, token_type, literal):
        super().__init__(token_type)
        self.literal = literal

    def recognize(self, tokenizer):
        start_pos = tokenizer.pos
        ret = tokenizer.peek_chars(len(self.literal))
        if ret == self.literal:
            tokenizer.forward(len(self.literal))
            return Token(self.token_type, ret, start_pos, tokenizer.pos)
        else:
            return None

    def __repr__(self):
        return "Literal(token_type={},literal={})".format(self.token_type, repr(self.literal))

    def __str__(self):
        return "'{}'::{}".format(self.literal, self.token_type)

class Regexp(Recognizer):
    def __init__(self, token_type, regexp, re_flags=0):
        super().__init__(token_type)
        import re
        self.re_str = regexp
        self.regexp = re.compile(regexp, re_flags)
        self.excludes = set()

    def recognize(self, tokenizer):
        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        start_pos = tokenizer.pos
        line = tokenizer.peek_line
        if line == None:
            return None
        match = self.regexp.match(line)
        if match is not None:
            for exclude in self.excludes:
                if match.group(0) == exclude:
                    return None
                
            tokenizer.forward(len(match.group(0)))
            return Token(self.token_type, match, start_pos, tokenizer.pos)
        else:
            return None

    def __repr__(self):
        return "Regexp(token_type={},regexp={})".format(self.token_type, self.re_str)

    def __str__(self):
        return '"{}"::{}'.format(self.re_str, self.token_type)            
        
class Tokenizer:
    '''
    The main tokenizer class that transforms a flow
    of characters into a flow of tokens.

    A tokenizer backend must be provided at initialization time.
    '''
    def __init__(self, tokenizer_backend):
        self.tokenizer_backend = tokenizer_backend

    @property
    def pos(self):
        return self.tokenizer_backend.pos()

    def at_eof(self):
        return self.tokenizer_backend.at_eof()

    def set_pos(self, pos):
        self.tokenizer_backend.move_to(pos.offset)

    def reset(self):
        self.tokenizer_backend.move_to(0)

    @property
    def peek_char(self):
        return self.tokenizer_backend.peek_char()

    @property
    def peek_line(self):
        return self.tokenizer_backend.peek_line()

    def next_char(self):
        return self.tokenizer_backend.next_char()

    def forward(self, nb_chars):
        self.tokenizer_backend.forward(nb_chars) 

    def peek_chars(self, nb_chars):
        return self.tokenizer_backend.peek_chars(nb_chars)

    def show_lines(self, nb_lines, cursor="_"):
        return self.tokenizer_backend.show_lines(nb_lines, cursor)

    def __str__(self):
        return self.show_lines(2)

class TokenError(Exception):
    pass

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

    >>> tokens.forward(6)
    ' crazy'

    >>> tokens.pos()
    ParsePosition(lpos=1, cpos=12, offset=11)

    >>> tokens.next_char()
    '\\n'

    >>> tokens.pos()
    ParsePosition(lpos=2, cpos=1, offset=12)

    >>> tokens.prev_char()
    '\\n'

    >>> tokens.pos()
    ParsePosition(lpos=1, cpos=12, offset=11)

    >>> tokens.backward(6)
    ' crazy'

    >>> tokens.pos()
    ParsePosition(lpos=1, cpos=6, offset=5)

    >>> tokens.backward(5)
    'hello'

    >>> tokens.pos()
    ParsePosition(lpos=1, cpos=1, offset=0)

    >>> tokens.prev_char()
    Traceback (most recent call last):
      ...
    AssertionError: cannot move backward at start of input

    >>> tokens.forward(16)
    'hello crazy\\nworl'

    >>> tokens.next_char()
    'd'

    >>> tokens.at_eof()
    True

    >>> tokens.next_char()
    Traceback (most recent call last):
      ...
    AssertionError: cannot move foward at end of input


    >>> tokens.move_to(2)
    'llo crazy\\nworld'

    >>> tokens.move_to(14)
    'llo crazy\\nwo'

    """
    def __init__(self, input_string):
        self.offset = 0
        self.lpos = 1
        self.cpos = 1
        self.eol_map = dict() # Map: offset of newline -> last character pos
        self.input_string = input_string
        self.input_length = len(input_string)
    
    def pos(self):
        return ParsePosition(self.lpos, self.cpos, self.offset)

    def at_eof(self):
        return self.offset == self.input_length

    def peek_char(self):
        if self.at_eof():
            return None
        return self.input_string[self.offset]

    def peek_chars(self, nb_chars):
        ret = ""
        for i in range(nb_chars):
            if self.offset+i>= self.input_length:
                return None
            ret += self.input_string[self.offset+i]
        return ret

    def peek_line(self):
        if self.offset == self.input_length:
            return None
        
        line = ""
        offset = self.offset
        while offset < self.input_length:
            ch = self.input_string[offset]
            if ch == '\n':
                return line + ch
            else:
                line += ch
                offset += 1
        return line

    def next_char(self):
        assert self.offset < self.input_length, "cannot move foward at end of input"
        ch = self.peek_char()
        if ch == '\n':
            self.eol_map[self.offset] = self.cpos
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

    def prev_char(self):
        assert self.offset >= 1, "cannot move backward at start of input"
        if (self.offset - 1) in self.eol_map:
            # cancel a new line
            self.lpos -= 1
            self.cpos = self.eol_map[self.offset-1]
            del self.eol_map[self.offset-1]
        else:
            self.cpos -= 1
        # finally decrement the offset
        self.offset -= 1
        return self.input_string[self.offset]
    
    def backward(self, nb_chars):
        ret = ""
        for i in range(nb_chars):
            ret = self.prev_char() + ret
        return ret

    def move_to(self, noffset):
        if noffset >= self.offset:
            return self.forward(noffset - self.offset)
        else:
            return self.backward(self.offset - noffset)

    def find_start_of_line(self, soffset):
        """Find the start of the current line.

        >>> tokens = StringTokenizer("hello crazy\\nworld")
        >>> tokens.find_start_of_line(14)
        12
        """
        while soffset > 0:
            if self.input_string[soffset-1] == '\n':
                return soffset
            else:
                soffset -= 1
        return soffset
    
    def show_lines(self, nb_lines, cursor):
        nb_found = 0
        soffset = self.find_start_of_line(self.offset)
        ret = ""
        while (nb_found <= nb_lines) and (soffset < self.input_length):
            ch = self.input_string[soffset]
            if ch == '\n':
                nb_found += 1
            if soffset == self.offset:
                ret += cursor
            ret += ch
            soffset += 1
        return ret
    
def make_string_tokenizer(input_string):
    return Tokenizer(StringTokenizer(input_string))


class FileTokenizer(TokenizerBackend):
    pass


class Lexer:
    '''The lexer generates the flow of tokens from
    the tokenizer.

    '''
    def __init__(self, tokenizer, *recognizers):
        self.tokenizer = tokenizer
        self.recognizers = recognizers

    @property
    def pos(self):
        return self.tokenizer.pos

    def show_line(self, cursor="_"):
        return self.show_lines(1, cursor)

    def show_lines(self, nb_lines=2, cursor="_"):
        return self.tokenizer.show_lines(nb_lines, cursor)

    def next_char(self):
        return self.tokenizer.next_char()

    def next_chars(self, nb_chars):
        return self.tokenizer.forward(nb_chars)

    def peek_char(self):
        return self.tokenizer.peek_char

    def peek_chars(self, nb_chars):
        return self.tokenizer.peek_chars(nb_chars)

    def next_token(self):
        for rec in self.recognizers:
            token = rec.recognize(self.tokenizer)
            if token is not None:
                return token

        return None
                
    def __next__(self):
        tok =  self.next_token()
        if tok is None:
            raise StopIteration()
        else:
            return tok
        
    def putback(self, token):
        """Put back a token in the lexer.
        Warning: this does not check the token was the correct
        one, only we go back to the position corresponding
        to the start of the token.
        """
        self.tokenizer.set_pos(token.start_pos)

    def move_to(self, pos):
        self.tokenizer.set_pos(pos)

    def at_eof(self):
        return self.tokenizer.at_eof()

    def __iter__(self):
        return self
            
def make_file_tokenizer(filename):
    pass

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
