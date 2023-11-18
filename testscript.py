# Scripts to test go here.

import bpy

scene = bpy.context.scene
for obj in scene.objects:
    obj.location.x += 1.0