import bpy
import math
import numpy as np
from mathutils import Vector
import os
import sys

modelpath = sys.argv[6]
top_png_path = sys.argv[7]
front_png_path = sys.argv[8]
left_png_path = sys.argv[9]

bpy.ops.import_scene.obj(filepath = modelpath)

# Top view
bpy.data.scenes['Scene'].render.filepath = top_png_path
camera = bpy.data.objects['Camera']
camera.location = (0, 0, 3)
camera.rotation_euler = (0,0,0)
bpy.context.scene.camera = camera

bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links
for n in tree.nodes:
    tree.nodes.remove(n)
rl = tree.nodes.new(type="CompositorNodeRLayers")
composite = tree.nodes.new(type="CompositorNodeComposite")
links.new(rl.outputs['Depth'], composite.inputs['Image'])
scene = bpy.context.scene
scene.view_layers['RenderLayer'].use_pass_mist = True
scene.world.mist_settings.start = 1
scene.world.mist_settings.depth = 5
links.new(rl.outputs['Mist'], composite.inputs['Image'])

print('rendering')
bpy.ops.render.render( write_still=True)
print('rendered')


# Front
bpy.data.scenes['Scene'].render.filepath = front_png_path
camera = bpy.data.objects['Camera']
camera.location = (0, -3, 0)
camera.rotation_euler = (math.radians(90),0,0)
bpy.context.scene.camera = camera

bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links
for n in tree.nodes:
    tree.nodes.remove(n)
rl = tree.nodes.new(type="CompositorNodeRLayers")
composite = tree.nodes.new(type="CompositorNodeComposite")
links.new(rl.outputs['Depth'], composite.inputs['Image'])
scene = bpy.context.scene
scene.view_layers['RenderLayer'].use_pass_mist = True
scene.world.mist_settings.start = 1
scene.world.mist_settings.depth = 5
# scene.world.mist_settings.intensity = 1
links.new(rl.outputs['Mist'], composite.inputs['Image'])

print('rendering')
bpy.ops.render.render( write_still=True)
print('rendered')

# Left
bpy.data.scenes['Scene'].render.filepath = left_png_path
camera = bpy.data.objects['Camera']
camera.location = (-3, 0, 0)
camera.rotation_euler = (math.radians(90),0,math.radians(-90))
bpy.context.scene.camera = camera

bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links
for n in tree.nodes:
    tree.nodes.remove(n)
rl = tree.nodes.new(type="CompositorNodeRLayers")
composite = tree.nodes.new(type="CompositorNodeComposite")
links.new(rl.outputs['Depth'], composite.inputs['Image'])
scene = bpy.context.scene
scene.view_layers['RenderLayer'].use_pass_mist = True
scene.world.mist_settings.start = 1
scene.world.mist_settings.depth = 5
links.new(rl.outputs['Mist'], composite.inputs['Image'])

print('rendering')
bpy.ops.render.render( write_still=True)
print('rendered')

sys.exit(0) # exit python and blender
print('exited')
