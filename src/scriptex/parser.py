"""Oarser.
The objective of the preliminary parsing phase is to
(try to) uncover the overall structure of the input document.

In particular it handles :
 - line comments
 - latex-style commands   \cmd[<opt>]{ <body> }
 - latex-style environments \begin{env}[<opt>] <body> \end{env}
 - latex-style sectionning commands \part \chapter \section \subsection \subsubsection \paragraph

"""

import scriptex.lexer as lexer
from scriptex.markup import Document, Section, Command, Environment, Text, Newlines, Spaces

class ParseError(Exception):
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

def section_of_depth(section_depth):
    if section_depth == 1:
        return "part"
    elif section_depth == 2:
        return "chapter"
    elif section_depth == 3:
        return "section"
    elif section_depth == 4:
        return "subsection"
    elif section_depth == 5:
        return "subsubsection"
    elif section_depth == 6:
        return "paragraph"
    else:
        raise ValueError("Not a valid section depth: {}".format(section_depth))
    
class Parser:
    def __init__(self):
        self.recognizers = []
        self.prepare_recognizers()

    def prepare_recognizers(self):
        ident_re = r"[a-zA-Z_][a-zA-Z_0-9]*"

        self.recognizers.append(lexer.CharIn("newline", "\n", "\r"))
        self.recognizers.append(lexer.Regexp("spaces", r"[ \t]+"))
        self.recognizers.append(lexer.Regexp("protected", r"\\{|\\}"))
        self.recognizers.append(lexer.EndOfInput("end_of_input"))
        self.recognizers.append(lexer.Regexp("line_comment", r"\%.*$"))
        self.recognizers.append(lexer.Regexp("env_header", r"\\begin{([^}]+)}(?:\[([^\]]+)\])?"))
        self.recognizers.append(lexer.Regexp("env_footer", r"\\end{([^}]+)}"))
        self.recognizers.append(lexer.Regexp("section", r"\\(part|chapter|section|subsection|subsubsection|paragraph){([^}]+)}"))
        self.recognizers.append(lexer.Regexp("cmd_pre_header", r"\\(" + ident_re + r")(?:\[([^\]]+)\])?{{{"))
        self.recognizers.append(lexer.Regexp("cmd_header", r"\\(" + ident_re + r")(?:\[([^\]]+)\])?"))
        self.recognizers.append(lexer.Char("open_curly", '{'))
        self.recognizers.append(lexer.Char("close_curly", '}'))

    class UnparsedContent:
        def __init__(self):
            self.content = ""
            self.start_pos = None
            self.end_pos = None

        def append_char(self, lexer,):
            if self.start_pos is None:
                self.start_pos = lexer.pos
            self.content += lexer.next_char()
            self.end_pos = lexer.pos

        def append_str(self, str_, start_pos, end_pos):
            if self.start_pos is None:
                self.start_pos = start_pos

                self.content += str_
                self.end_pos = end_pos

        def flush(self, parent):
            if self.content != "":
                parent.append(Text(self.content, self.start_pos, self.end_pos))
                self.content = ""
            self.start_pos = None
            self.end_pos = None

        def __repr__(self):
            return "UnparsedContent({},start_pos={},end_pos={})".format(repr(self.content), self.start_pos, self.end_pos)
        
    def parse(self, lex):

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #

        doc = Document(lex.pos)
        
        element_stack = []

        current_element = doc
        continue_parse = True
        unparsed_content = Parser.UnparsedContent()
        while continue_parse:
            tok = lex.next_token()
            if tok is None:
                unparsed_content.append_char(lex)
            elif tok.token_type == "newline":
                unparsed_content.flush(current_element)
                newlines = tok.value
                while lex.peek_char() == "\n" or lex.peek_char() == "\r":
                    newlines += lex.next_char()
                current_element.append(Newlines(newlines, tok.start_pos, tok.end_pos))
            elif tok.token_type == "spaces":
                unparsed_content.flush(current_element)
                current_element.append(Spaces(tok.value.group(0), tok.start_pos, tok.end_pos))
            elif tok.token_type == "end_of_input":
                unparsed_content.flush(current_element)
                continue_parse = False
            elif tok.token_type == "line_comment":
                pass # just skip this
            elif tok.token_type == "env_header":
                unparsed_content.flush(current_element)
                env = Environment(tok.value.group(1), tok.value.group(2), tok.start_pos, tok.end_pos)
                current_element.append(env)
                element_stack.append(current_element)
                current_element = env
            elif tok.token_type == "env_footer":
                if current_element.markup_type != "environment":
                    raise ParseError(tok.start_pos, tok.end_pos, "Cannot close environment")
                if current_element.env_name != tok.value.group(1):
                    raise ParseError(tok.start_pos, tok.end_pos, "Mismatch environment '{}' (expecting '{}')".format(tok.group(1), current_element.env_name))
                unparsed_content.flush(current_element)

                current_element.footer_start_pos = tok.start_pos
                current_element.end_pos = tok.end_pos

                # Pop parent element
                current_element = element_stack.pop()
            elif tok.token_type == "cmd_header":
                unparsed_content.flush(current_element)
                cmd = Command(tok.value.group(1), tok.value.group(2), tok.start_pos, tok.end_pos)
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
                    unparsed_content.flush(current_element)
                    current_element.end_pos = tok.end_pos
                    # Pop parent element
                    current_element = element_stack.pop()
                else:
                    unparsed_content.append_str("}", tok.start_pos, tok.end_pos)
            elif tok.token_type == "cmd_pre_header":
                unparsed_content.flush(current_element)
                cmd = Command(tok.value.group(1), tok.value.group(2), tok.start_pos, tok.end_pos, preformated=True)
                current_element.append(cmd)
                preformated = ""
                eat_preformated = True
                while eat_preformated:
                    footer = lex.peek_chars(3)
                    if footer is None:
                        raise ParseError(tok.start_pos, lex.pos, "Preformated command unfinished (missing '}}}')")
                    elif footer == "}}}":
                        cmd.content = preformated
                        eat_preformated = False
                        lex.next_chars(3)
                    else:
                        preformated += lex.next_char()
            elif tok.token_type == "open_curly":
                unparsed_content.append_str("{", tok.start_pos, tok.end_pos)
            elif tok.token_type == "section":
                section_title = tok.value.group(2)
                section_depth = depth_of_section(tok.value.group(1))
                if current_element.markup_type == "command":
                    raise ParseError(current_element.start_pos, tok.start_pos, "Unfinished command before section")
                elif current_element.markup_type == "environment":
                    raise ParseError(current_element.start_pos, tok.start_pos, "Unfinished environment before section")
                # ok to parse new section
                unparsed_content.flush(current_element)
                # close all sections of greater or equal depth
                while current_element.section_depth >= section_depth:
                    current_element.end_pos = tok.start_pos
                    current_element = element_stack.pop()
                section = Section(section_title, tok.value.group(1), section_depth, tok.start_pos, tok.end_pos)
                current_element.append(section)
                element_stack.append(current_element)
                current_element = section
            elif tok.token_type == "protected":
                unparsed_content.append_str(tok.value[1:], tok.start_pos, tok.end_pos)
            else:
                # unrecognized token type
                raise ParseError(tok.start_pos, tok.end_pos, "Unrecognized token type: {}".format(tok.token_type))

        # at the end of input
        unparsed_content.flush(current_element)

        
        while current_element != doc:
            if current_element.markup_type == "command":
                raise ParseError(current_element.start_pos, tok.start_pos, "Unfinished command before end of document")
            elif current_element.markup_type == "environment":
                raise ParseError(current_element.start_pos, tok.start_pos, "Unfinished environment before end of document")
            else:
                # ok to close
                current_element.end_pos = tok.start_pos
                current_element = element_stack.pop()

        # preparsing finished
        return doc

            
    def parse_from_string(self, input):
        tokens = lexer.Tokenizer(lexer.StringTokenizer(input))
        lex = lexer.Lexer(tokens, *self.recognizers)

        return self.parse(lex)

    def parse_from_file(self, filename):
        f = open(filename, "r")
        input = f.read()
        f.close()
        doc = self.parse_from_string(input)
        return doc
