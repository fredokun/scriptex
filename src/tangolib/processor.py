"""The document processor translates a parsed document
by interpreting commands and/or environments.

"""

from tangolib.markup import Markup, Text, Spaces, Newlines, SkipMarkup

class ProcessError(Exception):
    pass

class DocumentProcessor:
    def __init__(self, document):
        self.document = document
        self.cmd_processors = dict()
        self.env_processors = dict()
        self.sec_processors = dict()
        self.text_processor = TextProcessor()  # default: copy as source
        self.preformated_processor = PreformatedProcessor()
        self.spaces_processor = SpacesProcessor()
        self.newlines_processor = NewlinesProcessor()
        
    def register_command_processor(self, cmd_name, cmd_processor):
        if cmd_name in self.cmd_processors:
            raise ProcessError("Processor for command {} already registered".format(cmd_name))

        self.cmd_processors[cmd_name] = cmd_processor

    def register_environment_processor(self, env_name, env_processor):
        if env_name in self.env_processors:
            raise ProcessError("Processor for environment {} already registered".format(env_name))

        self.env_processors[env_name] = env_processor

    def register_section_processor(self, sec_depth, sec_processor):
        if sec_depth in self.sec_processors:
            raise ProcessError("Processor for section level {}: already registered".format(sec_depth))

        if not self.sec_processors:
            self.sec_processors[0] = sec_processor # global processor if only one
        else:
            del self.sec_processors[0] # no global processor if more than one
            
        self.sec_processors[sec_depth] = sec_processor

        
    def process(self):
        # Stack[Markup * Int]   (doc/cmd/env, index in child, -1 for unprocessed)
        self.markup_stack = [(self.document, 0, None, -1)]
        self.environment_stack = []
        self.command_stack = []
        self.section_stack = []

        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #

        while self.markup_stack:
            self.markup, self.content_index, self.source_markup, self.source_index = self.markup_stack.pop()
            if self.content_index == -1: # command/env not processed
                if self.markup.markup_type == "command":
                    if self.markup.cmd_name in self.cmd_processors:
                        self.cmd_processors[self.markup.cmd_name].enter_command(self, self.markup)
                    if self.markup.preformated:
                        if self.markup.cmd_name in self.cmd_processors:
                            new_content, recursive = self.cmd_processors[self.markup.cmd_name].process_command(self, self.markup)
                            if new_content is None:
                                self.source_markup.content[self.source_index] = markup.SkipMarkup(self.markup.start_pos, self.markup.end_pos)
                            else: # new content
                                if recursive:
                                    self.markup_stack.append(new_content, -1, self.source_markup, self.source_index)
                                self.source_markup.content[self.source_index] = new_content
                    else:
                        self.command_stack.append(self.markup)
                elif self.markup.markup_type == "environment":
                    if self.markup.env_name in self.env_processors:
                        self.env_processors[self.markup.env_name].enter_environment(self, self.markup)
                    self.environment_stack.append(self.markup)
                elif self.markup.markup_type == "section":
                    if 0 in self.sec_processors:
                        self.sec_processors[0].enter_section(self, self.markup)
                    elif self.markup.section_depth in self.sec_processors:
                        self.sec_processors[self.markup.section_depth].enter_section(self, self.markup)
                    self.section_stack.append(self.markup)
                if self.markup.markup_type != "command" or not self.markup.preformated:
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
                    elif self.markup.markup_type == "section":
                        check_sec = self.section_stack.pop()
                        assert check_sec == self.markup, "Invalid section stack (please report)"
                        new_content = None
                        recursive = False
                        if 0 in self.sec_processors:
                            new_content, recursive = self.sec_processors[0].process_section(self, self.markup)
                        elif self.markup.section_depth in self.sec_processors:
                            new_content, recursive = self.sec_processors[self.markup.section_depth].process_section(self, self.markup)
                        if new_content is not None:
                            if recursive:
                                self.markup_stack.append((new_content, -1, self.source_markup, self.source_index))
                            self.source_markup.content[self.source_index] = new_content
                else: # process a child
                    child = self.markup.content[self.content_index]
                    self.markup_stack.append((self.markup, self.content_index+1, self.source_markup, self.source_index))
                    if isinstance(child, Markup):
                        self.markup_stack.append((child, -1, self.markup, self.content_index))
                    elif isinstance(child, Text) and self.text_processor is not None:
                        ntext = self.text_processor.process_text(self, child)
                        if ntext is not None:
                            self.markup.content[self.content_index] = ntext
                    elif isinstance(child, Preformated) and self.preformated_processor is not None:
                        npreformated = self.preformated_processor.process_preformated(self, child)
                        if npreformated is not None:
                            self.markup.content[self.content_index] = npreformated
                    elif isinstance(child, Spaces) and self.spaces_processor is not None:
                        nspaces = self.spaces_processor.process_spaces(self, child)
                        if nspaces is not None:
                            self.markup.content[self.content_index] = nspaces                        
                    elif isinstance(child, Newlines) and self.newlines_processor is not None:
                        nnewlines = self.newlines_processor.process_newlines(self, child)
                        if nnewlines is not None:
                            self.markup.content[self.content_index] = nnewlines
                    elif isinstance(child, SkipMarkup):
                        pass # skip this markup
                    else:
                        raise ProcessError("Wrong child type: {} (please report)".format(repr(child)))

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


class SectionProcessor:
    def __init__(self):
        pass

    def enter_section(self, processing, cmd):
        pass # should be overriden

    def process_section(self, processing, cmd):
        return (None, False)  # default process is :  do nothing

class TextProcessor:
    def __init__(self):
        pass

    def process_text(self, processing, text):
        return text

class PreformatedProcessor:
    def __ini__(self):
        pass

    def process_preformated(self, processing, preformated):
        return preformated

class SpacesProcessor:
    def __init__(self):
        pass

    def process_spaces(self, processing, spaces):
        return spaces

class NewlinesProcessor:
    def __init__(self):
        pass

    def process_newlines(self, processing, newlines):
        return newlines
