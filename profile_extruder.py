#Author-Daniel
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        product = app.activeProduct #returns the active document
        #new_component = adsk.fusion.FeatureOperations.NewComponentFeatureOperation()
        design = adsk.fusion.Design.cast(product) #cast current design to design?

        importManager = app.importManager

        rootComp = design.rootComponent #getting the root component of the design

    
        # Create a new occurrence.	
        trans = adsk.core.Matrix3D.create()
        occ = rootComp.occurrences.addNewComponent(trans)

        # Get the associated component.	
        newComp = occ.component

        # Get dxf import options
        dxfFileName = 'C:\\Users\DRU\Desktop\heron_40x40.dxf'
        dxfOptions = importManager.createDXF2DImportOptions(dxfFileName, newComp.xZConstructionPlane)
        dxfOptions.isViewFit = False
        
        # Import dxf file to newComp
        importManager.importToTarget(dxfOptions, newComp)
        dxfOptions = importManager.createDXF2DImportOptions(dxfFileName, newComp.xZConstructionPlane)
        dxfOptions.isSingleSketchResult = False
        sketch = newComp.sketches.item(0)
        ui.messageBox('sketches:\n{}'.format(newComp.sketches.count))
        
       
        prof =sketch.profiles.item(7)
       
        extInput = newComp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(10.0)
        extInput.setDistanceExtent(False, distance)
        ext = newComp.features.extrudeFeatures.add(extInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Stop addin')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
