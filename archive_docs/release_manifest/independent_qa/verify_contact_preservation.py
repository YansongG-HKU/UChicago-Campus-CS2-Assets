import bpy,json,sys,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
import math
def sub(a,b):return tuple(float(a[i])-float(b[i]) for i in range(3))
def dot(a,b):return sum(a[i]*b[i] for i in range(3))
def robust_distance(p,a,b,c):
 ab=sub(b,a);ac=sub(c,a);ap=sub(p,a);aa=dot(ab,ab);bb=dot(ab,ac);cc=dot(ac,ac);d=dot(ap,ab);e=dot(ap,ac);den=aa*cc-bb*bb
 if den>1e-24:
  u=(cc*d-bb*e)/den;v=(aa*e-bb*d)/den
  if u>=-1e-9 and v>=-1e-9 and u+v<=1+1e-9:return math.sqrt(sum((ap[i]-u*ab[i]-v*ac[i])**2 for i in range(3)))
 vals=[]
 for x,y in [(a,b),(b,c),(c,a)]:
  xy=sub(y,x);xp=sub(p,x);dd=dot(xy,xy);t=max(0.,min(1.,dot(xp,xy)/dd)) if dd else 0.;vals.append(math.sqrt(sum((xp[i]-t*xy[i])**2 for i in range(3))))
 return min(vals)
R=Path('campus_repair_20261007').resolve();A=R/'assembly';Q=R/'independent_qa';rows=[]
for title in ['HarperCourtyard','SaiehAdditions','BlakeCobbContact','BlaineJuddBelfield']:
 D=A/'output'/title;rec=json.loads((D/'REPAIR_RECORD.json').read_text());p=D/(title+'.blend')
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 for base,comp in rec['source_components'].items():
  src=Path(comp['file']);src=src if src.is_absolute() else A/src
  for level in range(3):
   name=base+('' if level==0 else '_LOD'+str(level));final=bpy.data.objects.get(name)
   if final is None:continue
   boxes=[(c['cutter_min'],c['cutter_max']) for c in rec['cleanup'] if c['asset']==base and c['lod']==level]
   if not boxes:continue
   with bpy.data.libraries.load(str(src),link=False) as (a,b):b.objects=[name]
   original=b.objects[0];mw=final.matrix_world;fm=final.data;om=original.data;om.calc_loop_triangles()
   fm.calc_loop_triangles();tree=BVHTree.FromPolygons([mw@v.co for v in fm.vertices],[list(t.vertices) for t in fm.loop_triangles],all_triangles=True)
   def signature(points):return tuple(sorted(tuple(round(float(c),5) for c in v) for v in points))
   final_signatures={signature([mw@fm.vertices[i].co for i in t.vertices]) for t in fm.loop_triangles}
   kd=KDTree(len(fm.vertices))
   for i,v in enumerate(fm.vertices):kd.insert(mw@v.co,i)
   kd.balance();vc=vm=0;vmax=0.;vbad=[]
   for vert in om.vertices:
    v=mw@vert.co
    if any(all(lo[k]-1e-5<=v[k]<=hi[k]+1e-5 for k in range(3)) for lo,hi in boxes):continue
    vc+=1;dist=kd.find(v)[2];vmax=max(vmax,dist)
    if dist>0.0002:
     vm+=1
     if len(vbad)<12:vbad.append({"point":list(v),"distance_m":dist})
   count=inside=missing=0;maximum=0.;bad=[]
   for tri in om.loop_triangles:
    v=sum((mw@om.vertices[i].co for i in tri.vertices),start=mw.translation*0)/3
    if any(all(lo[k]-1e-5<=v[k]<=hi[k]+1e-5 for k in range(3)) for lo,hi in boxes):inside+=1;continue
    count+=1;near=tree.find_nearest(v);dist=near[3] if near[0] is not None else 1e9
    if near[0] is not None:
     ft=fm.loop_triangles[near[2]];dist=min(dist,robust_distance(v,*[mw@fm.vertices[i].co for i in ft.vertices]))
    if signature([mw@om.vertices[i].co for i in tri.vertices]) in final_signatures:dist=min(dist,0.000017321)
    maximum=max(maximum,dist)
    if dist>0.0002:
     missing+=1
     if len(bad)<12:bad.append({'point':list(v),'distance_m':dist})
   row=dict(assembly=title,object=name,final_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),outside_cutter_triangle_samples=count,inside_cutter_triangle_samples=inside,missing_outside_samples=missing,max_outside_distance_m=maximum,outside_vertex_preservation_passed=vm==0,sampled_surface_identical_within_0_2mm=missing==0,examples=bad,outside_vertices=vc,missing_outside_vertices=vm,max_vertex_delta_m=vmax,vertex_examples=vbad)
   rows.append(row);print(json.dumps(row),flush=True);bpy.data.objects.remove(original,do_unlink=True)
 (Q/'contact_preservation.json').write_text(json.dumps(rows,indent=2))
