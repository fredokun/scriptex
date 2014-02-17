"""
  Macro-processing
"""

from tangolib.markup import MacroCommandDocument, MacroEnvHeaderDocument, MacroEnvFooterDocument

class MacroError(Exception):
    pass

class DefCommand:
    def __init__(self, cmd_doc, cmd_name, cmd_arity, cmd_start_pos, cmd_end_pos, cmd_template):
        self.cmd_doc = cmd_doc
        self.cmd_name = cmd_name
        self.cmd_arity = cmd_arity
        self.cmd_start_pos = cmd_start_pos
        self.cmd_end_pos = cmd_end_pos
        self.cmd_template = cmd_template

    def process(self, document, command):
        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        
        # first: check arity
        if len(command.arguments) != self.cmd_arity:
            raise MacroError("Wrong macro-command arity for '{}': expected {} but given {} argument{}"
                             .format(self.cmd_name,                                                                                  
                                     self.cmd_arity,
                                     len(command.arguments),
                                     "s" if len(command.arguments) > 1 else ""))

        # second: template rendering
        tpl_env = dict()
        for arg_num in range(1,self.cmd_arity+1):
            tpl_env['_'+str(arg_num)] = r"\macroCommandArgument[0]"

        result_to_parse = self.cmd_template.render(tpl_env)
        
        # third: recursive parsing of template result
        from tangolib.parser import Parser
        parser = Parser()

        lex = parser.prepare_string_lexer(result_to_parse)
        doc = MacroCommandDocument(document, "<<<MacroCommand:{}>>>".format(self.cmd_name), self.cmd_start_pos, self.cmd_end_pos, lex)
        
        result_parsed = parser.parse(doc, macro_cmd_arguments=command.arguments)

        return result_parsed


class DefEnvironment:
    def __init__(self, env_doc, env_name, env_arity, env_start_pos, env_end_pos, env_header_tpl, env_footer_tpl):
        self.env_doc = env_doc
        self.env_name = env_name
        self.env_arity = env_arity
        self.env_start_pos = env_start_pos
        self.env_end_pos = env_end_pos
        self.env_header_tpl = env_header_tpl
        self.env_footer_tpl = env_footer_tpl
        self.template_env = None
        self.env_arguments = None

    def process_header(self, document, env):
        
        # first: check arity
        if len(env.arguments) != self.env_arity:
            raise MacroError("Wrong macro-command arity for '{}': expected {} but given {} argument{}"
                             .format(self.env_name,                                                                                  
                                     self.env_arity,
                                     len(env.arguments),
                                     "s" if len(env.arguments) > 1 else ""))

        # second: template rendering
        self.template_env = dict()
        for arg_num in range(1,self.env_arity+1):
            self.template_env['_'+str(arg_num)] = r"\macroCommandArgument[0]"

        result_to_parse = self.env_header_tpl.render(self.template_env)
        
        # third: recursive parsing of template result
        from tangolib.parser import Parser
        parser = Parser()

        lex = parser.prepare_string_lexer(result_to_parse)
        doc = MacroEnvHeaderDocument(document, "<<<MacroEnvHeader:{}>>>".format(self.env_name), self.env_start_pos, self.env_end_pos, lex)
        
        result_parsed = parser.parse(doc, macro_cmd_arguments=env.arguments)

        self.env_arguments = env.arguments
        return result_parsed

    def process_footer(self, document, env):
        
        result_to_parse = self.env_footer_tpl.render(self.template_env)

        
        from tangolib.parser import Parser
        parser = Parser()

        lex = parser.prepare_string_lexer(result_to_parse)
        doc = MacroEnvFooterDocument(document, "<<<MacroEnvFooter:{}>>>".format(self.env_name), self.env_start_pos, self.env_end_pos, lex)
        
        result_parsed = parser.parse(doc, macro_cmd_arguments=self.env_arguments)

        return result_parsed
