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
def alignPlaneToCam(camera, plane, distance: float):
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

def computeFocalLength(Fu: Coords2D, Fv: Coords2D, P: Coords2D):
    '''
   Computes the focal length based on two vanishing points and a center of projection.

   Code modified from https://github.com/stuffmatic/fSpy/blob/702189ec5acbbd2c8ba492db0e52ecb5fc908f5c/src/gui/solver/solver.ts#L305
   
   ### Parameters
    1. Fu : Coords2D
        - the first vanishing point in image plane coordinates.
    2. Fv : Coords2D
        - the second vanishing point in image plane coordinates.
    3. P : Coords2D
        - the center of projection in image plane coordinates.

    ### Returns
    - float
        - The relative focal length.
   '''
    # compute Puv, the orthogonal projection of P onto FuFv
    dirFuFv = mathutils.Vector((Fu.x - Fv.x, Fu.y - Fv.y)).normalize()
    FvP = mathutils.Vector((P.x - Fv.x, P.y - Fv.y))
    proj = dirFuFv.dot(FvP)
    Puv = Coords2D(proj * dirFuFv.x + Fv.x, proj * dirFuFv.y + Fv.y)

    PPuv = mathutils.Vector((P.x - Puv.x, P.y - Puv.y)).length
    FvPuv = mathutils.Vector((Fv.x - Puv.x, Fv.y - Puv.y)).length
    FuPuv = mathutils.Vector((Fu.x - Puv.x, Fu.y - Puv.y)).length

    fSq = FvPuv * FuPuv - PPuv * PPuv

    if (fSq <= 0):
      return None
    return mathutils.sqrt(fSq)

def solve2VP(vps: (Coords2D, Coords2D), imDimen: (int, int)):
    '''     
    Given 2 vanishing points, calculate the camera pose that corresponds with those vanishing points. 

    ### Parameters
    1. vps : Tuple[Coords2D, Coords2D]
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
    # Get principal point. Information on principal point is given here: https://fspy.io/tutorial/
    # Not entirely sure what it means, though. For now, we just assume that it's the midpoint of the image.
    principalPoint = Coords2D(0.0, 0.0)

    #compute focal length of camera using the 3 points
    computeFocalLength(vps[0], vps[1], principalPoint)

    #TODO: 262: check accuracy of vanishing points using a helper function at 607. we might skip this step

    #TODO: 264: compute camera parameters using a helper function at 737

    #TODO: https://github.com/stuffmatic/fSpy-Blender/blob/eec40b085d45cc623fd379998d85b88de679d4b8/fspy_blender/addon.py#L68: 
    # transform the output from the previous step into blender camera data
    
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
# Probably some function of original distance + original focal length and new focal length. Linearly related?