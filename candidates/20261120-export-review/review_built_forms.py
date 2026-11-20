"""Compare Booth far exports and measure the Smart/Cochrane garden interfaces."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['booth','smart-pair'])
parser.add_argument('source', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--old-fbx', type=Path)
parser.add_argument('--new-fbx', type=Path)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
args.output.mkdir()


def tree_for(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in mesh.vertices],
                                [tuple(t.vertices) for t in mesh.loop_triangles],
                                all_triangles=True)


def hit(tree, origin, direction, limit):
    point, normal, _, _ = tree.ray_cast(Vector(origin), Vector(direction), limit)
    return [list(point),list(normal)] if point is not None else None


def render(name, target, direction, scale, visible):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.use_nodes = False
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 820
    scene.render.resolution_percentage = 100
    scene.display.shading.color_type = 'SINGLE'
    scene.display.shading.single_color = (.69,.68,.63)
    scene.display.shading.show_cavity = True
    scene.display.shading.show_shadows = True
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.hide_render = obj.name not in visible
    camera = bpy.data.objects.new('Review camera '+name,bpy.data.cameras.new('Review camera '+name))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = scale
    camera.data.clip_end = 1000
    target = Vector(target)
    camera.location = target + Vector(direction).normalized()*250
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath = str(args.output/(name+'.png'))
    bpy.ops.render.render(write_still=True)


data = {}
bpy.ops.wm.open_mainfile(filepath=str(args.source.resolve()), load_ui=False)
if args.mode == 'booth':
    for suffix in ('','_LOD1','_LOD2'):
        name = 'BoothHarperCenter'+suffix
        ob = bpy.data.objects[name]
        solid = tree_for(ob)
        aperture = bpy.data.objects.get(name+'_Gls')
        glass = tree_for(aperture) if aperture else None
        data[name] = {
            'four_roof_quarters': [
               [x,y,hit(solid,(x,y,45),(0,0,-1),46),
                hit(glass,(x,y,45),(0,0,-1),46) if glass else None]
               for x in (-8,-4,4,8) for y in (-8,-4,4,8)],
            'west_entry': [
               [y,z,hit(solid,(-55,y,z),(1,0,0),17),
                hit(glass,(-55,y,z),(1,0,0),17) if glass else None]
               for y in (-1,0,1) for z in (.05,1.6,2,2.8,3.8)],
        }
    for name, path in [('public_far',args.old_fbx),('reexport_far',args.new_fbx)]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(path.resolve()),use_image_search=False)
        render(name,(0,0,12),(-.8,-1,.68),145,{'BoothHarperCenter_LOD2'})
else:
    for suffix in ('','_LOD1','_LOD2'):
        museum, center = ('SmartMuseum'+suffix,'CochraneWoods'+suffix)
        museum_tree = tree_for(bpy.data.objects[museum])
        center_tree = tree_for(bpy.data.objects[center])
        data[suffix or 'near'] = {
            'joins': [
                [x,z,hit(museum_tree,(x,18,z),(0,-1,0),4),hit(center_tree,(x,14,z),(0,1,0),4)]
                for cx in (-19.5,19.5) for x in (cx-.8,cx,cx+.8) for z in (.05,1,2,3.8)],
            'garden_passage': [
                [side,y,z,hit(center_tree,(side*23,y,z),(-side,0,0),8)]
                for side in (-1,1) for y in (24.5,26.5,28.5) for z in (.2,1,1.8,2.5,3.8)],
            'roof_anchors': [
                [mesh,x,y,hit(tree,(x,y,22),(0,0,-1),23)]
                for mesh,tree,anchors in [(museum,museum_tree,[(-16,1),(0,2),(12,5)]),
                                          (center,center_tree,[(-18,47),(0,47),(18,47)])]
                for x,y in anchors],
        }
        render('garden'+(suffix or '_near'),(0,25,4),(-.5,-.7,1.2),99,{museum,center})
(args.output/'geometry.json').write_text(json.dumps(
    {'source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'data':data},indent=2)+'\n')
