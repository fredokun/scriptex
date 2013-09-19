
# the Tango frontend

if __name__ == "__main__":
    import sys

    from tango.parser import TangoParser
    
    input_file = sys.argv[0]

    parser = TangoParser()

    ret = parser.parse_from_file(input_file)
    
    print(str(ret))

