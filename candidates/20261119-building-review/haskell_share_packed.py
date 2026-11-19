"""For a standalone Haskell copy only: use one packed image per proven duplicate."""
import bpy,hashlib,collections,sys,pathlib,json
source,output=sys.argv[sys.argv.index('--')+1:]
source=pathlib.Path(source).resolve()
output=pathlib.Path(output).resolve()
report=output.with_suffix('.json')
assert source.is_file() and not output.exists() and not report.exists() and source!=output
if hashlib.sha256(source.read_bytes()).hexdigest() != '98f513e92fd4de7d796ba7a57a479a167d0043f2d07eb874c002b59b6b81bf55':
    raise RuntimeError('Not the exact reviewed Haskell Hall A model; no changes made')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
def signature(im):
    assert im.source=='FILE' and len(im.tiles)==1 and len(im.packed_files)==1 and not im.library
    pf=im.packed_files[0]; raw=pf.packed_file.data
    return (hashlib.sha256(raw).hexdigest(),len(raw),im.colorspace_settings.name,im.alpha_mode,im.source,tuple(im.size),im.depth,im.file_format,im.use_view_as_render,im.use_half_precision)
images=[i for i in bpy.data.images if i.packed_files]
assert len(images)==19
groups=collections.defaultdict(list)
for i in images:groups[signature(i)].append(i)
assert len(groups)==10
allowed=set(bpy.data.materials)
for i,owners in bpy.data.user_map(subset=set(images)).items():
    assert all(u in allowed for u in owners) and not i.use_fake_user
def node_snapshot():
    return sorted((m.name,n.name,signature(n.image),n.interpolation,n.extension,n.projection,n.image_user.frame_start,n.image_user.frame_offset) for m in bpy.data.materials if m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.packed_files)
def geometry_snapshot():
    return {m.name:(tuple(tuple(v.co) for v in m.vertices),tuple((tuple(f.vertices),f.material_index) for f in m.polygons),tuple((l.name,tuple(tuple(d.uv) for d in l.data)) for l in m.uv_layers)) for m in bpy.data.meshes}
initial_geo=geometry_snapshot()
before=node_snapshot()
rewire=[]
for sig,ims in groups.items():
    keep=min(ims,key=lambda im:(len(im.name),im.name))
    for i in ims:
        if i==keep:continue
        users=[]
        for mat in bpy.data.materials:
            if not mat.node_tree:continue
            for n in mat.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image==i:
                    users.append((mat.name,n.name));n.image=keep
        assert users and not i.users
        rewire.append(dict(old=i.name,new=keep.name,nodes=users,bytes=sig[1],sha256=sig[0]))
        bpy.data.images.remove(i)
assert before==node_snapshot()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(output),relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(output),load_ui=False,use_scripts=False)
assert initial_geo==geometry_snapshot()
assert before==node_snapshot() and len([i for i in bpy.data.images if i.packed_files])==10
report.write_text(json.dumps(dict(source_size=source.stat().st_size,new_size=output.stat().st_size,deleted_embedded_raw_bytes=sum(x['bytes'] for x in rewire),aliases=rewire),ensure_ascii=False,indent=2)+'\n')
print(report.read_text())
