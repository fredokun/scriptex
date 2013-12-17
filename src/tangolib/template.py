
# a stupid template engine

import ast

from lexer import ParsePosition

class TemplateCompileError(Exception):
    def __init__(self, msg, template, start_pos, end_pos):
        super().__init__(msg)
        self.template = template
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.ctemplate = None


class TemplateRenderError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class Template:
    def __init__(self, 
                 template, 
                 safe_mode=False, 
                 escape_var="$", escape_inline="%", escape_block="%", escape_block_open="{", escape_block_close="}",
                 escape_emit_function="emit",
                 filename='<unknown>',
                 base_pos=None):
        assert escape_var != escape_inline, "Require distinct escape variable"
        assert escape_var != escape_block, "Require distinct escape variable"
        assert escape_block_open != escape_inline, "Require distinct escape block open"
        assert escape_block_close != escape_inline, "Require distinct escape block close"
        assert escape_block_open != escape_block, "Require distinct escape block open"
        assert escape_block_close != escape_block, "Require distinct escape block close"

        self.template = template
        self.escape_var = escape_var
        self.escape_inline = escape_inline
        self.escape_block = escape_block
        self.escape_block_open = escape_block_open
        self.escape_block_close = escape_block_close
        if base_pos is None:
           self.base_pos = ParsePosition()
       else:
           self.base_pos = base_pos
        self.escape_emit_function = escape_emit_function
        self.safe_mode = safe_mode
        self.ctemplate = None
        self.filename = filename

    def global_env(self):
        genv = None
        if self.safe_mode:
            genv = dict()
        else:
            genv = globals().copy()

        return genv


    def _install_render_env(self, env):
        global ___Template_emit_function___

        renv = env.copy()
        renv[self.escape_emit_function] = ___Template_emit_function___
        
        return renv
            
    def render(self, env):
        if self.ctemplate is None:
            raise TemplateRenderError("Template not compiled")

        ret = ""
        for element in self.ctemplate:
            ret += element.render(env)

        return ret

    def compile(self):
        len_template = len(self.template)
        self.ctemplate = []

        start_pos = self.base_pos
        current_pos = start_pos

        part = ""
        while current_pos.offset < len_template:
            current_char = self.template[current_pos.offset]
            if current_char == '\n':
                current_pos = current_pos.next_line()
                part += current_char
            elif current_char == self.escape_var and current_pos.offset + 1 < len_template \
                 and self.template[current_pos.offset+1] != self.escape_var:
                self._register_literal(part, start_pos, current_pos)
                part = ""
                start_pos = current_pos
                start_pos = self._parse_variable(start_pos)
                current_pos = start_pos
            elif current_char == self.escape_inline and (current_pos.offset + 1 >= len_template \
                 or (self.template[current_pos.offset+1] != self.escape_inline \
                 and self.template[current_pos.offset+1] != self.escape_block_open)):
                self._register_literal(part, start_pos, current_pos)
                part = ""
                start_pos = current_pos
                start_pos = self._parse_escape_inline(start_pos)
                current_pos = start_pos
            elif current_char == self.escape_block and (current_pos.offset + 1 >= len_template \
                 or self.template[current_pos.offset+1] == self.escape_block_open):
                self._register_literal(part, start_pos, current_pos)
                part = ""
                start_pos = current_pos
                start_pos = self._parse_escape_block(start_pos)
                current_pos = start_pos
            else: # a literal character
                part += current_char
                current_pos = current_pos.next_char()
                if current_char in { self.escape_var, self.escape_inline, self.escape_block, self.escape_block_open, self.escape_block_close }:
                    current_pos = current_pos.next_char() # protected escape

        # end of while
        if part != "":
            self._register_literal(part, start_pos, current_pos)
            start_pos = current_pos


    def _register_literal(self, literal, start_pos, end_pos):
        self.ctemplate.append(Template.Literal(self, literal, start_pos, end_pos))

    def _parse_variable(self, start_pos):
        assert self.template[start_pos.offset] == self.escape_var

        len_template = len(self.template)

        current_pos = start_pos.next_char()
        ident = ""
        continue_parse = True
        while continue_parse:
            if current_pos.offset >= len_template:
                continue_parse = False
            else:
                current_char = self.template[current_pos.offset]
                if (not current_char.isspace()) and current_char.isprintable():
                    ident += current_char
                    current_pos = current_pos.next_char()
                else: # a space or non-printable character
                    continue_parse = False

        # end of while
        ident_prefix = ident
        prefix_pos = current_pos
        while ident_prefix != "" and not ident_prefix.isidentifier() and not ident_prefix.isdecimal():
            ident_prefix = ident_prefix[:-1]
            prefix_pos = prefix_pos.prev_char()

        if ident_prefix == "":
            raise TemplateCompileError("Not a variable identifier: '{}'".format(ident), self.template, start_pos, current_pos)
        elif ident_prefix.isdecimal():
            ident_prefix = '_' + ident_prefix # '_n' with n decimal is a correct variable name in python
        # nothing to do if isidentifier()

        ident = ident_prefix
        current_pos = prefix_pos

        self.ctemplate.append(Template.Variable(self, ident, start_pos, current_pos))

        return current_pos

    def _parse_escape_inline(self, start_pos):
        assert self.template[start_pos.offset] == self.escape_inline
        
        len_template = len(self.template)

        current_pos = start_pos.next_char()
        inline_code = ""
        continue_parse = True
        while continue_parse:
            if current_pos.offset >= len_template:
                raise TemplateCompileError("Unexpected end of template within inline block (missing closing {})".format(self.escape_inline),
                                           self.template, start_pos, current_pos)
            current_char = self.template[current_pos.offset]
            if current_char == self.escape_inline and (current_pos.offset + 1 >= len_template \
                                                       or self.template[current_pos.offset+1] != self.escape_inline):
                # end of inline block
                current_pos = current_pos.next_char()
                continue_parse = False
            else:
                inline_code += current_char
                current_pos = current_pos.next_char()
        # end of while
        compiled_inline = inline_code  # TODO:  compile !

        parsed_inline = ast.parse(inline_code, self.filename, 'eval')
        ast.increment_lineno(parsed_inline, start_pos.line_pos)

        compiled_inline = compile(parsed_inline, self.filename, 'eval')

        self.ctemplate.append(Template.Inline(self, compiled_inline, start_pos, current_pos))

        return current_pos

    def _parse_escape_block(self, start_pos):
        assert self.template[start_pos.offset] == self.escape_block
        assert self.template[start_pos.offset + 1] == self.escape_block_open
        
        len_template = len(self.template)

        current_pos = start_pos.next_char().next_char()
        block_code = ""
        continue_parse = True
        while continue_parse:
            if current_pos.offset >= len_template:
                raise TemplateCompileError("Unexpected end of template within block block (missing closing {}{})".format(self.escape_block, self.escape_block_close),
                                           self.template, start_pos, current_pos)
            current_char = self.template[current_pos.offset]
            if current_char == self.escape_block \
            and (current_pos.offset + 1 < len_template \
                 and self.template[current_pos.offset+1] == self.escape_block_close):
                # end of block block
                current_pos = current_pos.next_char().next_char()
                continue_parse = False
            else:
                block_code += current_char
                current_pos = current_pos.next_char()
        # end of while
        compiled_block = block_code  # TODO:  compile !

        parsed_block = ast.parse(block_code, self.filename, 'exec')
        ast.increment_lineno(parsed_block, start_pos.line_pos)

        compiled_block = compile(parsed_block, self.filename, 'exec')

        self.ctemplate.append(Template.Block(self, compiled_block, start_pos, current_pos))

        return current_pos


    class Element:
        def __init__(self, template, kind, start_pos, end_pos):
            self.template = template
            self.kind = kind
            self.start_pos = start_pos
            self.end_pos = end_pos

    class Literal(Element):
        def __init__(self, template, literal, start_pos, end_pos):
            super().__init__(template, "literal", start_pos, end_pos)
            self.literal = literal

        def render(self, env):
            return self.literal

        def __repr__(self):
            return 'Template.Literal("{}", start_pos={}, end_pos={})'.format(self.literal, self.start_pos, self.end_pos)

    class Variable(Element):
        def __init__(self, template, variable, start_pos, end_pos):
            super().__init__(template, "variable", start_pos, end_pos)
            self.variable = variable
            
        def render(self, env):
            if self.variable not in env:
                raise TemplateRenderError("Variable '{}' not bound".format(self.variable), self.template, self.start_pos, self.end_pos)
            return "{}".format(env[self.variable])

        def __repr__(self):
            return 'Template.Variable(${}, start_pos={}, end_pos={})'.format(self.variable, self.start_pos, self.end_pos)


    class Inline(Element):
        def __init__(self, template, inline_code, start_pos, end_pos):
            super().__init__(template, "inline", start_pos, end_pos)
            self.inline_code = inline_code

        def render(self, env):

            genv = self.template.global_env()
            renv = self.template._install_render_env(env)
            
            ret = eval(self.inline_code, genv, renv)

            return "{}".format(ret)

        def __repr__(self):
            return 'Template.Inline({}, start_pos={}, end_pos={})'.format(self.inline_code, self.start_pos, self.end_pos)

    class Block(Element):
        def __init__(self, template, block_code, start_pos, end_pos):
            super().__init__(template, "block", start_pos, end_pos)
            self.block_code = block_code
            self.start_col = start_pos.char_pos

        def render(self, env):

            genv = self.template.global_env()
            renv = self.template._install_render_env(env)
            
            Template.___Template_render_string___ = StringBuffer()
            exec(self.block_code, genv, renv)
            #print("Rendered = {}".format(Template.___Template_render_string___.contents))
            
            render_str = Template.___Template_render_string___.contents
            if self.start_col > 1:
                indent_str = " " * (self.start_col - 1)
                render_str = indent_str.join(render_str.splitlines(True))

            return render_str

        def __repr__(self):
            return 'Template.Block({}, stat_col={}, start_pos={}, end_pos={})'.format(self.block_code, self.start_col, self.start_pos, self.end_pos)



class StringBuffer:
    def __init__(self):
        self.contents = ""

    def reset(self):
        self.contents=""

    def append(self,msg):
        self.contents += msg
            
def ___Template_emit_function___(msg):
    #print(">>> EMIT: {}".format(msg))
    Template.___Template_render_string___.append(msg)

    #print(">>>> HERE: {}".format(___Template_render_string___))

if __name__ == "__main__":
    t1 = Template(\
    """\
    %{for n in range(1,11):
        %the value is $n\n%
    %}""")

    print(t1.generate(var_env=None))

    #the value is 1  the value is 2 ...
