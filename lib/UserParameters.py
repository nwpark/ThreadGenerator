from adsk.core import ValueInput, CommandInputs, BoolValueCommandInput, IntegerSliderCommandInput, ValueCommandInput, \
    CommandInput

from .common.Common import unitsMgr, resourceFolder


class _UserParameter:
    def __init__(self, id: str, name: str):
        self._id = id
        self._name = name
        pass

    def getValue(self):
        pass

    def setValueFromCommandInput(self, commandInput: CommandInput):
        pass

    def addToCommandInputs(self, commandInputs: CommandInputs):
        pass

    def hasId(self, id: str):
        return id == self._id


class UserDimensionParameter(_UserParameter):
    def __init__(self, id, name: str, unitType: str, initValue: float):
        super().__init__(id, name)
        self._unitType = unitType
        self._value = initValue

    def getValue(self) -> float:
        # dimensions must be used with internal units
        return unitsMgr.convert(self._value, self._unitType, unitsMgr.internalUnits)

    def setValueFromCommandInput(self, commandInput: ValueCommandInput):
        # evaluateExpression returns value in internal units
        valueInInternalUnits = unitsMgr.evaluateExpression(commandInput.expression, self._unitType)
        self._value = unitsMgr.convert(valueInInternalUnits, unitsMgr.internalUnits, self._unitType)

    def addToCommandInputs(self, commandInputs: CommandInputs):
        commandInputs.addValueInput(self._id, self._name, self._unitType,
                                    ValueInput.createByReal(self.getValue()))


class UserBoolParameter(_UserParameter):
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


class UserParameters:
    # TODO: chamfer input
    # TODO: direction input
    _length = UserDimensionParameter('lengthId', 'Length', 'mm', 20)
    _majorDiameter = UserDimensionParameter('majorDiameterId', 'Major Diameter', 'mm', 11)
    _minorDiameter = UserDimensionParameter('minorDiameterId', 'Minor Diameter', 'mm', 10)
    _pitch = UserDimensionParameter('pitchId', 'Pitch', 'mm', 2)
    _cutAngle = UserDimensionParameter('cutAngleId', 'Cut Angle', 'deg', 30.0)
    _notchWidth = UserDimensionParameter('notchWidthId', 'Notch Width', 'mm', 0.5)
    _isMale = UserBoolParameter('isMaleId', 'Male', True)
    _generationCount = _UserIntegerSliderParameter('generationCountId', 'Generation Count', 1, 10)
    _majorDiameterStep = UserDimensionParameter('majorDiameterStepId', 'Major Diameter Step', 'mm', 0)
    _minorDiameterStep = UserDimensionParameter('minorDiameterStepId', 'Minor Diameter Step', 'mm', 0)
    _notchWidthStep = UserDimensionParameter('notchWidthStepId', 'Notch Width Step', 'mm', 0)

    @staticmethod
    def getLength() -> float:
        return UserParameters._length.getValue()

    @staticmethod
    def getMajorDiameter() -> float:
        return UserParameters._majorDiameter.getValue()

    @staticmethod
    def getMinorDiameter() -> float:
        return UserParameters._minorDiameter.getValue()

    @staticmethod
    def getPitch() -> float:
        return UserParameters._pitch.getValue()

    @staticmethod
    def getCutAngle() -> float:
        return UserParameters._cutAngle.getValue()

    @staticmethod
    def getNotchWidth() -> float:
        return UserParameters._notchWidth.getValue()

    @staticmethod
    def isThreadMale() -> bool:
        return UserParameters._isMale.getValue()

    @staticmethod
    def getGenerationCount() -> int:
        return UserParameters._generationCount.getValue()

    @staticmethod
    def getMajorDiameterStep() -> float:
        return UserParameters._majorDiameterStep.getValue()

    @staticmethod
    def getMinorDiameterStep() -> float:
        return UserParameters._minorDiameterStep.getValue()

    @staticmethod
    def getNotchWidthStep() -> float:
        return UserParameters._notchWidthStep.getValue()

    @staticmethod
    def asList():
        return [UserParameters._length,
                UserParameters._majorDiameter,
                UserParameters._minorDiameter,
                UserParameters._pitch,
                UserParameters._cutAngle,
                UserParameters._notchWidth,
                UserParameters._isMale,
                UserParameters._generationCount,
                UserParameters._majorDiameterStep,
                UserParameters._minorDiameterStep,
                UserParameters._notchWidthStep]

    @staticmethod
    def updateValuesFromCommandInputs(commandInputs: CommandInputs):
        for i in range(commandInputs.count):
            commandInput = commandInputs.item(i)
            userParameter = next(param for param in UserParameters.asList() if param.hasId(commandInput.id))
            userParameter.setValueFromCommandInput(commandInput)
