"""Measure roof and vestibule continuity of the current Cathey standalone model."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source, output = [Path(x) for x in sys.argv[sys.argv.index('--')+1:]]
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()), load_ui=False)


def tree_for(obj):
    obj.data.calc_loop_triangles()
    return BVHTree.FromPolygons(
        [obj.matrix_world @ v.co for v in obj.data.vertices],
        [tuple(t.vertices) for t in obj.data.loop_triangles], all_triangles=True)


def get_hit(tree, origin, direction, limit):
    result, _, _, _ = tree.ray_cast(Vector(origin), Vector(direction), limit)
    return [round(c, 5) for c in result] if result is not None else None


result = {}
for suffix in ('','_LOD1','_LOD2'):
    obj = bpy.data.objects['CatheyDining'+suffix]
    opaque = tree_for(obj)
    glass = bpy.data.objects.get(obj.name+'_Gls')
    glass_tree = tree_for(glass) if glass else None
    roof = [[x,y,get_hit(opaque,(x,y,30),(0,0,-1),35)]
            for x in (-23,-12,0,12,23) for y in (-3,1,7)]
    # Entry transect extends from its approach to the inner boundary
    # of the vestibule so it does not mistake an opposite glass wall for the door.
    entry = [[x,z,get_hit(opaque,(x,-17.5,z),(0,1,0),7),
              get_hit(glass_tree,(x,-17.5,z),(0,1,0),7) if glass_tree else None]
             for x in (-4,-2,0,2,4) for z in (.15,1,1.8,2.5)]
    ground = [[x,y,get_hit(opaque,(x,y,-.1),(0,0,1),1.1)]
              for x in (-3,0,3) for y in (-13.5,-12,-9,-5,4,12.5)]
    result[obj.name] = {'roof':roof,'entry_opaque_and_glass':entry,'ground_contact':ground}
output.write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'measurements':result},
                             indent=2)+'\n')
