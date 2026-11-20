"""Seat the authored lawn underside onto the paired Woodlawn podium."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


BASELINES = {
    "dde66c841fd9abf82d4679496b6c360b32152c8c2a82ec0cd7a4f969e65cbea8": False,
    "e750b32ead9c5d11c09721bef6ab81631c066f489b30b8562d45ba7cf8f0b21c": True,
}
UP = Vector((0, 0, 1))
VIEW_CENTER = Vector((-.28, -39.96, 4.20))


def tree(obj, lawn_bottom=None):
    mesh = obj.data
    mesh.calc_loop_triangles()
    vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
    triangles = [tuple(p.vertices) for p in mesh.loop_triangles
                 if lawn_bottom is None or all(
                     min(abs(mesh.vertices[i].co.z - lawn_bottom), abs(mesh.vertices[i].co.z - 4.235)) < 1e-5
                     for i in p.vertices)]
    return BVHTree.FromPolygons(vertices, triangles, all_triangles=True)


def hits(mesh_tree, anchor, delta, direction):
    point, *_ = mesh_tree.ray_cast(anchor + UP * delta, direction, .12)
    return round(point.z, 6) if point is not None else None


def sample(dining, residential, lawn_bottom):
    contact = []
    lawn = tree(dining, lawn_bottom)
    terrace = tree(dining)
    dwelling = tree(residential) if residential else None
    for x in (-13, -4, 1):
        for y in (-14, -22, -29, -35):
            if not dwelling and y < -26:
                continue
            roof = terrace if y > -26 else dwelling
            anchor = dining.matrix_world @ Vector((x, y, 4.194))
            contact.append({
                "xy_dining_local_m": [x, y],
                "lawn_underside_z_m": hits(lawn, anchor, 0, UP),
                "podium_z_m": hits(roof, anchor, .008, -UP),
                "roof_owner": "WoodlawnDining" if roof is terrace else "WoodlawnResidential",
            })
    return contact


def render(dining, target):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.use_nodes = False
    scene.render.resolution_x = 780
    scene.render.resolution_y = 525
    scene.render.resolution_percentage = 100
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (.68, .72, .65)
    scene.display.shading.show_cavity = True
    for obj in scene.objects:
        if obj.type == "MESH":
            obj.hide_render = obj not in (dining, bpy.data.objects.get(dining.name.replace("Dining", "Residential")))
    camera = bpy.data.objects.new("Lawn edge review", bpy.data.cameras.new("Lawn edge review"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    center = dining.matrix_world @ VIEW_CENTER
    camera.location = center + Vector((.12, -4, .14))
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = .28
    scene.render.filepath = str(target)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)


parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("target", type=Path)
parser.add_argument("report", type=Path)
parser.add_argument("--previews", type=Path)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
source, target = args.source.resolve(), args.target.resolve()
digest = sha256(source.read_bytes()).hexdigest()
if digest not in BASELINES or target.exists() or target.suffix != ".blend":
    raise ValueError("Use the audited source and a new Blender output")
is_assembly = BASELINES[digest]
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
observations = {"source_sha256": digest, "levels": {}}
if args.previews:
    args.previews.mkdir()
    # Render previews in a disposable scene state and reload before editing.
    render(bpy.data.objects["WoodlawnDining"], args.previews / "before.png")
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
for suffix in ("", "_LOD1", "_LOD2"):
    dining = bpy.data.objects["WoodlawnDining" + suffix]
    residential = bpy.data.objects.get("WoodlawnResidential" + suffix) if is_assembly else None
    before = sample(dining, residential, 4.205)
    assert all(p["lawn_underside_z_m"] == 4.205 and p["podium_z_m"] == 4.2 for p in before)
    vertices = [v for v in dining.data.vertices if abs(v.co.z - 4.205) < 1e-5]
    corners = {(round(v.co.x, 2), round(v.co.y, 2)) for v in vertices}
    assert corners == {(-21.87, -39.96), (6.39, -39.96), (6.39, -13.32), (-18.81, -9.72)}
    for vertex in vertices:
        vertex.co.z = 4.197
    dining.data.update()
    after = sample(dining, residential, 4.197)
    assert all(p["lawn_underside_z_m"] == 4.197 and p["podium_z_m"] == 4.2 for p in after)
    lawn = tree(dining)
    assert all(hits(lawn, dining.matrix_world @ Vector((*p["xy_dining_local_m"], 4.24)),
                    0, -UP) == 4.235 for p in after)
    observations["levels"][suffix or "near"] = {"vertices_moved": len(vertices), "before": before, "after": after}
bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
observations["candidate_sha256"] = sha256(target.read_bytes()).hexdigest()
args.report.write_text(json.dumps(observations, indent=2) + "\n")
if args.previews:
    render(bpy.data.objects["WoodlawnDining"], args.previews / "after.png")
