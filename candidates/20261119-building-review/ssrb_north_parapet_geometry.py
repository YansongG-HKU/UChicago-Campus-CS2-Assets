"""Generate the reviewed independent north portal stone-backing candidate (#90).
Blender 4.3.2 with --disable-autoexec. See README.
Only writes a new Blend; not a game prefab, FBX or site survey.
"""
import bpy,sys,pathlib,math,json,hashlib,os
from mathutils import Vector
A,p=sys.argv[sys.argv.index('--')+1:]
A=pathlib.Path(A).resolve(strict=True)
P=pathlib.Path(p).absolute()
if P.suffix.lower()!='.blend' or os.path.lexists(P) or not P.parent.is_dir():
 raise RuntimeError('Output must be a new .blend in an existing folder')
base=hashlib.sha256(A.read_bytes()).hexdigest()
if base!='c41335f183c8de0ddde72a688c448be1807fcc88d9255dfeaa2ceb38cac58a5e':
 raise RuntimeError('Exact verified independent SocialSciencesResearch source required')
bpy.ops.wm.open_mainfile(filepath=str(A),load_ui=False,use_scripts=False)
report={}
for lod,n in enumerate(('SocialSciencesResearch','SocialSciencesResearch_LOD1','SocialSciencesResearch_LOD2')):
 o=bpy.data.objects[n];old=o.data; assert o.matrix_world.is_identity
 U=old.uv_layers.active
 vv=[v.co.copy() for v in old.vertices]; ff=[]; uv=[]; nn=[]; smooth=[]
 for p in old.polygons:
  ff.append(tuple(p.vertices));uv.append([tuple(U.data[l].uv) for l in p.loop_indices]);nn.append([tuple(old.corner_normals[l].vector) for l in p.loop_indices]);smooth.append(p.use_smooth)
 base_faces=len(ff)
 # Stone backing follows the established pitched ornamental silhouette. Does not alter
 # existing stone mouldings, the stair, the door recess, or the connecting courtyard.
 prof=[(2.64,12.33),(11.16,12.33),(11.16,13.015),(6.90,14.19),(2.64,13.015)]
 rear,front=11.51,12.035
 q=[Vector((x,y,z)) for y in (rear,front) for x,z in prof]; i0=len(vv);vv.extend(q)
 # In x/z profile traversal is CCW; first profile is rear, facing -Y.
 poly=[(0,1,2),(0,2,3),(0,3,4),(5,7,6),(5,8,7),(5,9,8)]
 for i in range(5):
  j=(i+1)%5
  poly += [(j,i,i+5),(j,i+5,j+5)]
 # Actual far stone atlas bounds independently matched to the original nearby wall.
 if lod==2:
  u0,v0=.04,.06; span_u,span_v=.12,.13
 else:
  u0,v0=.032,.034;span_u,span_v=.29,.072
 for f in poly:
  ps=[q[i] for i in f];normal=(ps[1]-ps[0]).cross(ps[2]-ps[0])
  a,b=(0,2) if abs(normal.y)>.1 else ((1,2) if abs(normal.x)>abs(normal.z) else (0,1))
  A=min(p[a] for p in q);As=max(p[a] for p in q)-A;B=min(p[b] for p in q);Bs=max(p[b] for p in q)-B
  ff.append([i0+i for i in f]);uv.append([(u0+span_u*(p[a]-A)/As,v0+span_v*(p[b]-B)/Bs) for p in ps]);nn.append([(0,0,0)]*3);smooth.append(False)
 new=bpy.data.meshes.new(n+'_ParapetBacking')
 new.from_pydata(vv,[],ff);new.update()
 new.materials.append(old.materials[0]); U2=new.uv_layers.new(name=U.name)
 for p,xyz,s in zip(new.polygons,uv,smooth):
  p.use_smooth=s
  for i,z in zip(p.loop_indices,xyz):U2.data[i].uv=z
 new.normals_split_custom_set([p for ns in nn for p in ns]); o.data=new
 report[n]={'original_triangles':base_faces,'added_stone_triangles':len(poly),'bounds_front_rear_y':[front,rear],'north_top_profile_x_z':prof,'new_faces':list(range(base_faces,len(ff)))}
if os.path.lexists(P):
 raise FileExistsError(P)
bpy.context.preferences.filepaths.save_version=0
result=bpy.ops.wm.save_as_mainfile(filepath=str(P),relative_remap=False)
if result!={'FINISHED'}:
 raise RuntimeError(result)
print(json.dumps(report,indent=2))
