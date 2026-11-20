"""Measure paired ends and standing envelopes of the two historical groups."""
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source, document, target = [Path(v) for v in sys.argv[sys.argv.index('--')+1:]]
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()),load_ui=False)
record = json.loads(document.read_text())
if "joint_records" in record:
    segments = []
    used = set()
    for item in record["joint_records"]:
        owners = item["owner"],item["counterpart"]
        if frozenset(owners) in used:
            continue
        used.add(frozenset(owners))
        segments.append((item["id"],owners,item["position_xyz_m"],item["outward_normal_xyz"],4,15))
else:
    mapping = {"Mitchell_Hutchinson":(("MitchellTower","HutchinsonCommons"),4,13),
               "Mitchell_Reynolds":(("MitchellTower","ReynoldsClubhouse"),4,9),
               "Reynolds_Mandel":(("ReynoldsClubhouse","MandelHall"),5,9)}
    segments = [(key,mapping[key][0],meta["position"],meta["normal"],*mapping[key][1:])
                for key,meta in record["joint_planes_group_frame"].items()]
levels = {}
for suffix in ("","_LOD1","_LOD2"):
    trees = {}
    bounds = {}
    for key in sorted({name for _,owners,_,_,_,_ in segments for name in owners}):
        obj = bpy.data.objects[key+suffix]
        points = [obj.matrix_world @ v.co for v in obj.data.vertices]
        obj.data.calc_loop_triangles()
        faces = [tuple(t.vertices) for t in obj.data.loop_triangles]
        trees[key] = BVHTree.FromPolygons(points,faces,all_triangles=True)
        bounds[key] = {"min":[min(v[i] for v in points) for i in range(3)],
                       "max":[max(v[i] for v in points) for i in range(3)],
                        "triangles":len(faces)}
    result = {}
    for key,owners,anchor,d,w,h in segments:
        anchor = Vector(anchor)
        direction = Vector(d).normalized()
        tangent = Vector((-direction.y,direction.x,0))
        rows = []
        for f in (-.8,-.4,0,.4,.8):
            for z in (.1,2,5,h):
                station = anchor+f*w*tangent
                station.z = z
                row = {}
                for name in owners:
                    out = []
                    start = station-1.5*direction
                    for _ in range(12):
                        p,n,_,_ = trees[name].ray_cast(start,direction,3-(start-(station-1.5*direction)).length)
                        if p is None:
                            break
                        out.append([round((p-station).dot(direction),5),round(n.dot(direction),5)])
                        start = p+.000025*direction
                    row[name] = out
                rows.append([f,z,row])
        result[key] = rows
    levels[suffix or "near"] = {"standing_envelopes":bounds,"internal_joint_samples":result}
target.write_text(json.dumps({"source_sha256":sha256(source.read_bytes()).hexdigest(),"levels":levels},indent=2)+"\n")
