import math

from adsk.core import Point3D, ValueInput, ObjectCollection
from adsk.fusion import Component, FeatureOperations, SketchFittedSpline, ConstructionPlane, Profile

from .SketchUtils import createSketchByPlane, drawCircle, extrudeProfile, createRelativePoint


class ThreadFeature:
    def __init__(self,
                 component: Component,
                 origin: Point3D,
                 plane,
                 length: float,
                 majorDiameter: float,
                 minorDiameter: float,
                 pitch: float,
                 cutAngle: float,
                 notchWidth: float):
        self._component = component
        self._plane = plane
        self._origin = origin
        self._length = length
        self._pitch = pitch
        self._majorDiameter = majorDiameter
        self._minorDiameter = minorDiameter
        self._cutAngle = cutAngle
        self._notchWidth = notchWidth
        self._cutDepth = (self._majorDiameter - self._minorDiameter) / 2
        self._protrusionWidth = self._notchWidth + (self._cutDepth * math.tan(self._cutAngle) * 2)

    def createMaleThread(self):
        self._createShaft()
        spline = self._createHelixSpline()
        notchProfiles = self._createNotchProfilesAlongSpline(spline)
        self._createLoftAlongSpline(notchProfiles, spline, FeatureOperations.JoinFeatureOperation)
        self._createChamfer()

    # TODO: female chamfer
    def createFemaleThread(self):
        self._createHole()
        spline = self._createHelixSpline()
        notchProfiles = self._createNotchProfilesAlongSpline(spline)
        self._createLoftAlongSpline(notchProfiles, spline, FeatureOperations.CutFeatureOperation)

    def _createShaft(self):
        sketch = createSketchByPlane(self._component, self._plane)
        profile = drawCircle(sketch, self._origin, self._minorDiameter)
        extrudeProfile(self._component, profile, self._length, FeatureOperations.NewBodyFeatureOperation)

    def _createHole(self):
        sketch = createSketchByPlane(self._component, self._plane)
        profile = drawCircle(sketch, self._origin, self._minorDiameter)
        extrudeProfile(self._component, profile, self._length, FeatureOperations.CutFeatureOperation)

    def _createHelixSpline(self) -> SketchFittedSpline:
        helixAngle = math.asin(self._pitch / (math.pi * self._majorDiameter))
        origin = self._origin.copy()
        origin.z = origin.z + (self._protrusionWidth / 2)
        length = self._length - (self._protrusionWidth / 2)
        helixPoints = _HelixCurve(self._majorDiameter / 2, helixAngle, origin).getPoints(length)
        sketch = createSketchByPlane(self._component, self._plane)
        return sketch.sketchCurves.sketchFittedSplines.add(helixPoints)

    def _createNotchProfilesAlongSpline(self, spline: SketchFittedSpline):
        profiles = []
        pointIndices = [i for i in range(0, spline.fitPoints.count, 10)]
        pointIndices.append(spline.fitPoints.count - 1)
        for i in pointIndices:
            planeInput = self._component.constructionPlanes.createInput()
            planeInput.setByDistanceOnPath(spline, ValueInput.createByReal(i / (spline.fitPoints.count - 1)))
            plane = self._component.constructionPlanes.add(planeInput)
            notchProfile = self._createThreadNotchProfile(plane)
            profiles.append(notchProfile)
        return profiles

    def _createLoftAlongSpline(self, profiles, spline: SketchFittedSpline, operation: FeatureOperations):
        loftFeatures = self._component.features.loftFeatures
        loftInput = loftFeatures.createInput(operation)
        for profile in profiles:
            loftInput.loftSections.add(profile)
        loftInput.centerLineOrRails.addCenterLine(spline)
        loftFeatures.add(loftInput)

    def _createThreadNotchProfile(self, plane: ConstructionPlane) -> Profile:
        point1 = Point3D.create(0, self._notchWidth / 2, 0)
        point2 = Point3D.create(self._cutDepth + 0.001, self._protrusionWidth / 2, 0)
        point3 = Point3D.create(self._cutDepth + 0.001, -self._protrusionWidth / 2, 0)
        point4 = Point3D.create(0, -self._notchWidth / 2, 0)

        sketch = self._component.sketches.add(plane)
        sketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
        sketch.sketchCurves.sketchLines.addByTwoPoints(point2, point3)
        sketch.sketchCurves.sketchLines.addByTwoPoints(point3, point4)
        sketch.sketchCurves.sketchLines.addByTwoPoints(point4, point1)
        return sketch.profiles.item(0)

    def _createChamfer(self):
        # overshoot to compensate for small rounding errors in helix calculations
        overshoot = 0.01
        minorX = self._minorDiameter / 2 - self._protrusionWidth - overshoot
        majorX = self._majorDiameter / 2 + overshoot
        minorZ = self._length - self._protrusionWidth - overshoot
        majorZ = self._length + self._cutDepth + overshoot
        point1 = createRelativePoint(self._origin, minorX, 0, majorZ)
        point2 = createRelativePoint(self._origin, majorX, 0, majorZ)
        point3 = createRelativePoint(self._origin, majorX, 0, minorZ)

        sketch = createSketchByPlane(self._component, self._plane)
        sketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
        sketch.sketchCurves.sketchLines.addByTwoPoints(point2, point3)
        sketch.sketchCurves.sketchLines.addByTwoPoints(point3, point1)

        axisPoint1 = createRelativePoint(self._origin, 0, 0, 0)
        axisPoint2 = createRelativePoint(self._origin, 0, 0, 1)
        axis = sketch.sketchCurves.sketchLines.addByTwoPoints(axisPoint1, axisPoint2)
        profile = sketch.profiles.item(0)

        revolveFeatures = self._component.features.revolveFeatures
        revolveInput = revolveFeatures.createInput(profile, axis, FeatureOperations.CutFeatureOperation)
        revolveInput.setAngleExtent(False, ValueInput.createByReal(math.pi * 2))
        revolveFeatures.add(revolveInput)


class _HelixCurve:
    def __init__(self, radius, angle, origin: Point3D):
        self._radius = radius
        self._c = math.tan(angle) * self._radius
        self._origin = origin

    def _getPoint(self, t) -> Point3D:
        x = self._radius * math.cos(t)
        y = self._radius * math.sin(t)
        z = self._c * t
        return Point3D.create(self._origin.x + x, self._origin.y + y, self._origin.z + z)

    def getPoints(self, height) -> ObjectCollection:
        tRange = height / self._c
        pointsCollection = ObjectCollection.create()
        steps = int(3 * tRange / math.pi * 2)
        step = 1.0 / (steps - 1)

        for i in range(0, steps):
            t = tRange * step * i
            pointsCollection.add(self._getPoint(t))
        return pointsCollection
