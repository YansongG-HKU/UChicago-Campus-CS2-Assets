"""Restore Ratner's originally authored wall-base datum without moving the roof."""
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


SOURCE_SHA = "4e359fcd31123ceb44867256c2f1b0b4cd9d7dc8293b58cbc798183f8763e52b"
NAME = "RatnerAthletics"
TIERS = (("", 328), ("_LOD1", 201), ("_LOD2", 56))


def render(source, output):
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.use_nodes = False
    scene.render.resolution_x = 800
    scene.render.resolution_y = 535
    scene.render.resolution_percentage = 100
    for obj in scene.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name != NAME
    bpy.ops.mesh.primitive_plane_add(size=1000, location=(0, 0, 0))
    bpy.context.object.color = (.31, .36, .38, 1)
    bpy.data.objects[NAME].color = (.78, .76, .71, 1)
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_cavity = True
    ceiling = Vector((-31.195, 33, .05))
    camera = bpy.data.objects.new("Ratner wall base", bpy.data.cameras.new("Ratner wall base"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 3.4
    camera.location = ceiling + Vector((-12, -1.6, .21))
    camera.rotation_euler = (ceiling - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)


source, target, report, previews = [Path(arg).resolve() for arg in sys.argv[sys.argv.index("--") + 1:]]
if sha256(source.read_bytes()).hexdigest() != SOURCE_SHA or target.exists() or target.suffix != ".blend":
    raise ValueError("Use the audited source and a new Blender output")
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
stats = {}
for suffix, expected in TIERS:
    mesh = bpy.data.objects[NAME + suffix].data
    vertices = [v for v in mesh.vertices if abs(v.co.z - .04149) < 1e-5]
    assert len(vertices) == expected
    ids = {v.index for v in vertices}
    edges = {tuple(sorted((tuple(mesh.vertices[a].co.xy), tuple(mesh.vertices[b].co.xy))))
             for edge in mesh.edges for a, b in [tuple(edge.vertices)] if a in ids and b in ids}
    contact_length = sum((Vector(a) - Vector(b)).length for a, b in sorted(edges))
    for vertex in vertices:
        vertex.co.z = 0
    mesh.update()
    mesh.calc_loop_triangles()
    assert all(t.area > 1e-10 for t in mesh.loop_triangles)
    stats[suffix or "near"] = {"moved_vertices": expected, "triangles": len(mesh.loop_triangles),
                             "new_datum_edge_length_m_including_ground_triangulation": round(contact_length, 3)}
bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
report.write_text(json.dumps({"source_sha256": SOURCE_SHA, "candidate_sha256": sha256(target.read_bytes()).hexdigest(),
                              "old_wall_base_z_m": .04149, "new_wall_base_z_m": 0,
                              "tiers": stats}, indent=2) + "\n")
previews.mkdir()
render(source, previews / "before.png")
render(target, previews / "after.png")
