from enum import Enum

from adsk.core import ValueInput, CommandInputs, BoolValueCommandInput, IntegerSliderCommandInput, ValueCommandInput, \
    CommandInput, DropDownStyles, DropDownCommandInput

from .ThreadDefinitions import ThreadDefinition
from .common.Common import unitsMgr, resourceFolder, ui


class _UserParameter:
    def __init__(self, id: str, name: str):
        self._id = id
        self._name = name
        pass

    def getValue(self):
        pass

    def setValue(self, value):
        pass

    def setValueFromCommandInput(self, commandInput: CommandInput):
        pass

    def addToCommandInputs(self, commandInputs: CommandInputs):
        pass

    def getId(self) -> str:
        return self._id


class _UserDimensionParameter(_UserParameter):
    def __init__(self, id, name: str, unitType: str, initValue: float):
        super().__init__(id, name)
        self._unitType = unitType
        self._valueInSelfUnits = initValue
        self._commandInput = ValueCommandInput.cast(None)

    def getValue(self) -> float:
        # dimensions must be used with internal units
        return unitsMgr.convert(self._valueInSelfUnits, self._unitType, unitsMgr.internalUnits)

    def setValue(self, value):
        self._valueInSelfUnits = value
        self._commandInput.value = unitsMgr.convert(value, self._unitType, unitsMgr.internalUnits)

    def setValueFromCommandInput(self, commandInput: ValueCommandInput):
        # evaluateExpression returns value in internal units
        valueInInternalUnits = unitsMgr.evaluateExpression(commandInput.expression, self._unitType)
        self._valueInSelfUnits = unitsMgr.convert(valueInInternalUnits, unitsMgr.internalUnits, self._unitType)

    def addToCommandInputs(self, commandInputs: CommandInputs):
        self._commandInput = commandInputs.addValueInput(self._id, self._name, self._unitType,
                                    ValueInput.createByReal(self.getValue()))


class _UserBoolParameter(_UserParameter):
    def __init__(self, id: str, name: str, initValue: bool):
        super().__init__(id, name)
        self._value = initValue

    def getValue(self) -> bool:
        return self._value

    def setValueFromCommandInput(self, commandInput: BoolValueCommandInput):
        self._value = commandInput.value

    def addToCommandInputs(self, commandInputs: CommandInputs):
        commandInputs.addBoolValueInput(self._id, self._name, True, resourceFolder, self._value)


class _UserIntegerSliderParameter(_UserParameter):
    def __init__(self, id: str, name: str, min: int, max: int):
        super().__init__(id, name)
        self._min = min
        self._max = max
        self._value = min

    def getValue(self) -> int:
        return self._value

    def setValueFromCommandInput(self, commandInput: IntegerSliderCommandInput):
        self._value = commandInput.valueOne

    def addToCommandInputs(self, commandInputs: CommandInputs):
        commandInputs.addIntegerSliderCommandInput(self._id, self._name, self._min, self._max, False)


class UserDropDownParameter(_UserParameter):
    def __init__(self, id: str, name: str, dropDownOptions: [str], defaultOption: str):
        super().__init__(id, name)
        self._dropDownInput: DropDownCommandInput = DropDownCommandInput.cast(None)
        self._dropDownOptions = dropDownOptions
        self._defaultOption = defaultOption

    def getValue(self) -> str:
        return self._dropDownInput.selectedItem.name

    def setValueFromCommandInput(self, commandInput: IntegerSliderCommandInput):
        pass

    def addToCommandInputs(self, commandInputs: CommandInputs):
        self._dropDownInput = commandInputs.addDropDownCommandInput(self._id, self._name,
                                                                    DropDownStyles.TextListDropDownStyle)
        for option in self._dropDownOptions:
            self._dropDownInput.listItems.add(option, option == self._defaultOption)


class UserParameters(Enum):
    THREAD_DEFINITION_DROPDOWN = UserDropDownParameter('threadDefinitionDropdownId', 'Thread Definition', ThreadDefinition.getThreadNames(), ThreadDefinition.getThreadNames()[0])
    LENGTH = _UserDimensionParameter('lengthId', 'Length', 'mm', 20)
    MAJOR_DIAMETER = _UserDimensionParameter('majorDiameterId', 'Major Diameter', 'mm', 11)
    MINOR_DIAMETER = _UserDimensionParameter('minorDiameterId', 'Minor Diameter', 'mm', 10)
    PITCH = _UserDimensionParameter('pitchId', 'Pitch', 'mm', 2)
    CUT_ANGLE = _UserDimensionParameter('cutAngleId', 'Cut Angle', 'deg', 30.0)
    NOTCH_WIDTH = _UserDimensionParameter('notchWidthId', 'Notch Width', 'mm', 0.5)
    IS_MALE = _UserBoolParameter('isMaleId', 'Male', True)
    GENERATION_COUNT = _UserIntegerSliderParameter('generationCountId', 'Generation Count', 1, 10)
    MAJOR_DIAMETER_STEP = _UserDimensionParameter('majorDiameterStepId', 'Major Diameter Step', 'mm', 0)
    MINOR_DIAMETER_STEP = _UserDimensionParameter('minorDiameterStepId', 'Minor Diameter Step', 'mm', 0)
    NOTCH_WIDTH_STEP = _UserDimensionParameter('notchWidthStepId', 'Notch Width Step', 'mm', 0)

    @staticmethod
    def applySelectedThreadDefinition():
        threadName = UserParameters.THREAD_DEFINITION_DROPDOWN.value.getValue()
        threadDefinition = ThreadDefinition.fromThreadName(threadName)
        UserParameters.LENGTH.value.setValue(threadDefinition.length)
        UserParameters.MAJOR_DIAMETER.value.setValue(threadDefinition.majorDiameter)
        UserParameters.MINOR_DIAMETER.value.setValue(threadDefinition.minorDiameter)
        UserParameters.PITCH.value.setValue(threadDefinition.pitch)
        UserParameters.CUT_ANGLE.value.setValue(threadDefinition.cutAngle)
        UserParameters.NOTCH_WIDTH.value.setValue(threadDefinition.notchWidth)

    @staticmethod
    def getLength() -> float:
        return UserParameters.LENGTH.value.getValue()

    @staticmethod
    def getMajorDiameter() -> float:
        return UserParameters.MAJOR_DIAMETER.value.getValue()

    @staticmethod
    def getMinorDiameter() -> float:
        return UserParameters.MINOR_DIAMETER.value.getValue()

    @staticmethod
    def getPitch() -> float:
        return UserParameters.PITCH.value.getValue()

    @staticmethod
    def getCutAngle() -> float:
        return UserParameters.CUT_ANGLE.value.getValue()

    @staticmethod
    def getNotchWidth() -> float:
        return UserParameters.NOTCH_WIDTH.value.getValue()

    @staticmethod
    def isThreadMale() -> bool:
        return UserParameters.IS_MALE.value.getValue()

    @staticmethod
    def getGenerationCount() -> int:
        return UserParameters.GENERATION_COUNT.value.getValue()

    @staticmethod
    def getMajorDiameterStep() -> float:
        return UserParameters.MAJOR_DIAMETER_STEP.value.getValue()

    @staticmethod
    def getMinorDiameterStep() -> float:
        return UserParameters.MINOR_DIAMETER_STEP.value.getValue()

    @staticmethod
    def getNotchWidthStep() -> float:
        return UserParameters.NOTCH_WIDTH_STEP.value.getValue()

    @staticmethod
    def getAllParameters() -> [_UserParameter]:
        return list(map(lambda param: param.value, UserParameters))

    @staticmethod
    def fromId(id: str) -> _UserParameter:
        return next(param for param in UserParameters.getAllParameters() if param.getId() == id)

    @staticmethod
    def updateValuesFromCommandInputs(commandInputs: CommandInputs):
        for i in range(commandInputs.count):
            commandInput = commandInputs.item(i)
            userParameter = UserParameters.fromId(commandInput.id)
            userParameter.setValueFromCommandInput(commandInput)
