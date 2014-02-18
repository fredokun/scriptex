"""Extended regular expressions.

This module provides an object-oriented interface for
specifying regular expressions.

It also provides some debugging tools.
"""

import re

MULTILINE = re.MULTILINE

class ERegex:
    """The class of extended regular expressions.
    """
    def __init__(self, spec):
        if not isinstance(spec, str):
            raise ValueError("Extended regular expression specification must be  a string")
        self.spec = spec
        self.regex = None
        
    def compile(self, flags=0):
        self.regex = re.compile(self.spec, flags)

    def match(self, input):
        m = self.regex.match(input)
        if m is None:
            return m
        else:
            return ERegex.MatchObject(m)
        
    def orelse(self, others):
        lothers = [self.spec]
        lothers.extend((str(other) for other in others))
        self.spec = orelse(lothers)
        return self
        
    def __or__(self, other):
        return self.orelse([other])

    def __ror__(self, other):
        self.spec = orelse([str(other), self.spec])
        return self

    def then(self, others):
        lothers = [self.spec]
        lothers.extend((str(other) for other in others))
        self.spec = seq(lothers)
        return self

    def __add__(self, other):
        return self.then([other])

    def __radd__(self, other):
        self.spec = seq([str(other), self.spec])
        return self

    def __str__(self):
        return self.spec

    def __repr__(self):
        return 'ERegex(r"{}")'.format(self.spec)

    class MatchObject:
        def __init__(self, match):
            self.match = match

        def expand(self, tpl):
            return self.match.expand(tpl)

        def group(self, *args):
            return self.match.group(*args)
        
        @property
        def nb_groups(self):
            return len(self.match.groups())

        def start(self, group_id):
            return self.match.start(group_id)

        def end(self, group_id):
            return self.match.end(group_id)

        def show(self, show_open=">>", show_close="<<"):
            return '''Match details:
    Input matched = {open}{input}{close}
    {show_groups_by_num}
    {show_groups_by_name}
            '''.format(open=show_open,
                       close=show_close,
                       input=self.match.group(),
                       show_groups_by_num=self.show_groups_by_num(show_open, show_close),
                       show_groups_by_name=self.show_groups_by_name(show_open, show_close))

        def show_groups_by_num(self, show_open, show_close):
            return "\n".join(('    Group #{num} = {open}{grp}{close}'.format(num=num, open=show_open, close=show_close, grp=self.match.group(num)) for num in range(1, len(self.match.groups())+1)))

        def show_groups_by_name(self, show_open, show_close):
            return "\n".join(('    Group <{name}> = {open}{grp}{close}'.format(name=name, open=show_open, close=show_close, grp=self.match.group(name)) for name in self.match.groupdict()))
            
def backslash():
    return "\\\\"

def any_char():
    return "."

def dot():
    return "\\."

def str_begin():
    return "^"

def caret():
    return "\\^"

def str_end():
    return "$"

def dollar():
    return "\\$"

def charset(spec):
    return "[{}]".format(spec)

def charnset(spec):
    return "[^{}]".format(spec)

def open_sq():
    return "\\["

def close_sq():
    return "\\]"

def group(eregex, name=None):
    if isinstance(name, str):
        return "(?P<{}>{})".format(name, eregex)
    else:
        return "({})".format(eregex) 

def open_paren():
    return "\\("

def close_paren():
    return "\\)"
    
def backref(group_id):
    if isinstance(group_id, str):
        return "(?P={})".format(group_id)
    else:
        return "\\{}".format(group_id)

def _postfix(eregex, post_op, group=False, greedy=True):
    if isinstance(group, str):
        open_paren = "(?P{}".format(group)
    elif group:
        open_paren = "("
    else:
        open_paren = "(?:"
    
    greedy_end = "" if greedy else "?"
    
    return open_paren + eregex + post_op + greedy_end + ")"

def zero_or_more(eregex, group=False, greedy=True):
    return _postfix(eregex, '*', group, greedy)

def star():
    return "\\*"

def one_or_more(eregex, group=False, greedy=True):
    return _postfix(eregex, '+', group, greedy)

def plus():
    return "\\+"

def zero_or_one(eregex, group=False, greedy=True):
    return _postfix(eregex, '?', group, greedy)

def question():
    return "\\?"

def repeat(eregex, from_val, to_val=None, group=False, greedy=True):
    if to_val:
        return _postfix(eregex, "{{{},{}}}".format(from_val, to_val), group, greedy)
    else:
        return _postfix(eregex, "{{{}}}".format(from_val), group, greedy)

def open_curly():
    return "\\{"

def close_curly():
    return "\\}"

def orelse(exprs):
    return "|".join(exprs)

def bar():
    return "\\|"

def seq(exprs):
    return "".join(exprs)
    


