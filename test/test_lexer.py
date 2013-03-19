'''
Test lexer
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

import scriptex


class TestLexerString(unittest.TestCase):
    def test_emph(self):
        underscore = scriptex.lexer.Char('_', token_type="underscore")
        space = scriptex.lexer.CharIn("space", ' ', '\t')
        word = scriptex.lexer.Regexp(r'([^_ \t\n\r\f\v]+)',token_type='word')

        tokens = scriptex.make_string_tokenizer("_example in emphasis_")

        token = underscore.recognize(tokens)
        self.assertEqual(token.type,'underscore')
        self.assertEqual(token.value,'_')
        self.assertEqual(tokens.show_lines(1,cursor="<>") , "_<>example in emphasis_")
        self.assertEqual(tokens.pos.offset,1)

        token = underscore.recognize(tokens)
        self.assertEqual(token,None)
        self.assertEqual(tokens.pos.offset,1)

        token = word.recognize(tokens)
        self.assertEqual(token.type,'word')
        self.assertEqual(tokens.pos.offset,8)

        token = word.recognize(tokens)
        self.assertEqual(token,None)
        self.assertEqual(tokens.pos.offset,8)

        token = space.recognize(tokens)
        self.assertEqual(token.type,'space')
        self.assertEqual(tokens.pos.offset,9)

        tokens.reset()
        lexer = scriptex.lexer.Lexer(tokens, underscore, space, word)
        token = lexer.next()
        self.assertEqual(token.type, 'underscore')
        token = lexer.next()
        self.assertEqual(token.type, 'word')
        lexer.putback(token)
        token = lexer.next()
        self.assertEqual(token.type, 'word')

        tokens.reset()
        toks = [ tok for tok in lexer ]
        self.assertEqual([tok.type for tok in toks],['underscore', 'word', 'space', 'word', 'space', 'word', 'underscore'])
        

if __name__ == '__main__':
    unittest.main()
