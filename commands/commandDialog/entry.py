import adsk.core
import os

import adsk.fusion
from ...lib import fusion360utils as futil
from ... import config
import math
app = adsk.core.Application.get()
ui = app.userInterface

# TODO Major rework using OOP to keep a reference to model parameters and geometry. (Improve performance)

# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Command Dialog Sample'
CMD_Description = 'A Fusion 360 Add-in to create models for 2.5D laser surface texturing.'

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
_selected_ok = False
_texture_selector_changed = False

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

    global _selected_ok
    _selected_ok = False

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs : adsk.core.CommandInputs = args.command.commandInputs

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
    default_value = adsk.core.ValueInput.createByString('3 mm')
    period_input = inputs.addDistanceValueCommandInput('texture_period_input', 'Texture period', default_value)
    period_input.setManipulator(adsk.core.Point3D.create(0,0,0), adsk.core.Vector3D.create(0,1,0))

    # Create a distance input field for the texture depth and set the default to 1 mm. Set the 3D manipulator in depth direction.
    default_value = adsk.core.ValueInput.createByString('1 mm')
    depth_input = inputs.addDistanceValueCommandInput('texture_depth_input', 'Texture depth', default_value)
    depth_input.setManipulator(adsk.core.Point3D.create(0,0,0), adsk.core.Vector3D.create(0,0,-1))
    
    # Create a distance input field for the flank width and set the default to 2 mm. Set the 3D manipulator in width direction.
    default_value = adsk.core.ValueInput.createByString('1 mm')
    width_input = inputs.addDistanceValueCommandInput('texture_width_input', 'Texture width', default_value)
    width_input.setManipulator(adsk.core.Point3D.create(0,0,0), adsk.core.Vector3D.create(1,0,0))

    # Create an angle input field for the flank angle and set the default to 1 mm. Set the 3D manipulator on the X-Z-plane.
    defaultAngleUnits = app.activeProduct.unitsManager.defaultLengthUnits
    default_value = adsk.core.ValueInput.createByString('40 degree')
    flank_angle_input = inputs.addAngleValueCommandInput('texture_flank_angle_input', 'Flank angle', default_value)
    flank_angle_input.maximumValue = math.pi
    flank_angle_input.isMaximumValueInclusive = False
    flank_angle_input.setManipulator(adsk.core.Point3D.create(0,0,0), adsk.core.Vector3D.create(1,0,0), adsk.core.Vector3D.create(0,0,1))

    create_sketch(inputs)

    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    #futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs

    global _selected_ok
    _selected_ok = True

    flank_angle = inputs.itemById('texture_flank_angle_input').value
    depth = inputs.itemById('texture_depth_input').value
    width = inputs.itemById("texture_width_input").value

    set_flank_angle_dimension(flank_angle)
    set_depth_dimension(depth)
    set_width_dimension(width)

    create_texture(inputs)


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs
    global _texture_selector_changed
    
    create_texture(inputs)

    # TODO Optimisation suggestion: Use different configurations and model parameters to change the dimensions and texture type. Delete unnecessary configurations on command execution.
    
    # TODO Put all the geometry changes from inputs here
    depth_input : adsk.core.DistanceValueCommandInput = inputs.itemById("texture_depth_input")
    depth = depth_input.value
    set_depth_dimension(depth)

    flank_angle_input : adsk.core.AngleValueCommandInput = inputs.itemById("texture_flank_angle_input")
    flank_angle = flank_angle_input.value
    set_flank_angle_dimension(flank_angle)

    width_input : adsk.core.DistanceValueCommandInput = inputs.itemById("texture_width_input")
    width = width_input.value
    set_width_dimension(width)

    

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
        global _texture_selector_changed
        _texture_selector_changed = True

    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values. This controls if the OK button is enabled or not.
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')
    global _selected_ok
    if not _selected_ok:
        delete_all()
    #ui.messageBox("Destroyed")
    global local_handlers
    local_handlers = []


def create_sketch(inputs: adsk.core.CommandInputs):
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

    flank_angle = inputs.itemById("texture_flank_angle_input").value
    set_flank_angle_dimension(flank_angle)
    depth = inputs.itemById("texture_depth_input").value
    set_depth_dimension(depth)
    width = inputs.itemById("texture_width_input").value
    set_width_dimension(width)

def create_texture(inputs):
    texture_selector_input : adsk.core.DropDownCommandInput = inputs.itemById("texture_type_input")
    texture_type = texture_selector_input.selectedItem.name

    match texture_type:
        case "Dots":
            make_dots(inputs)
            create_rectangular_pattern(inputs)
        case "Lines":
            make_line(inputs)
            create_rectangular_pattern(inputs)
        case "Hatch":
            make_line(inputs)
            create_circular_pattern(inputs)
            create_rectangular_pattern(inputs)
    
    if texture_type == "Lines":
        period_input : adsk.core.DistanceValueCommandInput = inputs.itemById("texture_period_input")
        period = period_input.value
        #set_extrude_dimension(period)

def add_single_attribute(design, entity, groupName, attributeName, value):
    attrib = entity.attributes.itemByName(groupName, attributeName)
    if not attrib:
        # Get any existing attributes with this name and delete them.
        oldAttribs = design.findAttributes(groupName, attributeName)
        for oldAttrib in oldAttribs:
            oldAttrib.deleteMe()

        # Add the attribute to the specified entity.
        entity.attributes.add(groupName, attributeName, str(value))

def feature_getter(attribute_name:str):
    design = adsk.fusion.Design.cast(app.activeProduct)
    attribute = design.findAttributes("Surface-Texture-Creator", attribute_name)
    if len(attribute)>0:
        return attribute[0].parent
    else:
        return None

def get_feature_sketch() -> adsk.fusion.Sketch:
    return feature_getter("Feature_Sketch")

def get_flank_angle_dimension() -> adsk.fusion.SketchAngularDimension:
    return feature_getter("flankAngleDimension")

def get_width_dimension() -> adsk.fusion.SketchLinearDimension:
    return feature_getter("widthDimension")

def get_depth_dimension() -> adsk.fusion.SketchLinearDimension:
    return feature_getter("depthDimension")

def set_extrude_dimension(value : float):
    extrude = get_extrude_feature()
    sym_def : adsk.fusion.SymmetricExtentDefinition = extrude.extentOne
    distance : adsk.fusion.ModelParameter = sym_def.distance
    distance.value = value

def get_extrude_feature() -> (adsk.fusion.ExtrudeFeature | None):
    return feature_getter("ExtrudeFeature")
    
def set_flank_angle_dimension(angle : float):
    flankAngleDimension = get_flank_angle_dimension()
    flankAngleDimension.value = angle

def set_width_dimension(width : float):
    widthDimension = get_width_dimension()
    widthDimension.value = width

def set_depth_dimension(depth : float):
    depthDimension = get_depth_dimension()
    depthDimension.value = depth

def make_line(inputs : adsk.core.CommandInputs):
    design : adsk.fusion.Design = app.activeProduct

    # Get the active component of the active design
    component : adsk.fusion.Component = design.activeComponent
    extrudes = component.features.extrudeFeatures

    sketch = get_feature_sketch()
    profiles = [sketch.profiles.item(0), sketch.profiles.item(1)]
    profiles = adsk.core.ObjectCollection.createWithArray(profiles)
    texture_period = inputs.itemById('texture_period_input').expression
    default_value = adsk.core.ValueInput.createByString(texture_period)
    
    extrude_input = extrudes.createInput(profiles, 3)
    extrude_input.setSymmetricExtent(default_value, True)
    extrude = extrudes.add(extrude_input)

    add_single_attribute(design, extrude, "Surface-Texture-Creator", "ExtrudeFeature","")

def make_dots(inputs : adsk.core.CommandInputs):
    
    design : adsk.fusion.Design = app.activeProduct
    
    # Get the active component
    component : adsk.fusion.Component = design.activeComponent
    revolves = component.features.revolveFeatures

    sketch = get_feature_sketch()
    profile = sketch.profiles.item(0)

    revolve_axis = component.zConstructionAxis

    revolve_input = revolves.createInput(profile, revolve_axis, 3)
    revolve_angle = adsk.core.ValueInput.createByString("360degree")
    revolve_input.setAngleExtent(isSymmetric=True, angle=revolve_angle)

    revolve = revolves.add(revolve_input)

    add_single_attribute(design, revolve, "Surface-Texture-Creator", "RevolveFeature","")

def get_revolve_feature() -> (adsk.fusion.RevolveFeature | None):
    return feature_getter("RevolveFeature")

def create_rectangular_pattern(inputs : adsk.core.CommandInputs):
    design : adsk.fusion.Design = app.activeProduct
    component : adsk.fusion.Component = design.activeComponent

    rectangular_patterns = component.features.rectangularPatternFeatures

    texture_selector_input : adsk.core.DropDownCommandInput = inputs.itemById("texture_type_input")
    texture_type = texture_selector_input.selectedItem.name

    input_entities = adsk.core.ObjectCollection.create()
    x_axis = component.xConstructionAxis
    y_axis = component.yConstructionAxis

    add_second_direction = True

    match texture_type:
        case "Dots":
            revolve = get_revolve_feature()
            input_entities.add(revolve)

        case "Lines":
            extrude = get_extrude_feature()
            input_entities.add(extrude)
            add_second_direction = False

        case "Hatch":
            extrude = get_extrude_feature()
            circular_pattern = get_circular_pattern_feature()
            combine_feature = get_combine_feature()
            input_entities.add(extrude)
            input_entities.add(circular_pattern)
            input_entities.add(combine_feature)
    
    quantity = adsk.core.ValueInput.createByReal(2)
    distance_input : adsk.core.DistanceValueCommandInput = inputs.itemById("texture_period_input")
    distance = adsk.core.ValueInput.createByReal(distance_input.value)

    rectangular_pattern_input = rectangular_patterns.createInput(input_entities, x_axis, quantity, distance, 1)
    if add_second_direction:
        rectangular_pattern_input.setDirectionTwo(y_axis, quantity, distance)

    rectangular_pattern = rectangular_patterns.add(rectangular_pattern_input)
    combine_features = component.features.combineFeatures
    target_body = rectangular_pattern.bodies.item(0)
    tool_body = adsk.core.ObjectCollection.create()
    for i in range(1, 4):
        tool_body.add(rectangular_pattern.bodies.item(i))
    combine_feature_input = combine_features.createInput(target_body, tool_body)
    combine_features.add(combine_feature_input)

    add_single_attribute(design, rectangular_patterns.item(0), "Surface-Texture-Creator", "RectangularPattern","")

def get_rectangular_pattern() -> (adsk.fusion.RectangularPatternFeature | None):
    return feature_getter("RectangularPattern")


def create_circular_pattern(inputs : adsk.core.CommandInputs):
    design : adsk.fusion.Design = app.activeProduct
    component : adsk.fusion.Component = design.activeComponent

    circular_patterns = component.features.circularPatternFeatures
    extrude = get_extrude_feature()
    input_entities = adsk.core.ObjectCollection.create()
    input_entities.add(extrude)
    z_axis = component.zConstructionAxis
    circular_pattern_input = circular_patterns.createInput(input_entities, z_axis)
    quantity = adsk.core.ValueInput.createByReal(2)
    total_angle = adsk.core.ValueInput.createByString("90 degree")
    circular_pattern_input.quantity = quantity
    circular_pattern_input.totalAngle = total_angle

    circular_pattern = circular_patterns.add(circular_pattern_input)

    combine_features = component.features.combineFeatures
    target_body = extrude.bodies.item(0)
    tool_body = adsk.core.ObjectCollection.create()
    tool_body.add(circular_pattern.bodies.item(0))
    combine_feature_input = combine_features.createInput(target_body, tool_body)
    combine_features.add(combine_feature_input)

    add_single_attribute(design, circular_pattern, "Surface-Texture-Creator", "CircularPattern","")
    add_single_attribute(design, combine_features.item(0), "Surface-Texture-Creator", "CombineFeature","")

def get_combine_feature():
    return feature_getter("CombineFeature")

def get_circular_pattern_feature() -> (adsk.fusion.CombineFeature | None):
    return feature_getter("CircularPattern")

def deleter(getter:callable)->bool:
    to_delete = getter()
    if to_delete is not None:
        to_delete.deleteMe()
        return True
    else:
        return False

def delete_sketch():
    deleter(get_feature_sketch)

def delete_extrude() -> bool:
    deleter(get_extrude_feature)


def delete_revolve() -> bool:
    deleter(get_revolve_feature)
    
def delete_pattern() -> bool:
    deleter(get_circular_pattern_feature)

def delete_all():
    delete_sketch()
    delete_extrude()
    delete_revolve()
    delete_pattern()


    # TODO Check the texture selector input and use linear or circular pattern accordingly.
    # TODO Use rectangularPatternFeatures and circularPatternFeatures.