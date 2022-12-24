import math

from adsk.core import Point3D, CommandEventArgs, CommandEventHandler
from adsk.fusion import FeatureOperations, SketchPoint, Component

from .UserParameters import UserParameters
from .common.Common import printTrace, ui, design
from .sketch.SketchUtils import createNewComponent, extrudeProfile, createXYSketch, createCylinder
from .sketch.ThreadFeature import ThreadFeature


class OnExecuteHandler(CommandEventHandler):
    def __init__(self):
        super().__init__()
        self._boltThickness = 0.25

    def notify(self, args: CommandEventArgs):
        try:
            # TODO: different behavior if preview (set `args.isValidResult = False` when rendering preview)
            ui.messageBox(args.firingEvent.name)
            UserParameters.updateValuesFromCommandInputs(args.firingEvent.sender.commandInputs)
            self.run()
            args.isValidResult = True
        except:
            printTrace()

    def run(self):
        initTimelineIndex = design.timeline.markerPosition
        component = createNewComponent()
        # TODO: raise error if selection is not exactly 1 point coincident with a face
        if ui.activeSelections.count > 0:
            selectedSketchPoint = SketchPoint.cast(ui.activeSelections.item(0).entity)
            self._buildSingleThread(component, selectedSketchPoint)
        else:
            self._buildMultipleThreadsWithTolerances(component)

        timelineGroups = design.timeline.timelineGroups
        timelineGroup = timelineGroups.add(initTimelineIndex, design.timeline.markerPosition - 1)
        timelineGroup.name = 'Thread'

    def _buildSingleThread(self, component: Component, sketchPoint: SketchPoint):
        self._buildThread(component, sketchPoint)

    def _buildMultipleThreadsWithTolerances(self, component: Component):
        self._createBaseCuboid(component)
        for i, sketchPoint in enumerate(self._createSketchPoints(component)):
            if not UserParameters.isThreadMale():
                self._createCylinder(component, sketchPoint.geometry)
            self._buildThread(component, sketchPoint, i)

    def _createBaseCuboid(self, component: Component):
        boxWidth = UserParameters.getMajorDiameter()
        boxLength = (UserParameters.getMajorDiameter() * UserParameters.getGenerationCount() * 2) - UserParameters.getMajorDiameter()
        boxDepth = 0.1
        offset = boxWidth / 2
        if not UserParameters.isThreadMale():
            boxWidth = boxWidth + (self._boltThickness * 2)
            boxLength = boxLength + (self._boltThickness * 2)
            offset = offset + self._boltThickness
        sketch = createXYSketch(component)
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(Point3D.create(-offset, -offset, 0),
                                                             Point3D.create(boxLength - offset, boxWidth - offset, 0))
        profile = sketch.profiles.item(0)
        extrudeProfile(component, profile, -boxDepth, FeatureOperations.NewBodyFeatureOperation)

    def _createSketchPoints(self, component: Component):
        sketch = createXYSketch(component)
        sketchPoints = []
        for i in range(int(UserParameters.getGenerationCount())):
            x = UserParameters.getMajorDiameter() * i * 2
            sketchPoint = sketch.sketchPoints.add(Point3D.create(x, 0, 0))
            sketchPoints.append(sketchPoint)
        return sketchPoints

    def _createCylinder(self, component: Component, center: Point3D):
        diameter = UserParameters.getMajorDiameter() + (self._boltThickness * 2)
        # TODO: replace compensation offset by chamfer
        length = UserParameters.getLength() - 0.1
        createCylinder(component, center, diameter, length)

    def _buildThread(self, component: Component, sketchPoint: SketchPoint, generationCount: int = 0):
        origin = sketchPoint.geometry
        plane = sketchPoint.parentSketch.referencePlane
        notchWidthTolerance = self._getToleranceValue(UserParameters.getNotchWidthStep(), generationCount, 1, 3)
        majorDiameterTolerance = self._getToleranceValue(UserParameters.getMajorDiameterStep(), generationCount, 2, 3)
        minorDiameterTolerance = self._getToleranceValue(UserParameters.getMinorDiameterStep(), generationCount, 3, 3)
        threadFeature = ThreadFeature(component,
                                      origin,
                                      plane,
                                      UserParameters.getLength(),
                                      UserParameters.getMajorDiameter() + majorDiameterTolerance,
                                      UserParameters.getMinorDiameter() + minorDiameterTolerance,
                                      UserParameters.getPitch(),
                                      UserParameters.getCutAngle(),
                                      UserParameters.getNotchWidth() + notchWidthTolerance)
        if UserParameters.isThreadMale():
            threadFeature.createMaleThread()
        else:
            threadFeature.createFemaleThread()

    def _getToleranceValue(self, stepSize: float, stepCount: int, fromStep: int, interval: int) -> float:
        # increment tolerance value every `interval` steps
        intervalCount = math.floor((stepCount - fromStep) / interval) + 1
        return max(0, intervalCount) * stepSize
