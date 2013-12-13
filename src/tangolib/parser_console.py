"""
A simple console for playing with the tango parser
"""

import sys
import os

if __name__ == "__main__":
    tangodir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.append(tangodir)

import tangolib.parser

def process_command(cmd):
    if cmd == ":quit":
        print("bye bye !")
        sys.exit(0)
    
    else:
        print("Unknown command '{}'".format(cmd))

def parse_line(line):
    p = tangolib.parser.Parser()
    try:
        result = p.parse_from_string(line)
        print(result)
    except tangolib.parser.ParseError as e:
        print("Parsing failed:")
        print(e)

if __name__ == "__main__":
    print("Tango parser console")
    
    while True:
        line = input("> ")
        
        if line.startswith(":"):
            process_command(line)
        else:
            parse_line(line)
