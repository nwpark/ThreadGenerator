from adsk.core import CommandCreatedEventArgs, NamedValues, CommandCreatedEventHandler

from .OnDestroyHandler import OnDestroyHandler
from .OnExecuteHandler import OnExecuteHandler
from .UserParameters import UserParameters
from .common.Common import ui, printTrace, resourceFolder


class GenerateThreadsCommand:
    def __init__(self):
        self._commandCreatedHandler = self._CommandCreatedHandler()
        self._commandDefinition = ui.commandDefinitions.itemById('ThreadGenerator')
        if not self._commandDefinition:
            self._commandDefinition = ui.commandDefinitions.addButtonDefinition('ThreadGenerator', 'Generate Thread',
                                                                                'Generates threads.', resourceFolder)
        self._commandDefinition.commandCreated.add(self._commandCreatedHandler)

    def execute(self):
        inputs = NamedValues.create()
        self._commandDefinition.execute(inputs)

    class _CommandCreatedHandler(CommandCreatedEventHandler):
        def __init__(self):
            super().__init__()
            self._onExecuteHandler = None
            self._onExecutePreviewHandler = None
            self._onDestroyHandler = None

        def notify(self, args: CommandCreatedEventArgs):
            try:
                cmd = args.command
                cmd.isRepeatable = False

                self._onExecuteHandler = OnExecuteHandler()
                self._onExecutePreviewHandler = OnExecuteHandler()
                self._onDestroyHandler = OnDestroyHandler()
                cmd.execute.add(self._onExecuteHandler)
                cmd.executePreview.add(self._onExecutePreviewHandler)
                cmd.destroy.add(self._onDestroyHandler)

                for userParameter in UserParameters.asList():
                    userParameter.addToCommandInputs(cmd.commandInputs)
            except:
                printTrace()
