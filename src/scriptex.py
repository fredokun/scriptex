
# the ScripTex frontend

if __name__ == "__main__":
    import sys

    from scriptex.parser import ScripTexParser
    
    input_file = sys.argv[0]

    parser = ScripTexParser()

    ret = parser.parse_from_file(input_file)
    
    print(str(ret))

