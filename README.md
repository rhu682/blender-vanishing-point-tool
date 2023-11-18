# blender-vanishing-point-tool
A Blender Addon to automatically calculate perspective from vanishing points.

# TODO
## Workflow draft:
[X] Import image as plane - We are not implementing this; the user has to do it themselves.
[ ] Align viewport to be orthographically aligned with image
[ ] make a plane and align to a perspective in the image
[ ] select image and plane and hit an operator
[ ] do vanishing point and camera calculations (seperate function, requires math)
[ ] set camera to the calculated pose data and move the image to be head on with camera