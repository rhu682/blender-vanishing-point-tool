import bpy
import mathutils
from collections import namedtuple

"""
DOCSTRING REFERENCE vvv

[summary]

### Parameters
1. a : str
    - [description]
2. *b : int, (default 5)
    - [description]
3. *c : Tuple[int, int], (default (1, 2))
    - [description]

### Returns
- Any
    - [description]

Raises
------
- ValueError
    - [description]
"""

# Currently this script is a skeleton for the basic operation of our add-on.
# It will later be turned from a script into an add-on.

#################
## DEFINITIONS ##
#################
# See https://docs.python.org/3/library/collections.html#collections.namedtuple for information on namedtuples.
Coords3D = namedtuple('Coords3D', 'x y z')
Coords2D = namedtuple('Coords2D', 'x y')
# A namedtuple to store camera pose information.
# Location is a Coords3D tuple, rotation is a Coords3D tuple of euler rotation.
CameraPose = namedtuple('CameraPose', 'location rotation focal_length')

######################
## HELPER FUNCTIONS ##
######################
def alignPlaneToCam(camera, plane, distance):
    '''
    Takes in a plane and aligns it so that it is head-on with the camera, with the x-axis.
    
    :param camera: the camera object
    :type camera: bpy.types.object
    :param plane: the plane
    :type plane: bpy.types.object
    :param distance: distance from the camera to place the plane
    :type distance: float
    :param return: none'''
    cam_orig = camera.location
    cam_dir = camera.rotation_euler

    rot_mat = cam_dir.to_matrix()
    forwardVec = mathutils.Vector((0,0,1))
    forwardVec.rotate(cam_dir)

    # calculate the position to place the plane (origin + direction vector * distance)
    plane.location = cam_orig - (forwardVec) * distance

    # rotate plane so that it is facing -direction vector
    plane.rotation_euler = cam_dir

def solve2VP(vps, imDimen):
    ''' Given 2 vanishing points, calculate the camera pose that corresponds with those vanishing points. 

    :param vps: an array of vanishing point locations. 
                These locations should be given in relative coordinates relative to the image plane. 
                Points inside the plane are in the range (-1.0, 1.0).
    :type vps: an array of tuples of floats. Should have a length of 2. 
    :param imDimen: the dimensions of the image plane, in pixels. 
    :type imDimen: A tuple of 2 floats in (horizontal_width, vertical_width) order. 
    :param return: Pose data for a camera. 
    :type return: A CameraPose namedtuple.'''

    pose = CameraPose(Coords3D(0.0, 0.0, 0.0), Coords3D(0.0, 0.0, 0.0), 10)

    #TODO: 211: get "principal point", which is described as "the center of projection in image plane coordinates". I'm not entirely sure what that means?
    #TODO: 248: compute focal length of camera using the 3 vanishing points, using a helper function at 305
    #TODO: 262: check accuracy of vanishing points using a helper function at 607. we might skip this step
    #TODO: 264: compute camera parameters using a helper function at 737
    #TODO: https://github.com/stuffmatic/fSpy-Blender/blob/eec40b085d45cc623fd379998d85b88de679d4b8/fspy_blender/addon.py#L68: transform the output from the previous step into blender camera data
    
    return pose

##########
## SCRIPT ##
##########
''' User must select *first* the image, then the aligning plane, and nothing 
else, and then trigger this script.'''

scene = bpy.context.scene

# Get image and plane data from selected objects.
aligner = bpy.context.active_object

if len(bpy.context.selected_objects) != 2:
    raise RuntimeError("Expected only two objects to be selected.")

if bpy.context.selected_objects[0] == aligner:
    image = bpy.context.selected_objects[1]
else:
    image = bpy.context.selected_objects[0]
    
# TODO: Get distance from camera to image, and store it, and later pass it into alignPlaneToCam.

# TODO: transform aligner data and pass it to vanishing point calculation function
# We want to transform the data into relative coordinates wrt image plane.
# Should include error handling for when "aligner" is not a 4 point plane.
print("Vanishing point calculation not yet implemented.")

# TODO: Transform output into Blender camera pose data
# Make new camera, give it a dummy position/rotation/perspective
# https://blender.stackexchange.com/questions/151319/adding-camera-to-scene
cam = bpy.data.cameras.new("VP_cam")
cam.lens = 18
cam_obj = bpy.data.objects.new("VP_cam", cam)
cam_obj.location = (1, 1, 1)
cam_obj.rotation_euler = (0.6799, 0, 0.8254)
bpy.context.scene.collection.objects.link(cam_obj)

# Move image to be head-on with camera
alignPlaneToCam(cam_obj,image, 1) 
# TODO: 1 is a dummy value -- replace with the appropriate value.