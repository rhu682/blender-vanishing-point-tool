import bpy
import mathutils
from collections import namedtuple
from math import sqrt

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
        - the first vanishing point in image plane coordinates. Unit in pixels.
    2. Fv : Coords2D
        - the second vanishing point in image plane coordinates. Unit in pixels.
    3. P : Coords2D
        - the center of projection in image plane coordinates. Unit in pixels.

    ### Returns
    - float
        - The relative focal length.
   '''
    # compute Puv, the orthogonal projection of P onto FuFv
    dirFuFv = mathutils.Vector((Fu.x - Fv.x, Fu.y - Fv.y))
    dirFuFv.normalize()
    FvP = mathutils.Vector((P.x - Fv.x, P.y - Fv.y))
    proj = dirFuFv.dot(FvP)
    Puv = Coords2D(proj * dirFuFv.x + Fv.x, proj * dirFuFv.y + Fv.y)

    PPuv = mathutils.Vector((P.x - Puv.x, P.y - Puv.y)).length
    FvPuv = mathutils.Vector((Fv.x - Puv.x, Fv.y - Puv.y)).length
    FuPuv = mathutils.Vector((Fu.x - Puv.x, Fu.y - Puv.y)).length

    fSq = FvPuv * FuPuv - PPuv * PPuv

    if (fSq <= 0):
      return None
    return sqrt(fSq)

def pixelToNormCoords2d (coords: Coords2D, imSize: (int, int)):
    return Coords2D(coords.x / imSize[0],coords.y / imSize[1])

def computeCameraRotationMatrix(Fu: Coords2D, Fv: Coords2D, f: float, P: Coords2D):
    """
    Computes the camera rotation matrix based on two vanishing points.
    Code adapted from https://github.com/stuffmatic/fSpy/blob/702189ec5acbbd2c8ba492db0e52ecb5fc908f5c/src/gui/solver/solver.ts#L336

    ### Parameters
    1. Fu : Coords2
        - the first vanishing point in normalized image coordinates.
    2. Fv : Coords2
        - the second vanishing point in normalized image coordinates.
    3. f : float
        - the relative focal length
    4. P : Coords2
        - the principal point

    ### Returns
    - mathutils.Matrix([4,4])
    """        
    OFu = mathutils.Vector((Fu.x - P.x, Fu.y - P.y, -f))
    OFv = mathutils.Vector((Fv.x - P.x, Fv.y - P.y, -f))

    s1 = OFu.length
    upRc = OFu.normalized()

    s2 = OFv.length
    vpRc = OFv.normalized()

    wpRc = upRc.cross(vpRc)

    M = mathutils.Matrix.Identity(3) 

    M[0][0] = OFu[0] / s1
    M[0][1] = OFv[0] / s2
    M[0][2] = wpRc[0]

    M[1][0] = OFu[1] / s1
    M[1][1] = OFv[1] / s2
    M[1][2] = wpRc[1]

    M[2][0] = -f / s1
    M[2][1] = -f / s2
    M[2][2] = wpRc[2]

    return M  

def solve2VP(vps: (Coords2D, Coords2D), imDimen: (int, int)):
    '''     
    Given 2 vanishing points, calculate the camera pose that corresponds with those vanishing points. 

    ### Parameters
    1. vps : Tuple[Coords2D, Coords2D]
        - An array of vanishing point locations. 
        - These locations should be given in pixel coordinates relative to the image plane, 
        with the top left corner being (0,0).
    2. imDimen : Tuple[int, int]
        - The dimensions of the image plane, in pixels. 

    ### Returns
    - TODO: fill out
    '''
    # not used - replaced w/ rotation matrix
    # pose = CameraPose(Coords3D(0.0, 0.0, 0.0), Coords3D(0.0, 0.0, 0.0), 10)

    # Code adapted from: https://github.com/stuffmatic/fSpy/blob/develop/src/gui/solver/solver.ts
    # Get principal point. Information on principal point is given here: https://fspy.io/tutorial/
    # Not entirely sure what it means, though. For now, we just assume that it's the midpoint of the image.
    # TODO: figure out what principal point is and correct it?
    principalPoint = Coords2D(imDimen.x/2, imDimen.y/2)

    #compute focal length of camera using the 3 points
    focal_length = computeFocalLength(vps[0], vps[1], principalPoint)

    # compute camera rotation
    # https://github.com/stuffmatic/fSpy/blob/702189ec5acbbd2c8ba492db0e52ecb5fc908f5c/src/gui/solver/solver.ts#L737C14-L737C14
    transformMatrix = computeCameraRotationMatrix(pixelToNormCoords2d(vps[0],imDimen), pixelToNormCoords2d(vps[1],imDimen), focal_length, Coords2D(0.5, 0.5))
    
    return transformMatrix, focal_length

############
## SCRIPT ##
############
''' User must select *first* the image, then the aligning plane, and nothing 
else, and then trigger this script. Aligning plane must be the upper plane of a cube.'''

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

rotMat,focal_length = solve2VP((Coords2D(-1000,-100), Coords2D(4000,-100)),\
     Coords2D(bpy.data.scenes[0].render.resolution_x,bpy.data.scenes[0].render.resolution_y))

# https://blender.stackexchange.com/questions/151319/adding-camera-to-scene
cam.data.lens = focal_length * 0.001
loc, rot, sca = cam.matrix_world.decompose()
cam.matrix_world = mathutils.Matrix.LocRotScale(loc, rotMat, sca)
cam.scale = mathutils.Vector((1,1,1))

# Move image to be head-on with camera
alignPlaneToCam(cam,image, 5) 
# TODO: 1 is a dummy value -- replace with the appropriate value. 
# Probably some function of original distance + original focal length and new focal length. Linearly related?