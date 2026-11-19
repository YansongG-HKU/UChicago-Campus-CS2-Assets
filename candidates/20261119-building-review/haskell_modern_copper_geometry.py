"""Rebuild the reviewed C geometry on the exact Haskell A texture-sharing Blend.
Use Blender 4.3.2 with --disable-autoexec. See README. Does not export FBX,
set a game preset, or resolve survey dimensions.
"""
import bpy, pathlib,sys,math,hashlib,json,collections,statistics,os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
A,p=sys.argv[sys.argv.index('--')+1:]
A=pathlib.Path(A).resolve(strict=True)
P=pathlib.Path(p).absolute()
if P.suffix.lower()!='.blend' or os.path.lexists(P) or not P.parent.is_dir():
 raise RuntimeError('Output must be a new .blend in an existing folder')
base=hashlib.sha256(A.read_bytes()).hexdigest()
if base!='d59b76ec1340505772bbbec4dce027b0d3498768b702b8bb0c69557ed8f000f7':
 raise RuntimeError('Exact Haskell A texture-sharing candidate required; not a historical B source')
bpy.ops.wm.open_mainfile(filepath=str(A),load_ui=False,use_scripts=False)
report={'base_sha256':base,'models':{}}
C=-1.215
atlas={'dark':(.024,.773,.224,.966),'bronze':(.772,.77,.974,.970)}
for lod,n in enumerate(('HaskellHall','HaskellHall_LOD1','HaskellHall_LOD2')):
 o=bpy.data.objects[n]; old=o.data;assert o.matrix_world.is_identity
 U=old.uv_layers.active
 vv=[v.co.copy() for v in old.vertices]
 ff=[];uu=[];nn=[];smooth=[];cut=collections.Counter();added=collections.Counter();first_used=set()
 def local(v):return abs(v.x-C)<2.75 and 5.05<abs(v.y)<21.0 and v.z>19.62
 for p in old.polygons:
  ids=tuple(p.vertices); v=[vv[i] for i in ids]; u,w=[statistics.mean(U.data[l].uv[i] for l in p.loop_indices) for i in range(2)]
  if all(local(a) for a in v) and min(q.y for q in v)*max(q.y for q in v)>0:
   label='glass' if w>.5 and .25<u<.75 else 'bronze' if w>.75 and u>.75 else 'trim' if .5<w<.75 and u<.25 else None
   if label:cut[label]+=1;continue
  ff.append(ids); first_used.update(ids);uu.append([tuple(U.data[l].uv) for l in p.loop_indices]);nn.append([tuple(old.corner_normals[l].vector) for l in p.loop_indices]);smooth.append(p.use_smooth)
 assert dict(cut)==({'glass':8,'bronze':1240,'trim':1344} if lod==0 else {'glass':8,'bronze':40,'trim':64} if lod==1 else {'glass':8,'bronze':24}),cut
 base_faces=len(ff)
 def surface(ids,reg):
  if len(ids)>4:
   for tri in tessellate_polygon([[vv[i] for i in ids]]):surface([ids[int(i)] for i in tri],reg)
   return
  u,v,x,y=atlas[reg]; tex=[(u,v),(x,v),(x,y),(u,y)] if len(ids)==4 else [(u,v),(x,v),(x,y)]
  for k in range(1,len(ids)-1):
   ff.append([ids[0],ids[k],ids[k+1]]);uu.append([tex[0],tex[k],tex[k+1]]);nn.append([(0.,0.,0.)]*3);smooth.append(False);added[reg]+=1
 def solid(points,faces,reg):
  start=len(vv); vv.extend(Vector((C+x,y,z)) for x,y,z in points)
  for f in faces:surface([start+i for i in f],reg)
 def loft(rings, reg='bronze', base=True,top=True):
  # ring tuples center_y, half-x, half-y, z; counterclockwise seen from above.
  pts=[(s*x,c+t*y,z) for c,x,y,z in rings for s,t in ((-1,-1),(1,-1),(1,1),(-1,1))]
  faces=[]
  if base:faces.append((3,2,1,0))
  for k in range(len(rings)-1):
   for i in range(4):
    j=(i+1)%4; faces.append((4*k+i,4*k+j,4*(k+1)+j,4*(k+1)+i))
  if top:faces.append(tuple(4*(len(rings)-1)+i for i in range(4)))
  solid(pts,faces,reg)
 def box(x0,x1,y0,y1,z0,z1,reg='bronze'):
  pts=[(x,y,z) for z in (z0,z1) for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))]
  solid(pts,[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],reg)
 def ext(profile,y0,y1,reg='bronze'):
  # Force clockwise x/z profile; y+ end then faces outward.
  if sum(x*b-a*z for (x,z),(a,b) in zip(profile,profile[1:]+profile[:1]))>0:profile=profile[::-1]
  p=len(profile); pts=[(x,y,z) for y in (y0,y1) for x,z in profile]
  faces=[tuple(reversed(range(p))),tuple(range(p,2*p))]+[(i,(i+1)%p,(i+1)%p+p,i+p) for i in range(p)]
  # Traversing clockwise viewed in x/z makes first ring normal +y; side order must oppose far ring.
  solid(pts,faces,reg)
 for sign in (-1,1):
  a,b=sorted((sign*5.55,sign*20.05)); mid=(a+b)/2; length=b-a
  if lod==2:
   # Simplified shared-atlas shell preserves both seams, black vents and terminal caps.
   loft([(mid,.715,length/2,21.23),(mid,.715,length/2,22.105)],'dark',base=False,top=False)
   ext([(-.91,22.082),(.91,22.082),(.91,22.16),(0,22.27),(-.91,22.16)],a-.05,b+.05)
   for s in (-1,1):
    ext([(s*x,z) for x,z in ((.695,21.26),(2.105,19.925),(2.105,19.995),(.72,21.34))],a,b)
   y=sign*19.96
   loft([(y,1.06,.72,20.56),(y,.67,.55,21.62),(y,.67,.55,22.23)],'dark',base=False,top=False)
   loft([(y,.78,.65,22.18),(y,.55,.42,22.64),(y,.07,.06,23.36)],base=False)
   continue
  # Dark, inboard screen. Not glass and not an assertion of a solid historical passage across the attic.
  box(-.715,.715,a,b,21.23,22.105,'dark')
  # Deep copper cap with a low pitched/sloped cross section.
  ext([(-.91,22.082),(.91,22.082),(.91,22.16),(.57,22.24),(0,22.27),(-.57,22.24),(-.91,22.16)],a-.05,b+.05)
  for s in (-1,1):
   # Lower fold crosses roof according to z=21.3-.65*abs(x). Upper side overlaps the screen.
   def skirt(p): return [(s*x,z) for x,z in p]
   ext(skirt([(.695,21.20),(2.075,19.925),(2.105,19.925),(2.105,19.995),(.77,21.365),(.695,21.365)]),a,b)
   k=17 if lod==0 else (8 if lod==1 else 0)
   if k:
    for j in range(k+1):
     y=a+.10+j*(length-.20)/k
     w=.026 if lod==0 else .045
     xx=sorted((s*.695,s*.791))
     box(*xx,y-w,y+w,21.28,22.105)
     if lod==0 and 0<j<k:
      ext(skirt([(.80,21.355),(.82,21.33),(1.97,20.15),(2.0,20.15),(1.985,20.195),(.815,21.385)]),y-.021,y+.021)
    # The count is illustrative, not inferred from photo. Dark gaps are preserved between narrow rails.
    for z in (21.60,21.84) if lod==0 else (21.72,):
     xx=sorted((s*.706,s*.742))
     box(*xx,a+.015,b-.015,z-.018,z+.018)
  # End opposite the central cross-gable is clearly documented. Inboard stop remains simple.
  y=sign*19.96
  loft([(y,1.06,.72,20.56),(y,.86,.68,21.25),(y,.76,.61,21.54)])
  loft([(y,.65,.55,21.46),(y,.65,.55,22.23)],'dark')
  if lod<2:
   for x in (-.574,.574):
    box(x-.065,x+.065,y-.565,y+.565,21.45,22.25)
   for z in (21.63,21.80,21.97,22.13):
    ey=y+sign*.55; box(-.47,.47,ey-.06,ey+.06,z-.029,z+.038)
  loft([(y,.78,.65,22.18),(y,.81,.67,22.27),(y,.60,.46,22.57),(y,.56,.43,22.64),(y,.35,.29,22.92),(y,.17,.14,23.16),(y,.035,.035,23.24)])
  if lod==0:
   loft([(y,.052,.052,23.19),(y,.052,.052,23.41),(y,.007,.007,23.69)])
  else:
   loft([(y,.05,.05,23.19),(y,.011,.011,23.56)])
  # Short inboard end cheek, not an invented ornamental tower.
  start=sign*5.59
  loft([(start,.93,.14,20.32),(start,.73,.13,21.24),(start,.74,.14,22.14)])
 # Restore only used coordinates, no orphan data from removed roof semantic parts.
 used=sorted({i for f in ff for i in f}); ids={oldid:newid for newid,oldid in enumerate(used)}
 new=bpy.data.meshes.new(n+'_ModernRidge')
 new.from_pydata([vv[i] for i in used],[],[[ids[i] for i in f] for f in ff]);new.update()
 new.materials.append(old.materials[0])
 vlayer=new.uv_layers.new(name=U.name)
 for p,coords,s in zip(new.polygons,uu,smooth):
  p.use_smooth=s
  for i,u in zip(p.loop_indices,coords):vlayer.data[i].uv=u
 new.normals_split_custom_set([u for s in nn for u in s])
 o.data=new
 report['models'][n]={'triangle_count':len(ff),'removed_uv_triangles':dict(cut),'added_uv_triangles':dict(added),'preserved_before_append':base_faces,'ranges_y':[[-20.05,-5.55],[5.55,20.05]],'roof_base_rule':'Z=21.3-.65*abs(X+1.215)','roof_join_nominal_z':19.932,'lower_apron_edge_z':19.925,'external_end_center_y':[-19.96,19.96]}
if os.path.lexists(P):
 raise FileExistsError(P)
bpy.context.preferences.filepaths.save_version=0
result=bpy.ops.wm.save_as_mainfile(filepath=str(P),relative_remap=False)
if result!={'FINISHED'}:
 raise RuntimeError(result)
print(json.dumps(report,indent=2))
