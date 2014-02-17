"""Tango Parser.
The objective of the preliminary parsing phase is to
(try to) uncover the overall structure of the input document.

In particular it handles :
 - line comments
 - latex-style commands   \cmd[<opt>]{<arg1>}{...}{<argN>}
 - special preformated commands \cmd[<opt>]{{{ <preformated>}}}
 - latex-style environments \begin{env}[<opt>]{<arg1>}{...}{<argN>} <body> \end{env}
 - latex-style sectionning commands \part \chapter \section \subsection \subsubsection \paragraph

"""

import tangolib.eregex as ere

import tangolib.lexer as lexer
from tangolib.markup import Document, Section, Command, CommandArg, \
    Environment, Text, Newlines, Spaces, Preformated, SubDocument, EnvArg

import tangolib.template as template

from tangolib.macros import DefCommand, DefEnvironment

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

REGEX_LINE_COMMENT = ere.ERegex('%') + ere.zero_or_more(ere.any_char()) + ere.str_end()

REGEX_ENV_HEADER = ere.ERegex(r"\\begin{(" + REGEX_IDENT_STR + r")}(?:\[([^\]]+)\])?")
REGEX_ENV_FOOTER = ere.ERegex(r"\\end{(" + REGEX_IDENT_STR + r")}")

REGEX_INCLUDE = ere.ERegex(r"\\include{([^}]+)}")

REGEX_SECTION = ere.ERegex(r"\\(part|chapter|section|subsection|subsubsection|paragraph){([^}]+)}")
REGEX_MDSECTION = ere.ERegex(r"^(=+)\s+([^=]+)\s+(=*)(.*)$")

REGEX_CMD_PRE_HEADER = ere.ERegex(r"\\(" + REGEX_IDENT_STR + r")(?:\[([^\]]+)\])?{{{")
REGEX_CMD_HEADER = ere.ERegex(r"\\(" + REGEX_IDENT_STR + r")(?:\[([^\]]+)\])?")

REGEX_SPACE_STR = r"[^\S\n\f\r]"
REGEX_SPACE = ere.ERegex(REGEX_SPACE_STR)
REGEX_SPACES = ere.ERegex("({})+".format(REGEX_SPACE_STR))

REGEX_MDLIST_OPEN = ere.ERegex("(?:^{0}*\\n)+({0}+)([-+*\\d](?:\\.)?){0}".format(REGEX_SPACE_STR))
REGEX_MDLIST_ITEM = ere.ERegex("^({0}+)([-+*\\d](?:\\.)?){0}".format(REGEX_SPACE_STR))

REGEX_INLINE_PREFORMATED = ere.ERegex("`([^`]*)`")

REGEX_EMPH_STAR = ere.ERegex(r"(\*)(?=[^*]+\*)")
REGEX_STRONG_STAR = ere.ERegex(r"(\*)\*(?=[^*]+\*\*)")
REGEX_EMPH_UNDER = ere.ERegex(r"(_)(?=[^_]+_)")
REGEX_STRONG_UNDER = ere.ERegex(r"(_)_(?=[^_]+__)")

REGEX_DEF_CMD_HEADER = ere.ERegex(r"\\defCommand{\\(" + REGEX_IDENT_STR + r")}(?:\[([0-9]+)\])?")
REGEX_DEF_CMD_HEADER_SHORT = ere.ERegex(r"\\defCmd{\\(" + REGEX_IDENT_STR + r")}(?:\[([0-9]+)\])?")
REGEX_DEF_ENV_HEADER = ere.ERegex(r"\\defEnvironment{(" + REGEX_IDENT_STR + r")}(?:\[([0-9]+)\])?")
REGEX_DEF_ENV_HEADER_SHORT = ere.ERegex(r"\\defEnv{(" + REGEX_IDENT_STR + r")}(?:\[([0-9]+)\])?")
REGEX_MACRO_CMD_ARG = ere.ERegex(r"\\macroCommandArgument\[([0-9]+)\]")

# main parser class

class Parser:
    def __init__(self):
        self.recognizers = []
        self.prepare_recognizers()

    def prepare_recognizers(self):
        self.recognizers.append(lexer.Regexp("protected", REGEX_PROTECTED))
        self.recognizers.append(lexer.EndOfInput("end_of_input"))
        self.recognizers.append(lexer.Regexp("line_comment", REGEX_LINE_COMMENT))

        self.recognizers.append(lexer.Regexp("def_env_header", REGEX_DEF_ENV_HEADER))
        self.recognizers.append(lexer.Regexp("def_env_header", REGEX_DEF_ENV_HEADER_SHORT))
        self.recognizers.append(lexer.Regexp("def_cmd_header", REGEX_DEF_CMD_HEADER))
        self.recognizers.append(lexer.Regexp("def_cmd_header", REGEX_DEF_CMD_HEADER_SHORT))

        self.recognizers.append(lexer.Regexp("macro_cmd_arg", REGEX_MACRO_CMD_ARG))

        self.recognizers.append(lexer.Regexp("env_header", REGEX_ENV_HEADER))
        self.recognizers.append(lexer.Regexp("env_footer", REGEX_ENV_FOOTER))
        self.recognizers.append(lexer.Regexp("include", REGEX_INCLUDE))
        self.recognizers.append(lexer.Regexp("section", REGEX_SECTION))
        self.recognizers.append(lexer.Regexp("mdsection", REGEX_MDSECTION, re_flags=ere.MULTILINE))
        self.recognizers.append(lexer.Regexp("inline_preformated", REGEX_INLINE_PREFORMATED))
        self.recognizers.append(lexer.Regexp("strong", REGEX_STRONG_STAR))
        self.recognizers.append(lexer.Regexp("strong", REGEX_STRONG_UNDER))
        self.recognizers.append(lexer.Regexp("emph", REGEX_EMPH_STAR))
        self.recognizers.append(lexer.Regexp("emph", REGEX_EMPH_UNDER))
    
        # markdown lists
        self.recognizers.append(lexer.Regexp("mdlist_open", REGEX_MDLIST_OPEN, re_flags=ere.MULTILINE))
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
                parent.append(Text(parent.doc, self.content, self.start_pos, self.end_pos))
                self.content = ""
            self.start_pos = None
            self.end_pos = None

        def __repr__(self):
            return "UnparsedContent({},start_pos={},end_pos={})".format(repr(self.content), self.start_pos, self.end_pos)
        
    def parse(self, doc, macro_cmd_arguments=None):

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #

        element_stack = []

        current_element = doc
        continue_parse = True
        unparsed_content = Parser.UnparsedContent()

        lex = doc.lex

        while continue_parse:

            tok = lex.next_token()
            if tok is None:
                next_char = lex.peek_char()
                # When closing an emphasis
                if next_char in { '*', '_' } and current_element.markup_type == "command" \
                   and current_element.cmd_name in { "emph" , "strong" }:
                    
                    if current_element.cmd_name == "emph":
                        if current_element.cmd_opts['emph_type'] == next_char:
                            lex.next_char() # consume
                            unparsed_content.flush(current_element)
                            current_element = element_stack.pop()
                        else:
                            unparsed_content.append_char(lex)
                    elif current_element.cmd_name == "strong":
                        if current_element.cmd_opts['strong_type'] == next_char:
                            lex.next_chars(2) # consume two
                            unparsed_content.flush(current_element)
                            current_element = element_stack.pop()
                        else:
                            unparsed_content.append_char(lex)
                    else:
                        unparsed_content.append_char(lex)

                else: # in the other case just append the character
                    unparsed_content.append_char(lex)
 
            ###############################################
            ### End of input                            ###
            ###############################################
            elif tok.token_type == "end_of_input":
                unparsed_content.flush(current_element)

                while current_element.markup_type not in { "document", "subdoc", "macrocmddoc", "envcmddoc" }:
                    if current_element.markup_type == "command":
                        raise ParseError(current_element.start_pos, tok.start_pos, "Unfinished command before end of document")
                    elif current_element.markup_type == "environment":
                        raise ParseError(current_element.start_pos, tok.start_pos, "Unfinished environment before end of document")
                    else:
                        # ok to close
                        current_element.end_pos = tok.start_pos
                        current_element = element_stack.pop()

                if current_element.markup_type == "subdoc":
                    lex = current_element.sublex
                    doc = current_element.doc
                    current_element = element_stack.pop()
                else: # end of document
                    continue_parse = False

            ### Line comment ###
            elif tok.token_type == "line_comment":
                pass # just skip this

            ###############################################
            ### Environments                            ###
            ###############################################
            elif tok.token_type == "env_header":
                unparsed_content.flush(current_element)
                env = Environment(doc, tok.value.group(1), tok.value.group(2), tok.start_pos, tok.end_pos)
                current_element.append(env)
                element_stack.append(current_element)
                current_element = env

                # check if the environment has at least an argument
                ntok = lex.next_token() 
                if ntok is None:
                    pass  # special case: no more tokens (last command)
                elif ntok.token_type == "open_curly":
                    env.parsing_argument = True
                    lex.putback(ntok)  # need the bracket for argument parsing
                else:
                    env.parsing_argument = False
                    lex.putback(ntok)  # command without argument

            # start of argument  (or dummy bracket somewhere)
            elif current_element.markup_type == "environment" and current_element.parsing_argument and tok.token_type == "open_curly":
                # first argument
                env_arg = EnvArg(doc,current_element, tok.start_pos)
                current_element.add_argument(env_arg)
                element_stack.append(current_element)
                current_element = env_arg
                    
            # end of argument (or dummy bracket somewhere)
            elif current_element.markup_type == "env_arg" and tok.token_type == "close_curly":
                unparsed_content.flush(current_element)
                current_element.end_pos = tok.end_pos
                # Pop parent element (environment)
                current_element = element_stack.pop()

                # check if the environment has at least a further argument
                ntok = lex.next_token() 
                if ntok is None: # no more token ? ==> ERROR !
                    raise ParseError(tok.start_pos, tok.end_pos, "Missing closing environment at end of input")
                elif ntok.token_type == "open_curly":
                    current_element.parsing_argument = True
                    lex.putback(ntok)
                else:
                    current_element.parsing_argument = False
                    # keep the environment as current element for further argument or the body
                    lex.putback(ntok)  # need the bracket for argument parsing

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

            ###############################################
            ### Commands                                ###
            ###############################################
            elif tok.token_type == "cmd_header":
                unparsed_content.flush(current_element)
                cmd = Command(doc, tok.value.group(1), tok.value.group(2), tok.start_pos, tok.end_pos)
                current_element.append(cmd)
                
                # check if the command has at least an arguemnt
                ntok = lex.next_token() 
                if ntok is None:
                    pass  # special case: no more tokens (last command)
                elif ntok.token_type == "open_curly":
                    element_stack.append(current_element)
                    current_element = cmd
                    lex.putback(ntok)  # need the bracket for argument parsing
                else:
                    lex.putback(ntok)  # command without argument

            # start of argument  (or dummy bracket somewhere)
            elif current_element.markup_type == "command" and tok.token_type == "open_curly":
                # first argument
                cmd_arg = CommandArg(doc,current_element, tok.start_pos)
                current_element.add_argument(cmd_arg)
                element_stack.append(current_element)
                current_element = cmd_arg
                    
            # end of argument (or dummy bracket somewhere)
            elif current_element.markup_type == "command_arg" and tok.token_type == "close_curly":
                unparsed_content.flush(current_element)
                current_element.end_pos = tok.end_pos
                # Pop parent element (command)
                current_element = element_stack.pop()

                # check if the command has at least an arguemnt
                ntok = lex.next_token() 
                if ntok is None:
                    current_element = element_stack.pop()  # special case: no more tokens (last command, pop it)
                elif ntok.token_type == "open_curly":
                    # keep the command as current element
                    lex.putback(ntok)  # need the bracket for argument parsing
                else:
                    # pop the command
                    current_element = element_stack.pop()
                    lex.putback(ntok)  # command without more argument
                    
            elif tok.token_type == "cmd_pre_header":
                unparsed_content.flush(current_element)
                cmd = Command(doc, tok.value.group(1), tok.value.group(2), tok.start_pos, tok.end_pos, preformated=True)
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
            ### Include and subdocuments                ###
            ###############################################
            elif tok.token_type == "include":
                unparsed_content.flush(current_element)
                sub_filename = tok.value.group(1)
                try:
                    sub_file = open(sub_filename, "r")
                except OSError:
                    raise ParseError(tok.start_pos, lex.pos, "Cannot open included file: {}".format(sub_filename))

                try:
                    sub_input = sub_file.read()
                except IOError:
                    raise ParseError(tok.start_pos, lex.pos, "Cannot read included file: {} (IO error)".format(sub_filename))
                finally:
                    sub_input.close()
                    
                sub_tokens = lexer.Tokenizer(lexer.StringTokenizer(sub_input))
                sub_lex = lexer.Lexer(sub_tokens, *self.recognizers)

                sub_doc = SubDocument(doc, sub_filename, tok.start_pos, sub_lex)

                element_stack.push(current_element)
                current_element = sub_doc
                
                doc = sub_doc
                lex = sub_lex

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
                while current_element.markup_type == "section" \
                      and current_element.section_depth >= section_depth: # TODO: fix probably needed for mixing inclusion and sectionnning
                    current_element.end_pos = tok.start_pos
                    current_element = element_stack.pop()
                section = Section(doc, section_title, section_of_depth(section_depth), section_depth, tok.start_pos, tok.end_pos)
                current_element.append(section)
                element_stack.append(current_element)
                current_element = section

            ############################################
            ### Markdown-style itemize and enumerate ###
            ############################################$
            elif tok.token_type == "mdlist_open" or tok.token_type == "mdlist_item":
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

                    # TODO: fix probably needed for closing with subdocument
                    while current_element.markup_type not in { "command", "environment", "section", "document", "subdoc" }:
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
                            mditem = Command(doc, "item", None, tok.start_pos, tok.end_pos)
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
                        mdlist = Environment(doc, mditem_style, None, tok.start_pos, tok.end_pos)
                        mdlist.markdown_style = True
                        mdlist.markdown_indent = mditem_indent
                        current_element.append(mdlist)
                        element_stack.append(current_element)
                        current_element = mdlist

                        mditem = Command(doc, "item", None, tok.start_pos, tok.end_pos)
                        mditem.markdown_style = True
                        current_element.append(mditem)
                        element_stack.append(current_element)
                        current_element = mditem

                # loop if continue_closing == True

                # and we're done

            ###########################################
            ### Inline preformated                  ###
            ###########################################
            elif tok.token_type == "inline_preformated":
                unparsed_content.flush(current_element)
                preformated = Preformated(doc, tok.value.group(1), "inline", tok.start_pos, tok.end_pos)
                current_element.append(preformated)

            ### Emphasis (normal) ###
            elif tok.token_type == "emph":
                unparsed_content.flush(current_element)
                cmd = Command(doc, "emph", {'emph_type': tok.value.group(1) }, tok.start_pos, tok.end_pos)
                current_element.append(cmd)
                element_stack.append(current_element)
                current_element = cmd

            ### Strong emphasis ###
            elif tok.token_type == "strong":
                unparsed_content.flush(current_element)
                cmd = Command(doc, "strong", {'strong_type': tok.value.group(1) }, tok.start_pos, tok.end_pos)
                current_element.append(cmd)
                element_stack.append(current_element)
                current_element = cmd

            ######################################################
            ### Macros: commands and environments definitions  ###
            ######################################################
            ### command definition
            elif tok.token_type == "def_cmd_header":
                unparsed_content.flush(current_element)

                def_cmd_name = tok.value.group(1)
                def_cmd_arity = 0
                if tok.value.group(2) is not None:
                    def_cmd_arity = int(tok.value.group(2))
                                
                tok2 = lex.next_token()
                if tok2.token_type != "open_curly":
                    raise ParseError(tok.end_pos, tok.end_pos.next_char(), "Missing '{' for \\defCommand body")

                # prepare the template string
                def_cmd_lex_start_pos = lex.pos
                def_cmd_lex_str = ""
                nb_curly = 1
                while nb_curly > 0:
                    ch = lex.next_char()
                    if ch is None:
                        raise ParseError(def_cmd_lex_start_pos, lex.pos, "Unexpected end of input while parsing \\defCommand body")
                    elif ch == '}':
                        nb_curly -= 1
                        if nb_curly > 0:
                            def_cmd_lex_str += ch
                    else:
                        if ch == '{':
                            nb_curly += 1
                        def_cmd_lex_str += ch


                def_cmd_tpl = template.Template(def_cmd_lex_str,
                                                safe_mode = False,
                                                escape_var='#',
                                                escape_inline='@',
                                                escape_block='@',
                                                escape_block_open='{',
                                                escape_block_close='}',
                                                escape_emit_function='emit',
                                                filename='<defCommand:{}>'.format(def_cmd_name),
                                                base_pos=def_cmd_lex_start_pos)

                def_cmd_tpl.compile()

                # register the command
                doc.def_commands[def_cmd_name] = DefCommand(doc, def_cmd_name, def_cmd_arity, tok.start_pos, tok.end_pos, def_cmd_tpl)

            ### macro-command argument
            elif tok.token_type == "macro_cmd_arg": ### XXX: dead code ?
                unparsed_content.flush(current_element)
                arg_num = int(tok.value.group(1))
                command_arg_markup = macro_cmd_arguments[arg_num]
                current_element.append(command_arg_markup)
                element_stack.append(current_element)
                current_element = command_arg_markup
                

            ### environment definition
            elif tok.token_type == "def_env_header":

                unparsed_content.flush(current_element)

                def_env_name = tok.value.group(1)
                def_env_arity = 0
                if tok.value.group(2) is not None:
                    def_env_arity = int(tok.value.group(2))

                tok2 = lex.next_token()
                if tok2.token_type != "open_curly":
                    raise ParseError(tok.end_pos, tok.end_pos.next_char(), "Missing '{' for \\defEnvironment header body")


                # prepare the template string for the header part
                def_env_header_lex_start_pos = lex.pos
                def_env_header_lex_str = ""

                nb_curly = 1
                while nb_curly > 0:
                    ch = None
                    try:
                        ch = lex.next_char()
                        if ch is None:
                            raise ParseError(def_env_header_lex_start_pos, lex.pos, "Unexpected end of input while parsing \\defEnvironment header body")
                    except:
                        raise ParseError(def_env_header_lex_start_pos, lex.pos, "Unexpected end of input while parsing \\defEnvironment header body")
                    if ch == '}':
                        nb_curly -= 1
                        if nb_curly > 0:
                            def_env_header_lex_str += ch
                    else:
                        if ch == '{':
                            nb_curly += 1
                        def_env_header_lex_str += ch
                    
                def_env_header_tpl = template.Template(def_env_header_lex_str,
                                                       safe_mode=False,
                                                       escape_var='#',
                                                       escape_inline='@',
                                                       escape_block='@',
                                                       escape_block_open='{',
                                                       escape_block_close='}',
                                                       escape_emit_function='emit',
                                                       filename='<defEnvironment:{}>'.format(def_env_name),
                                                       base_pos=def_env_header_lex_start_pos)
                def_env_header_tpl.compile()

                # prepare the template string for the footer part

                tok2 = lex.next_token()
                if tok2.token_type != "open_curly":
                    raise ParseError(tok.end_pos, tok.end_pos.next_char(), "Missing '{' for \\defEnvironment footer body")

                def_env_footer_lex_start_pos = lex.pos
                def_env_footer_lex_str = ""

                nb_curly = 1
                while nb_curly > 0:
                    ch = None
                    try:
                        ch = lex.next_char()
                        if ch is None:
                            raise ParseError(def_env_footer_lex_start_pos, lex.pos, "Unexpected end of input while parsing \\defEnvironment footer body")
                    except:
                        raise ParseError(def_env_footer_lex_start_pos, lex.pos, "Unexpected end of input while parsing \\defEnvironment footer body")
                    
                    if ch == '}':
                        nb_curly -= 1
                        if nb_curly > 0:
                            def_env_footer_lex_str += ch
                    else:
                        if ch == '{':
                            nb_curly += 1
                        def_env_footer_lex_str += ch
                    
                def_env_footer_tpl = template.Template(def_env_footer_lex_str,
                                                       safe_mode=False,
                                                       escape_var='#',
                                                       escape_inline='@',
                                                       escape_block='@',
                                                       escape_block_open='{',
                                                       escape_block_close='}',
                                                       escape_emit_function='emit',
                                                       filename='<defEnvironment:{}>'.format(def_env_name),
                                                       base_pos=def_env_footer_lex_start_pos)
                def_env_footer_tpl.compile()

                # register the environement
                doc.def_environments[def_env_name] = DefEnvironment(doc, def_env_name, def_env_arity, def_env_header_lex_start_pos, lex.pos, def_env_header_tpl, def_env_footer_tpl)
            


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
                if len(newlines) >= 2 or lex.at_eof():
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
                            element_stack_copy = []
                        elif current_element_copy.markup_type == "environment":
                            top_mdlist = current_element_copy
                        
                        
                    if top_mdlist: # found a markdown list to close
                        while current_element is not top_mdlist:
                            current_element = element_stack.pop()

                        # close the top markdown list
                        current_element = element_stack.pop()
                        

                current_element.append(Newlines(doc, newlines, tok.start_pos, tok.end_pos))

            elif tok.token_type == "spaces":
                unparsed_content.flush(current_element)
                current_element.append(Spaces(doc, tok.value.group(0), tok.start_pos, tok.end_pos))
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


    def prepare_string_lexer(self, input):
        tokens = lexer.Tokenizer(lexer.StringTokenizer(input))
        lex = lexer.Lexer(tokens, *self.recognizers)
        return lex
        
    def parse_from_string(self, input, filename="<string>"):
        self.filename = filename
        lex = self.prepare_string_lexer(input)
        doc = Document(self.filename, lex)            
        return self.parse(doc)

    def parse_from_file(self, filename):
        f = open(filename, "r")
        input = f.read()
        f.close()
        doc = self.parse_from_string(input, filename)
        return doc

