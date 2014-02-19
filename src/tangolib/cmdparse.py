"""A dedicated command line parser.

Remark: We do not use the parsers from the standard
library because they do not fit our needs
(especially passing arbitrary arguments to the
processed documents).
"""

class CmdLineArguments:
    def __init__(self):
        self.input_filename = None
        self.output_directory = "tango_output"
        self.output_type = None
        self.modes = set()
        self.code_active = False
        self.banner = False
        self.help = False
        self.extra_options = dict()

    def __str__(self):
        return \
"""Banner = {}
Help = {}
Output type = {}
Modes = {}
Code Active = {}
Input file name = {}
Output directory = {}
Extra options = {}
""".format(self.banner,
           self.help,
           self.output_type,
           self.modes,
           self.code_active,
           self.input_filename,
           self.output_directory,
           self.extra_options)

class CmdLineError(Exception):
    pass

class CmdLineParser:
    def __init__(self, argv):
        self.argv = argv
        self.cmd_args = CmdLineArguments()


    def parse(self):
        self.tango_cmd = self.argv[0]

        cmd_args = self.argv[1:]

        while cmd_args:
            cmd_args = self.parse_next(cmd_args)

        return self.cmd_args
        
    def parse_next(self, cmd_args):
        next_opt = cmd_args[0]
        
        if next_opt == "--latex" or next_opt == "-l":
            if self.cmd_args.output_type is not None:
                raise CmdLineError("Mismatch {} option : output type already set".format(next_opt))

            self.cmd_args.output_type =  "latex"
            return cmd_args[1:]

        elif next_opt == "--codeactive":
            self.cmd_args.code_active = True
            return cmd_args[1:]

        elif next_opt == "--banner":
            self.cmd_args.banner = True
            return cmd_args[1:]

        elif next_opt == "--help" or next_opt == "-h":
            self.cmd_args.help = True
            return cmd_args[1:]

        elif next_opt == "--mode" or next_opt == "-m":
            cmd_args = cmd_args[1:]
            if not cmd_args:
                raise CmdLineError("Missing mode")
            if cmd_args[0].startswith("-"):
                raise CmdLineError("Missing mode before {}".format(cmd_args[0]))

            modes_str = cmd_args[0]
            modes = modes_str.split(",")
            self.cmd_args.modes = self.cmd_args.modes.union(set(modes))

            return cmd_args[1:]

        elif next_opt == "--output" or next_opt == "-o":
            cmd_args = cmd_args[1:]
            if not cmd_args:
                raise CmdLineError("Missing output directory")
            if cmd_args[0].startswith("-"):
                raise CmdLineError("Missing output directory before {}".format(cmd_args[0]))

            self.cmd_args.output_directory = cmd_args[0]

            return cmd_args[1:]

        elif not next_opt.startswith("-"):
            if self.cmd_args.input_filename is not None:
                raise CmdLineError("Cannot handle '{}': input file already set".format(next_opt))
            self.cmd_args.input_filename = next_opt
            return cmd_args[1:]

        else:
            next_opt = next_opt.lstrip('-')
            cmd_args = cmd_args[1:]
            if cmd_args and not cmd_args[0].startswith("-"):
                self.cmd_args.extra_options[next_opt] = cmd_args[0]
                return cmd_args[1:]

            self.cmd_args.extra_options[next_opt] = True
            return cmd_args

   
# Special global variable for parsed command line arguments
GLOBAL_COMMAND_LINE_ARGUMENTS = None        


if __name__ == "__main__":
    import sys
    
    print("command line = {}".format(sys.argv))

    cmdline_parser = CmdLineParser(sys.argv)
    
    cmd_args = cmdline_parser.parse()

    print(cmd_args)

