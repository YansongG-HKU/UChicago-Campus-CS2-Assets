"""Make a separate review assembly with one wall at the Cathey–Burton join."""
import hashlib
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

cathey, burton, target = [Path(value).resolve() for value in sys.argv[sys.argv.index('--')+1:]]
for path, expected in [
    (cathey,'ad6007625b8f320b1531bff4cafde5eb425bd50e80470b00ef7952f14f216675'),
    (burton,'24ca75b6b870c6f520a4308116c0ef5f3bfe6d8d40f4135a58c9edddb70230bb'),
]:
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f'Unexpected source: {path.name}')
if target.exists() or target.suffix != '.blend':
    raise ValueError('Choose a new .blend path')
bpy.ops.wm.open_mainfile(filepath=str(cathey), load_ui=False)

suffixes = ('','_LOD1','_LOD2')
with bpy.data.libraries.load(str(burton), link=False) as (available, loaded):
    loaded.objects = ['BurtonJudsonCourts'+suffix for suffix in suffixes]
for obj in loaded.objects:
    bpy.context.scene.collection.objects.link(obj)
    obj.hide_render = '_LOD' in obj.name
for suffix, face_count in zip(suffixes,(12,2,2)):
    name = 'CatheyDining'+suffix
    obj = bpy.data.objects[name]
    obj.location = Vector((6.3,-43.3,0))
    pane = bpy.data.objects.get(name+'_Gls')
    if pane:
        pane.location = obj.location
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    faces = [f for f in bm.faces if f.normal.y > .999 and all(
         abs(v.co.y-14)<.0001 and abs(v.co.x)<=5.0001 and
         -.0001<=v.co.z<=4.8001 for v in f.verts)]
    assert len(faces)==face_count and abs(sum(f.calc_area() for f in faces)-48)<1e-4
    bmesh.ops.delete(bm, geom=faces, context='FACES')
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    print(name, face_count)
bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
