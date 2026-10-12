import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
R=Path('campus_repair_20261007').resolve();rows=[]
configs=[('SaiehHall',R/'geometry/SaiehHall/SaiehHall_CS2_v0.1',1,[(x,16.515,z) for x in [17,18,34,35,36] for z in [2,8,12]]),('KellerCenter',R/'geometry/Keller/KellerCenter',1,[(x,12,.217) for x in [-45.5,-44,-42.5,-41]]),('QuadrangleClub',R/'geometry/QuadrangleClub/QuadrangleClub',0,[(2.35,y,.117) for y in [14.5,14.8,15.1,15.4,15.7,16]])]
for name,root,axis,points in configs:
 for phase,p in [('before',root/(name+'_before.blend')),('after',root/'source'/(name+'.blend'))]:
  bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  for o in bpy.data.objects:
   if o.type!='MESH' or not o.name.startswith(name) or o.name.endswith('_Gls'):continue
   m=o.data;m.calc_loop_triangles();candidate=[t for t in m.loop_triangles if t.normal[axis]>.99];samples=[]
   for point in points:
    for offset in [.011,.039,.067]:
     v=Vector(point)
     for k in range(3):
      if k!=axis:v[k]+=offset
     origin=v.copy();origin[axis]+=1;direction=Vector((0,0,0));direction[axis]=-1;hits=set()
     for t in candidate:
      vs=[m.vertices[i].co for i in t.vertices]
      if max(abs(w[axis]-v[axis]) for w in vs)>0.0001:continue
      h=intersect_ray_tri(*vs,direction,origin,True)
      if h is not None and (h-v).length<.0001:hits.add(t.polygon_index)
     samples.append({'point':list(v),'surface_count':len(hits)})
   rows.append({'asset':name,'phase':phase,'object':o.name,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'samples':samples,'max_overlap':max(a['surface_count'] for a in samples),'zero_samples':sum(a['surface_count']==0 for a in samples)})
 (R/'independent_qa/overlap_probes.json').write_text(json.dumps(rows,indent=2))
