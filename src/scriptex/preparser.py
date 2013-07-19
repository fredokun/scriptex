"""Preparser.
The objective of the preliminary parsing phase is to
(try to) uncover the overall structure of the input document.

In particular it handles :
 - line comments
 - latex-style commands   \cmd[<opt>]{ <body> }
 - latex-style environments \begin{env}[<opt>] <body> \end{env}
 - latex-style sectionning commands \part \chapter \section \subsection \subsubsection \paragraph

"""

from premarkup import PreDocument, PreComment, PreSection, PreCommand, 

class PreparseError(Exception):
    pass


class Preparser:
    def __init__(self):
        self.recognizers = self.prepare_recognizers()

    def _register_recognizer(self,rec):
        self.recognizers[rec.token_type] = rec
        
    def prepare_recognizers(self):
        ident_re = r"[a-zA-Z_][a-zA-Z_0-9]*"

        self._register_recognizer(lexer.EndOfInput("end_of_input"))
        self._register_recognizer(lexer.Regexp("line_comment", r"%(.)*$"))
        self._register_recognizer(lexer.Regexp("env_header", r"\\begin{([^}]+)}(\[[^\]]+\])"))
        self._register_recognizer(lexer.Regexp("env_footer", r"\\end{([^}]+)}"))
        self._register_recognizer(lexer.Regexp("cmd_header", r"\\(" + ident_re + r")(\[[^\]]+\])"))
        self._register_recognizer(lexer.Char("open_curly", '{'))
        self._register_recognizer(lexer.Char("close_curly", '}'))

    
    def preparse(lex):

        doc = PreDocument()
        
        element_stack = []

        current_element = doc
        continue_preparse = True
        unparsed_content = ""
        while continue_preparse:
            tok = lex.next_token()
            if tok.token_type == "line_comment":
                pass # just skip this
            elif tok.token_type == "env_header":
                if unparsed_content != "":
                    current_element.append(unparsed_content)
                env = PreEnvironment(tok.group(1), tok.group(2), tok.start_pos, tok.end_pos)
                element_stack.put(current_element)
                current_element = env
            elif tok.token_type == "env_footer":
                if current_element.markup_type != "environment":
                    raise PreParseError(tok.
                if unparsed_content != "":
                    current_element.append(unparsed_content)
                
                
                
            
            
            
    def preparse_from_string(input):
        tokens = lexer.Tokenizer(lexer.StringTokenizer(input))
        recs = [rec for _,rec in self.recognizers.items()]
        # print("recs = {}".format([str(r) for r in recs]))
        lex = lexer.Lexer(tokens, *recs)

        return self.preparse(lex)

    
