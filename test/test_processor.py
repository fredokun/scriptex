'''
Test processor
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from tangolib.parser import Parser
from tangolib.processor import DocumentProcessor, CommandProcessor, EnvironmentProcessor

class TestCommandProcess(unittest.TestCase):

    class CountItem(CommandProcessor):
        def __init__(self):
            self.count = 0

        def enter_command(self, processing, cmd):
            self.count += 1

    def test_count_item(self):
        parser = Parser()
        # BREAKPOINT >>> # import pdb; pdb.set_trace()  # <<< BREAKPOINT #
        doc = parser.parse_from_file("../examples/basic.tango.tex")

        processor = DocumentProcessor(doc)

        count = TestCommandProcess.CountItem()
        processor.register_command_processor("item",count)

        processor.process()

        #print("count = {}".format(count.count))
        self.assertEqual(count.count, 5)
        
if __name__ == '__main__':
    unittest.main()
