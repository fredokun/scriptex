
# the Tango frontend

import argparse
import sys

from tangolib.parser import Parser
from tangolib.processor import DocumentProcessor
from tangolib.processors import core, codeactive
from tangolib.generators.latex.article import LatexArticleGenerator

def tangoArgumentParser():
    parser = argparse.ArgumentParser(prog="tango", description="a programmable document processor")

    parser.add_argument("input_file", type=str, help="input file", action="store")

    parser.add_argument("--banner", help="show nice banner", action="store_true")

    parser.add_argument("--latex", help="output latex", action="store_true")

    parser.add_argument("--codeactive", help="support for active python code", action="store_true")

    parser.add_argument("--output-dir", type=str, default="tango_output", help="set output directory", action="store")

    return parser
    

def tangoBanner():
    return \
r"""

                         .~""~.,--.       TANGO                       |
                          > :::i_, ~;                                 |
              mmn        <, ?::j~?`_{}          a Programmable        |
              (_)         l_  fl_ f {}                                |
               \ `.     ,__}--{_/_l___.      Document                 |
                \  `--~'           `m,_`.                             |
                 \                      )}           Processor        |
                  `~----f     i  :-----~'                             |
                        }     |  |-'/                                 |
________________________|     !  | f__________________________________!
                        l        j |                                   \
                        }==I===I={~(                                    \
                        f.       1( )                                    \
                        |      } }` `.                                    \
                        |     '  { ) )                                     \
                        }    f   |(  `\                                     \
                        |    |   |  )  )
                        |    |   |.  ( `.
                        |    |  ,l ) `. )
                       /{    |    \   ( `\
                      ('|    |\    \ ; `. )
                     (;!|    |`\    \  ',' )
                      YX|    |XX\    \XXXXXY
                        !____j_) \__,'> _)         (C) 2013 Frederic Peschanski
                     ,_.'`--('Y,_' ,^' /`!               
                     L___-__J  L_,'`--'     mab'95

"""


if __name__ == "__main__":

    print("""   ______                      
  /_  __/___ _____  ____ _____ 
   / / / __ `/ __ \/ __ `/ __ \  Programmable Document Processor v0.1
  / / / /_/ / / / / /_/ / /_/ /
 /_/  \__,_/_/ /_/\__, /\____/   (C) 2013 F.Peschanski (see LICENSE)
                 /____/        
---
Ready to process ...""")

    arg_parser = tangoArgumentParser()
    args = arg_parser.parse_args()

    if args.banner:
        print(tangoBanner())

    enable_process_phase = True
        
    if enable_process_phase:
        print("Process phase enabled", file=sys.stderr)

    enable_generate_phase = True
    if not enable_process_phase:
        enable_generate_phase = False

    if enable_generate_phase:
        print("Generate phase enabled", file=sys.stderr)

    enable_write_phase = False
    if args.latex:
        enable_write_phase = True

    if not enable_generate_phase:
        enable_write_phase = False

    if enable_write_phase:
        print("Write phase enabled", file=sys.stderr)

    import os
    print("Current work directory = '{}'".format(os.getcwd()), file=sys.stderr)

    print("----", file=sys.stderr)

    # 1) parsing

    parser = Parser()
    # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
    

    print("Parsing from file '{}'".format(args.input_file), file=sys.stderr)

    doc = parser.parse_from_file(args.input_file)

    # 2) processing

    if enable_process_phase:

        processor = DocumentProcessor(doc)
        core.register_core_processors(processor)

        # support for active python code
        if args.codeactive:
            print("Enabling active python code processors", file=sys.stderr)

            py_ctx = codeactive.PythonContext()
            codeactive.register_processors(processor, py_ctx)

        try:
            processor.process()
        except codeactive.CheckPythonFailure:
            print("CheckPython failed, aborpting ...", file=sys.stderr)
            sys.exit(1)

    # 3) generating

    generator = None
    
    if enable_generate_phase:

        if args.latex:
            # latex mode
            print("Generating latex", file=sys.stderr)

            generator = LatexArticleGenerator(doc)
            
        if not generator:
            print("No generator set, aborpting ...", file=sys.stderr)

        generator.generate()
        
    # 4) writing

    if enable_write_phase:

        if args.latex:
            output_mode_dir = "latex"
           
        output_directory = args.output_dir + "/" + output_mode_dir
 
        try:
            os.makedirs(output_directory)
        except OSError:
            print("Using ", file=sys.stderr, end="")
        else:
            print("Creating ", file=sys.stderr, end="")

        print("output directory '{}'".format(output_directory), file=sys.stderr)

        infile_without_ext = args.input_file.split(".")
        if infile_without_ext[-1] == "tex":
            infile_without_ext = ".".join(infile_without_ext[:-1])
        else:
            infile_without_ext = args.input_file

        main_output_filename = output_directory + "/" + infile_without_ext + "-gen." + output_mode_dir

        print("Writing main {} file '{}'".format(output_mode_dir, main_output_filename), file=sys.stderr)

        main_output_file = open(main_output_filename, 'w')
        main_output_file.write(str(generator.output))
        main_output_file.close()


    print("... bye bye ...")

