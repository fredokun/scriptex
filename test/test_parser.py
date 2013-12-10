'''
Test parser
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from tangolib.parser import Parser

class TestLexerString(unittest.TestCase):
    def test_line_comment(self):
        parser = Parser()

        ret = parser.parse_from_string("""
% this is a comment
    % after some space

""")

        print("doc 1 = {}".format(ret))

    def test_command_simple(self):
        parser = Parser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_string(r"""
% this is a comment
\mycommand[key1=value1,key2=value2]{
contents of the command
% a comment in the command
}
    % after some space

""")

        print("doc 2 = {}".format(ret))

    def test_command_simple_preformated(self):
        parser = Parser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_string(r"""
% this is a comment
\mycommand[key1=value1,key2=value2]{{{
contents of the command
  is preformated with {  curly brackets
  allowed }  
% a comment in the command
}}}
    % after some space

""")

        print("doc 2 bis = {}".format(ret))

    def test_env_simple(self):
        parser = Parser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_string(r"""
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

        print("doc 3 = {}".format(ret))

    def test_env_itemize(self):
        parser = Parser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_string(r"""
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
        parser = Parser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_string(r"""
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
        parser = Parser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_string(r"""
text (in parentheses)
""")

        print("doc 6 = {}".format(ret))
        
    def test_basic_example(self):
        parser = Parser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_file("../examples/basic.tango.tex")

        print(ret)
        
    def test_section_simple(self):
        parser = Parser()

        # BREAKPOINT >>> # import ipdb; ipdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_string(r"""

\section{section 1}

this is in section \emph{section 1} 

\subsection{subsection 1.1} 

this is in section \emph{subsection 1.1} 

\subsection{subsection 1.2} 

this is in section \emph{subsection 1.2}

\section{section 2} 

this is in section \emph{section 2} 

\subsection{subsection 2.1} 

this is in section \emph{subsection 2.1} 

\subsection{subsection 2.2} 

this is in section \emph{subsection 2.2}

""")

        print("doc 7 = {}".format(ret))
        
        # TODO: validate the result

    def test_mdsection_simple(self):
        parser = Parser()

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = parser.parse_from_string(r"""

= section 1 =

this is in section \emph{section 1} 

== subsection 1.1 ==

this is in section \emph{subsection 1.1} 

== subsection 1.2 ==

this is in section \emph{subsection 1.2}

= section 2 = 

this is in section \emph{section 2} 

== subsection 2.1 ==

this is in section \emph{subsection 2.1} 

== subsection 2.2 ==

this is in section \emph{subsection 2.2}

""")

        print("doc 8 = {}".format(ret))
        
        # TODO: validate the result


    def test_list_simple(self):
        parser = Parser()

        ret = parser.parse_from_string(r"""

\begin{itemize}

\item item 1.1
\item item 1.2

\begin{enumerate}

\item item 2.1
\item item 2.2

\end{enumerate}

\end{itemize}
""")

        print("doc 9 = {}".format(ret))
        
        # TODO: validate the result
        

    def test_mdlist_simple(self):
        parser = Parser()

        ret = parser.parse_from_string(r"""

   - item 1.1
   - item 1.2
     * item 2.1
     * item 2.2

""")

        print("doc 10 = {}".format(ret))
        
        # TODO: validate the result

        
    def test_inline_preformated(self):
        parser = Parser()

        ret = parser.parse_from_string(r"""

  The following is `inline preformated` and not the rest.

""")

        print("doc 11 = {}".format(ret))

if __name__ == '__main__':
    unittest.main()
