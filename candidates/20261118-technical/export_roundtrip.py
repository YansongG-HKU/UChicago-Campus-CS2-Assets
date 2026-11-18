import bpy,pathlib,json,sys,hashlib,numpy as np,math
from mathutils import Vector,kdtree
args=sys.argv[sys.argv.index('--')+1:];base=pathlib.Path(args[0]);audit=json.loads(pathlib.Path(args[1]).read_text());out=pathlib.Path(args[2]);out.mkdir(parents=True,exist_ok=True)
def snapshot(ob):
 me=ob.data;me.calc_loop_triangles();points=np.array([tuple(ob.matrix_world@v.co) for v in me.vertices]);uv=[]
 for layer in me.uv_layers:
  vals=np.empty(len(layer.data)*2,dtype=np.float32);layer.data.foreach_get('uv',vals);uv.append(vals)
 return {'points':points,'triangles':len(me.loop_triangles),'materials':[m.name if m else None for m in me.materials],'uv':uv,'bounds':[points.min(axis=0).tolist(),points.max(axis=0).tolist()]}
def distance(a,b):
 tree=kdtree.KDTree(len(b))
 for i,p in enumerate(b):tree.insert(p,i)
 tree.balance();return max((tree.find(p)[2] for p in a),default=0.)
allresults=[]
for idx,s in enumerate(audit):
 bpy.ops.wm.open_mainfile(filepath=str(base/s['source']),load_ui=False)
 names=sorted({m['name'] for f in s['families'] for m in f['meshes'] if not ('PREVIEW' in m['name'].upper())})
 saved=[];folder=out/'fbx'/f'{idx+1:03d}' ;folder.mkdir(parents=True,exist_ok=True)
 for name in names:
  ob=bpy.data.objects.get(name)
  if not ob or ob.type!='MESH':continue
  before=snapshot(ob);bpy.ops.object.select_all(action='DESELECT');ob.hide_set(False);ob.select_set(True);bpy.context.view_layer.objects.active=ob
  dest=folder/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(dest),use_selection=True,object_types={'MESH'},use_mesh_modifiers=True,use_triangles=True,add_leaf_bones=False,bake_anim=False,path_mode='AUTO',axis_forward='-Z',axis_up='Y')
  saved.append((name,dest,before))
 records=[]
 for name,dest,before in saved:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(dest));meshes=[ob for ob in bpy.data.objects if ob.type=='MESH'];r={'object':name,'fbx':dest.relative_to(out).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'mesh_count':len(meshes),'fbx_version':int.from_bytes(dest.read_bytes()[23:27],'little')}
  if len(meshes)==1:
   after=snapshot(meshes[0]);r.update({'triangles_before':before['triangles'],'triangles_after':after['triangles'],'material_names_before':before['materials'],'material_names_after':after['materials'],'uv_layers_before':len(before['uv']),'uv_layers_after':len(after['uv']),'bounds_max_delta_m':float(np.max(np.abs(np.array(before['bounds'])-np.array(after['bounds'])))),'vertex_bidirectional_max_delta_m':max(distance(before['points'],after['points']),distance(after['points'],before['points']))})
   r['geometry_roundtrip_pass']=r['triangles_before']==r['triangles_after'] and r['bounds_max_delta_m']<0.0001 and r['vertex_bidirectional_max_delta_m']<0.0001 and r['uv_layers_before']==r['uv_layers_after']
  else:r['geometry_roundtrip_pass']=False
  records.append(r)
 allresults.append({'source':s['source'],'source_sha256':hashlib.sha256((base/s['source']).read_bytes()).hexdigest(),'objects':records});(out/'roundtrip.json').write_text(json.dumps(allresults,ensure_ascii=False,indent=2));print('ROUNDTRIP',idx+1,len(records),flush=True)
print('DONE',len(allresults),flush=True)
