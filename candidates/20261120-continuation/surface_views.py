"""Orthographic depth/face-orientation views of the current registered Blender meshes.

Geometry-only evidence: source coordinates and BVH triangle intersections.
Orange marks an observed back-facing triangle; blue marks an actual _Gls/_Wat mesh.
These views do not aim to model materials, shadows, or runtime fades.
"""
import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("root", type=Path)
parser.add_argument("plan", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--size", type=int, default=128)
parser.add_argument("--families", nargs="+")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
plan = json.loads(args.plan.read_text())
args.output.mkdir(parents=True,exist_ok=True)
report = {}
cached_path = None
for name in args.families or plan:
    row = plan[name]
    path = args.root/row["source"]
    if path != cached_path:
        bpy.ops.wm.open_mainfile(filepath=str(path.resolve()),load_ui=False)
        cached_path = path
    tier_names = [
        [name,*[key for key in (name+"_Gls",name+"_Wat",name+"_Win") if key in bpy.data.objects]],
        [name+"_LOD1",*[name+"_LOD1_"+k for k in ("Gls","Wat","Win") if name+"_LOD1_"+k in bpy.data.objects]],
        [name+"_LOD2",*[name+"_LOD2_"+k for k in ("Gls","Wat","Win") if name+"_LOD2_"+k in bpy.data.objects]],
    ]
    opaque = [bpy.data.objects.get(t[0]) for t in tier_names]
    if opaque[0] is None:
        report[name] = {"status":"missing exact main", "available":sorted(o.name for o in bpy.data.objects if o.type=="MESH")}
        continue
    points = [obj.matrix_world@Vector(p) for obj in opaque if obj for p in obj.bound_box]
    lo = Vector([min(p[i] for p in points) for i in range(3)])
    hi = Vector([max(p[i] for p in points) for i in range(3)])
    center = (lo+hi)/2
    span = max((hi-lo).length, 1)
    stats = []
    rgb = np.full((args.size*3,args.size*3,3),(25,31,39),dtype=np.uint8)
    for tier, names in enumerate(tier_names):
        if opaque[tier] is None:
            stats.append(None)
            continue
        verts, faces, dark = [], [], []
        for i,obj_name in enumerate(names):
            obj = bpy.data.objects[obj_name]
            mesh = obj.data
            mesh.calc_loop_triangles()
            first = len(verts)
            verts.extend(obj.matrix_world@p.co for p in mesh.vertices)
            faces.extend(tuple(first+k for k in p.vertices) for p in mesh.loop_triangles)
            dark.extend([i>0]*len(mesh.loop_triangles))
        tree = BVHTree.FromPolygons(verts,faces,all_triangles=True)
        hits_per_view = []
        for view,d in enumerate(((1,-1,.75),(-1,1,.65),(0,0,1))):
            outward = Vector(d).normalized()
            right = Vector((0,0,1)).cross(outward)
            if right.length<.01:
                right = Vector((1,0,0))
            right.normalize()
            up = outward.cross(right).normalized()
            width = max(max(abs((p-center).dot(axis)) for p in points)*2 for axis in (right,up))*1.11
            viewport = center+outward*span
            rows = []
            for y in range(args.size):
                start = viewport+up*((.5-(y+.5)/args.size)*width)-right*(width/2)
                rows.append(start)
            steps = [right*((x+.5)/args.size*width) for x in range(args.size)]
            covered = back = additional = 0
            light = (outward*.8 + up*.55 - right*.24).normalized()
            for y,start in enumerate(rows):
                for x,step in enumerate(steps):
                    point, normal, i, length = tree.ray_cast(start+step,-outward,3*span)
                    if i is None:
                        continue
                    covered += 1
                    shade = .48 + .46 * max(0,normal.dot(light))
                    if normal.dot(outward) < -.001:
                        base = (237,153,87)
                        back += 1
                    elif dark[i]:
                        base = (127,194,236)
                        additional += 1
                    else:
                        base = (224,228,226)
                    rgb[tier*args.size+y,view*args.size+x] = [int(v*shade) for v in base]
            hits_per_view.append({"covered_pixels":covered,"first_hit_backface_pixels":back,"glass_or_water_pixels":additional})
        stats.append({"triangles":len(faces),"view_stats":hits_per_view})
    output = args.output/f"{name}.ppm"
    with output.open("wb") as img:
        img.write(f"P6\n{rgb.shape[1]} {rgb.shape[0]}\n255\n".encode())
        img.write(rgb.tobytes())
    report[name] = {"source":row["source"],"tiers":stats}
    (args.output/"views.json").write_text(json.dumps(report,indent=2)+"\n")
    print(name,flush=True)
