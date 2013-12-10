
"""Tango Code-active processors allow
to embed python code within tango documents.
"""

import ast
import doctest
import pprint

from tangolib.processor import CommandProcessor
from tangolib import markup

class PythonContext:
    def __init__(self):
        self.globals = __builtins__ # dictionnary of globals
        self.pprint = pprint.PrettyPrinter()
        self.defs = dict()

    def eval_python_expr(self, expr, filename='<unknown>', line_pos=None):
        code = ast.parse(expr, filename, 'eval')
        if line_pos is not None:
            ast.increment_lineno(code, line_pos)

        ccode = compile(code, filename, 'eval')
        ret = eval(ccode, self.globals)

        return ret

    def exec_python(self, source, filename='<unknown>', line_pos=None):
        code = ast.parse(source, filename, 'exec')
        if line_pos is not None:
            ast.increment_lineno(code, line_pos)
        ccode = compile(code, filename, 'exec')
            
        exec(ccode, self.globals)

    def def_python(self, def_name, def_source, filename='<unknown>', line_pos=None):
        self.exec_python(def_source, filename, line_pos)
        # TODO: check the def in the context
        self.defs[def_name] = def_source # TODO: register only if defined        

class EvalPythonProcessor(CommandProcessor):
    def __init__(self, python_context):
        super().__init__()
        self.python_context = python_context

    def process_command(self, processor, cmd):
        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        ret = self.python_context.eval_python_expr(cmd.content, processor.document.filename, cmd.header_end_pos.lpos)
        output = self.python_context.pprint.pformat(ret)
        return (markup.Preformated(cmd.doc, output, "python-3", cmd.start_pos, cmd.end_pos), False)

class DefPythonProcessor(CommandProcessor):
    def __init__(self, python_context):
        super().__init__()
        self.python_context = python_context

    def process_command(self, processor, cmd):
        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        self.python_context.def_python(cmd.cmd_opts, cmd.content, processor.document.filename, cmd.header_end_pos.lpos)
        # TODO: log the registered function
        return (markup.SkipMarkup(cmd.doc, cmd.start_pos, cmd.end_pos), False)
        
class CheckPythonProcessor(CommandProcessor):
    def __init__(self, python_context):
        super().__init__()
        self.python_context = python_context

    def process_command(self, processor, cmd):
        test_parser = doctest.DocTestParser()
        test = test_parser.get_doctest(cmd.content, self.python_context.globals, "<checkPython>", processor.document.filename, cmd.header_end_pos.lpos)
        runner = CheckPythonRunner()
        runner.run(test)
        # XXX : for the moment an exception should be launched, think about different behaviors
        # if we are here then everything went fine (?)
        if cmd.cmd_opts == "hide":
            return (markup.SkipMarkup(cmd.doc, cmd.start_pos, cmd.end_pos), False)
        else:
            return (markup.Preformated(cmd.doc, cmd.content, "python-3", cmd.start_pos, cmd.end_pos), False)


class CheckPythonFailure(Exception):
    pass

class CheckPythonRunner(doctest.DocTestRunner):
    def __init__(self):
        super().__init__()


    def report_failure(self, out, test, example, got):
        super().report_failure(out, test, example, got)
        raise CheckPythonFailure()

def register_processors(processor, python_context):
    processor.register_command_processor("evalPython", EvalPythonProcessor(python_context))
    processor.register_command_processor("defPython", DefPythonProcessor(python_context))
    processor.register_command_processor("checkPython", CheckPythonProcessor(python_context))

