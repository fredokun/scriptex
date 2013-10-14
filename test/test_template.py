'''
Test template engine
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

import tangolib
from tangolib.template import Template

class TestBasicTemplates(unittest.TestCase):
    def test_variable_escape(self):
        template = Template("The value of myvar is '$myvar' obtained by $$myvar\n and that's it ...")
        template.compile()
        # print(template.ctemplate)
        myvar = 42
        ret = template.render(locals())
        print(ret)

    def test_alt_variable_escape(self):
        template = Template("The value of myvar is '?myvar' obtained by ??myvar\n and that's it ...", escape_var='?')
        template.compile()
        # print(template.ctemplate)
        myvar = 42
        ret = template.render(locals())
        print(ret)

    def test_inline_escape_var(self):
        template = Template(
            """The value of myvar is '%"{}".format(myvar)%' with inline escape char '%%'
            and that's it...""")
        template.compile()
        #print(template.ctemplate)
        myvar = 42
        ret = template.render(locals())
        print(ret)

    def test_alt_inline_escape_var(self):
        template = Template(
            """The value of myvar is '$"{}".format(myvar)$' with inline escape char '$$'
            and that's it...""", escape_var="?", escape_inline="$")
        template.compile()
        #print(template.ctemplate)
        myvar = 42
        ret = template.render(locals())
        print(ret)

    def test_block_escape_var(self):
        template = Template(
            """The value of myvar is '%{emit("{}".format(myvar))%}' with block escape char '%%'
            and that's it...""")
        template.compile()
        #print(template.ctemplate)
        myvar = 42
        ret = template.render(locals())
        print(ret)
        

if __name__ == '__main__':
    unittest.main()


    
