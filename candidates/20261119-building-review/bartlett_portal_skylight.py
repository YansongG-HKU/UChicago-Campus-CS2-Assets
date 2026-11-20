"""Portable verified Bartlett portal and exterior ridge-light candidate.
blender -b --disable-autoexec ORIGINAL.blend --python-exit-code 1 --python bartlett_portal_skylight.py -- NEW.blend
"""
from pathlib import Path
import hashlib
import sys
import bpy
import bmesh

SOURCE_SHA='62ef0f7ee072ab7cf9ffcc4adc3a37dba14b4f5360216066ea5f875643eefdaf'
TRIM = {
    'BartlettHall': (
        (14.015, (23838, 23843, 23850, 23851, 23853, 23856)),
        (14.015, (23862, 23867, 23874, 23875, 23877, 23880)),
        (14.015, (23886, 23891, 23898, 23899, 23901, 23904)),
        (14.015, (23910, 23915, 23922, 23923, 23925, 23928)),
        (-14.015, (46569, 46570, 46574, 46577, 46587, 46588)),
        (-14.015, (46593, 46594, 46598, 46601, 46611, 46612)),
        (-14.015, (46617, 46618, 46622, 46625, 46635, 46636)),
        (-14.015, (46641, 46642, 46646, 46649, 46659, 46660)),
    ),
    'BartlettHall_LOD1': (
        (14.015, (9816, 9821, 9828, 9829, 9831, 9834)),
        (14.015, (9840, 9845, 9852, 9853, 9855, 9858)),
        (14.015, (9864, 9869, 9876, 9877, 9879, 9882)),
        (14.015, (9888, 9893, 9900, 9901, 9903, 9906)),
        (-14.015, (19298, 19299, 19303, 19306, 19316, 19317)),
        (-14.015, (19322, 19323, 19327, 19330, 19340, 19341)),
        (-14.015, (19346, 19347, 19351, 19354, 19364, 19365)),
        (-14.015, (19370, 19371, 19375, 19378, 19388, 19389)),
    ),
}
SOUTH=-28.70
NORTH=31.55
PS=0.043
def build_ridge(bm, lu, lod):
    far=lod==2
    xs=(-1.575,-1.505,0.0,1.505,1.575) if far else (-1.575,-1.505,-.0225,.0225,1.505,1.575)
    ys=[SOUTH,NORTH]
    count=(96,48,0)[lod]
    if count:
        step=(NORTH-SOUTH)/count
        ys=[SOUTH,SOUTH+.08]+[v for i in range(1,count) for v in (SOUTH+i*step-PS/2,SOUTH+i*step+PS/2)]+[NORTH-.08,NORTH]
    zlambda=lambda x:22.206-abs(x)*5.2/12.325
    top=[[bm.verts.new((x,y,zlambda(x))) for x in xs] for y in ys]
    bot=[[bm.verts.new((x,y,21.21)) for x in (xs[0],xs[-1])] for y in ys]
    glass=(.25,.90,.0025) if far else (.45,.60,.002)
    frame=(.15,.10,.002) if far else (.15,.70,.002)
    made=[]
    def tri(seq,style):
        f=bm.faces.new(seq); f.material_index=0
        u,v,h=style
        for loop,(a,b) in zip(f.loops,((u-h,v-h),(u+h,v-h),(u+h,v+h))):loop[lu].uv=(a,b)
        made.append(f)
    def quad(a,b,c,d,style):
        tri([a,b,c],style);tri([a,c,d],style)
    for j in range(len(ys)-1):
        a=top[j];c=top[j+1]; ll,rr=bot[j]; lm,rm=bot[j+1]
        for i in range(len(xs)-1):
            rail=i in (0,len(xs)-2) or (not far and i==2)
            rib=count and j%2==0
            quad(a[i],a[i+1],c[i+1],c[i],frame if rail or rib else glass)
        quad(ll,lm,rm,rr,frame)
        quad(ll,a[0],c[0],lm,frame)
        quad(rr,rm,c[-1],a[-1],frame)
    for i in (0,-1):
        cap=[*bot[i],*reversed(top[i])]
        for j in range(1,len(cap)-1):tri([cap[0],cap[j],cap[j+1]][::(-1 if i else 1)],frame)
    assert all(not f.smooth and len(f.verts)==3 for f in made)
    new_edges={e for f in made for e in f.edges}
    assert all(len(e.link_faces)==2 for e in new_edges)
    return len(made)
src=Path(bpy.data.filepath).resolve()
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
if src==out or out.exists() or out.suffix!='.blend' or not out.parent.is_dir():
    raise ValueError('Output must be a new .blend in a valid directory')
if hashlib.sha256(src.read_bytes()).hexdigest()!=SOURCE_SHA:
    raise ValueError('Incorrect Bartlett original')
for lod,(name,before) in enumerate(zip(('BartlettHall','BartlettHall_LOD1','BartlettHall_LOD2'),(56854,17846,474))):
    o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles()
    assert o.matrix_world.is_identity and m.users==1 and len(m.loop_triangles)==before
    moved=set()
    for x, ids in TRIM.get(name,()):
        assert len(ids)==6 and not moved.intersection(ids)
        for i in ids:
            v=m.vertices[i]
            assert abs(v.co.x-x)<.00001 and -2.681<=v.co.y<=5.521
            v.co.x += -0.209 if x>0 else 0.209
        moved.update(ids)
    assert len(moved)==(48,48,0)[lod]
    bm=bmesh.new();bm.from_mesh(m)
    lu=bm.loops.layers.uv.active
    assert lu is not None
    add=build_ridge(bm,lu,lod)
    bm.to_mesh(m);bm.free();m.update();m.calc_loop_triangles()
    assert len(m.loop_triangles)==before+add and all(t.area>1e-10 for t in m.loop_triangles)
    print(name,'trim vertices',len(moved),'skylight triangles',add,'total',len(m.loop_triangles))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
