import adsk.core
import os

import adsk.fusion
from ...lib import fusion360utils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Command Dialog Sample'
CMD_Description = 'A Fusion 360 Add-in Command with a dialog'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # TODO Define the dialog for your command by adding different inputs to the command.

    # Create dropdown menu for texture type
    texture_selector = inputs.addDropDownCommandInput('texture_type_input', 'Texture type', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    texture_types = texture_selector.listItems
    texture_types.add('Dots', True, '')
    texture_types.add('Lines', False, '')
    texture_types.add('Hatch', False, '')

    # Create image to label texture-specific parameters
    imagefile = os.path.join(ICON_FOLDER, 'ExamplePicture.png')
    inputs.addImageCommandInput('texture_image', '', imagefile)

    # Create a value input field for the texture period and set the default using 1 unit of the default length unit.
    defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits
    default_value = adsk.core.ValueInput.createByString('1')
    inputs.addValueInput('texture_period_input', 'Texture period', defaultLengthUnits, default_value)

    # Create a value input field for the texture period and set the default using 1 unit of the default length unit.
    default_value = adsk.core.ValueInput.createByString('1')
    inputs.addValueInput('texture_depth_input', 'Texture depth', defaultLengthUnits, default_value)

    # Create a value input field for the texture period and set the default using 1 unit of the default length unit.
    defaultAngleUnits = app.activeProduct.unitsManager.defaultLengthUnits
    default_value = adsk.core.ValueInput.createByString('1')
    inputs.addFloatSliderCommandInput('texture_flank_angle_input', 'Flank angle', defaultAngleUnits, 0, 179.9)

    # Create a simple text box input.
    inputs.addTextBoxCommandInput('text_box', 'Some Text', 'Enter some text.', 1, False)

    # Create a value input field and set the default using 1 unit of the default length unit.
    default_value = adsk.core.ValueInput.createByString('1')
    inputs.addValueInput('value_input', 'Some Value', defaultLengthUnits, default_value)

    create_sketch()

    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    text_box: adsk.core.TextBoxCommandInput = inputs.itemById('text_box')
    value_input: adsk.core.ValueCommandInput = inputs.itemById('value_input')

    # Do something interesting
    text = text_box.text
    expression = value_input.expression
    msg = f'Your text: {text}<br>Your value: {expression}'
    ui.messageBox(msg)

    create_sketch()



# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    changed_input_id = changed_input.id

    inputs = args.inputs

    if changed_input_id == 'texture_type_input':
        # TODO Get new value of selector
        # Change image according to new value
        # Change parameters according to new value
        pass
    elif changed_input_id == "texture_depth_input":
        # TODO Put this part into the command_preview function instead.
        set_depth_dimension(changed_input.value)

    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values. This controls if the OK button is enabled or not.
    valueInput = inputs.itemById('value_input')
    if valueInput.value >= 0:
        args.areInputsValid = True
    else:
        args.areInputsValid = False
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')
    delete_sketch()
    global local_handlers
    local_handlers = []

# TODO Create_sketch function needs input arguments for depth width and flank angel. Alternatively, use attributes of the component or user parameters for this.
def create_sketch():
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        ui.messageBox("Sketch not created. No active Fusion design", "No Design")
        return
    
    # Get the active component of the active design
    component : adsk.fusion.Component = design.activeComponent # Use type hints between ":" and "=" to make code completion work properly

    # Create a sketch on the yz plane
    sketches = component.sketches
    sketchPlane = component.xZConstructionPlane
    sketch = sketches.add(sketchPlane)

    # Draw the shape
    points = adsk.core.Point3D
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs

    ## Define corner points (all units in cm)
    point0 = points.create(0, 0, 0)
    point1 = points.create(0.1, 0, 0)
    point2 = points.create(-0.1, 0, 0)
    point3 = points.create(-0.05, 0.07, 0)
    point4 = points.create(0.05, 0.07, 0)
    pointDepth = points.create(0, 0.1, 0)

    ## Draw lines
    lineTop = lines.addByTwoPoints(point1, point2)
    lineLeft = lines.addByTwoPoints(lineTop.endSketchPoint, point3)
    arcBottom = arcs.addByThreePoints(point4, pointDepth, lineLeft.endSketchPoint)
    lineRight = lines.addByTwoPoints(arcBottom.startSketchPoint, lineTop.startSketchPoint)

    midline = sketch.project(component.zConstructionAxis).item(0)
    midline.isCenterLine = True

    topRef = sketch.project(component.xConstructionAxis).item(0)
    topRef.isConstruction = True

    depthRef = lines.addByTwoPoints(point0, pointDepth)
    depthRef.isConstruction = True

    # Add geometric constraints
    geomConstraints = sketch.geometricConstraints

    ## Tangent constraints of arc
    geomConstraints.addTangent(arcBottom, lineLeft)
    geomConstraints.addTangent(arcBottom, lineRight)

    ## Symmetry constraint of flanks
    geomConstraints.addSymmetry(lineLeft, lineRight, midline)

    ## Coincident constraints
    geomConstraints.addCoincident(lineTop.endSketchPoint, topRef)
    geomConstraints.addCoincident(lineTop.startSketchPoint, topRef)
    geomConstraints.addCoincident(depthRef.startSketchPoint, topRef)
    geomConstraints.addCoincident(depthRef.endSketchPoint, arcBottom)

    ## Collinear constraints
    geomConstraints.addCollinear(depthRef, midline)

    # Add sketch dimensions
    dimensions = sketch.sketchDimensions
    flankAngleDimension = dimensions.addAngularDimension(lineRight, lineLeft, points.create(0,-0.2,0))
    widthDimension = dimensions.addDistanceDimension(lineTop.endSketchPoint, lineTop.startSketchPoint, 1, points.create(0,-0.02,0))
    depthDimension = dimensions.addDistanceDimension(depthRef.endSketchPoint, depthRef.startSketchPoint, 2, points.create(0.02,0.02,0))
    add_single_attribute(design, sketch, "Surface-Texture-Creator", "Feature_Sketch", "")
    add_single_attribute(design, flankAngleDimension, "Surface-Texture-Creator", "flankAngleDimension", "")
    add_single_attribute(design, widthDimension, "Surface-Texture-Creator", "widthDimension", "")
    add_single_attribute(design, depthDimension, "Surface-Texture-Creator", "depthDimension", "")

def update_sketch():
    sketch = retrieve_feature_sketch()

def delete_sketch():
    sketch = retrieve_feature_sketch()
    sketch.deleteMe()

def add_single_attribute(design, entity, groupName, attributeName, value):
    attrib = entity.attributes.itemByName(groupName, attributeName)
    if not attrib:
        # Get any existing attributes with this name and delete them.
        oldAttribs = design.findAttributes(groupName, attributeName)
        for oldAttrib in oldAttribs:
            oldAttrib.deleteMe()

        # Add the attribute to the specified entity.
        entity.attributes.add(groupName, attributeName, str(value))

def retrieve_feature_sketch():
    design = adsk.fusion.Design.cast(app.activeProduct)
    return design.findAttributes("Surface-Texture-Creator", "Feature_Sketch")[0].parent

def retrieve_flank_angle_dimension():
    design = adsk.fusion.Design.cast(app.activeProduct)
    return design.findAttributes("Surface-Texture-Creator", "flankAngleDimension")[0].parent

def retrieve_width_dimension():
    design = adsk.fusion.Design.cast(app.activeProduct)
    return design.findAttributes("Surface-Texture-Creator", "widthDimension")[0].parent

def retrieve_depth_dimension():
    design = adsk.fusion.Design.cast(app.activeProduct)
    return design.findAttributes("Surface-Texture-Creator", "depthDimension")[0].parent

# TODO For set functions it might be necessary to use expressions instead of values
def set_flank_angle(angle):
    flankAngleDimension = retrieve_flank_angle_dimension()
    flankAngleDimension.value = angle

def set_width_dimension(width):
    widthDimension = retrieve_width_dimension()
    widthDimension.value = width

def set_depth_dimension(depth):
    depthDimension = retrieve_depth_dimension()
    depthDimension.parameter.value = depth