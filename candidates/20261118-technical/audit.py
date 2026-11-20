import bpy, pathlib, json, csv, sys, re, math, hashlib, numpy as np
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];BASE=pathlib.Path(args[0]);OUT=pathlib.Path(args[1]);REPO=pathlib.Path(args[2]);OUT.mkdir(parents=True,exist_ok=True)
register=list(csv.DictReader(open(REPO/'audit/20261013/review_register_136.csv',encoding='utf-8-sig')))
byfile={}
for r in register:byfile.setdefault(r['source_path'],[]).append(r)
results=[]
for n,(relative,rows) in enumerate(sorted(byfile.items())):
 if len(args)>3 and relative!=args[3]:continue
 p=BASE/relative
 record={'source':relative,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'families':[],'images':[],'errors':[]}
 try:
  bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False)
  for img in bpy.data.images:
   if img.source!='FILE':continue
   im={'name':img.name,'filepath':img.filepath,'dimensions':list(img.size),'channels':img.channels,'format':img.file_format,'packed':bool(img.packed_file),'colorspace':img.colorspace_settings.name}
   im['power_of_two_size']=all(int(x) in [512,1024,2048,4096] for x in img.size)
   if 'maskmap' in img.name.lower():
    a=np.empty(len(img.pixels),dtype=np.float32);img.pixels.foreach_get(a);a=a.reshape((-1,img.channels));im['blue_nonzero_pixels']=int(np.count_nonzero(a[:,2]>1/255+1e-6)) if img.channels>=3 else None;im['blue_max']=float(a[:,2].max()) if img.channels>=3 else None
   record['images'].append(im)
  for row in rows:
   family=row['family'];f={'row_id':row['row_id'],'family':family,'family_type':row['family_type'],'meshes':[],'missing_expected_levels':[]}
   for level in json.loads(row['levels']):
    name=family if level=='main' else family+'_'+level
    if name not in bpy.data.objects:f['missing_expected_levels'].append(name)
   relevant=[o for o in bpy.data.objects if o.type=='MESH' and (o.name==family or o.name.startswith(family+'_'))]
   for ob in relevant:
    me=ob.data;me.calc_loop_triangles();special=bool(re.search(r'_(Win|Wim|Gls|Gra|Wat)$',ob.name));coords=[ob.matrix_world@Vector(c) for c in ob.bound_box];m={'name':ob.name,'special_shader':special,'triangles':len(me.loop_triangles),'materials':[x.name if x else None for x in me.materials],'material_count':len(me.materials),'uv_layers':len(me.uv_layers),'location':list(ob.location),'rotation':list(ob.rotation_euler),'scale':list(ob.scale),'world_min':[min(c[i] for c in coords) for i in range(3)],'world_max':[max(c[i] for c in coords) for i in range(3)],'degenerate_faces':sum(p.area<1e-16 for p in me.polygons)}
    m['material_count_ok']=m['material_count']==(0 if special else 1)
    m['material_name_ok']=special or (len(me.materials)==1 and me.materials[0] and me.materials[0].name in [ob.name,ob.name+'_Mtl'])
    bad=outside=0
    for uv in me.uv_layers:
     a=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',a);bad+=int(np.count_nonzero(~np.isfinite(a)));outside+=int(np.count_nonzero((a < -1e-6)|(a>1+1e-6)))
    m['uv_nonfinite_values']=bad;m['uv_out_of_0_1_values']=outside
    f['meshes'].append(m)
   main=next((m for m in f['meshes'] if m['name']==family),None)
   lod1=next((m for m in f['meshes'] if m['name']==family+'_LOD1'),None)
   lod2=next((m for m in f['meshes'] if m['name']==family+'_LOD2'),None)
   f['lod1_ratio']=lod1['triangles']/main['triangles'] if main and lod1 and main['triangles'] else None
   f['lod2_over_500_recommendation']=bool(lod2 and lod2['triangles']>500)
   record['families'].append(f)
 except Exception as e:record['errors'].append(type(e).__name__+': '+str(e))
 results.append(record);(OUT/'source_audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('AUDITED',n+1,relative,flush=True)
print('DONE',len(results),flush=True)
