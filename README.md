# Blender Vanishing Point Tool
A Blender Addon to automatically calculate perspective from vanishing points.

This is a class project for CS155 FA23.

# TODO
## Workflow draft:
- [X] Import image as plane - We are not implementing this; the user has to do it themselves.
- [X] make a plane and align to a perspective in the image
- [X] select image and plane and hit an operator
- [ ] do vanishing point and camera calculations (seperate function, requires math) (function solve2VP in testscript.py)
- [X] set camera to the calculated pose data and move the image to be head on with camera

## Stretch goals:
- [ ] Incorporation "importing image as plane" into our addon
- [ ] Make it so that we don't neccessarily have to be orthographic to run this script - what if the image is not axis-aligned?
    - [ ] Have operator automatically create a camera "head-on" with the selected image
    - [ ] Have all calculations take place relative to the camera, not necessarily to x-axis
- [ ] alignPlaneToCam() presumes that the image is a plane facing the x-axis. What if it isn't? Implement it differently to account for different directions (check the plane's normal and use that instead of the x-axis)
- [ ] add functionality for 1 and 3 point perspective
- [ ] add some fancy blender UI stuff with lines so that we don't have to use a plane

## TODO
- [ ] Convert aligning plane data to relative 2D coordinates wrt image plane
- [ ] Finish solve2VP
- [ ] Realign image with camera
- [ ] Move testscript.py stuff to `_init_` and turn it into an addon
- [X] Study vanishing point to camera pose calculations

# Resources/References
- Textbook: [Multiple View Geometry in Computer Vision](https://github.com/DeepRobot2020/books/blob/master/Multiple%20View%20Geometry%20in%20Computer%20Vision%20(Second%20Edition).pdf) Section 8.6.1
- [fSpy](https://fspy.io/)
- [Camera Position Tutorial](https://www.fxphd.com/tips/finding-the-cameras-position-tutorial/)
- [Blender Addon Tutorial](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html)
- [Blender Real Camera Addon](https://gitlab.com/marcopavanello/real-camera) (use this as reference for addons)
- [Camera Calibration using Perspective Views of Rectangles](https://github.com/mrossini-ethz/camera-calibration-pvr)