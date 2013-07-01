'''
Test parser
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from scriptex.parser import ScripTexParser

class TestLexerString(unittest.TestCase):
    def test_line_comment(self):
        parser = ScripTexParser()

        ret = parser.parse_from_string("""
% this is a comment
    % after some space

""")

        print("ret = " + ret)
                                    

if __name__ == '__main__':
    unittest.main()
