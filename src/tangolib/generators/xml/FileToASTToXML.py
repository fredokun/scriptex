import sys
import os

if __name__ == "__main__":
    tangodir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir,os.pardir)
    sys.path.append(tangodir)

import tangolib.parser

p = tangolib.parser.Parser()
doc = p.parse_from_file("basic.tango.tex")
print(doc)


