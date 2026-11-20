"""Fit the historic Alumni House model's existing stair rail to its four actual steps.
blender -b --disable-autoexec ORIGINAL.blend --python-exit-code 1 --python alumni_house_rail_support.py -- NEW.blend
"""
from pathlib import Path
from collections import defaultdict
import bpy, hashlib, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BASE='189399d49ffab0be5de07b0f8ae3b4e1dd8ce422d19a5cc60eb4fdf1be70fa50'
src=Path(bpy.data.filepath).resolve()
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
if hashlib.sha256(src.read_bytes()).hexdigest()!=BASE: raise ValueError('Alumni House source version differs')
if out.exists() or out.suffix!='.blend' or not out.parent.is_dir():raise ValueError('Provide a new .blend file in an existing folder')
m=bpy.data.objects['AlumniHouse'].data
vs=m.vertices
par=list(range(len(vs)))
def r(i):
    while par[i]!=i:
        i=par[i]
    return i
for e in m.edges:
    a,b=map(r,e.vertices)
    if a!=b: par[b]=a
groups=defaultdict(list)
for i in range(len(vs)):groups[r(i)].append(i)

def comp(x,y,z,count=8):
    matches=[]
    for ids in groups.values():
        if len(ids)!=count:continue
        vv=[vs[i].co for i in ids]
        cc=[(min(v[j] for v in vv)+max(v[j] for v in vv))/2 for j in range(3)]
        if max(abs(a-b) for a,b in zip(cc,(x,y,z)))<1e-4:matches.append(ids)
    assert len(matches)==1,(x,y,z,len(matches))
    return matches[0]

step_groups=[comp(-3.4,y,z) for y,z in ((-13.25,.39),(-13.57,.29),(-13.89,.19),(-14.21,.09))]
steps={i for ids in step_groups for i in ids}
tree=BVHTree.FromPolygons([v.co.copy() for v in vs],[tuple(f.vertices) for f in m.polygons if all(i in steps for i in f.vertices)])
changed=set()
for x,dx in ((-4.95,.08),(-1.85,-.08)):
    for n in range(7):
        y=-13.2-.26*n
        ids=comp(x,y,.95)
        newY=.12 if n==6 else 0
        samples=[]
        for idx in ids:
            v=vs[idx].co
            if v.z<.6:
                hit,no,_,_=tree.ray_cast(Vector((v.x+dx,v.y+newY,1)),Vector((0,0,-1)),2)
                assert hit is not None and no.z>.99
                samples.append(hit.z)
        assert len(samples)==4 and max(samples)-min(samples)<1e-6
        expected=(.78,.78,.78,.58,.38,.18,.18)[n]
        assert abs(expected-samples[0])<1e-6,(n,samples)
        for idx in ids:
            v=vs[idx].co
            v.x+=dx;v.y+=newY
            if v.z<.6: v.z=samples[0]-.01
        changed.update(ids)
        print('rail post',x,n,'tread',round(samples[0],3),'foot',round(samples[0]-.01,3))
    ids=comp(x,-14,1.4)
    for idx in ids:
        v=vs[idx].co
        v.x+=dx
        if v.y<-14.4:v.y+=.09
    changed.update(ids)
assert len(changed)==128
m.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
