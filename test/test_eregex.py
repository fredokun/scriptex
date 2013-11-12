'''
Test extended regular expressions
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

import tangolib.parser as parser
import tangolib.eregex as ere


MD_LIST_EX1 = """

 - firt item
    - item 1.1
    - item 1.2
  - second item

"""

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

    def test_markdown_list_open(self):
        expr = parser.REGEX_MDLIST_OPEN
        # print(str(expr))
        expr.compile(ere.MULTILINE)
        m = expr.match("""    
          - item
        """)
        self.assertTrue(m.group(1) == "          ")
        self.assertTrue(m.group(2) == "-")

    def test_markdown_list_item(self):
        expr = parser.REGEX_MDLIST_ITEM

        expr.compile(ere.MULTILINE)
        m = expr.match("""   - item 1
   - item2""")
        
        self.assertTrue(m.group(1) == "   ")
        self.assertTrue(m.group(2) == "-")
        self.assertTrue(m.group(3) == "item 1")
        
        m = expr.match("""   - item last

        """)

        self.assertTrue(m is None)

    def test_markdown_list_item_last(self):
        expr = parser.REGEX_MDLIST_ITEM_LAST

        expr.compile(ere.MULTILINE)
        m = expr.match("""   - item 1
   - item2""")
        
        self.assertTrue(m is None)
        
        m = expr.match("""   - item last

        """)

        self.assertTrue(m.group(1) == "   ")
        self.assertTrue(m.group(2) == "-")
        self.assertTrue(m.group(3) == "item last")

if __name__ == '__main__':
    unittest.main()
