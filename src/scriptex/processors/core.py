"""Core processors.

"""

from scriptex.processor import CommandProcessor

class TitleProcessor(CommandProcessor):
    def __init__(self):
        pass

    def process_command(self, processor, cmd):
        processor.document.title = cmd
        return ("", False) # XXX: we use "" to remove a command from the source

class AuthorProcessor(CommandProcessor):
    def __init__(self):
        pass

    def process_command(self, processor, cmd):
        processor.document.author = cmd
        return ("", False)

class DateProcessor(CommandProcessor):
    def __init__(self):
        pass

    def process_command(self, processor, cmd):
        processor.document.author = cmd
        return ("", False)


def register_core_processors(processor):
    processor.register_command_processor("title", TitleProcessor())
    processor.register_command_processor("author", AuthorProcessor())
    processor.register_command_processor("date", DateProcessor())

