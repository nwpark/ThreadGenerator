from adsk.core import Point3D
from adsk.fusion import FeatureOperations, ExtentDirections, SketchPoint, Component, Sketch

from .common import *
from .sketch import createNewComponent, drawCircle, extrudeProfile, ThreadFeature, createSketchByPlane, createXYSketch, createCylinder


class OnExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
        self._boltThickness = 0.25

    def notify(self, args):
        try:
            # update user parameters to match the current input values
            for commandInput in args.firingEvent.sender.commandInputs:
                getUserParameter(commandInput.id).setValueFromCommandInput(commandInput)
            self.run()
            args.isValidResult = True
        except:
            printTrace()

    def run(self):
        component = createNewComponent()
        # TODO: raise error if selection is not exactly 1 point coincident with a face
        if ui.activeSelections.count > 0:
            selectedSketchPoint = SketchPoint.cast(ui.activeSelections.item(0).entity)
            self._buildSingleThread(component, selectedSketchPoint)
        else:
            self._buildMultipleThreadsWithTolerances(component)

    def _buildSingleThread(self, component: Component, sketchPoint: SketchPoint):
        self._buildThread(component, sketchPoint)

    def _buildMultipleThreadsWithTolerances(self, component: Component):
        self._createBaseCuboid(component)
        for sketchPoint in self._createSketchPoints(component):
            if not bool(isMale.getValueInUserUnits()):
                self._createCylinder(component, sketchPoint.geometry)
            self._buildThread(component, sketchPoint)

    def _createBaseCuboid(self, component: Component):
        boxWidth = majorDiameter.getValueInInternalUnits()
        boxLength = (majorDiameter.getValueInInternalUnits() * generationCount.getValueInUserUnits() * 2) - majorDiameter.getValueInInternalUnits()
        boxDepth = 0.1
        offset = boxWidth / 2
        if not bool(isMale.getValueInUserUnits()):
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
        for i in range(int(generationCount.getValueInUserUnits())):
            x = majorDiameter.getValueInInternalUnits() * i * 2
            sketchPoint = sketch.sketchPoints.add(Point3D.create(x, 0, 0))
            sketchPoints.append(sketchPoint)
        return sketchPoints

    def _createCylinder(self, component: Component, center: Point3D):
        diameter = majorDiameter.getValueInInternalUnits() + (self._boltThickness * 2)
        createCylinder(component, center, diameter, length.getValueInInternalUnits())

    def _buildThread(self, component: Component, sketchPoint: SketchPoint):
        origin = sketchPoint.geometry
        plane = sketchPoint.parentSketch.referencePlane
        isMaleThread = bool(isMale.getValueInUserUnits())
        correctedLength = length.getValueInInternalUnits() + (0.1 if not isMaleThread else 0)
        threadFeature = ThreadFeature(component,
                                      origin,
                                      plane,
                                      correctedLength,
                                      majorDiameter.getValueInInternalUnits(),
                                      minorDiameter.getValueInInternalUnits(),
                                      pitch.getValueInInternalUnits(),
                                      cutAngle.getValueInInternalUnits(),
                                      notchWidth.getValueInInternalUnits())
        threadFeature.create(isMaleThread)
