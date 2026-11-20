"""Replay only Gates center on the verified #92 north Blake candidate.
blender -b --disable-autoexec BLAKE92.blend --python-exit-code 1 --python gates_central_geometry.py -- NEW.blend
"""
from pathlib import Path
import sys
import bmesh
from mathutils import Vector
import bpy,hashlib,struct
def fingerprint():
    d=hashlib.sha256()
    def name(s):
        a=s.encode('utf-8');d.update(struct.pack('<I',len(a)));d.update(a)
    def seq(s,fmt):
        d.update(struct.pack('<I',len(s)))
        for a in s:d.update(struct.pack(fmt,*a))
    for o in sorted((o for o in bpy.data.objects if o.type=='MESH'),key=lambda o:o.name):
        name(o.name);m=o.data
        seq([tuple(x) for x in o.matrix_world],'<4f')
        seq([tuple(v.co) for v in m.vertices],'<3f')
        seq([tuple(e.vertices) for e in m.edges],'<2I')
        for p in m.polygons:
            seq([(v,) for v in p.vertices],'<I')
            seq([(p.material_index,int(p.use_smooth))],'<2I')
        for slot in o.material_slots:name(slot.name)
        for uv in m.uv_layers:
            name(uv.name);seq([tuple(q.uv) for q in uv.data],'<2f')
        seq([tuple(q.vector) for q in m.corner_normals],'<3f')
    for i in sorted(i for i in bpy.data.images.keys() if bpy.data.images[i].packed_file):
        im=bpy.data.images[i]
        for k in (i,im.colorspace_settings.name,im.alpha_mode,hashlib.sha256(im.packed_file.data).hexdigest()):name(k)
        seq([tuple(im.size)],'<2I')
    return d.hexdigest()

TRIM = {
    'GatesBlakeHall': (
        ('sill', -6.7075, (71, 72)),
        ('sill', -6.7075, (654, 660)),
        ('sill', -6.7075, (774, 779)),
        ('sill', -6.7075, (1263, 1268)),
        ('sill', -6.7075, (1360, 1366)),
        ('sill', -6.7075, (1966, 1967)),
        ('sill', -6.7075, (2089, 2094)),
        ('sill', -6.7075, (2576, 2577)),
        ('sill', -6.7075, (2672, 2678)),
        ('sill', -6.7075, (3255, 3261)),
        ('sill', -6.7075, (3384, 3388)),
        ('sill', -6.7075, (3895, 3897)),
        ('sill', -6.7075, (3994, 3995)),
        ('sill', -6.7075, (4572, 4579)),
        ('sill', -6.7075, (4694, 4695)),
        ('sill', -6.7075, (5185, 5186)),
        ('sill', -6.7075, (5279, 5280)),
        ('sill', -6.7075, (5894, 5895)),
        ('sill', -6.7075, (6010, 6011)),
        ('sill', -6.7075, (6501, 6502)),
        ('sill', -6.7075, (6594, 6599)),
        ('sill', -6.7075, (7176, 7177)),
        ('band', -6.6825, (7249, 7250)),
        ('sill', 6.6825, (7742, 7744)),
        ('sill', 6.6825, (8329, 8330)),
        ('sill', 6.6825, (8444, 8449)),
        ('sill', 6.6825, (8937, 8939)),
        ('sill', 6.6825, (9038, 9039)),
        ('sill', 6.6825, (9644, 9646)),
        ('sill', 6.6825, (9762, 9764)),
        ('sill', 6.6825, (10249, 10251)),
        ('sill', 6.6825, (10345, 10348)),
        ('sill', 6.6825, (10930, 10932)),
        ('sill', 6.6825, (12301, 12304)),
        ('sill', 6.6825, (12402, 12403)),
        ('sill', 6.6825, (12983, 12986)),
        ('sill', 6.6825, (13104, 13105)),
        ('sill', 6.6825, (13588, 13593)),
        ('sill', 6.6825, (13687, 13691)),
        ('sill', 6.6825, (14297, 14302)),
        ('sill', 6.6825, (14420, 14422)),
        ('sill', 6.6825, (14902, 14908)),
        ('sill', 6.6825, (14998, 15003)),
        ('sill', 6.6825, (15583, 15588)),
        ('band', 6.6575, (15657, 15661)),
    ),
    'GatesBlakeHall_LOD1': (
        ('band', -6.6825, (3335, 3336)),
        ('band', 6.6575, (6804, 6807)),
    ),
}
STATE = {
    'GatesBlakeHall': (57755, 19391, 24, 34),
    'GatesBlakeHall_LOD1': (25601, 8212, 20, 32),
    'GatesBlakeHall_LOD2': (461, 757, 8, 12),
}
src = Path(bpy.data.filepath).resolve()
out = Path(sys.argv[sys.argv.index('--')+1]).resolve()
if src == out or out.exists() or out.suffix != '.blend' or not out.parent.is_dir():
    raise ValueError("Output must be a new Blend file in an existing directory")
if fingerprint() != '385fe30955c41497c130fc6bd6fb00be0523bed1eef6acbc147b89ca3fce5b72':
    raise ValueError("Wrong precondition: expected exact verified #92 Blake mesh, UV and packed texture fingerprint")
for name, (original, start, n, faces) in STATE.items():
    o = bpy.data.objects[name]
    m = o.data
    m.calc_loop_triangles()
    c = [v.co.copy() for v in m.vertices]
    assert len(m.loop_triangles)==original and o.matrix_world.is_identity and m.users==1
    far=name.endswith('LOD2')
    donor=set(range(start,start+n))
    donor_faces=[p for p in m.polygons if donor.intersection(p.vertices)]
    assert len(donor_faces)==faces and all(set(p.vertices)<=donor and len(p.vertices)==3 for p in donor_faces)
    if not far:
        removed=set(range(start+n,start+2*n))
        removed_face=[p for p in m.polygons if removed.intersection(p.vertices)]
        assert len(removed_face)==faces and all(set(p.vertices)<=removed and len(p.vertices)==3 for p in removed_face)
        assert all(abs(c[i].y+18.1)<.56 and abs(c[i].x+.0125)<.44 for i in donor)
        assert all(abs(c[i].y+7.1)<.56 and abs(c[i].x+.0125)<.44 for i in removed)
        for i in donor:
            m.vertices[i].co += Vector((-1.2875, 3.05, -1.39))
        moved=donor.copy()
        for kind, old_x, ii in TRIM.get(name, ()):
            assert not (removed|moved).intersection(ii)
            delta=(.047 if kind=='sill' else .022)*(1 if old_x<0 else -1)
            for i in ii:
                assert abs(c[i].x-old_x)<1e-5 and c[i].y<3.401
                m.vertices[i].co.x += delta
            moved.update(ii)
        if name=='GatesBlakeHall':
            for first in (11712,11784,11856):
                ii=set(range(first,first+72))
                assert not (moved|removed).intersection(ii) and all(6.7049<c[i].x<6.771 and -13.6<c[i].y<-11.6 for i in ii)
                linked=[set(p.vertices) for p in m.polygons if ii.intersection(p.vertices)]
                assert len(linked)==144 and all(fust<=ii for fust in linked)
                for i in ii:m.vertices[i].co.x -= .0695
                moved.update(ii)
        assert {i for i,v in enumerate(m.vertices) if v.co!=c[i]}==moved
        assert all(c[i].y<=3.401 for i in moved|removed)
        bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(removed)],context='VERTS')
        expected=original-faces
        print(name,'moved',len(moved),'removed',len(removed))
    else:
        assert all(abs(c[i].x+1.30)<.36 and abs(c[i].y-17.10)<.48 for i in donor)
        assert abs(min(c[i].z for i in donor)-20.835)<1e-5
        uv=[(p.index,tuple(p.vertices),p.material_index,p.use_smooth,tuple(m.uv_layers.active.data[i].uv.copy() for i in p.loop_indices)) for p in donor_faces]
        bm=bmesh.new();bm.from_mesh(m);lu=bm.loops.layers.uv.active
        verts={i:bm.verts.new(c[i]+Vector((0,-32.15,4.475))) for i in sorted(donor)}
        for _,v,mi,sm,coords in uv:
            ff=bm.faces.new([verts[i] for i in v]);ff.material_index=mi;ff.smooth=sm
            coord=dict(zip((verts[i] for i in v),coords))
            for loop in ff.loops:loop[lu].uv=coord[loop.vert]
        expected=original+faces
        print(name,'new stubs',n,'vertices,',faces,'triangles')
    bm.to_mesh(m);bm.free();m.update();m.calc_loop_triangles()
    assert len(m.loop_triangles)==expected
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
