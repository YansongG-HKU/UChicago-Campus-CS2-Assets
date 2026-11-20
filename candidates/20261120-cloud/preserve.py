"""Compare packed images and stable source geometry across the saved candidates."""
import hashlib
import json
from pathlib import Path
import struct
import sys
from collections import Counter

import bpy
from mathutils import Vector


def collect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    meshes = {}
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        mesh = obj.data
        mesh.calc_loop_triangles()
        layers = [layer.data for layer in mesh.uv_layers]
        corners = Counter()
        for tri in mesh.loop_triangles:
            rows = [struct.pack('<3f', *mesh.vertices[mesh.loops[k].vertex_index].co)
                    + b''.join(struct.pack('<2f', *layer[k].uv) for layer in layers)
                    for k in tri.loops]
            oriented = min(rows[i:] + rows[:i] for i in range(3))
            corners[b''.join(oriented)] += 1
        meshes[obj.name] = {
            'corners': corners,
            'matrix': [list(row) for row in obj.matrix_world],
            'mesh_materials': [m.name if m else None for m in mesh.materials],
            'texture_bindings': {
                m.name: {
                    n.name: hashlib.sha256(n.image.packed_file.data).hexdigest()
                    for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image and n.image.packed_file
                }
                for m in mesh.materials if m and m.node_tree
            },
        }
    return meshes


before, after, mode, output = map(Path, sys.argv[sys.argv.index('--')+1:])
original = collect(before)
candidate = collect(after)
assert set(original) == set(candidate)
rows = {}
for name in sorted(original):
    a, b = original[name], candidate[name]
    removed = (a['corners'] - b['corners']).total()
    added = (b['corners'] - a['corners']).total()
    rows[name] = {'position_uv_triangles_removed': removed, 'position_uv_triangles_added': added,
                  **{field + '_unchanged': a[field] == b[field]
                     for field in ('matrix', 'texture_bindings', 'mesh_materials')}}
    assert a['matrix'] == b['matrix']
    assert a['texture_bindings'] == b['texture_bindings']
    assert a['mesh_materials'] == b['mesh_materials']
    if mode.name == 'billings':
        assert (removed, added) == ((0, 28) if name == 'BillingsHospital_LOD2' else (0, 0))
    elif mode.name == 'assembly' and name.startswith('CampusNorthResidential'):
        assert (removed, added) == (0, 0)
output.write_text(json.dumps(rows, indent=2) + '\n')
