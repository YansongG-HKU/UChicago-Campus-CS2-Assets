"""Probe the authored interface in Woodlawn's assembly and Cathey's current source pair."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

parser = argparse.ArgumentParser()
parser.add_argument('asset', choices=['cathey','woodlawn','law'])
parser.add_argument('source', type=Path)
parser.add_argument('contract', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--burton', type=Path)
parser.add_argument("--already-paired", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.open_mainfile(filepath=str(args.source.resolve()), load_ui=False)
args.output.mkdir()
contract = json.loads(args.contract.read_text())
suffixes = ('','_LOD1','_LOD2')
if args.asset == 'cathey':
    shift = Vector((0,0,0))
    if not args.already_paired:
        with bpy.data.libraries.load(str(args.burton.resolve()), link=False) as (available, loaded):
            loaded.objects = ['BurtonJudsonCourts'+suffix for suffix in suffixes]
        for item in loaded.objects:
            bpy.context.scene.collection.objects.link(item)
        shift = Vector(contract['baseline_fit']['translation'])
    segments = [{'anchor_common_m':[6.3,-29.3,2.4], 'tangent_xyz':[1,0,0],
                 'outward_normal_xyz':[0,1,0], 'width_m':10, 'height_m':4.8}]
    names = ('CatheyDining','BurtonJudsonCourts')
elif args.asset == 'woodlawn':
    segments = contract['joint_segments']
    shift = Vector((0,0,0))
    names = ('WoodlawnDining','WoodlawnResidential')
else:
    segments = [
        {'anchor_common_m': j['assembly_anchor_m'], 'tangent_xyz': j['tangent'],
         'width_m': j['width_m'], 'height_m': j['height_m'],
         'outward_normal_xyz': j['outward_normals'][0]} for j in contract['joints']
    ]
    shift = Vector((0,0,0))
    names = ('LawClassroomAdministration','DAngeloLawLibrary')


def build_tree(obj, extra_translation):
    mesh = obj.data
    mesh.calc_loop_triangles()
    verts = [obj.matrix_world @ v.co + extra_translation for v in mesh.vertices]
    return BVHTree.FromPolygons(
        verts, [tuple(t.vertices) for t in mesh.loop_triangles], all_triangles=True)


def hits(tree, point, direction):
    start = point-1.6*direction
    results = []
    for _ in range(12):
        found, norm, _, _ = tree.ray_cast(start,direction,3.2-(start-(point-1.6*direction)).length)
        if found is None:
            break
        results.append([round((found-point).dot(direction),6),round(norm.dot(direction),6)])
        start = found + .00002*direction
    return results


scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.use_nodes = False
scene.render.resolution_x = 1050
scene.render.resolution_y = 790
scene.render.resolution_percentage = 100
scene.display.shading.color_type = 'OBJECT'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
camera = bpy.data.objects.new('QA camera', bpy.data.cameras.new('QA camera'))
scene.collection.objects.link(camera)
scene.camera = camera
camera.data.type = 'ORTHO'
camera.data.clip_end = 1000
measures = {}
for suffix in suffixes:
    objs = [bpy.data.objects[name+suffix] for name in names]
    trees = [build_tree(obj, shift if i==0 else Vector((0,0,0))) for i,obj in enumerate(objs)]
    samples = []
    for i, segment in enumerate(segments):
        center = Vector(segment['anchor_common_m'])
        tangent = Vector(segment['tangent_xyz'])
        direction = Vector(segment['outward_normal_xyz'])
        for s in (-.4,-.2,0,.2,.4):
            for z in (.05,1.0,1.8,3.6,4.2):
                point = center + s*segment['width_m']*tangent
                point.z = z
                samples.append({'segment':i+1,'fraction':s,'z':z,
                                'hits':{name:hits(tree,point,direction) for name,tree in zip(names,trees)}})
    measures[suffix or 'near'] = samples
    visible = set(obj.name for obj in objs)
    if args.asset == 'law':
        water = bpy.data.objects[names[0]+suffix+'_Wat']
        water.color = (.35,.54,.65,1)
        visible.add(water.name)
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.hide_render = obj.name not in visible
    if args.asset == 'cathey':
        objs[0].location += shift
        target = Vector((6,-48,12))
        camera.data.ortho_scale = 97
    elif args.asset == 'woodlawn':
        target = Vector((4,-8,15))
        camera.data.ortho_scale = 138
    else:
        target = Vector((6,21,8))
        camera.data.ortho_scale = 145
    objs[0].color = (.66,.73,.57,1)
    objs[1].color = (.69,.64,.57,1)
    camera.location = target + Vector((-.4,-1,.7)).normalized()*250
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath = str(args.output/f'pair{suffix or "_near"}.png')
    bpy.ops.render.render(write_still=True)

report = {'source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(), 'rays':measures}
if args.burton:
    report['burton_source_sha256'] = hashlib.sha256(args.burton.read_bytes()).hexdigest()
(args.output/'pair-rays.json').write_text(json.dumps(report,indent=2)+'\n')
