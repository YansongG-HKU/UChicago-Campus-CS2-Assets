"""Check authored vertical contacts for the three science-library work units."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source, output = [Path(s) for s in sys.argv[sys.argv.index('--')+1:]]
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()),load_ui=False)
name = source.stem
if name.endswith("_repair"):
    name = name.removesuffix("_repair")


def tree_for(objects):
    vertices, faces = [], []
    for obj in objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        first = len(vertices)
        vertices.extend(obj.matrix_world@p.co for p in mesh.vertices)
        faces.extend(tuple(first+i for i in tri.vertices) for tri in mesh.loop_triangles)
    return BVHTree.FromPolygons(vertices,faces,all_triangles=True)


def column(tree, x, y, top, bottom):
    found = []
    origin = Vector((x,y,top))
    direction = Vector((0,0,-1))
    while origin.z > bottom and len(found)<32:
        point, normal, _, _ = tree.ray_cast(origin,direction,origin.z-bottom)
        if point is None:
            break
        found.append([round(point.z,6),round(normal.z,2)])
        origin = point+direction*.000025
    return [x,y,found]


results = {}
for suffix in ("","_LOD1","_LOD2"):
    objects = [bpy.data.objects[name+suffix]]
    glass = bpy.data.objects.get(name+suffix+"_Gls")
    if glass:
        objects.append(glass)
    tree = tree_for(objects)
    if name=="HenryHindsLaboratory":
        values = {
            "five_roof_rows": [column(tree,x,y,39,18) for x in (-5,11.9,12.1) for y in (-24,-8,8,24)],
            "open_fork_and_head": [column(tree,x,y,39,25) for x in (10.6,12.1,13.05)
                                  for y in (-24,-8,8,24)],
            "paired_ramps": [column(tree,18,y,4,-.01) for y in (-22,-18,-14,-10,-6,6,10,14,18,22)],
            "armillary": [column(tree,16.5+x,-3+y,4,1.45) for x in (-.12,-.06,0,.06,.12)
                           for y in (-.12,-.06,0,.06,.12)],
        }
    elif name=="WilliamEckhardtResearchCenter":
        values = {
            "exhaust": [column(tree,-1.5+x,y,z,35.3) for z in (42,35.73)
                        for x in (-.75,0,.75) for y in (-14,-8.4,-2.8,2.8,8.4,14)],
            "main_roof_canopies": [column(tree,x,y,42,-.02) for x,y in ((15.8,40),(9,-46.8),(9,-48),(0,0),(12,14))],
        }
    elif name=="JohnCrerarLibrary":
        values = {
            "pyramidal_lanterns": [column(tree,x,y,23,14.8)
                                   for x,y in ((3.3236,-27),(4.3236,-27),(-6.6764,15),(-7.6764,15))],
            "added_rooflights": [column(tree,2.3236,y,22,14.8) for y in (-12,-4,4,25,33)],
            "main_body": [column(tree,x,y,22,-.02) for x in (-20,-15,0,17) for y in (-30,0,30)],
        }
    else:
        raise ValueError(name)
    results[suffix or "near"] = values

output.write_text(json.dumps({"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
                              "asset":name,"tiers":results},indent=2)+"\n")
