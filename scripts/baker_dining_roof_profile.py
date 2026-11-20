"""Source-bound Baker Dining three-LOD roof-profile candidate; Blender 4.3.
Keep the original terrace side as a deliberate baseline; only the planted
dining-roof field is fitted. Its transition is not a surveyed curb detail.
blender -b --disable-autoexec ORIGINAL.blend --python-exit-code 1 --python baker_dining_roof_profile.py -- NEW.blend
"""
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
import bmesh,bpy,hashlib,sys
BASE='c4b265b12ac02659fec970085d66ffcc05bbcdef99e696d5de5c6edf3a873cba'
NAMES=('BakerDining','BakerDining_LOD1','BakerDining_LOD2')
ORIGINAL=(3858,650,230)
EDGE=5.8
DOOR=3.7
CAP=8.92
SLOPE=(.0478957,.00125751,7.77331)
# Photographic roof-field divider, approximated by two projected straight segments.
# 1.8 is a conservative transitional face slope, not a physical curb measurement.
R1=(.03*1.8,-1.8,EDGE+1.13*1.8)
R2=(1.026*1.8,-1.8,EDGE+8.35*1.8)
def ev(l,x,y):return l[0]*x+l[1]*y+l[2]
def branch(x,y):
    r=max((R1,R2),key=lambda l:ev(l,x,y))
    r=min((r,SLOPE,(0.,0.,CAP)),key=lambda l:ev(l,x,y))
    return r if ev(r,x,y)>EDGE else (0.,0.,EDGE)
def roof(x,y):return ev(branch(x,y),x,y)
def delta(x,y,z):return (roof(x,y)-EDGE)*max(0.,min(1.,(z-DOOR)/(EDGE-DOOR)))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))

src=Path(bpy.data.filepath).resolve()
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
if hashlib.sha256(src.read_bytes()).hexdigest()!=BASE:raise ValueError('Baker source differs')
if out.exists() or out.suffix!='.blend' or not out.parent.is_dir():raise ValueError('Output must be a new .blend')
for lod,name in enumerate(NAMES):
    o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles()
    assert o.matrix_world.is_identity and len(m.loop_triangles)==ORIGINAL[lod]
    bm=bmesh.new();bm.from_mesh(m)
    marked=bm.faces.layers.int.new('roof_patch_core')
    bm.verts.index_update()
    unseen=set(bm.verts);core_groups=[]
    while unseen:
        a=unseen.pop();stack=[a];g={a}
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                w=e.other_vert(v)
                if w in unseen:unseen.remove(w);g.add(w);stack.append(w)
        if len(g)>5 and min(v.co.z for v in g)==0 and abs(max(v.co.z for v in g)-EDGE)<1e-5:core_groups.append(g)
    core=set().union(*core_groups)
    owned={f for v in core for f in v.link_faces}
    assert len(owned)==68
    for f in owned:f[marked]=1
    bmesh.ops.remove_doubles(bm,verts=sorted(core,key=lambda v:v.index),dist=1e-5)
    # Select the two pre-existing rectangular rooftop units by exact three-axis bounds.
    groups=[]
    for cx,cy in ((-16,4),(-23,-5)):
        g={v for v in bm.verts if abs(v.co.x-cx)<=1.50001 and abs(v.co.y-cy)<=2.00001 and EDGE-1e-5<=v.co.z<=6.80001}
        if lod<2:
            assert len(g)==8 and sum(v.co.z>6 for v in g)==4,(name,cx,len(g))
            groups.append((cx,cy,g))
        else:assert not g
    eq=set().union(*(g for _,_,g in groups))
    # Subdivide only where the bounded roof function changes branch. BMesh
    # interpolates the original corner UVs. Lower surfaces and roof units
    # are not used to choose cuts; shared edges remain continuous.
    cutplanes=(sub(SLOPE,(0,0,CAP)),sub(R1,R2),sub(R1,(0,0,EDGE)),sub(R2,(0,0,EDGE)),
               sub(R1,SLOPE),sub(R2,SLOPE),sub(R1,(0,0,CAP)),sub(R2,(0,0,CAP)))
    f_eps=.00005
    for a,b,c in cutplanes:
        def sd(v):return a*v.co.x+b*v.co.y+c
        faces=[]
        for f in bm.faces:
            vs=f.verts
            if eq.intersection(vs) or (not f[marked] and max(v.co.z for v in vs)<=DOOR+f_eps):continue
            ds=[sd(v) for v in vs]
            if min(ds)>=-f_eps or max(ds)<=f_eps:continue
            vv=[v.co for v in vs]
            intersections=[]
            for j,(d,e) in enumerate(zip(ds,ds[1:]+ds[:1])):
                if d*e<0:
                    u,v=vv[j],vv[(j+1)%len(vv)]
                    intersections.append(u.lerp(v,d/(d-e)))
            if len(intersections)<2: continue
            u,v=intersections[:2]
            bx,by=(a*.0007,b*.0007)
            if not any(branch(w.x+bx,w.y+by)!=branch(w.x-bx,w.y-by) for w in (u,u.lerp(v,.25),u.lerp(v,.5),u.lerp(v,.75),v)):
                continue
            faces.append(f)
        if faces:
            es={e for f in faces for e in f.edges};vs={v for f in faces for v in f.verts}
            bm.edges.index_update();bm.verts.index_update()
            geom=[*faces,*sorted(es,key=lambda e:e.index),*sorted(vs,key=lambda v:v.index)]
            scale=a*a+b*b
            bmesh.ops.bisect_plane(bm,geom=geom,dist=1e-5,
                plane_co=Vector((-a*c/scale,-b*c/scale,0)),plane_no=Vector((a,b,0)).normalized(),
                clear_inner=False,clear_outer=False)
    for v in bm.verts:
        if v not in eq:
            x,y,z=v.co;v.co.z=z+delta(x,y,z)
    for cx,cy,g in groups:
        cap_z=max(roof(v.co.x,v.co.y) for v in g)+1.0
        for v in g:
            x,y,z=v.co;v.co.z=(roof(x,y)-.025 if z<6.0 else cap_z)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='FIXED',ngon_method='EAR_CLIP')
    bmesh.ops.dissolve_degenerate(bm,dist=1e-5,edges=list(bm.edges))
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3],quad_method="FIXED",ngon_method="EAR_CLIP")
    zero=[f for f in bm.faces if f.calc_area()<=1e-8]
    if zero: bmesh.ops.delete(bm,geom=zero,context='FACES')
    core_edges={e for f in bm.faces if f[marked] for e in f.edges}
    bad=[e for e in core_edges if len(e.link_faces)!=2 or not e.is_contiguous]
    print('core topology after all cuts',len(core_edges),'unpaired edges',len(bad))
    assert not bad
    bm.faces.layers.int.remove(marked)
    bm.normal_update()
    bm.to_mesh(m);bm.free();m.update();m.calc_loop_triangles()
    print("bounds and worst",min(v.co.z for v in m.vertices), min(t.area for t in m.loop_triangles),sum(t.area<=1e-8 for t in m.loop_triangles),flush=True)
    for t in m.loop_triangles:
        if t.area<=1e-8: print("DEGEN",t.index,[tuple(m.vertices[k].co) for k in t.vertices],flush=True)
    assert min(v.co.z for v in m.vertices)==0 and all(t.area>1e-8 for t in m.loop_triangles)
    print(name,'triangles',len(m.loop_triangles),'from',ORIGINAL[lod], 'roof units',len(groups))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
