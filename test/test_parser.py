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

        print("ret 1 = " + str([str(p) for p in ret]))

    def test_command_simple(self):
        parser = ScripTexParser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_string(r"""
% this is a comment
\mycommand[key1=value1,key2=value2]{
contents of the command
% a comment in the command
}
    % after some space

""")

        print("ret 2 = " + str([str(p) for p in ret]))


        
if __name__ == '__main__':
    unittest.main()
