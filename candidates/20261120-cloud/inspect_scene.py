"""Fresh-process Blender inspection; writes evidence outside the baseline.
blender -b -t 2 --factory-startup --disable-autoexec --python-exit-code 1
  --python inspect_scene.py -- SOURCE OUTPUT_DIRECTORY [--fbx]
"""
import bpy, hashlib, json, math, pathlib, sys, time, resource
from mathutils import Vector
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:]
src=pathlib.Path(args[0]);out=pathlib.Path(args[1]);out.mkdir(parents=True,exist_ok=True)
start=time.monotonic()
if '--fbx' in args:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(src),use_image_search=False)
else:
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False)
record={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'import_seconds':time.monotonic()-start,'meshes':[]}
objects=[o for o in bpy.data.objects if o.type=='MESH']
for o in objects:
    m=o.data;m.calc_loop_triangles();pts=[o.matrix_world@v.co for v in m.vertices]
    r={'name':o.name,'vertices':len(pts),'triangles':len(m.loop_triangles),'uv_layers':len(m.uv_layers),'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'materials':[s.name if s else None for s in m.materials],'zero_triangles':sum(t.area<=1e-10 for t in m.loop_triangles),'matrix':[list(row) for row in o.matrix_world]}
    if 'Levi' in o.name:
        tree=BVHTree.FromPolygons(pts,[tuple(p.vertices) for p in m.polygons])
        rays=[]
        for y in (-2,-1,0,1,2):
            for z in (0.2,1.0,1.8,2.5,4.0,6.0):
                origin=Vector((-20,y,z));hits=[]
                for n in range(20):
                    p,normal,idx,d=tree.ray_cast(origin,Vector((1,0,0)),40)
                    if p is None:break
                    hits.append(list(p));origin=p+Vector((0.0001,0,0))
                rays.append({'y':y,'z':z,'hits':hits})
        r['west_east_portal_rays']=rays
    record['meshes'].append(r)
record['images']=[{'name':i.name,'filepath':i.filepath,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
record['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
(out/'inspection.json').write_text(json.dumps(record,indent=2))
if '--fbx' not in args:
    scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    for ob in objects:ob.hide_render=('LOD' in ob.name or 'PREVIEW' in ob.name.upper() or 'ground' in ob.name.lower())
    shown=[o for o in objects if not o.hide_render]
    points=[o.matrix_world@Vector(v) for o in shown for v in o.bound_box]
    lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));center=(lo+hi)/2
    cam_data=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',cam_data);scene.collection.objects.link(cam);scene.camera=cam;cam_data.type='ORTHO';cam_data.ortho_scale=max(hi-lo)*1.3;cam_data.clip_end=10000
    for name,direction in [('south',(0,-1,.45)),('northwest',(-1,1,.7)),('top',(0,0,1))]:
        cam.location=center+Vector(direction).normalized()*max(hi-lo)*3;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('INSPECT_DONE',json.dumps({'source':str(src),'meshes':len(objects),'elapsed':time.monotonic()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}),flush=True)
