"""Seat the modelled north facade projections against their existing support wall."""
import hashlib
import sys
from pathlib import Path

import bpy

source, target = [Path(value).resolve() for value in sys.argv[sys.argv.index("--") + 1:]]
if hashlib.sha256(source.read_bytes()).hexdigest() != "5452d61c34fdfa5ee877e7c69267e973496318009d5834de1a685e987b08dce0":
    raise ValueError("Expected the locked standalone residence")
if target.exists() or target.suffix != '.blend':
    raise ValueError("Choose a new .blend path")
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
for name, count, triangles in [('CampusNorthResidential', 580, 75560),
                               ('CampusNorthResidential_LOD1', 690, 18216)]:
    obj = bpy.data.objects[name]
    assert obj.matrix_world.is_identity
    mesh = obj.data
    mesh.calc_loop_triangles()
    assert len(mesh.loop_triangles) == triangles
    anchors = [v for v in mesh.vertices if abs(v.co.y-55.503123) < .00002
               and -.25 <= v.co.x <= 25.97]
    assert len(anchors) == count
    for point in anchors:
        point.co.y -= .023
    mesh.update()
    mesh.calc_loop_triangles()
    assert len(mesh.loop_triangles) == triangles
    assert min(t.area for t in mesh.loop_triangles) > 1e-10
    print(name, len(anchors), triangles)
bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
