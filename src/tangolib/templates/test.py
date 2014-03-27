from markup import Text,Each,Call,Variable,Document
from lexer import Lexer
from parser import Parser
from compiler import Compiler,CompilerError

import re


with open('basic.tango.tex') as content_file:
    content = content_file.read()


l = Lexer(content)
lexedContent = l.process()

p = Parser(lexedContent)
parsedContent = p.process() 

data = { 'var1' : "OK1", 'var2' : "OK2", "list" : "[1,2]" }

c = Compiler(parsedContent,data)
print(c.process())


