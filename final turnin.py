import bpy
import bpy_extras
import mathutils
from collections import namedtuple
import math

###########
# AUTHORS #
###########
# Rohan Huang: bhuang@g.hmc.edu
# YJ Tsai: sstsai@g.hmc.edu
# 
# Code for FA23 CS155 final project taught by Professor Carter Slocum.



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
def getNewDist(origDist: float, origFocalLength: float, newFocalLength: float):
    ''' Given an image that is some distance to the camera, and a camera that changes focal lengths,
    returns the new distance the image should be to the camera.'''
    return newFocalLength / (origFocalLength / origDist)

def line_intersection(line1, line2):
    ''' 
    code from https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
    '''
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

def VPfromAligner(cam, aligner):
    '''
    Given a plane with 4 vertices, calculates the 2 "vanishing points" from the plane in 2D image plane coordinates.

    ### Parameters
    1. camera : bpy.types.object
        - the camera object
    2. aligner : bpy.types.object
        - the alignin plane

    ### Returns
    - (Coords2D, Coords2D)
        - The two vanishing points in image plane pixel coordinates.
    '''
    bpy.context.view_layer.update()
    
    # project all points to 2d image plane coords
    normCoord = [Coords2D(0.0, 0.0) for x in range(4)]
    i = 0
    for vert in aligner.data.vertices:
        coord = aligner.matrix_world @ vert.co
        normCoord[i] = bpy_extras.object_utils.world_to_camera_view(bpy.context.scene,cam,coord)
        i += 1

    # scale points to pixel coordinates instead of norm coordinates
    pixCoord = [Coords2D(0.0, 0.0) for x in range(4)]
    for j in range(4):
        pixCoord[j] = Coords2D(normCoord[j][0] * bpy.context.scene.render.resolution_x,
                                normCoord[j][1] * bpy.context.scene.render.resolution_y)

    
    # calculate intersection from both pairs of parallel lines.
    vp = [Coords2D(0.0, 0.0) for x in range(2)]
    # line 0-1 with line 2-3
    x,y = line_intersection([pixCoord[0], pixCoord[1]],[pixCoord[2], pixCoord[3]])
    vp[0] = Coords2D(x,y)
    # line 0-2 with line 1-3
    x,y = line_intersection([pixCoord[0], pixCoord[2]],[pixCoord[1], pixCoord[3]])
    vp[1] = Coords2D(x,y)

    return vp

def VPfromCam(cam):
    '''
    Given a camera, calculates the 2 x-y "vanishing points" 2D image plane coordinates.

    fill out params
    ### Parameters

    ### Returns
    - (Coords2D, Coords2D)
        - The two vanishing points in image plane pixel coordinates.
    '''
    bpy.context.view_layer.update()

    # get the 2d coordinates of a plane flat on the ground
    planeVertices = [mathutils.Vector((1,0,0)), mathutils.Vector((0,0,0)), mathutils.Vector((1,1,0)), mathutils.Vector((0,1,0))]
    normCoord = [Coords2D(0.0, 0.0) for x in range(4)]
    i = 0
    for i in range(4):
        normCoord[i] = bpy_extras.object_utils.world_to_camera_view(bpy.context.scene,cam,planeVertices[i])

    # scale points to pixel coordinates instead of norm coordinates
    pixCoord = [Coords2D(0.0, 0.0) for x in range(4)]
    for j in range(4):
        pixCoord[j] = Coords2D(normCoord[j][0] * bpy.context.scene.render.resolution_x,
                                normCoord[j][1] * bpy.context.scene.render.resolution_y)

    vp = [Coords2D(0.0, 0.0) for x in range(2)]
    
    # calculate intersection from both pairs of parallel lines.
    # line 0-1 with line 2-3
    x,y = line_intersection([pixCoord[0], pixCoord[1]],[pixCoord[2], pixCoord[3]])
    vp[0] = Coords2D(x,y)
    # line 0-2 with line 1-3
    x,y = line_intersection([pixCoord[0], pixCoord[2]],[pixCoord[1], pixCoord[3]])
    vp[1] = Coords2D(x,y)
    return vp

def midpoint2D(p1, p2):
    # midpoint of 2 Coord2Ds
    return Coords2D(p2.x - p1.x / 2, p2.y - p1.y / 2)

def computeFocalLength(Fu: Coords2D, Fv: Coords2D, P: Coords2D):
    '''
   Computes the focal length based on two vanishing points and a center of projection.

   Formula given by Prof Slocum.
   
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
    vanishV = mathutils.Vector(Fv)
    vanish2V = mathutils.Vector(Fu)
    principalV = mathutils.Vector(P)
    fSq = (-(vanish2V - principalV)).dot(vanishV - principalV) 

    if (fSq <= 0):
      return None
    return math.sqrt(fSq)

def camToVP(vps, image, cam, error, max_iter = 1000):
    '''
    Given a camera with focal length already calculated and given vanishing points, 
    adjusts the y and x rotation of the camera and image to better align with the vanishing points.
    
    The camera must be parented to the image.

    ### Parameters
    1. vps : Tuple[Coords2d, Coords2d]
        - The vanishing points of the image in pixel image plane coordinates.
    2. image : bpy.types.object
        - The plane of the image we are aligning to.
    2. cam : bpy.types.object
        - The camera we are aligning.
    2. error : int
        - The biggest acceptable error in pixel coordinates.
    2. max_iter : int, (default 1000)
        - The maximum number of iterations allowed in adjusting.

    ### Returns
    - None
    '''
    # make sure the blender world vanishing points are in view
    image.rotation_euler[2] = math.radians(45.0)

    # get midpoints of vanishing points
    v1 = vps[0]
    v2 = vps[1]
    vMid = midpoint2D(v1, v2)

    # set y rotation from horizon line
    y_rot = math.atan2(v2.y - v1.y, v2.x - v1.x)
    image.rotation_euler[1] = y_rot

    # get the world vanishing points based on camera position and midpoint
    camVP = VPfromCam(cam)
    camMid = midpoint2D(camVP[0], camVP[1])

    iter = 0
    dist = camMid.y - vMid.y # unit is pixels

    # until we are within an accepted error, loop and adjust x rotation, 
    # which is linked to the y position of the image plane
    while (abs(dist) > error and iter < max_iter):
        # adjust by rotating it by 1 degree
        if dist > 0:
            image.rotation_euler[0] += math.radians(1)
        else:
            image.rotation_euler[0] -= math.radians(1)

        # update
        camVP = VPfromCam(cam)
        camMid = midpoint2D(camVP[0], camVP[1])
        dist = camMid.y - vMid.y
        iter += 1
    return

def worldCoordofPix(coordinate, cam):
    '''
    converts from Blender world coordinates to image coordinates
    
    ### Parameters
    1. coordinate: Coords2D
        - The coordinates of image plane in Blender world units
    2. cam : bpy.types.object
        - The camera we are aligning.
    
    ### Returns
        returns a 3D vector
    '''
    # get 4 corners of camera frame as vectors
    camFrame = cam.data.view_frame()

    # convert coordinate from pixel coordinates to relative coordinates
    relCoord = Coords2D(coordinate.x / bpy.context.scene.render.resolution_x,
                        coordinate.y / bpy.context.scene.render.resolution_y)
    
    # lerp top edge
    topEdge = camFrame[3].lerp(camFrame[0], relCoord.x)
    # lerp bottom edge
    bottomEdge = camFrame[2].lerp(camFrame[1], relCoord.x)
    
    # lerp results of previous two lerps and return
    return topEdge.lerp(bottomEdge, relCoord.y)


def pixelToNormCoords2d (coords: Coords2D, imSize: (int, int)):
    '''Converts coordinates in image pixel coordinates (0, image_width/height) to normalized coordinates (0,1)'''
    return Coords2D(coords.x / imSize[0],coords.y / imSize[1])


def solve2VP(vps: (Coords2D, Coords2D), imDimen: (int, int)):
    '''     
    Given 2 vanishing points, calculate the focal length that corresponds with those vanishing points. 

    ### Parameters
    1. vps : Tuple[Coords2D, Coords2D]
        - An array of vanishing point locations. 
        - These locations should be given in pixel coordinates relative to the image plane, 
        with the top left corner being (0,0).
    2. imDimen : Tuple[int, int]
        - The dimensions of the image plane, in pixels. 

    ### Returns
    - float
        - The focal length.
    '''
    # Code adapted from: https://github.com/stuffmatic/fSpy/blob/develop/src/gui/solver/solver.ts
    # Get principal point. Information on principal point is given here: https://fspy.io/tutorial/
    # We assume that it's the midpoint of the image.
    principalPoint = Coords2D(imDimen.x/2, imDimen.y/2)

    #compute focal length of camera using the 3 points
    focal_length = computeFocalLength(vps[0], vps[1], principalPoint)

    return focal_length

############
## SCRIPT ##
############
''' User must select *first* the image, then the aligning plane, and nothing 
else, and then trigger this script. Aligning plane must be the upper plane of a cube.
Image must be the parent of camera such that its distance to the camera is determined solely by the camera's z location.
Camera must be head-on to the image.'''

scene = bpy.context.scene

# Get image and plane data from selected objects.
aligner = bpy.context.active_object

# Verify that only 2 objects are selected.
if len(bpy.context.selected_objects) != 2:
    raise RuntimeError("Expected exactly two objects to be selected.")

if bpy.context.selected_objects[0] == aligner:
    image = bpy.context.selected_objects[1]
else:
    image = bpy.context.selected_objects[0]

# Get camera
cam = scene.camera
if cam == None:
    raise RuntimeError("No active camera.")

# Get distance from camera to image
origDist = cam.location[2]
origFocalLength = cam.data.lens

# transform aligner data and pass it to vanishing point calculation function
vanishingPoints = VPfromAligner(cam, aligner)
focal_length = solve2VP(vanishingPoints,\
     Coords2D(bpy.data.scenes[0].render.resolution_x,bpy.data.scenes[0].render.resolution_y))

# Correct units of camera focal length
cam.data.lens = focal_length / 100

# adjust distance of image to camera
newDist = getNewDist(origDist, origFocalLength, cam.data.lens)
cam.location[2] = newDist

# adjust rotation of camera
camToVP(vanishingPoints, image, cam, 10)