'''
Created on 27 déc. 2012

@author: fredericpeschanski
'''


class RenderError(Exception):
    def __init__(self, message):
        super.__init__(message)


class Render:
    pass

    class Element:

        def render_to_string(self, env):
            raise NotImplementedError("Abstract method")

        def render_to_file(self, env, fileobj):
            fileobj.write(self.render_to_string(env))

    class Text(Element):
        def __init__(self, text):
            self.text = text

        def render_to_string(self, env):
            return self.text

    class Param(Element):
        def __init__(self, param):
            self.param = param

        def render_to_string(self, env):
            if self.param not in env:
                raise RenderError("No such parameter: {0}".format(self.param))
            return env[self.param]
