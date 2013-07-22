"""The document processor translates a parsed document
by interpreting commands and/or environments.

"""

class ProcessError(Exception):
    pass

class DocumentProcessing:
    def __init__(self, document):
        self.document = document
        self.cmd_processors = dict()
        self.env_processors = dict()
        
    def register_command_processor(self, cmd_name, cmd_processor):
        if cmd_name in self.cmd_processors:
            raise ProcessError("Processor for command {} already registered".format(cmd_name))

        self.cmd_processors[cmd_name] = cmd_processor

    def register_environment_processor(self, env_name, env_processor):
        if env_name in self.env_processors:
            raise ProcessError("Processor for environment {} already registered".format(env_name))

        self.env_processors[env_name] = env_processor

    def process(self):
        # Stack[Markup * Int]   (doc/cmd/env, index in child, -1 for unprocessed)
        self.markup_stack = [(document, 0, None, -1)]
        self.environment_stack = []
        self.command_stack = []

        while self.markup_stack:
            self.markup, self.content_index, self.source_markup, self.source_index = self.markup_stack.pop()
            if self.content_index == -1: # command/env not processed
                if self.markup.markup_type == "command":
                    if self.markup.cmd_name in self.cmd_processors:
                        self.cmd_processors[self.markup.cmd_name].enter_command(self, self.markup)
                    self.command_stack.append(self.markup)
                elif self.markup.markup_type == "environment":
                    if self.markup.env_name in self.env_processors:
                        self.env_processors[self.markup.env_name].enter_environment(self, self.markup)
                    self.environment_stack.append(self.markup)
                # push back in queue but next time process content at index 0 (first child)
                self.markup_stack.append((self.markup, 0, self.source_markup, self.source_index))
            else: # processing of markup already started
                if self.content_index == len(self.markup.content):
                    # done processing content
                    if self.markup.markup_type == "command":
                        check_cmd = self.command_stack.pop()
                        assert check_cmd == self.markup,  "invalid command stack (please report)"
                        if self.markup.cmd_name in self.cmd_processors:
                            new_content, recursive = self.cmd_processors[self.markup.cmd_name].process_command(self, self.markup)
                            if new_content is not None:
                                if recursive:
                                    self.markup_stack.append((new_content, -1, self.source_markup, self.source_index))
                                self.source_markup.content[self.source_index] = new_content
                    elif self.markup.markup_type == "environment":
                        check_env = self.environment_stack.pop()
                        assert check_env == self.markup,  "invalid environment stack (please report)"
                        if self.markup.env_name in self.env_processors:
                            new_content, recursive = self.env_processors[self.markup.env_name].process_environment(self, self.markup)
                            if new_content is not None:
                                if recursive:
                                    self.markup_stack.append((new_content, -1, self.source_markup, self.source_index))
                                self.source_markup.content[self.source_index] = new_content
                else: # process a child
                    child = self.markup.content[self.content_index]
                    self.markup_stack.append((self.markup, self.content_index+1, self.source_markup, self.source_index))
                    if isinstance(child, Markup):
                        self.markup_stack.append((child, -1, self.markup, self.content_index))
                    else:
                        pass # XXX: process non-markup content in some way ?

        # done processing



class CommandProcessor:
    def __init__(self):
        pass

    def enter_command(self, processing, cmd):
        pass # should be overriden

    def process_command(self, processing, cmd):
        return (None, False)  # default process is :  do nothing


class EnvironmentProcessor:
    def __init__(self):
        pass

    def enter_environment(self, processing, env):
        pass # should be overriden

    def process_environment(self, processing, env):
        return (None, False)  # default process is :  do nothing


