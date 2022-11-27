import traceback

import adsk.core
import adsk.fusion
from adsk.core import ValueInput

app = adsk.core.Application.get()
ui = app.userInterface
unitsMgr = app.activeProduct.unitsManager
design = adsk.fusion.Design.cast(app.activeProduct)


def printTrace():
    ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class UserParameter:
    def __init__(self, id, name, unitType, initValue):
        self.id = id
        self.name = name
        self.unitType = unitType
        self._value = initValue

    def getValueInUserUnits(self) -> float:
        return self._value

    def getValueInInternalUnits(self) -> float:
        return unitsMgr.convert(self._value, self.unitType, unitsMgr.internalUnits)

    def setValueFromCommandInput(self, commandInput):
        # evaluateExpression returns value in internal units
        valueInInternalUnits = unitsMgr.evaluateExpression(commandInput.expression, self.unitType)
        self._value = unitsMgr.convert(valueInInternalUnits, unitsMgr.internalUnits, self.unitType)

    def asValueInput(self) -> ValueInput:
        # value inputs must always be in internal units
        return ValueInput.createByReal(self.getValueInInternalUnits())


# TODO: chamfer input
# TODO: direction input
length = UserParameter('lengthId', 'Length', 'mm', 20)
majorDiameter = UserParameter('majorDiameterId', 'Major Diameter', 'mm', 11)
minorDiameter = UserParameter('minorDiameterId', 'Minor Diameter', 'mm', 10)
pitch = UserParameter('pitchId', 'Pitch', 'mm', 2)
cutAngle = UserParameter('cutAngleId', 'Cut Angle', 'deg', 30.0)
notchWidth = UserParameter('notchWidthId', 'Notch Width', 'mm', 0.5)
isMale = UserParameter('isMaleId', 'Male', 'mm', 1)
generationCount = UserParameter('generationCountId', 'Generation Count', 'mm', 3)

userParameters = [length, majorDiameter, minorDiameter, pitch, cutAngle, notchWidth, isMale, generationCount]


def getUserParameter(id):
    return next(userParameter for userParameter in userParameters if userParameter.id == id)
