import bpy
import mathutils

# Currently this script is a skeleton for the basic operation of our add-on.
# It will later be turned from a script into an add-on.


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
# Should include error handling for when "aligner" is not a 4 point plane.
print("Vanishing point calculation not yet implemented.")

# Make new camera, give it a dummy position/rotation/perspective
# https://blender.stackexchange.com/questions/151319/adding-camera-to-scene
cam = bpy.data.cameras.new("VP_cam")
cam.lens = 18
cam_obj = bpy.data.objects.new("VP_cam", cam)
cam_obj.location = (1, 1, 1)
cam_obj.rotation_euler = (0.6799, 0, 0.8254)
bpy.context.scene.collection.objects.link(cam_obj)

# Move image to be head-on with camera
def alignPlaneToCam(camera, plane, distance):
    '''
    Takes in a plane and aligns it so that it is head-on with the camera, with the x-axis.
    
    :param camera: the camera object
    :type camera: bpy.types.object
    :param plane: the plane
    :type plane: bpy.types.object
    :param distance: distance from the camera to place the plane
    :type distance: float'''
    cam_orig = camera.location
    cam_dir = camera.rotation_euler

    rot_mat = cam_dir.to_matrix()
    forwardVec = mathutils.Vector((0,0,1))
    forwardVec.rotate(cam_dir)

    # calculate the position to place the plane (origin + direction vector * distance)
    plane.location = cam_orig - (forwardVec) * distance

    # rotate plane so that it is facing -direction vector
    plane.rotation_euler = cam_dir

alignPlaneToCam(cam_obj,image, 1) 
# TODO: 1 is a dummy value -- replace with the appropriate value.