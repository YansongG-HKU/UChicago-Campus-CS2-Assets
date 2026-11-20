"""Give the buried garden-wall end faces one owner in the paired review scene."""
from hashlib import sha256
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

source, target = [Path(x).resolve() for x in sys.argv[sys.argv.index('--')+1:]]
if sha256(source.read_bytes()).hexdigest() != '3d0b924ba647da073f4deb0cfcdd5a291193067c42a168a5dceb791094ce71d8':
    raise ValueError('Expected the locked Smart/Cochrane paired source')
if target.exists() or target.suffix != '.blend':
    raise ValueError('Choose a new .blend target')
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)

for suffix in ('','_LOD1','_LOD2'):
    name = 'CochraneWoods'+suffix
    mesh = bpy.data.objects[name].data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    def ends():
        return [f for f in bm.faces if f.normal.y<-.999 and
                all(abs(v.co.y+20.5)<.0001 for v in f.verts)]

    assert len(ends()) == 8
    # The museum reaches x=±21. Trim the concealed section only; preserve
    # the screen's visible 0.15 m overhang beyond both sides of the museum.
    for boundary in (-21,21):
        cross = [f for f in ends()
                 if min(v.co.x for v in f.verts)<boundary<max(v.co.x for v in f.verts)]
        geom = cross + list({e for f in cross for e in f.edges}) + list({v for f in cross for v in f.verts})
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6,
                              plane_co=Vector((boundary,0,0)), plane_no=Vector((1,0,0)),
                              clear_inner=False, clear_outer=False)
        bm.normal_update()

    concealed = [f for f in ends() if all(abs(v.co.x)<=21.000001 for v in f.verts)]
    assert abs(sum(f.calc_area() for f in concealed) - 24.15) < .0001
    bmesh.ops.delete(bm, geom=concealed, context='FACES')
    assert abs(sum(f.calc_area() for f in ends())-.15) < .0001
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts)>3])
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    mesh.calc_loop_triangles()
    assert all(triangle.area>1e-10 for triangle in mesh.loop_triangles)
    print(name,len(mesh.loop_triangles))

bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
