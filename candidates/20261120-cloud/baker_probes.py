import bpy,sys,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=p[0],load_ui=False)
report={}
for suffix in ('','_LOD1','_LOD2'):
 names=['BakerDining'+suffix]+(['CampusNorthResidential'+suffix] if 'CampusNorthResidential'+suffix in bpy.data.objects else [])
 trees={}
 for name in names:
  o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles()
  trees[name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True)
 origin=bpy.data.objects[names[0]].matrix_world.translation
 st=Vector((-4.524375,26.67,0))+origin;en=Vector((16.906875,29.4084375,0))+origin
 n=Vector((-(en-st).y,(en-st).x,0)).normalized()
 rows=[]
 for frac in (.1,.3,.5,.7,.9):
  for z in (.05,.5,1.8,3.5,4.75,5.7,5.81,6.1,7,8):
   c=st.lerp(en,frac);c.z=z
   hits={}
   for name,t in trees.items():
    pos=c-1.5*n; coords=[]
    for i in range(20):
     hit,_,_,d=t.ray_cast(pos,n,3-(pos-(c-1.5*n)).length)
     if hit is None: break
     coords.append(round((hit-c).dot(n),5));pos=hit+n*.00005
    hits[name]=coords
   rows.append([frac,z,hits])
 paving=[]
 for x,y in [(-11.751,6.571),(2.829,24.571),(-.771,11.611),(24.069,23.491)]:
  c=Vector((x,y,80))+origin
  row=[]
  for name,t in trees.items():
   hit,norm,idx,d=t.ray_cast(c,Vector((0,0,-1)))
   m=bpy.data.objects[name].data
   row.append([name,float(hit.z) if hit else None,[[round(v,4) for v in m.vertices[j].co] for j in m.loop_triangles[idx].vertices] if hit else None])
  paving.append([[x,y],row])
 report[suffix or 'near']={'seam':rows,'paving':paving}
open(p[1],'w').write(json.dumps(report,indent=2))
