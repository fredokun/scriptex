'''
Test macro commands
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from tangolib.parser import Parser
from tangolib.processor import DocumentProcessor

class TestCommandMacro(unittest.TestCase):

    def test_macro_simple_text(self):
        parser = Parser()

        doc = parser.parse_from_string(r"""

% macro definition
\defCommand{\hello}[0]{brave world}
\defCommand{\hello2}{brave world 2}

% macro expansion
Hello \hello 

% macro expansion
Hello \hello2 

""")

        print("simple_text (before expansion) = {}".format(doc))

        processor = DocumentProcessor(doc)

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        processor.process()

        print("simple_text (after expansion) = {}".format(doc))

    def test_macro_simple_replace(self):
        parser = Parser()

        doc = parser.parse_from_string(r"""

% macro definition
        \defCommand{\hello}[1]{brave #1 world}

% macro expansion
Hello \hello{new} 

""")

        # print("simple_replace (before expansion) = {}".format(doc))

        processor = DocumentProcessor(doc)

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        processor.process()

        # print("simple_replace (after expansion) = {}".format(doc))
        
    def test_macro_nested_replace(self):
        parser = Parser()

        doc = parser.parse_from_string(r"""

% macro definition
    \defCommand{\new}[0]{New}
    \defCommand{\hello}[1]{brave #1 world}

% macro expansion
Hello \hello{\new} 

""")

        print("nested_replace (before expansion) = {}".format(doc))

        processor = DocumentProcessor(doc)

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        processor.process()

        print("nested_replace (after expansion) = {}".format(doc))


if __name__ == '__main__':
    unittest.main()
