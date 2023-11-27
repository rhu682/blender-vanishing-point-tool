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

    ### Parameters
    1. camera : bpy.types.object
        - the camera object
    2. plane : bpy.types.object
        - the plane
    3. distance : float
        - distance from the camera to place the plane

    ### Returns
    - None'''
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
    '''     
    Given 2 vanishing points, calculate the camera pose that corresponds with those vanishing points. 

    ### Parameters
    1. vps : Tuple[float, float]
        - An array of vanishing point locations. 
        - These locations should be given in relative coordinates relative to the image plane. 
        - Points inside the plane are in the range (-1.0, 1.0).
    2. imDimen : Tuple[int, int]
        - The dimensions of the image plane, in pixels. 

    ### Returns
    - CameraPose
        - Pose data for a camera. 
    '''

    pose = CameraPose(Coords3D(0.0, 0.0, 0.0), Coords3D(0.0, 0.0, 0.0), 10)

    # Reference: https://github.com/stuffmatic/fSpy/blob/develop/src/gui/solver/solver.ts
    #TODO: 211: get "principal point", which is described as "the center of projection in image plane coordinates". I'm not entirely sure what that means?
    #TODO: 248: compute focal length of camera using the 3 vanishing points, using a helper function at 305
    #TODO: 262: check accuracy of vanishing points using a helper function at 607. we might skip this step
    #TODO: 264: compute camera parameters using a helper function at 737
    #TODO: https://github.com/stuffmatic/fSpy-Blender/blob/eec40b085d45cc623fd379998d85b88de679d4b8/fspy_blender/addon.py#L68: transform the output from the previous step into blender camera data
    
    print("Vanishing point calculation not yet implemented.")

    return pose

##########
## SCRIPT ##
##########
''' User must select *first* the image, then the aligning plane, and nothing 
else, and then trigger this script.'''

scene = bpy.context.scene

# Get image and plane data from selected objects.
aligner = bpy.context.active_object

# Verify that only 2 objects are selected.
if len(bpy.context.selected_objects) != 2:
    raise RuntimeError("Expected only two objects to be selected.")

if bpy.context.selected_objects[0] == aligner:
    image = bpy.context.selected_objects[1]
else:
    image = bpy.context.selected_objects[0]

# Get camera.
cam = bpy.context.scene.camera
if cam == None:
    raise RuntimeError("No active camera.")

# Get distance from camera to image
dist = (cam.location - image.location).length

# TODO: transform aligner data and pass it to vanishing point calculation function
# We want to transform the data into relative coordinates wrt image plane.
# Should include error handling for when "aligner" is not a 4 point plane.

pose = solve2VP(None, None)

# https://blender.stackexchange.com/questions/151319/adding-camera-to-scene
cam.data.lens = pose.focal_length
cam.location = pose.location
cam.rotation_euler = pose.rotation

# Move image to be head-on with camera
alignPlaneToCam(cam,image, 5) 
# TODO: 1 is a dummy value -- replace with the appropriate value.