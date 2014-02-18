'''
Test macro environments
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from tangolib.parser import Parser
from tangolib.processor import DocumentProcessor

class TestCommandMacro(unittest.TestCase):

    def test_macro_env_simple_text(self):
        parser = Parser()

        doc = parser.parse_from_string(r"""

% macro definition
\defEnv{hello}[0]{hello}{world}
\defEnv{hello2}{hello2}{world2}

% macro expansion
\begin{hello}
brave
\end{hello}

% macro expansion
\begin{hello2}
brave 
\end{hello2}

""")

        print("env_simple_text (before expansion) = {}".format(doc))

        processor = DocumentProcessor(doc)

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        processor.process()

        print("env_simple_text (after expansion) = {}".format(doc))

    def test_macro_env_simple_replace(self):
        parser = Parser()

        doc = parser.parse_from_string(r"""

% macro definition
\defEnv{hello}[1]{hello #1}{#1 world}

% macro expansion
\begin{hello}{brave}
new
\end{hello}

""")

        print("env_simple_replace (before expansion) = {}".format(doc))

        processor = DocumentProcessor(doc)

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        processor.process()

        print("env_simple_replace (after expansion) = {}".format(doc))
        
    def test_macro_ev_nested_replace(self):
        parser = Parser()

        doc = parser.parse_from_string(r"""

% macro definition
\defEnv{new}[0]{New}{Old}
\defEnv{hello}[1]{hello #1}{#1 world}

% macro expansion
\begin{hello}{\begin{new}
    crazy
\end{new}}
brave
\end{hello} 

""")

        print("env_nested_replace (before expansion) = {}".format(doc))

        processor = DocumentProcessor(doc)

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        processor.process()

        print("env_nested_replace (after expansion) = {}".format(doc))


if __name__ == '__main__':
    unittest.main()
