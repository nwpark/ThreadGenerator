# Author-Nick Park
# Description-Generate set of threads with different tolerance

import adsk.cam
import adsk.core
import adsk.fusion

from .lib.GenerateThreadsCommand import GenerateThreadsCommand
from .lib.common import ui, design, printTrace


def run(context):
    try:
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return
        
        # maintain a global reference to command to keep its handlers alive
        global generateThreadsCommand
        generateThreadsCommand = GenerateThreadsCommand()
        generateThreadsCommand.execute()

        adsk.autoTerminate(False)
    except:
        printTrace()
