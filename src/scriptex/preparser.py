"""Preparser.
The objective of the preliminary parsing phase is to
(try to) uncover the overall structure of the input document.

In particular it handles :
 - line comments
 - latex-style commands   \cmd[<opt>]{ <body> }
 - latex-style environments \begin{env}[<opt>] <body> \end{env}
 - latex-style sectionning commands \part \chapter \section \subsection \subsubsection \paragraph

"""

import scriptex.lexer as lexer
from scriptex.premarkup import PreDocument, PreSection, PreCommand, PreEnvironment

class PreparseError(Exception):
    pass


def depth_of_section(section_type):
    if section_type == 'part':
        return 1
    elif section_type == 'chapter':
        return 2
    elif section_type == 'section':
        return 3
    elif section_type == 'subsection':
        return 4
    elif section_type == 'subsubsection':
        return 5
    elif section_type == 'paragraph':
        return 6
    else:
        raise ValueError("Not a valid section type: {}".format(section_type))

class Preparser:
    def __init__(self):
        self.recognizers = []
        self.prepare_recognizers()

    def prepare_recognizers(self):
        ident_re = r"[a-zA-Z_][a-zA-Z_0-9]*"

        self.recognizers.append(lexer.Regexp("protected", r"\\{|\\}"))
        self.recognizers.append(lexer.EndOfInput("end_of_input"))
        self.recognizers.append(lexer.Regexp("line_comment", r"\%.*$"))
        self.recognizers.append(lexer.Regexp("env_header", r"\\begin{([^}]+)}(?:\[([^\]]+)\])?"))
        self.recognizers.append(lexer.Regexp("env_footer", r"\\end{([^}]+)}"))
        self.recognizers.append(lexer.Regexp("section", r"\\(part|chapter|section|subsection|subsubsection|paragraph){([^}]+)}"))
        self.recognizers.append(lexer.Regexp("cmd_header", r"\\(" + ident_re + r")(?:\[([^\]]+)\])?"))
        self.recognizers.append(lexer.Char("open_curly", '{'))
        self.recognizers.append(lexer.Char("close_curly", '}'))
    
    def preparse(self, lex):

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #

        doc = PreDocument(lex.pos)
        
        element_stack = []

        current_element = doc
        continue_preparse = True
        unparsed_content = ""
        while continue_preparse:
            tok = lex.next_token()
            if tok is None:
                unparsed_content += lex.next_char()
            elif tok.token_type == "end_of_input":
                continue_preparse = False
            elif tok.token_type == "line_comment":
                pass # just skip this
            elif tok.token_type == "env_header":
                if unparsed_content != "":
                    current_element.append(unparsed_content)
                    unparsed_content = ""
                env = PreEnvironment(tok.value.group(1), tok.value.group(2), tok.start_pos, tok.end_pos)
                current_element.append(env)
                element_stack.append(current_element)
                current_element = env
            elif tok.token_type == "env_footer":
                if current_element.markup_type != "environment":
                    raise PreparseError(tok.start_pos, tok.end_pos, "Cannot close environment")
                if current_element.env_name != tok.value.group(1):
                    raise PreparseError(tok.start_pos, tok.end_pos, "Mismatch environment '{}' (expecting '{}')".format(tok.group(1), current_element.env_name))
                if unparsed_content != "":
                    current_element.append(unparsed_content)
                    unparsed_content = ""

                current_element.footer_start_pos = tok.start_pos
                current_element.end_pos = tok.end_pos

                # Pop parent element
                current_element = element_stack.pop()
            elif tok.token_type == "cmd_header":
                if unparsed_content != "":
                    current_element.append(unparsed_content)
                    unparsed_content = ""
                cmd = PreCommand(tok.value.group(1), tok.value.group(2), tok.start_pos, tok.end_pos)
                current_element.append(cmd)
                
                ntok = lex.next_token()
                if ntok is None:
                    pass
                elif ntok.token_type == "open_curly":
                    element_stack.append(current_element)
                    current_element = cmd
                else:
                    lex.putback(ntok)
            elif tok.token_type == "close_curly":
                if current_element.markup_type == "command":
                    if unparsed_content != "":
                        current_element.append(unparsed_content)
                        unparsed_content = ""
                    current_element.end_pos = tok.end_pos
                    # Pop parent element
                    current_element = element_stack.pop()
                else:
                    unparsed_content += "}"
            elif tok.token_type == "open_curly":
                unparsed_content += "{"
            elif tok.token_type == "section":
                section_title = tok.value.group(1)
                section_depth = depth_of_section(tok.value.group(1))
                if current_element.markup_type == "command":
                    raise PreparseError(current_element.start_pos, tok.start_pos, "Unfinished command before section")
                elif current_element.markup_type == "environment":
                    raise PreparseError(current_element.start_pos, tok.start_pos, "Unfinished environment before section")
                # ok to parse new section
                if unparsed_content != "":
                    current_element.append(unparsed_content)
                    unparsed_content = ""
                # close all sections of greater or equal depth
                while current_element.section_depth >= section_depth:
                    current_element.end_pos = tok.start_pos
                    current_element = element_stack.pop()
                section = PreSection(section_title, section_depth, tok.start_pos, tok.end_pos)
                current_element.append(section)
                element_stack.append(current_element)
                current_element = section
            elif tok.token_type == "protected":
                unparsed_content += tok.value[1:]
            else:
                # unrecognized token type
                raise PreparseError(tok.start_pos, tok.end_pos, "Unrecognized token type: {}".format(tok.token_type))

        # at the end of input
        if unparsed_content != "":
            current_element.append(unparsed_content)
            unparsed_content = ""
        
        while current_element != doc:
            if current_element.markup_type == "command":
                raise PreparseError(current_element.start_pos, tok.start_pos, "Unfinished command before end of document")
            elif current_element.markup_type == "environment":
                raise PreparseError(current_element.start_pos, tok.start_pos, "Unfinished environment before end of document")
            else:
                # ok to close
                current_element.end_pos = tok.start_pos
                current_element = element_stack.pop()

        # preparsing finished
        return doc

            
    def preparse_from_string(self, input):
        tokens = lexer.Tokenizer(lexer.StringTokenizer(input))
        lex = lexer.Lexer(tokens, *self.recognizers)

        return self.preparse(lex)

    def preparse_from_file(self, filename):
        f = open(filename, "r")
        input = f.read()
        f.close()
        doc = self.preparse_from_string(input)
        return doc
