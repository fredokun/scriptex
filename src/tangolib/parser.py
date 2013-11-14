"""Tango Parser.
The objective of the preliminary parsing phase is to
(try to) uncover the overall structure of the input document.

In particular it handles :
 - line comments
 - latex-style commands   \cmd[<opt>]{ <body> }
 - latex-style environments \begin{env}[<opt>] <body> \end{env}
 - latex-style sectionning commands \part \chapter \section \subsection \subsubsection \paragraph

"""

import tangolib.eregex as ere

import tangolib.lexer as lexer
from tangolib.markup import Document, Section, Command, Environment, Text, Newlines, Spaces

class ParseError(Exception):
    pass


def depth_of_section(section_type):
    if section_type == 'part':
        return -1
    elif section_type == 'chapter':
        return 0
    elif section_type == 'section':
        return 1
    elif section_type == 'subsection':
        return 2
    elif section_type == 'subsubsection':
        return 3
    elif section_type == 'paragraph':
        return 4
    else:
        raise ValueError("Not a valid section type: {}".format(section_type))

def section_of_depth(section_depth):
    if section_depth == -1:
        return "part"
    elif section_depth == 0:
        return "chapter"
    elif section_depth == 1:
        return "section"
    elif section_depth == 2:
        return "subsection"
    elif section_depth == 3:
        return "subsubsection"
    elif section_depth == 4:
        return "paragraph"
    else:
        raise ValueError("Not a valid section depth: {}".format(section_depth))
    

# extended regular expressions constants

REGEX_IDENT_STR = r"[a-zA-Z_][a-zA-Z_0-9]*"

REGEX_PROTECTED = ere.ERegex(r"\\{|\\}") 

#import pdb ; pdb.set_trace()
REGEX_LINE_COMMENT = ere.ERegex('%') + ere.zero_or_more(ere.any_char()) + ere.str_end()

REGEX_ENV_HEADER = ere.ERegex(r"\\begin{([^}]+)}(?:\[([^\]]+)\])?")
REGEX_ENV_FOOTER = ere.ERegex(r"\\end{([^}]+)}")

REGEX_SECTION = ere.ERegex(r"\\(part|chapter|section|subsection|subsubsection|paragraph){([^}]+)}")
REGEX_MDSECTION = ere.ERegex(r"^(=+)\s+([^=]+)\s+(=*)(.*)$")

REGEX_CMD_PRE_HEADER = ere.ERegex(r"\\(" + REGEX_IDENT_STR + r")(?:\[([^\]]+)\])?{{{")
REGEX_CMD_HEADER = ere.ERegex(r"\\(" + REGEX_IDENT_STR + r")(?:\[([^\]]+)\])?")

REGEX_SPACE_STR = r"[^\S\n\f\r]"
REGEX_SPACE = ere.ERegex(REGEX_SPACE_STR)
REGEX_SPACES = ere.ERegex("({})+".format(REGEX_SPACE_STR))

REGEX_MDLIST_OPEN = ere.ERegex("(?:^{0}*\\n)+({0}+)([-+*\\d](?:\\.)?){0}".format(REGEX_SPACE_STR))
#REGEX_MDLIST_ITEM_LAST = ere.ERegex("^({0}+)([-+*\\d](?:\\.)?){0}([^\\n]*)\\n{0}*\\n".format(REGEX_SPACE_STR))
REGEX_MDLIST_ITEM = ere.ERegex("^({0}+)([-+*\\d](?:\\.)?){0}".format(REGEX_SPACE_STR))

# main parser class

class Parser:
    def __init__(self):
        self.recognizers = []
        self.prepare_recognizers()

    def prepare_recognizers(self):
        self.recognizers.append(lexer.Regexp("protected", REGEX_PROTECTED))
        self.recognizers.append(lexer.EndOfInput("end_of_input"))
        self.recognizers.append(lexer.Regexp("line_comment", REGEX_LINE_COMMENT))
        self.recognizers.append(lexer.Regexp("env_header", REGEX_ENV_HEADER))
        self.recognizers.append(lexer.Regexp("env_footer", REGEX_ENV_FOOTER))
        self.recognizers.append(lexer.Regexp("section", REGEX_SECTION))
        self.recognizers.append(lexer.Regexp("mdsection", REGEX_MDSECTION, re_flags=ere.MULTILINE))

        # markdown lists
        self.recognizers.append(lexer.Regexp("mdlist_open", REGEX_MDLIST_OPEN, re_flags=ere.MULTILINE))
        #self.recognizers.append(lexer.Regexp("mdlist_item_last", REGEX_MDLIST_ITEM_LAST, re_flags=ere.MULTILINE))
        self.recognizers.append(lexer.Regexp("mdlist_item", REGEX_MDLIST_ITEM, re_flags=ere.MULTILINE))

        self.recognizers.append(lexer.Regexp("cmd_pre_header", REGEX_CMD_PRE_HEADER))
        self.recognizers.append(lexer.Regexp("cmd_header", REGEX_CMD_HEADER))
        self.recognizers.append(lexer.Char("open_curly", '{'))
        self.recognizers.append(lexer.Char("close_curly", '}'))
        self.recognizers.append(lexer.CharIn("newline", "\n", "\r"))
        self.recognizers.append(lexer.Regexp("spaces", REGEX_SPACES))

    class UnparsedContent:
        def __init__(self):
            self.content = ""
            self.start_pos = None
            self.end_pos = None

        def append_char(self, lexer):
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

        doc = Document(self.filename, lex.pos)
        
        element_stack = []

        current_element = doc
        continue_parse = True
        unparsed_content = Parser.UnparsedContent()

        while continue_parse:
            tok = lex.next_token()
            if tok is None:
                unparsed_content.append_char(lex)
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

            ###############################################
            ### Sections (latex-style or markdown-style ###
            ###############################################
            elif tok.token_type == "section" or tok.token_type == "mdsection":
                if tok.token_type == "section":
                    # latex section markup
                    section_title = tok.value.group(2)
                    section_depth = depth_of_section(tok.value.group(1))
                elif tok.token_type == "mdsection":
                    # markdown section markup
                    section_title = tok.value.group(2)
                    section_depth = len(tok.value.group(1))
                    if tok.value.group(3) != "" and tok.value.group(3) != tok.value.group(1):
                        raise ParseError(tok.start_pos.next_char(tok.value.start(3)), tok.start_pos.next_char(tok.value.end(3)), 'Wrong section marker: should be "" or "{}"'.format(tok.value.group(1)))
                    if tok.value.group(4) != "" and not tok.value.group(4).isspace():
                        raise ParseError(tok.start_pos.next_char(tok.value.start(4)), tok.start_pos.next_char(tok.value.end(3)), "Unexpected text '{}' after section markup".format(tok.value.group(4)))

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
                section = Section(section_title, section_of_depth(section_depth), section_depth, tok.start_pos, tok.end_pos)
                current_element.append(section)
                element_stack.append(current_element)
                current_element = section

            ############################################
            ### Markdown-style itemize and enumerate ###
            ############################################$
            elif tok.token_type == "mdlist_open" or tok.token_type == "mdlist_item":
                # BREAKPOINT >>> # 
                import pdb; pdb.set_trace()  # <<< BREAKPOINT #

                mditem_indent = len(tok.value.group(1))
                mditem_style = "itemize" if (tok.value.group(2)[0] == '-' or tok.value.group(2)[0] == '+') else "enumerate"

                unparsed_content.flush(current_element)
                
                # remove the previous item if it is active
                if current_element.markup_type == "command" and current_element.cmd_name == "item":
                    if not hasattr(current_element, "markdown_style"):
                        raise ParseError(current_element.start_pos, tok.start_pos, "Mixing latex-style and markdown-style lists is forbidden")
                    current_element = element_stack.pop()

                continue_closing = True

                while continue_closing:

                    dig_once_more = False

                    while current_element.markup_type not in { "command", "environment", "section", "document" }:
                        current_element = element_stack.pop()

                    if (current_element.markup_type == "environment") and (current_element.env_name in { "itemize", "enumerate" }) \
                    and (current_element.env_name == mditem_style):
                        try:
                            if current_element.markdown_style:
                                pass # ok
                        except AttributeError:
                            raise ParseError(current_element.start_pos, tok.start_pos, "Mixing latex-style and markdown-style lists is forbidden")
   
                        if current_element.markdown_indent == mditem_indent:
                            # add a further item at the same level
                            element_stack.append(current_element)
                            mditem = Command(mditem_style, None, tok.start_pos, tok.end_pos)
                            mditem.markdown_style = True
                            current_element.append(mditem)
                            current_element = mditem
                            continue_closing = False
                        elif current_element.markdown_indent > mditem_indent:
                            # close one
                            current_element = element_stack.pop()
                            continue_closing = True
                        else: # dig one level more
                            dig_once_more = True
                            continue_closing = False

                    else:
                        dig_once_more = True
                        continue_closing = False

                    if dig_once_more:
                        mdlist = Environment(mditem_style, None, tok.start_pos, tok.end_pos)
                        mdlist.markdown_style = True
                        mdlist.markdown_indent = mditem_indent
                        current_element.append(mdlist)
                        element_stack.append(current_element)
                        current_element = mdlist

                        mditem = Command(mditem_style, None, tok.start_pos, tok.end_pos)
                        mditem.markdown_style = True
                        current_element.append(mditem)
                        element_stack.append(current_element)
                        current_element = mditem

                # loop if continue_closing == True

                # and we're done

            ###########################################
            ### Special characters (newlines, etc.) ###
            ###########################################
            elif tok.token_type == "protected":
                unparsed_content.append_str(tok.value[1:], tok.start_pos, tok.end_pos)
            elif tok.token_type == "newline":
                unparsed_content.flush(current_element)
                newlines = tok.value
                while lex.peek_char() == "\n" or lex.peek_char() == "\r":
                    newlines += lex.next_char()

                ##  Special treatment for markdown lists
                if len(newlines) >= 2:
                    # remove the previous item if it is active
                    if current_element.markup_type == "command" and current_element.cmd_name == "item":
                        if not hasattr(current_element, "markdown_style"):
                            raise ParseError(current_element.start_pos, tok.start_pos, "Mixing latex-style and markdown-style lists is forbidden")
                        current_element = element_stack.pop()

                    # check if we need to finish some markdown list
                    element_stack_copy = element_stack[:]
                    element_stack_copy.append(current_element)
                    top_mdlist = None
                    while element_stack_copy:
                        current_element_copy = element_stack_copy.pop()
                        if current_element_copy.markup_type in { "command", "environment", "section", "document" } \
                           and not hasattr(current_element_copy, "markdown_style"):
                            element_stack = []
                        elif current_element_copy.markup_type == "environment":
                            top_mdlist = current_element_copy
                        
                        
                    if top_mdlist: # found a markdown list to close
                        while current_element is not top_mdlist:
                            current_element = element_stack.pop()

                        # close the top markdown list
                        current_element = element_stack.pop()
                        

                current_element.append(Newlines(newlines, tok.start_pos, tok.end_pos))

            elif tok.token_type == "spaces":
                unparsed_content.flush(current_element)
                current_element.append(Spaces(tok.value.group(0), tok.start_pos, tok.end_pos))
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

            
    def parse_from_string(self, input, filename="<string>"):
        self.filename = filename
        tokens = lexer.Tokenizer(lexer.StringTokenizer(input))
        lex = lexer.Lexer(tokens, *self.recognizers)

        return self.parse(lex)

    def parse_from_file(self, filename):
        f = open(filename, "r")
        input = f.read()
        f.close()
        doc = self.parse_from_string(input, filename)
        return doc
