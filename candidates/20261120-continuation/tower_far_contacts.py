"""Remove buried end-wall portions at the three Tower Group far interfaces."""
from hashlib import sha256
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

source,destination = [Path(s).resolve() for s in sys.argv[sys.argv.index('--')+1:]]
if sha256(source.read_bytes()).hexdigest()!="be0ac5a6c9914ccc9db2a667ad9c84ed53730ab8c4c6d2fef839f29a5864c1cf":
    raise ValueError("Expected the audited Tower Group assembly")
if destination.exists() or destination.suffix!=".blend":
    raise ValueError("Choose a new Blender candidate file")
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)

edits = [
    ("HutchinsonCommons_LOD2", 0, 12.7074995, 1, 1, 30., 40., 3),
    ("ReynoldsClubhouse_LOD2", 1, 30., 1, 0, 12.7074995, 22.7074995, 4),
    ("ReynoldsClubhouse_LOD2", 1, -4., -1, 0, 3.7074995, 23.7074995, 4),
]
for name,axis,plane,direction,span,low,high,owned_count in edits:
    obj = bpy.data.objects[name]
    assert obj.matrix_world.is_identity
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    ownership = bm.faces.layers.int.new("contact_end")
    faces = [f for f in bm.faces if f.normal[axis]*direction>.999 and f.calc_area()>1
             and all(abs(v.co[axis]-plane)<.0001 for v in f.verts)]
    assert len(faces)==owned_count
    for face in faces:
        face[ownership]=1
    if plane==-4.:
        # Mandel's opposing wall is a convex gable. The four source
        # triangles lie fully within the polygon; edge ornament is excluded.
        for face in faces:
            for v in face.verts:
                envelope=14.5+7.5*(1-abs(v.co.x-13.7074995)/10.)
                assert low-.00001 <= v.co.x <= high+.00001 and v.co.z<=envelope+.00001
    else:
        for boundary in (low,high):
            active=[f for f in bm.faces if f[ownership]
                    and min(v.co[span] for v in f.verts)<boundary<max(v.co[span] for v in f.verts)]
            if not active:
                continue
            pivot = Vector((0,0,0)); pivot[span]=boundary
            normal = Vector((0,0,0)); normal[span]=1
            bm.edges.index_update(); bm.verts.index_update()
            edges=sorted({e for f in active for e in f.edges},key=lambda e:e.index)
            verts=sorted({v for f in active for v in f.verts},key=lambda v:v.index)
            bmesh.ops.bisect_plane(bm,geom=active+edges+verts,dist=1e-6,plane_co=pivot,plane_no=normal)
    remove=[f for f in bm.faces if f[ownership] and
            all(low-.00001 <= v.co[span] <= high+.00001 for v in f.verts)]
    assert remove
    print(name,plane,"removed area",sum(f.calc_area() for f in remove))
    bmesh.ops.delete(bm,geom=remove,context="FACES")
    bm.faces.layers.int.remove(ownership)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts)>3])
    bm.to_mesh(mesh); bm.free(); mesh.update()
    mesh.calc_loop_triangles()
    assert all(t.area>1e-10 for t in mesh.loop_triangles)
    print(name,"triangles",len(mesh.loop_triangles))
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
