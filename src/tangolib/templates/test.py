from markup import Text,Each,Call,Variable
from lexer import Lexer

import re

with open('basic.tango.tex') as content_file:
    content = content_file.read()


l = Lexer(content)
print(l.process())


