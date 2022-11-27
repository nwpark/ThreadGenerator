from adsk.core import Point3D, ValueInput, Matrix3D
from adsk.fusion import Sketch, Component, Profile, FeatureOperations, ExtrudeFeature

from ..common.Common import design


def createNewComponent() -> Component:
    allOccurrences = design.rootComponent.occurrences
    newOccurrence = allOccurrences.addNewComponent(Matrix3D.create())
    if newOccurrence.component is None:
        raise ('New component failed to create', 'New Component Failed')
    return newOccurrence.component


def createXYSketch(component: Component) -> Sketch:
    return component.sketches.add(component.xYConstructionPlane)


def createXZSketch(component: Component) -> Sketch:
    return component.sketches.add(component.xZConstructionPlane)


def createCylinder(component: Component, center: Point3D, diameter: float, height: float):
    sketch = createXYSketch(component)
    profile = drawCircle(sketch, center, diameter)
    extrudeProfile(component, profile, height)


def drawCircle(sketch: Sketch, center: Point3D, diameter: float) -> Profile:
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center, diameter / 2)
    return sketch.profiles.item(0)


def createSketchByPlane(component: Component, plane) -> Sketch:
    planeInput = component.constructionPlanes.createInput()
    planeInput.setByOffset(plane, ValueInput.createByReal(0))
    plane = component.constructionPlanes.add(planeInput)
    return component.sketches.add(plane)


def createRelativePoint(relativeTo: Point3D, x: float, y: float, z: float) -> Point3D:
    return Point3D.create(relativeTo.x + x, relativeTo.y + y, relativeTo.z + z)


def extrudeProfile(component: Component, profile: Profile, extentDistance: float,
                   operation=FeatureOperations.NewBodyFeatureOperation) -> ExtrudeFeature:
    extrudes = component.features.extrudeFeatures
    extrudeInput = extrudes.createInput(profile, operation)
    extrudeInput.setDistanceExtent(False, ValueInput.createByReal(extentDistance))
    return extrudes.add(extrudeInput)
