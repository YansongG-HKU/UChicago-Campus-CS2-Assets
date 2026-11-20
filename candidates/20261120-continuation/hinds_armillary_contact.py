"""Join the base of the existing Hinds entry sculpture to its modelled support."""
from hashlib import sha256
from pathlib import Path
import sys
import bpy

source, target = [Path(s).resolve() for s in sys.argv[sys.argv.index('--')+1:]]
if sha256(source.read_bytes()).hexdigest() != "2635421fdfb3f78ec2a07263f5b909cdd76237a6113361ee9fa7e9a131464dae":
    raise ValueError("Expected the exact audited Hinds standalone source")
if target.exists() or target.suffix != ".blend":
    raise ValueError("Choose a new .blend destination")
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
for suffix,count in [("",33442),("_LOD1",10354)]:
    mesh = bpy.data.objects["HenryHindsLaboratory"+suffix].data
    vertices = [v for v in mesh.vertices if abs(v.co.z-2.3)<1e-5
                and abs(abs(v.co.x-16.5)-.325)<1e-5 and abs(abs(v.co.y+3)-.325)<1e-5]
    assert len(vertices) == 4
    for vertex in vertices:
        vertex.co.z = 2.335
    mesh.update()
    mesh.calc_loop_triangles()
    assert len(mesh.loop_triangles) == count
    assert all(t.area>1e-10 for t in mesh.loop_triangles)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
