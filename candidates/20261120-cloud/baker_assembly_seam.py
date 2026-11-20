"""Apply the replayed Baker roof and transfer ownership of the buried seam."""
import hashlib
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

assembly, roof, destination = map(Path, sys.argv[sys.argv.index("--") + 1:])
if hashlib.sha256(assembly.read_bytes()).hexdigest() != "a94fb0b130c8b97366014fb847cb67db432ba96a86b10a941bc99725d6ec8a02":
    raise ValueError("Expected the exact material-patched assembly")
if destination.exists() or destination.suffix != ".blend":
    raise ValueError("Choose a new .blend path")
bpy.ops.wm.open_mainfile(filepath=str(assembly.resolve()), load_ui=False)
bpy.context.preferences.filepaths.save_version = 0

start = Vector((-4.524375, 26.67, 0))
end = Vector((16.906875, 29.4084375, 0))
tangent = (end - start).normalized()
normal = Vector((-tangent.y, tangent.x, 0))
length = (end - start).length
names = ["BakerDining", "BakerDining_LOD1", "BakerDining_LOD2"]
with bpy.data.libraries.load(str(roof.resolve()), link=False) as (available, imported):
    imported.objects = names.copy()
for name, imported_object, expected in zip(names, imported.objects, (4686, 906, 382)):
    mesh = imported_object.data
    mesh.calc_loop_triangles()
    if len(mesh.loop_triangles) != expected or not imported_object.matrix_world.is_identity:
        raise ValueError(f"Unexpected standalone roof replay: {name}")
    assembly_object = bpy.data.objects[name]
    original_mesh = assembly_object.data
    material = original_mesh.materials[0]
    if len(mesh.materials) != 1:
        raise ValueError(f"Expected one original atlas material: {name}")
    mesh.materials[0] = material
    assembly_object.data = mesh
    bpy.data.objects.remove(imported_object)
    bpy.data.meshes.remove(original_mesh)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    faces = [
        f for f in bm.faces
        if f.normal.dot(normal) > .9999
        and all(abs((v.co - start).dot(normal)) < 1e-5
                and -1e-5 < (v.co - start).dot(tangent) < length + 1e-5
                and -1e-5 <= v.co.z <= 5.80001 for v in f.verts)
    ]
    removed_area = sum(f.calc_area() for f in faces)
    print(name, len(faces), removed_area, flush=True)
    if not abs(removed_area - length * 5.8) < .001:
        raise ValueError(f"Seam area changed unexpectedly: {name}")
    bmesh.ops.delete(bm, geom=faces, context="FACES")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    mesh.calc_loop_triangles()
    assert len(mesh.loop_triangles) == expected - len(faces)
bpy.ops.wm.save_as_mainfile(filepath=str(destination.resolve()), compress=True)
