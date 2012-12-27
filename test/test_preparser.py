'''
Test preparser
'''

import unittest

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

import scriptex


class TestPreMarkup(unittest.TestCase):
    def test_emph(self):
        tokens = scriptex.make_string_tokenizer("_example in emphasis_")
        preparser = scriptex.PreParser(tokens)
        scriptex.default_premarkup_rules(preparser)
        result = preparser.preparse_to_string()
        print("result =")
        print(result)

if __name__ == '__main__':
    unittest.main()
