'''
Test parser
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from scriptex.preparser import Preparser

class TestLexerString(unittest.TestCase):
    def test_line_comment(self):
        parser = Preparser()

        ret = parser.preparse_from_string("""
% this is a comment
    % after some space

""")

        # print("doc 1 = {}".format(ret))

    def test_command_simple(self):
        parser = Preparser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.preparse_from_string(r"""
% this is a comment
\mycommand[key1=value1,key2=value2]{
contents of the command
% a comment in the command
}
    % after some space

""")

        # print("doc 2 = {}".format(ret))

    def test_env_simple(self):
        parser = Preparser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.preparse_from_string(r"""
% a comment before the environment
\begin{env}
% this is a comment
\mycommand[key1=value1,key2=value2]{
contents of the command
% a comment in the command
}
    % after some space
\end{env}

% a last comment outside the environment
""")

        #print("doc 3 = {}".format(ret))

    def test_env_itemize(self):
        parser = Preparser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.preparse_from_string(r"""
% a comment before the environment
\begin{itemize}
% this is a comment
\item first item
\item second item with command \mycommand[key1=value1,key2=value2]{
contents of the command
% a comment in the command
}

\item an item
    % after some space
\end{itemize}

% a last comment outside the environment
""")

        print("doc 4 = {}".format(ret))
        

    def test_env_itemize2(self):
        parser = Preparser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.preparse_from_string(r"""
% a comment before the environment
\begin{itemize}
\item 1
\item 2
\begin{itemize}
\item a (b)
\item 3.2
\end{itemize}
\item 4
\end{itemize}

% a last comment outside the environment
""")

        print("doc 5 = {}".format(ret))

    def test_parentheses(self):
        parser = Preparser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.preparse_from_string(r"""
text (in parentheses)
""")

        print("doc 6 = {}".format(ret))
        
    def test_basic_example(self):
        parser = Preparser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.preparse_from_file("../examples/basic.scrip.tex")

        print(ret)

        
if __name__ == '__main__':
    unittest.main()
