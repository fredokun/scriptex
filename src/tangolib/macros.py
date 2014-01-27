"""
  Macro-processing
"""

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
        # first: check arity
        if len(command.arguments) != self.cmd_arity:
            raise MacroError("Wrong macro-command arity: expected {} but given {} argument{}",
                             self.cmd_arity,
                             len(command.arguments),
                             "s" if len(command.arguments) > 1 else "")

        # second: template rendering
        tpl_env = dict()
        for arg_num in range(1,self.cmd_arity+1)):
            tpl_env[str(arg_num)] = r"\macroCommandArgument[0]"

        result_to_parse = self.cmd_template.render(tpl_env)
        
        # third: recursive parsing of template result
        parser = Parser()

        lex = parse.prepare_string_lexer(result_to_parse)
        doc = MacroCommandDocument(document, "<<<MacroCommand:{}>>>".format(self.cmd_name), self.cmd_start_pos, self.cmd_end_pos, lex)
        
        result_parsed = self.parse(doc, macro_cmd_arguments=command.arguments)

        return result_parsed

class DefEnvironment:
    def __init__(self, env_name, env_header_tpl, env_footer_tpl):
        self.env_name = env_name
        self.env_header_tpl = env_header_tpl
        self.env_footer_tpl = env_footer_tpl

