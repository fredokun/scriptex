'''
Test extended regular expressions
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

import tangolib.parser as parser
import tangolib.eregex as ere


class TestExtendedRegex(unittest.TestCase):
    def test_spaces(self):
        expr = parser.REGEX_SPACE
        expr.compile()
        m = expr.match(" ")
        self.assertTrue(m.group(0) == " ")

        m = expr.match("\n")
        self.assertTrue(m is None)

        m = expr.match("n")
        self.assertTrue(m is None)

    def test_markdown_lists(self):
        expr = parser.REGEX_MDLIST_OPEN
        # print(str(expr))
        expr.compile(ere.MULTILINE)
        m = expr.match("""    
          - item
        """)
        self.assertTrue(m.group(1) == "          ")
        self.assertTrue(m.group(2) == "-")

if __name__ == '__main__':
    unittest.main()
