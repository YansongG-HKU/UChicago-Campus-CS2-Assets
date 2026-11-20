"""Measure the repaired north facade and render the same detail in both files."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

before, after, output = map(Path, sys.argv[sys.argv.index('--')+1:])
output.mkdir()
results = {}
for label, src in (('before', before), ('after', after)):
    bpy.ops.wm.open_mainfile(filepath=str(src.resolve()), load_ui=False)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.use_nodes = False
    scene.render.resolution_x = 1050
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.display.shading.color_type = 'SINGLE'
    scene.display.shading.single_color = (.72,.73,.70)
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    camera = bpy.data.objects.new('QA camera', bpy.data.cameras.new('QA camera'))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 23
    target = Vector((16.8,55.48,8.5))
    camera.location = (35.4,61,12.1)
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    data = {}
    for suffix in ('','_LOD1'):
        name = 'CampusNorthResidential'+suffix
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.hide_render = obj.name != name
        mesh = bpy.data.objects[name].data
        mesh.calc_loop_triangles()
        verts = [v.co for v in mesh.vertices]
        tree = BVHTree.FromPolygons(verts, [tuple(t.vertices) for t in mesh.loop_triangles], all_triangles=True)
        rows = {}
        for feature, x0, z0 in [('pier', 22.214, 5.5), ('band',20.343,10.25)]:
            scans = []
            for bay in range(4):
                for x_shift in (-.06,0,.06):
                    x = x0 - bay * 3.741964 + x_shift
                    origin = Vector((x,56.9,z0))
                    direction = Vector((0,-1,0))
                    hits = []
                    for _ in range(8):
                        p,n,_,_ = tree.ray_cast(origin,direction,2.1)
                        if p is None or p.y < 55.4:
                            break
                        hits.append([round(p.y,6),round(n.y,6)])
                        origin = p + direction * .00002
                    scans.append({'x':x,'z':z0,'hits_y_normal_y':hits})
            rows[feature] = scans
        data[name] = rows
        scene.render.filepath = str(output/f'{label}{suffix or "_near"}.png')
        bpy.ops.render.render(write_still=True)
    results[label] = {'source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'levels':data}
(output/'north-facade-rays.json').write_text(json.dumps(results, indent=2)+'\n')
