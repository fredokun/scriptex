"""Core processors.

"""

from tangolib.processor import CommandProcessor, ProcessError
from tangolib.markup import SkipMarkup, Preformated, SubDocument, search_content_by_types

class TitleProcessor(CommandProcessor):
    def __init__(self):
        pass

    def process_command(self, processor, cmd):
        processor.document.title = cmd
        return (SkipMarkup(cmd.doc, cmd.start_pos, cmd.end_pos), False) # XXX: we use "" to remove a command from the source

class AuthorProcessor(CommandProcessor):
    def __init__(self):
        pass

    def process_command(self, processor, cmd):
        processor.document.author = cmd
        return (SkipMarkup(cmd.doc, cmd.start_pos, cmd.end_pos), False)

class DateProcessor(CommandProcessor):
    def __init__(self):
        pass

    def process_command(self, processor, cmd):
        processor.document.author = cmd
        return (SkipMarkup(cmd.doc, cmd.start_pos, cmd.end_pos), False)

class IncludeError(ProcessError):
    pass

class IncludeProcessor(CommandProcessor):
    def __init__(self):
        pass

    def process_command(self, processor, cmd):
        if len(cmd.arguments) != 1:
            raise IncludeError("Cannot include document: expecting file name argument")            

        sub_filename = search_content_by_types(cmd.content,{"text","preformated"})
        if not sub_filename:
            raise IncludeError("Cannot find include pathname")
        else:
            sub_filename = sub_filename.text

        try:
            sub_file = open(sub_filename, "r")
        except OSError:
            raise IncludeError("Cannot open included file: {}".format(sub_filename))

        try:
            sub_input = sub_file.read()
        except IOError:
            raise IncludeError("Cannot read included file: {} (IO error)".format(sub_filename))
        finally:
            sub_file.close()
     

        from tangolib.parser import Parser
        parser = Parser()
        sub_lex = parser.prepare_string_lexer(sub_input)
        sub_doc = SubDocument(cmd.doc, sub_filename, cmd.start_pos, sub_lex)

        result_parsed = parser.parse(sub_doc)
   
        return (result_parsed, True)

class CmdLineOptionProcessor(CommandProcessor):
    def __init__(self):
        pass

    def process_command(self, processor, cmd):
        import tangolib.cmdparse

        option_name = None
        if isinstance(cmd.cmd_opts, str):
            option_name = cmd.cmd_opts
        else:
            raise ProcessError("Missing command line option")

        option_line_processor = None
        try:
            cmd_args = tangolib.cmdparse.get_global_command_line_arguments()
            option_line_processor = cmd_args.extra_options[option_name]
        except:
            raise ProcessError("No such command line option: {}".format(option_name))

        return (Preformated(cmd.doc, option_line_processor, "cmdline", cmd.start_pos, cmd.end_pos), False)


def register_core_processors(processor):
    processor.register_command_processor("title", TitleProcessor())
    processor.register_command_processor("author", AuthorProcessor())
    processor.register_command_processor("date", DateProcessor())
    processor.register_command_processor("include", IncludeProcessor())
    processor.register_command_processor("cmdLineOption", CmdLineOptionProcessor())

