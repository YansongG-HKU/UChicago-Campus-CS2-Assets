"""Restore the authored south entrance tread envelope to the far LOD only."""
import hashlib
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

source, destination = map(Path, sys.argv[sys.argv.index("--") + 1:])
if hashlib.sha256(source.read_bytes()).hexdigest() != "f893fd65aa691bb2f14533e9bc25ade615e1fcf43069cda79d18128fda865687":
    raise ValueError("Expected the locked Billings Hospital source")
if destination.exists() or destination.suffix != ".blend":
    raise ValueError("Choose a new .blend path")
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()), load_ui=False)
mesh = bpy.data.objects["BillingsHospital_LOD2"].data
mesh.calc_loop_triangles()
assert len(mesh.loop_triangles) == 252

# Union of the source build's three trim boxes, clipping internal caps.
# The top tread continues 0.10 m behind the far wall, as in the near model.
profile = [
    (-18.62, 0.00), (-16.90, 0.00), (-16.90, 0.68),
    (-17.90, 0.68), (-17.90, 0.42), (-18.26, 0.42),
    (-18.26, 0.16), (-18.62, 0.16),
]
bm = bmesh.new()
bm.from_mesh(mesh)
uv = bm.loops.layers.uv.active
sides = [[bm.verts.new((x, y, z)) for y, z in profile] for x in (-2.6, 2.6)]
prism = [bm.faces.new(sides[0][::-1]), bm.faces.new(sides[1])]
for i in range(len(profile)):
    j = (i + 1) % len(profile)
    prism.append(bm.faces.new((sides[0][i], sides[0][j], sides[1][j], sides[1][i])))
bmesh.ops.recalc_face_normals(bm, faces=prism)
for face in prism:
    axes = sorted(range(3), key=lambda dimension: abs(face.normal[dimension]))[:2]
    minimum = [min(v.co[k] for v in face.verts) for k in axes]
    maximum = [max(v.co[k] for v in face.verts) for k in axes]
    for loop in face.loops:
        u, v = [(loop.vert.co[k] - l) / (h - l) for k, l, h in zip(axes, minimum, maximum)]
        # Inside the documented far 'trim' tile with 4 px of padding.
        loop[uv].uv = (.308 + .078 * u, .012 + .077 * v)
bmesh.ops.triangulate(bm, faces=prism)
bm.to_mesh(mesh)
bm.free()
mesh.update()
mesh.calc_loop_triangles()
assert len(mesh.loop_triangles) == 280
assert all(tri.area > 1e-10 for tri in mesh.loop_triangles)
bpy.ops.wm.save_as_mainfile(filepath=str(destination.resolve()), compress=True)
