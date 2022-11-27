import adsk.cam
import adsk.core
import adsk.fusion

from .OnDestroyHandler import OnDestroyHandler
from .OnExecuteHandler import OnExecuteHandler
from .common import ui, userParameters, printTrace


class GenerateThreadsCommand:
    def __init__(self):
        self.commandCreatedHandler = self._CommandCreatedHandler()
        self.commandDefinition = ui.commandDefinitions.itemById('ThreadGenerator')
        if not self.commandDefinition:
            self.commandDefinition = ui.commandDefinitions.addButtonDefinition('ThreadGenerator', 'Generate Thread',
                                                                               'Generates threads.', './resources')

        self.commandDefinition.commandCreated.add(self.commandCreatedHandler)

    def execute(self):
        inputs = adsk.core.NamedValues.create()
        self.commandDefinition.execute(inputs)

    class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
        def __init__(self):
            super().__init__()
            self.onExecuteHandler = None
            self.onExecutePreviewHandler = None
            self.onDestroyHandler = None

        def notify(self, args):
            try:
                cmd = args.command
                cmd.isRepeatable = False

                self.onExecuteHandler = OnExecuteHandler()
                self.onExecutePreviewHandler = OnExecuteHandler()
                self.onDestroyHandler = OnDestroyHandler()
                cmd.execute.add(self.onExecuteHandler)
                cmd.executePreview.add(self.onExecutePreviewHandler)
                cmd.destroy.add(self.onDestroyHandler)

                for userParameter in userParameters:
                    cmd.commandInputs.addValueInput(userParameter.id, userParameter.name, userParameter.unitType,
                                                    userParameter.asValueInput())
            except:
                printTrace()
