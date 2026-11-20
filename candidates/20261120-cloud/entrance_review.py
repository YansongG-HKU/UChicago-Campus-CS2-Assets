"""Measure LODs and render each at fixed positions in headless Blender."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("asset", choices=["baker", "baker-standalone", "billings", "levi", "lying-in"])
parser.add_argument('--measure-only', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
args.output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(args.source.resolve()), load_ui=False)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.use_nodes = False
scene.render.resolution_x = 1000
scene.render.resolution_y = 750
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.single_color = (0.67, 0.66, 0.62)
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
camera = bpy.data.objects.new('QA_camera', bpy.data.cameras.new('QA_camera'))
scene.collection.objects.link(camera)
scene.camera = camera
camera.data.type = 'ORTHO'
camera.data.clip_end = 1000

views = {
    'baker': [('campus', (0,0,15), (-.4,-.8,1.1), 170),
              ('seam', (-7,37,5.8), (0,-.9,.8), 47),
              ('court-plan', (-18,22,5), (0,0,1), 89)],
    'baker-standalone': [('roof', (0,0,4), (-.5,.9,.8), 104),
                         ('roof-plan', (0,0,4), (0,0,1), 104)],
    'billings': [('south', (0,-18,18), (0,-1,.12), 75),
                 ('south-entry', (0,-17,1.3), (1,-2,.9), 14),
                 ('court', (0,0,15), (-.5,.4,1), 125)],
    'levi': [('west-entry', (0,0,4.4), (-2,.15,.22), 20),
             ('east-entry', (0,0,4.4), (2,-.15,.22), 20),
             ('northwest', (0,0,13), (-1,1,.56), 90)],
    'lying-in': [('west-entry', (-30,-2,5), (-1,0,.22), 26),
                 ('southwest', (0,0,16), (-1,-1,.65), 95),
                 ('court', (0,0,16), (-.5,.5,1), 100)],
}
prefixes = {
    'baker': ['BakerDining', 'CampusNorthResidential'],
    'baker-standalone': ['BakerDining'],
    'billings': ['BillingsHospital'],
    'levi': ['EdwardHLeviHall'],
    'lying-in': ['ChicagoLyingIn'],
}


def geometry_tree(objects):
    vertices, faces = [], []
    for obj in objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        offset = len(vertices)
        vertices.extend(obj.matrix_world @ v.co for v in mesh.vertices)
        faces.extend(tuple(offset + i for i in tri.vertices) for tri in mesh.loop_triangles)
    return BVHTree.FromPolygons(vertices, faces, all_triangles=True)


def ray(tree, origin, direction, distance):
    hit, _, _, _ = tree.ray_cast(Vector(origin), Vector(direction), distance)
    return [round(v, 5) for v in hit] if hit is not None else None


all_rows = {}
for suffix in ('', '_LOD1', '_LOD2'):
    names = [p + suffix for p in prefixes[args.asset]]
    visible = set(names)
    if args.asset == 'levi' and suffix != '_LOD2':
        visible.add(names[0] + '_Gls')
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.hide_render = obj.name not in visible
    tree = geometry_tree([bpy.data.objects[n] for n in names])
    measurements = {}
    if args.asset == 'billings':
        measurements['tread'] = [
            [x,y,ray(tree,(x,y,2),(0,0,-1),2.1)]
            for x in (-2,-1,0,1,2) for y in (-18.55,-18.1,-17.7,-17.25)
        ]
        measurements['riser_and_entrance'] = [
            [x,z,ray(tree,(x,-23,z),(0,1,0),9)]
            for x in (-2,-1,0,1,2) for z in (.05,.15,.35,.60,.7,1.8,4.5)
        ]
        measurements['tower_roofs'] = [
            [x,y,ray(tree,(x,y,65),(0,0,-1),30)]
            for cx in (-23,23) for x in (cx-5,cx,cx+5) for y in (-21,-16,-11)
        ]
    if args.asset == 'levi':
        through = geometry_tree([bpy.data.objects[name] for name in visible])
        measurements['portal_clearance'] = [
            [y,z,ray(through,(-13,y,z),(1,0,0),26)]
            for y in (-2,-1,0,1,2) for z in (1,1.8,2.5,4,6)
        ]
        measurements['walkway_floor'] = [
            [x,y,ray(tree,(x,y,.87),(0,0,-1),.9)]
            for x in range(-10,11) for y in (-2,0,2)
        ]
    if args.asset == 'lying-in':
        # The authored source shifts Y by +1 m; the cloister runs -24..-18 m.
        # The short ray spans both of its facades and stops before the far range.
        measurements['five_arches'] = [
            [x, z, ray(tree, (x,-25,z), (0,1,0), 8)]
            for x in (-15.4,-11.2,-7,-2.8,1.4) for z in (1,1.8,3,4.5)
        ]
        measurements['pier_feet'] = [
            [x, ray(tree, (x,-25,.05), (0,1,0), 2)]
            for x in (-17.5,-13.3,-9.1,-4.9,-.7,3.5)
        ]
        measurements['tower_roof'] = [
            [x,y,ray(tree,(x,y,55),(0,0,-1),30)]
            for x in (-16,-12.5,-9) for y in (8,12,16)
        ]
    all_rows[suffix or 'near'] = measurements
    if args.measure_only:
        continue
    for view, target, direction, scale in views[args.asset]:
        focus = Vector(target)
        camera.location = focus + Vector(direction).normalized()*250
        camera.rotation_euler = (focus - camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.ortho_scale = scale
        scene.render.filepath = str(args.output / f"{view}{suffix or '_near'}.png")
        bpy.ops.render.render(write_still=True)

(args.output / 'measurements.json').write_text(json.dumps({
    'sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(), 'asset': args.asset, 'measurements': all_rows,
}, indent=2) + '\n')
