from markup import Text,Each,Call,Variable
from lexer import Lexer
from parser import Parser

import re

with open('basic.tango.tex') as content_file:
    content = content_file.read()


l = Lexer(content)
lexedContent = l.process()

print(lexedContent)
print("\n\n")

p = Parser(lexedContent)

parsedContent = p.process() 

print(parsedContent)
print("\n\n")


for i in parsedContent:
    print(i.toString())

