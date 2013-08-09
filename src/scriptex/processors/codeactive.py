
"""Scriptex Code-active processors allow
to embed python code within scriptex documents.
"""

import ast
import pprint

from scriptex.processor import CommandProcessor

class PythonContext:
    def __init__(self):
        self.globals = dict()  # dictionnary of globals
        self.pprint = pprint.PrettyPrinter()

    def eval_python_expr(self, expr, filename='<unknown>', line_pos=None):
        code = ast.parse(expr, filename, 'eval')
        if line_pos is not None:
            ast.increment_lineno(code, line_pos)

        ret = eval(code, self.globals)

        return ret



    def exec_python(self, source, filename='<unknown>', line_pos=None):
        code = ast.parse(source, filename, 'exec')
        if line_pos is not None:
            ast.increment_lineno(code, line_pos)

        exec(code, self.globals)


class EvalPythonProcessor(CommandProcessor):
    def __init__(self, python_context):
        super().__init__()
        self.python_context = python_context

    def process_command(self, processor, cmd):
        ret = self.python_context.eval_python_expr(cmd.content, processor.document.filename, cmd.header_end_pos.lpos)
        output = self.python_content.pprint.pformat(ret)
        return (markup.Preformated(output, cmd.start_pos, cmd.end_pos), False)

def register_code_active_processors(processor):
    processor.register_command_processor("evalPython", EvalPythonProcessor())

