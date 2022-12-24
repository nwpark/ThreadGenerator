from enum import Enum
from typing import NamedTuple


class _ThreadParameters(NamedTuple):
    threadName: str
    length: float
    majorDiameter: float
    minorDiameter: float
    pitch: float
    cutAngle: float
    notchWidth: float


class ThreadDefinition(Enum):
    G_1_4 = _ThreadParameters(threadName='G 1/4',
                              length=9.0,
                              majorDiameter=13.16,
                              minorDiameter=11.44,
                              pitch=1.34,
                              cutAngle=27.5,
                              notchWidth=0.2)
    G_1_8 = _ThreadParameters(threadName='G 1/8',
                              length=9.0,
                              majorDiameter=13.16,
                              minorDiameter=11.44,
                              pitch=1.34,
                              cutAngle=27.5,
                              notchWidth=0.2)

    @staticmethod
    def fromThreadName(threadName: str) -> _ThreadParameters:
        threadParams = next(
            threadParams for threadParams in ThreadDefinition if threadParams.value.threadName == threadName)
        return threadParams.value

    @staticmethod
    def getThreadNames() -> [str]:
        return list(map(lambda threadParams: threadParams.value.threadName, ThreadDefinition))
