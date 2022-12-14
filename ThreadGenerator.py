# Author-Nick Park
# Description-Generate set of threads with different tolerance

import adsk.cam
import adsk.core
import adsk.fusion

from .lib.GenerateThreadsCommand import GenerateThreadsCommand
from .lib.common.Common import ui, design, printTrace

# maintain a global reference to command to keep its handlers alive
command = None


def run(context):
    try:
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return

        global command
        command = GenerateThreadsCommand()
        command.execute()

        adsk.autoTerminate(False)
    except:
        printTrace()
