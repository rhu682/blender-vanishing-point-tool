# Currently this script is a skeleton for the basic operation of our add-on.
# It will later be turned from a script into an add-on.
import bpy

scene = bpy.context.scene
''' User must select *first* the image, then the aligning plane, and nothing 
else, and then trigger this script.'''

# Get image and plane data from selected objects.
aligner = bpy.context.active_object

if len(bpy.context.selected_objects) != 2:
    raise RuntimeError("Expected only two objects to be selected.")

if bpy.context.selected_objects[0] == aligner:
    image = bpy.context.selected_objects[1]
else:
    image = bpy.context.selected_objects[0]

# TODO: transform aligner data and pass it to vanishing point calculation function
print("Vanishing point calculation not yet implemented.")

# TODO: Make new camera, give it a dummy position/rotation/perspective
bpy.ops.object.camera_add()

# TODO: Move image to be head-on with camera