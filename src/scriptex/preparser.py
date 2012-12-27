'''
The ScripTeX preparser

Created on 27 déc. 2012

@author: F.Peschanski
'''


class PreParser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.templates = []

    def template(self, template):
        self.templates.append(template)
        return self


class PreTemplate:
    def __init__(self):
        self.recognizers = []
        self.renders = []

    def when(self, recognizer, param=None):
        self.recognizers.append(tuple(recognizer, param))
        return self

    def then(self, recognizer, param=None):
        return self.when(recognizer, param)

    def render(self, render):
        self.renders.append(render)
        return self
