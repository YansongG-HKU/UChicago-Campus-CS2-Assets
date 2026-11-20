import bpy,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1],load_ui=False)
for name in ('BakerDining','BakerDining_LOD1'):
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles()
 vert=[v.co.copy() for v in m.vertices]; ts=[tuple(t.vertices) for t in m.loop_triangles];tree=BVHTree.FromPolygons(vert,ts,all_triangles=True)
 st=Vector((-4.524375,26.67,5.7)); en=Vector((16.906875,29.4084375,5.7)); n=Vector((-(en-st).y,(en-st).x,0)).normalized()
 for f in (.1,.3,.5,.7,.9):
  c=st.lerp(en,f)
  p,normal,idx,d=tree.ray_cast(c-1.2*n,n,2)
  print(name, f, list(p-c), list(normal), [list(vert[i]) for i in ts[idx]])
