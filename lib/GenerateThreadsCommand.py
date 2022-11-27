from adsk.core import CommandCreatedEventArgs, NamedValues, CommandCreatedEventHandler

from .OnDestroyHandler import OnDestroyHandler
from .OnExecuteHandler import OnExecuteHandler
from .UserParameters import UserParameters
from .common.Common import ui, printTrace, resourceFolder


class GenerateThreadsCommand:
    def __init__(self):
        self.commandCreatedHandler = self._CommandCreatedHandler()
        self.commandDefinition = ui.commandDefinitions.itemById('ThreadGenerator')
        if not self.commandDefinition:
            self.commandDefinition = ui.commandDefinitions.addButtonDefinition('ThreadGenerator', 'Generate Thread',
                                                                               'Generates threads.', resourceFolder)
        self.commandDefinition.commandCreated.add(self.commandCreatedHandler)

    def execute(self):
        inputs = NamedValues.create()
        self.commandDefinition.execute(inputs)

    class _CommandCreatedHandler(CommandCreatedEventHandler):
        def __init__(self):
            super().__init__()
            self.onExecuteHandler = None
            self.onExecutePreviewHandler = None
            self.onDestroyHandler = None

        def notify(self, args: CommandCreatedEventArgs):
            try:
                cmd = args.command
                cmd.isRepeatable = False

                self.onExecuteHandler = OnExecuteHandler()
                self.onExecutePreviewHandler = OnExecuteHandler()
                self.onDestroyHandler = OnDestroyHandler()
                cmd.execute.add(self.onExecuteHandler)
                cmd.executePreview.add(self.onExecutePreviewHandler)
                cmd.destroy.add(self.onDestroyHandler)

                for userParameter in UserParameters.asList():
                    userParameter.addToCommandInputs(cmd.commandInputs)
            except:
                printTrace()
