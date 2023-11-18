# This is where I'm testing scripts.

import bpy

scene = bpy.context.scene
for obj in scene.objects:
    obj.location.x += 1.0