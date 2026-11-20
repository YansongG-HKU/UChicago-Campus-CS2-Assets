"""Check the Keller canopy supports and named roof elements in the locked source."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source,output = [Path(s) for s in sys.argv[sys.argv.index('--')+1:]]
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()),load_ui=False)
columns = [(x,sign*19.2) for x in (-38.4+3.2*i for i in range(25)) for sign in (-1,1)]
columns += [(sign*38.4,y) for y in (-19.2+3.2*i for i in range(1,12)) for sign in (-1,1)]


def tree_for(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in mesh.vertices],
        [tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)


def cast(tree, origin, direction, limit):
    point,_,_,_ = tree.ray_cast(Vector(origin),Vector(direction),limit)
    return [round(float(c),5) for c in point] if point is not None else None


rows={}
for suffix in ('','_LOD1','_LOD2'):
    name='KellerCenter'+suffix
    tree=tree_for(bpy.data.objects[name])
    rows[name] = {
        'supports': [[x,y,cast(tree,(x,y,2),(0,0,-1),2.1),
                     cast(tree,(x,y,2),(0,0,1),14)] for x,y in columns],
        'roof': [[label,x,y,cast(tree,(x,y,25),(0,0,-1),25)] for label,x,y in
                 [('sky_suite',0,12),('service_west',-18,0),('service_east',18,0),
                  ('glazed_teeth_west',-24,0),('glazed_teeth_center',0,0),
                  ('glazed_teeth_east',24,0),('solar_west',-32,0),
                  ('solar_south',0,-13),('vegetation',-21,12)]],
    }
output.write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                              'measurements':rows},indent=2)+'\n')
