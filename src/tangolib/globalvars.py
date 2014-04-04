"""
Some shared global variables
"""

import tangolib.cmdparse


TANGO_CMD_LINE_ARGUMENTS = None
TANGO_EVAL_GLOBAL_ENV = None


def makeTangoEvalGlobalEnv(safe_mode=False):
    global TANGO_GLOBAL_ENV
    if safe_mode:
        TANGO_GLOBAL_ENV = dict()
    else:
        TANGO_GLOBAL_ENV = __builtins__

def init_global_vars():
    global TANGO_CMD_LINE_ARGUMENTS
    TANGO_CMD_LINE_ARGUMENTS = tangolib.cmdparse.GLOBAL_COMMAND_LINE_ARGUMENTS
    makeTangoEvalGlobalEnv(TANGO_CMD_LINE_ARGUMENTS.safe_mode)

