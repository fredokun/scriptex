'''
Test exercise generator
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from scriptex.parser import Parser
from scriptex.processor import DocumentProcessor
from scriptex.processors import core, codeactive
from scriptex.generators.latex.article import LatexArticleGenerator

class TestExos(unittest.TestCase):

    def test_eval_python(self):
        parser = Parser()
        doc = parser.parse_from_string(""""
\evalPython{{{3+2}}}
""")

        #print("Before processing = \n" + str(doc));

        process = DocumentProcessor(doc)
        py_ctx = codeactive.PythonContext()
        codeactive.register_processors(process, py_ctx)
        process.process()

        #print("After processing = \n" + str(doc));

    def test_def_python(self):
        parser = Parser()
        doc = parser.parse_from_string(""""
\defPython[fact]{{{
def fact(n):
    return 1 if n<=1 else n*fact(n-1)
}}}

\evalPython{{{3+fact(4)}}}
""")

        print("Before processing = \n" + str(doc));

        process = DocumentProcessor(doc)
        py_ctx = codeactive.PythonContext()
        codeactive.register_processors(process, py_ctx)
        process.process()

        print("After processing = \n" + str(doc));
        
    
    def test_exos_liste(self):
        # 1) parsing
        
        parser = Parser()
        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        doc = parser.parse_from_file("../examples/exosliste.script.tex")

        # 2) processing
        processor = DocumentProcessor(doc)
        core.register_core_processors(processor)
        processor.process()

        # 3) generating
        generator = LatexArticleGenerator(doc)
        generator.generate()

        # print("Output =\n" + str(generator.output))
        
        
if __name__ == '__main__':
    unittest.main()
