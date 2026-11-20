"""Build the Goodspeed support and 2024/25 roof candidate from the locked independent source.
Run: blender -b --disable-autoexec INPUT.blend --python-exit-code 1 \
    --python goodspeed_modern_ridge.py -- /new/path/GoodspeedHall.blend
"""
from pathlib import Path
import hashlib
import sys
import bpy
import bmesh

BASE_SHA = '1b41b79e72862f112cebaef117cba695ba8b426803c00e71edfacad561a9773d'
STATE = {
    'GoodspeedHall': (25439, 6.831, 15127, 24, 34),
    'GoodspeedHall_LOD1': (11327, 6.831, 6565, 20, 32),
    'GoodspeedHall_LOD2': (240, 0, 375, 8, 12),
}
TRIM = {
    'GoodspeedHall': (
        ('sill', -6.7075, (66, 71)),
        ('sill', -6.7075, (654, 660)),
        ('sill', -6.7075, (1148, 1150)),
        ('sill', -6.7075, (1736, 1740)),
        ('sill', -6.7075, (2223, 2225)),
        ('sill', -6.7075, (2808, 2809)),
        ('sill', -6.7075, (3294, 3297)),
        ('sill', -6.7075, (3882, 3883)),
        ('sill', -6.7075, (4370, 4371)),
        ('sill', -6.7075, (4965, 4966)),
        ('band', -6.6825, (5394, 5396)),
        ('band', -6.6825, (5402, 5406)),
        ('band', -6.6825, (5411, 5414)),
        ('sill', 6.6825, (5925, 5927)),
        ('sill', 6.6825, (6515, 6517)),
        ('sill', 6.6825, (7008, 7010)),
        ('sill', 6.6825, (7592, 7595)),
        ('sill', 6.6825, (8080, 8083)),
        ('sill', 6.6825, (9899, 9905)),
        ('sill', 6.6825, (10490, 10492)),
        ('sill', 6.6825, (10975, 10977)),
        ('sill', 6.6825, (11567, 11569)),
        ('band', 6.6575, (12008, 12010)),
        ('band', 6.6575, (12016, 12017)),
    ),
    'GoodspeedHall_LOD1': (
        ('band', -6.6825, (2475, 2480)),
        ('band', -6.6825, (2483, 2485)),
        ('band', -6.6825, (2495, 2496)),
        ('band', 6.6575, (5119, 5122)),
        ('band', 6.6575, (5126, 5128)),
    ),
}
RINGS = (9327, 9399, 9471)
src = Path(bpy.data.filepath).resolve()
out = Path(sys.argv[sys.argv.index('--')+1]).resolve()
if src == out or out.exists() or out.suffix != '.blend' or not out.parent.is_dir():
    raise ValueError("Output must be a new Blend file in an existing directory")
if hashlib.sha256(src.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError("Wrong Goodspeed Hall independent source")
for name, (original, center, start, num_verts, num_faces) in STATE.items():
    o = bpy.data.objects[name]
    m = o.data
    m.calc_loop_triangles()
    c = [o.matrix_world @ v.co for v in m.vertices]
    remove = set(range(start, start+num_verts))
    assert len(m.loop_triangles) == original and m.users == 1
    assert all(abs(c[i].x)<.5 and abs(c[i].y-center)<.56 and 21.899<c[i].z<23.736 for i in remove)
    assert min(c[i].z for i in remove) < 21.901 and max(c[i].z for i in remove) > 23.59
    hits = [set(p.vertices) for p in m.polygons if remove.intersection(p.vertices)]
    assert len(hits) == num_faces and all(s<=remove and len(s)==3 for s in hits)
    assert set.union(*hits) == remove
    assert o.matrix_world.is_identity
    shifted = set()
    for kind, old_x, ids in TRIM.get(name, ()):
        delta = (0.047 if kind == 'sill' else 0.022) * (1 if old_x < 0 else -1)
        assert not (shifted | remove).intersection(ids)
        for i in ids:
            assert abs(c[i].x-old_x) < 0.00001
            m.vertices[i].co.x += delta
        shifted.update(ids)
    if name == 'GoodspeedHall':
        for first in RINGS:
            ids = set(range(first, first+72))
            assert not (shifted | remove).intersection(ids)
            assert min(c[i].x for i in ids) > 6.7049 and max(c[i].x for i in ids) < 6.771
            linked = [set(p.vertices) for p in m.polygons if ids.intersection(p.vertices)]
            assert len(linked) == 144 and all(s <= ids for s in linked)
            for i in ids:
                m.vertices[i].co.x -= 0.0695
            shifted.update(ids)
    assert len(shifted) == {'GoodspeedHall':264, 'GoodspeedHall_LOD1':10, 'GoodspeedHall_LOD2':0}[name]
    bm = bmesh.new()
    bm.from_mesh(m)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in sorted(remove)], context='VERTS')
    bm.to_mesh(m)
    bm.free()
    m.update()
    m.calc_loop_triangles()
    assert len(m.loop_triangles) == original-num_faces
    print(name, original, '->', len(m.loop_triangles))
bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
