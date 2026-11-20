"""Replay Blake north wing correction only; use the locked Gates–Blake Blend.
blender -b --disable-autoexec SOURCE --python-exit-code 1 --python blake_north_geometry.py -- NEW.blend
"""
from pathlib import Path
import bpy
import hashlib
import sys

BASE_SHA = '23aefafed694e15484af6af6444ffa2e1b43e69efa8246195ebfd1ed842c0b45'
STATE = {
    'GatesBlakeHall': (57755, 36968, 24, 34, 9.196),
    'GatesBlakeHall_LOD1': (25601, 16957, 20, 32, 9.196),
    'GatesBlakeHall_LOD2': (461, 757, 8, 12, 16.0),
}
TRIM = {
    'GatesBlakeHall': (
        ('sill', -6.7075, (19507, 19512)),
        ('sill', -6.7075, (20094, 20100)),
        ('sill', -6.7075, (20586, 20591)),
        ('sill', -6.7075, (21176, 21177)),
        ('sill', -6.7075, (21674, 21676)),
        ('sill', -6.7075, (22255, 22256)),
        ('sill', -6.7075, (22770, 22772)),
        ('sill', -6.7075, (23576, 23577, 23581, 23589)),
        ('sill', -6.7075, (24332, 24333)),
        ('sill', -6.7075, (25258, 25262)),
        ('band', -6.6825, (25920, 25923)),
        ('sill', 6.6825, (26548, 26549)),
        ('sill', 6.6825, (27135, 27136)),
        ('sill', 6.6825, (27622, 27625)),
        ('sill', 6.6825, (28216, 28219)),
        ('sill', 6.6825, (30010, 30014)),
        ('sill', 6.6825, (30528, 30530, 30535)),
        ('sill', 6.6825, (31304, 31306)),
        ('sill', 6.6825, (32060, 32065, 32066, 32068)),
        ('sill', 6.6825, (32985, 32986)),
        ('band', 6.6575, (33666, 33667)),
    ),
    'GatesBlakeHall_LOD1': (
        ('band', -6.6825, (11690, 11694, 11696)),
        ('band', 6.6575, (15260, 15261)),
    ),
}
src = Path(bpy.data.filepath).resolve()
out = Path(sys.argv[sys.argv.index('--')+1]).resolve()
if src == out or out.exists() or out.suffix != '.blend' or not out.parent.is_dir():
    raise ValueError("Output must be a new Blend file in an existing directory")
if hashlib.sha256(src.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError("Wrong Gates-Blake independent source")
for name, (original, start, n, faces, old_cy) in STATE.items():
    o = bpy.data.objects[name]
    m = o.data
    m.calc_loop_triangles()
    c = [v.co.copy() for v in m.vertices]
    assert len(m.loop_triangles)==original and o.matrix_world.is_identity and m.users==1
    ids = set(range(start,start+n))
    assert all(abs(c[i].x+.0125)<.44 and abs(c[i].y-old_cy)<.56 and 21.899<c[i].z<23.737 for i in ids)
    ff = [set(p.vertices) for p in m.polygons if ids.intersection(p.vertices)]
    assert len(ff) == faces and all(f<=ids for f in ff) and set.union(*ff)==ids
    for i in ids:
        v=m.vertices[i].co
        v.x += -1.30+.0125
        v.y += 17.10-old_cy
        v.z -= 1.065
    moved = ids.copy()
    for kind, old_x, ii in TRIM.get(name, ()):
        assert not moved.intersection(ii)
        delta=(.047 if kind=='sill' else .022)*(1 if old_x<0 else -1)
        for i in ii:
            assert abs(c[i].x-old_x)<1e-5 and c[i].y>3.399
            m.vertices[i].co.x += delta
        moved.update(ii)
    if name == 'GatesBlakeHall':
        for first in (29366,29438,29510):
            ii = set(range(first,first+72))
            assert not moved.intersection(ii) and all(6.7049<c[i].x<6.771 and c[i].y>13.7 for i in ii)
            linked=[set(p.vertices) for p in m.polygons if ii.intersection(p.vertices)]
            assert len(linked)==144 and all(f<=ii for f in linked)
            for i in ii: m.vertices[i].co.x -= .0695
            moved.update(ii)
    changed=[i for i,v in enumerate(m.vertices) if v.co != c[i]]
    assert set(changed)==moved and all(c[i].y>3.399 for i in changed)
    assert len(changed)=={'GatesBlakeHall':287,'GatesBlakeHall_LOD1':25,'GatesBlakeHall_LOD2':8}[name]
    m.update()
    print(name,len(changed))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
