"""Trim only the covered part of opposing Tower Group wall faces at LOD0/1."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector


FAR_CANDIDATE_SHA = "02269c8a07e48847fd8b6b4fb585a185c545ed92edce437f1c862be6242c7b2e"
JUNCTIONS = (
    ("HutchinsonCommons", "MitchellTower", 0, 12.7074995, 1, -1),
    ("ReynoldsClubhouse", "MitchellTower", 1, 30.0, 1, -1),
    ("ReynoldsClubhouse", "MitchellTower", 1, 30.0, 1, 1),
    ("ReynoldsClubhouse", "MandelHall", 1, -4.0, -1, 1),
)
PLANE_TOLERANCE = 0.00002
AREA_TOLERANCE = 0.000001


def wall_faces(faces, axis, plane, outward):
    return [
        face for face in faces if face.normal[axis] * outward > .999
        and all(abs(vertex.co[axis] - plane) < PLANE_TOLERANCE for vertex in face.verts)
    ]


def projected_polygon(face, tangent):
    return Polygon([(vertex.co[tangent], vertex.co.z) for vertex in face.verts])


def replacement_face(mesh, source, xy, axis, plane, tangent, uv_layers):
    vertices = []
    for s, z in xy:
        point = Vector((0, 0, z))
        point[axis] = plane
        point[tangent] = s
        vertices.append(mesh.verts.new(point))
    face = mesh.faces.new(vertices)
    face.normal_update()
    if face.normal.dot(source.normal) < 0:
        face.normal_flip()
    face.material_index = source.material_index
    face.smooth = source.smooth
    for loop in face.loops:
        loop.copy_from_face_interp(source, False, False)
    assert face.calc_area() > 1e-10
    assert all(all(-.001 <= value <= 1.001 for value in loop[layer].uv)
               for layer in uv_layers for loop in face.loops)
    return face


def trim(scene, suffix):
    measurements = []
    for owner, cover, axis, plane, outward, opposing_direction in JUNCTIONS:
        source = scene.objects[owner + suffix]
        opposite = scene.objects[cover + suffix]
        assert source.matrix_world.is_identity and opposite.matrix_world.is_identity
        tangent = 1 - axis
        retained = bmesh.new()
        retained.from_mesh(opposite.data)
        retained.normal_update()
        cover_poly = union_all([projected_polygon(face, tangent)
                                for face in wall_faces(retained.faces, axis, plane, opposing_direction)])
        assert cover_poly.is_valid and not cover_poly.is_empty
        retained.free()

        mesh = bmesh.new()
        mesh.from_mesh(source.data)
        mesh.normal_update()
        uv_layers = list(mesh.loops.layers.uv.values())
        candidates = wall_faces(mesh.faces, axis, plane, outward)
        remove, added = [], []
        trimmed_area = 0.0
        for face in candidates:
            original = projected_polygon(face, tangent)
            if original.area < AREA_TOLERANCE:
                continue
            remainder = original.difference(cover_poly)
            difference = original.area - remainder.area
            if difference < AREA_TOLERANCE:
                continue
            remove.append(face)
            trimmed_area += difference
            for patch in get_parts(remainder):
                if patch.geom_type != "Polygon" or patch.area < AREA_TOLERANCE:
                    continue
                triangles = list(get_parts(constrained_delaunay_triangles(patch)))
                assert abs(sum(triangle.area for triangle in triangles) - patch.area) < AREA_TOLERANCE
                for triangle in triangles:
                    if triangle.area >= AREA_TOLERANCE:
                        added.append(replacement_face(mesh, face, list(triangle.exterior.coords)[:-1],
                                                      axis, plane, tangent, uv_layers))
        before = union_all([projected_polygon(face, tangent) for face in candidates] + [cover_poly])
        removed = set(remove)
        surviving = [face for face in candidates if face not in removed] + added
        after = union_all([projected_polygon(face, tangent) for face in surviving] + [cover_poly])
        lost_area = before.difference(after).area
        added_area = after.difference(before).area
        print(owner, cover, suffix, outward, opposing_direction, len(candidates), len(remove), lost_area, added_area, flush=True)
        assert remove and lost_area < .001 and added_area < .001
        overlap = cover_poly.intersection(union_all([projected_polygon(face, tangent) for face in surviving])).area
        bmesh.ops.delete(mesh, geom=remove, context="FACES")
        mesh.to_mesh(source.data)
        mesh.free()
        source.data.update()
        source.data.calc_loop_triangles()
        assert all(triangle.area > 1e-10 for triangle in source.data.loop_triangles)
        measurements.append({
            "owner": source.name, "opposite_unchanged": opposite.name, "plane_axis": axis, "plane_m": plane,
            "owner_normal_sign": outward, "cover_normal_sign": opposing_direction,
            "removed_faces": len(removed), "replacement_triangles": len(added),
            "overlap_removed_m2_summed_by_source_face": trimmed_area, "remaining_planar_overlap_m2": overlap,
            "union_lost_m2": lost_area, "union_added_m2": added_area,
        })
    return measurements


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("report", type=Path)
parser.add_argument("--dependency-dir", type=Path)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
if args.dependency_dir:
    sys.path.insert(0, str(args.dependency_dir.resolve()))
from shapely import constrained_delaunay_triangles, get_parts, union_all
from shapely.geometry import Polygon

source = args.source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest() == FAR_CANDIDATE_SHA
assert not args.output.exists()
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
data = {suffix or "near": trim(bpy.context.scene, suffix) for suffix in ("", "_LOD1")}
bpy.ops.wm.save_as_mainfile(filepath=str(args.output.resolve()), compress=True)
args.report.write_text(json.dumps({
    "source_sha256": FAR_CANDIDATE_SHA,
    "candidate_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "planes": data,
}, indent=2) + "\n")
