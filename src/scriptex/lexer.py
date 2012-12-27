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
        self.token_type = token_type
        self.token_value = token_value
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __repr__(self):
        return "Token({0}, {1}, start_pos={2}, end_pos={3})"\
            .format(self.token_type, self.token_value,
                    self.start_pos, self.end_pos)

    class Recognizer:
        def __init__(self, token_type):
            self.token_type = token_type

        def recognize(self, tokenizer):
            raise NotImplementedError("Abstract method")

    class Char(Recognizer):
        def __init__(self, token_type='Char', char):
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

    class AnyOf(Recognizer):
        def __init__(self, token_type='NotIn', *args):
            self.recognizers = args

        def recognize(self, tokenizer):
            start_pos = tokenizer.pos
            for recognizer in self.recognizers:
                token = recognizer.recognize(tokenizer)
                if token is not None:
                    return token
                tokenizer.set_pos(start_pos)
            # nothing recognized

        def __repr__(self):
            return "AnyOf{0}".format(repr(self.recognizers))

    class Repeat(Recognizer):
        def __init__(self, token_type='Repeat', recognizer, minimum=0):
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


class TokenizerBackend:
    @property
    def pos(self):
        raise NotImplementedError("Abstract method")

    @property
    def peek_char(self):
        raise NotImplementedError("Abstract method")


class StringTokenizer(TokenizerBackend):
    pass


def make_string_tokenizer(input_string):
    return Tokenizer(StringTokenizer(input_string))


class FileTokenizer(TokenizerBackend):
    pass


def make_file_tokenizer(filename):
    pass
