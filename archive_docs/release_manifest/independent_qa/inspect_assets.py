"""Independent read-only Blender evidence. One factory-empty state per file; never saves assets."""
import bpy, sys,json,hashlib,pathlib,traceback,math,struct,array,time
P=pathlib.Path

def digest(data):return hashlib.sha256(data).hexdigest()
def filehash(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def collection_digest(coll,prop,count,kind='f'):
 a=array.array(kind,[0])*count;coll.foreach_get(prop,a);return digest(a.tobytes())
def mesh(o):
 m=o.data;m.calc_loop_triangles();points=[o.matrix_world@v.co for v in m.vertices]
 lo=[min((v[i] for v in points),default=0) for i in range(3)];hi=[max((v[i] for v in points),default=0) for i in range(3)]
 uvs=[]
 for layer in m.uv_layers:
  a=array.array('f',[0])*(2*len(layer.data));layer.data.foreach_get('uv',a)
  uvs.append({'name':layer.name,'elements':len(layer.data),'finite':all(math.isfinite(v) for v in a),'sha256':digest(a.tobytes())})
 return dict(name=o.name,data_name=m.name,collections=[c.name for c in o.users_collection],vertices=len(m.vertices),edges=len(m.edges),faces=len(m.polygons),triangles=len(m.loop_triangles),bounds_min=lo,bounds_max=hi,dimensions=[hi[i]-lo[i] for i in range(3)],finite=all(math.isfinite(x) for v in points for x in v),uv_layers=uvs,materials=[x.name if x else None for x in m.materials],material_indices_sha256=collection_digest(m.polygons,'material_index',len(m.polygons),'i'),positions_sha256=collection_digest(m.vertices,'co',3*len(m.vertices)),loop_vertex_indices_sha256=collection_digest(m.loops,'vertex_index',len(m.loops),'i'),matrix_world=[list(row) for row in o.matrix_world],modifiers=[{'name':m.name,'type':m.type} for m in o.modifiers])
def image(im):
 path=im.filepath;absolute=P(bpy.path.abspath(path,library=im.library));exists=absolute.is_file()
 packed=[{'path':p.filepath,'sha256':digest(bytes(p.packed_file.data))} for p in im.packed_files]
 return dict(name=im.name,source=im.source,path=path,relative=path.startswith('//'),resolved_path=str(absolute),exists=exists,external_sha256=filehash(absolute) if exists else None,packed=packed,colorspace=im.colorspace_settings.name,alpha_mode=im.alpha_mode,size=list(im.size),channels=im.channels)
jobs=json.loads(P(sys.argv[sys.argv.index('--')+1]).read_text())
for j in jobs:
 out=P(j['report']);out.parent.mkdir(parents=True,exist_ok=True)
 p=P(j['path']);sha=filehash(p)
 if out.exists() and json.loads(out.read_text()).get('sha256')==sha:continue
 start=time.time();r={'path':str(p),'relative_path':j.get('relative_path'), 'phase':j.get('phase'),'sha256':sha,'blender_version':bpy.app.version_string}
 try:
  bpy.ops.wm.read_factory_settings(use_empty=True)
  if p.suffix.lower()=='.blend':bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  else:bpy.ops.import_scene.fbx(filepath=str(p),use_image_search=False)
  r.update(status='passed',objects=len(bpy.data.objects),meshes=[mesh(o) for o in bpy.data.objects if o.type=='MESH'],images=[image(i) for i in bpy.data.images if i.source!='VIEWER'],libraries=[{'name':x.name,'path':x.filepath} for x in bpy.data.libraries])
  r['finite']=all(m['finite'] and all(l['finite'] for l in m['uv_layers']) for m in r['meshes'])
  r['unchanged_by_inspection']=filehash(p)==sha
 except Exception as e:r.update(status='failed',error=repr(e),traceback=traceback.format_exc())
 r['elapsed_seconds']=time.time()-start;out.write_text(json.dumps(r,indent=2,ensure_ascii=False));print('QA',r['status'],p,flush=True)
