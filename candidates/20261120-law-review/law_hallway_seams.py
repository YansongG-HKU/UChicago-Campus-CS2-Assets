"""Resolve co-planar end faces in the two halls of the current combined file."""
import hashlib
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source, target = [Path(s).resolve() for s in sys.argv[sys.argv.index('--')+1:]]
if hashlib.sha256(source.read_bytes()).hexdigest() != 'dd512bcb190c5b7bc962b39c09652c716c6feab41d5296a514ae95693824faca':
    raise ValueError('Expected the locked quadrangle assembly')
if target.exists() or target.suffix != '.blend':
    raise ValueError('Choose a new .blend output')
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)

for suffix, expected_count, expected_area in [('',10,32.00281),('_LOD1',8,32),('_LOD2',4,90)]:
    classroom = bpy.data.objects['LawClassroomAdministration'+suffix]
    library = bpy.data.objects['DAngeloLawLibrary'+suffix]
    mesh = classroom.data
    library.data.calc_loop_triangles()
    tree = BVHTree.FromPolygons(
        [library.matrix_world @ v.co for v in library.data.vertices],
        [tuple(t.vertices) for t in library.data.loop_triangles], all_triangles=True)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    removable = []
    for x, orientation in [(-33.25,1),(8.75,-1)]:
        faces = [face for face in bm.faces if face.normal.x*orientation > .999 and all(
            abs(v.co.x-x)<.0001 and -36.7501 <= v.co.y <= -26.7499
            and -.0001 <= v.co.z <= 4.5001 for v in face.verts)]
        normal = Vector((orientation,0,0))
        for face in faces:
            # For each candidate facet check its centre and three interior
            # near-corner points are backed by the library's opposite face.
            center = face.calc_center_median()
            for local in [center,*[center.lerp(v.co,.92) for v in face.verts]]:
                world = classroom.matrix_world @ local
                point, backing_normal, _, _ = tree.ray_cast(world - .00015*normal,normal,.0003)
                if point is None or (point-world).length > .00002 or backing_normal.dot(normal)>-.999:
                    raise ValueError(f'No opposite library face along the seam: {suffix} {tuple(world)}')
        removable.extend(faces)
    assert len(removable)==expected_count
    assert abs(sum(f.calc_area() for f in removable)-expected_area)<.0001
    bmesh.ops.delete(bm, geom=removable, context='FACES')
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
