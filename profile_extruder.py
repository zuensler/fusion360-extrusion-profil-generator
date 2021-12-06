#Author-Daniel Ruescher
#Description-creates an extrusion profile.

import adsk.core, adsk.fusion, adsk.cam, traceback
import math
import os
from sys import platform

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''
_handlers = []

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Create a command definition and add a button to the CREATE panel.
        cmdDef = _ui.commandDefinitions.addButtonDefinition('profile_extruder', 'Add Heron Profile', 'Creates a heron profile with a specific length', 'Resources/')        
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        extrusionButton = createPanel.controls.addCommand(cmdDef)
        
        # Connect to the command created event.
        onCommandCreated = ExtrusionCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        if context['IsApplicationStartup'] == False:
            _ui.messageBox('The "Heron generator" command has been added\nto the CREATE panel of the MODEL workspace.')
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        extrusionButton = createPanel.controls.itemById('profile_extruder')      
        if extrusionButton:
            extrusionButton.deleteMe()
        
        cmdDef = _ui.commandDefinitions.itemById('profile_extruder')
        if cmdDef:
            cmdDef.deleteMe()
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Verfies that a value command input has a valid expression and returns the 
# value if it does.  Otherwise it returns False.  This works around a 
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make 
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager
        
        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class ExtrusionCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            
            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()
                
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            
           
            
            global  _profileLength
            global _profileResources 
            global _profileTypeDd

            #path to eextension -> make setup at the beginning of the plugin install
            # talk dirty to me
            #resourcePath ='C:\\Users\DRU\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\profile_extruder\Resources\profiles\\'
            resourcePath = ""
            if platform == "darwin":
                resourcePath = os.path.expanduser('~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/profile_extruder/Resources/profiles/')
            elif platform == "win32":
                resourcePath = os.getenv("APPDATA")+'\Autodesk\Autodesk Fusion 360\API\AddIns\profile_extruder\Resources\profiles\\'
            
            _profileResources = {}

            #inputs here 
            _profileTypeDd = inputs.addDropDownCommandInput('profileType', 'Profil Types', adsk.core.DropDownStyles.TextListDropDownStyle)
            profileTypes = _profileTypeDd.listItems
            isFirst = True
            for file in os.listdir(resourcePath):
                if file.endswith(".dxf"):
                    profileName = (file.replace(".dxf","")).replace("_", " ")
                    profileTypes.add(profileName, isFirst)
                    isFirst = False
                    
                    _profileResources[profileName] = resourcePath+file

            
            
            _profileLength = inputs.addDistanceValueCommandInput('profileLength', 'Profile length', adsk.core.ValueInput.createByReal(1))
            
            
            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True
            
            # Connect to the command related events.
            onExecute = ExtrusionCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)        
            
            onInputChanged = ExtrusionCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)     
            
            onValidateInputs = ExtrusionCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)        
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class ExtrusionCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            drawProfile(des, _profileLength.value, )
         
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                c


        
# Event handler for the inputChanged event.
class ExtrusionCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
            
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
        
# Event handler for the validateInputs event.
class ExtrusionCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
         
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))




def drawProfile(design, profile_length):
    try:
        importManager = _app.importManager
        # Create a new component by creating an occurrence.
        occs = design.rootComponent.occurrences
        mat = adsk.core.Matrix3D.create()
        newOcc = occs.addNewComponent(mat)        
        newComp = adsk.fusion.Component.cast(newOcc.component)
        
        #import dxf
        # Get dxf import options

        #this is not cool yet
        #dxfFileName = '%appdata%\Autodesk\Autodesk Fusion 360\API\AddIns\profile_extruder\Resources\profiles\heron_40x40.dxf'
        dxfFileName = _profileResources[_profileTypeDd.selectedItem.name]
        dxfOptions = importManager.createDXF2DImportOptions(dxfFileName, newComp.xZConstructionPlane)
        dxfOptions.isViewFit = False
        
        # Import dxf file to newComp
        importManager.importToTarget(dxfOptions, newComp)
        dxfOptions = importManager.createDXF2DImportOptions(dxfFileName, newComp.xZConstructionPlane)
        dxfOptions.isSingleSketchResult = False
        #dxf sketch
        sketch = newComp.sketches.item(0)

        
        for item in sketch.profiles:
            area = item.areaProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy).area
            #_ui.messageBox('Area {}'.format(area))
                
            if (area > 10.38890 and area < 10.38892) or (area > 5.6692 and area < 5.66925) or (area > 15.79155 and area < 15.79158) or (area > 0.59564 and 
            area < 0.59567) or (area > 9.74503 and area < 9.74505) or (area > 6.66195 and area <  6.66197) or(area > 21.01280 and 
            area <  21.01282) or(area > 6.57096 and area <  6.57098) or(area > 0.4535673 and area <  0.4535675) or(area > 1.0602874 and area <  1.0602876) or(area > 0.1570795 and 
            area <  0.1570797) or(area > 0.2199114 and area <  0.2199116):
                extrudes = newComp.features.extrudeFeatures
                extInput = extrudes.createInput(item, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

                #define the extrusin length
                distance = adsk.core.ValueInput.createByReal(profile_length)
                extInput.setDistanceExtent(False, distance)

                # Create the extrusion.
                baseExtrude = extrudes.add(extInput)
                break   
        newComp.name =('{}x{}mm'.format(_profileTypeDd.selectedItem.name,profile_length*10))
        
        return newComp



    except Exception as error:
        _ui.messageBox("draw extrusion profile failed Failed : " + str(error)) 
        return None





