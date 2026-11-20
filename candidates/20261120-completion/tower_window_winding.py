"""Turn only atlas-verified window panes toward their documented outside face."""
from hashlib import sha256
import json
from pathlib import Path
import sys

import bmesh
import bpy


HARPER = "HarperMemorialLibrary"
SAIEH = "SaiehHall"
HASHES = {
    HARPER: "bb03527fb16b5e1e6dae9281108209f860bcbf3de6ab761c3fa0672c6976ece6",
    SAIEH: "bcd8d7dbae3d68340c1352dda766a58b3598fbd2b890d6b24207079b8a2d5474",
}
GLASS = (.25, .50, .75, 1)
DARK = (0, .75, .25, 1)


def pane_groups(asset, suffix):
    if asset == HARPER:
        count = {"": 13, "_LOD1": 5, "_LOD2": 0}[suffix]
        return [(f"inner_tower_{side}_{y}", 0, side * 22.4112, y - 1.8, y + 1.8, 24.7, 30.96, -side,
                 GLASS, count) for side in (-1, 1) for y in (-6, 6)]
    far = suffix == "_LOD2"
    groups = [
        ("great_tower_east_lancet", 0, -3.20692 if far else -3.21852, -2.92, -.05, 18.26, 39.8, 1,
         GLASS if far else DARK, {"": 13, "_LOD1": 11, "_LOD2": 2}[suffix]),
        ("great_tower_east_upper_lancet", 0, -3.20692 if far else -3.21852, -2.96, -.02, 41.5, 47.6, 1,
         GLASS if far else DARK, {"": 13, "_LOD1": 11, "_LOD2": 2}[suffix]),
        ("square_tower_west", 0, 31.795, -13.85, -9.12, 1.4, 28.8, -1, GLASS, 2 if far else 12),
        ("square_tower_north", 1, -6.42, 33.99, 38.73, 1.4, 28.8, 1, GLASS, 2 if far else 12),
        ("chapel_court_windows", 0, -34.825 if far else -34.83, -13.4, 14.1, 7.5, 16, 1, GLASS,
         {"": 78, "_LOD1": 66, "_LOD2": 6}[suffix]),
    ]
    if far:
        groups.extend([
            ("office_court_windows", 1, 2.42, 19, 32, 4.9, 14.5, -1, GLASS, 4),
            ("west_range_court_windows", 1, 3.37, -32.1, -12.1, 4.9, 14.5, -1, GLASS, 6),
        ])
    return groups


def belongs(mesh, poly, spec):
    _, axis, plane, low, high, z_low, z_high, _, region, _ = spec
    tangent = 1 - axis
    return all(
        abs(mesh.vertices[i].co[axis] - plane) < .00003
        and low <= mesh.vertices[i].co[tangent] <= high and z_low <= mesh.vertices[i].co.z <= z_high
        for i in poly.vertices
    ) and all(
        region[0] - 1e-5 <= mesh.uv_layers.active.data[j].uv.x <= region[2] + 1e-5
        and region[1] - 1e-5 <= mesh.uv_layers.active.data[j].uv.y <= region[3] + 1e-5
        for j in poly.loop_indices
    )


def face_attributes(mesh, poly):
    return (poly.material_index, poly.use_smooth, tuple(sorted(
        (mesh.loops[i].vertex_index, *(tuple(layer.data[i].uv) for layer in mesh.uv_layers))
        for i in poly.loop_indices)))


def fix(mesh, specs):
    affected = {}
    groups = {}
    for spec in specs:
        name, axis, _plane, _low, _high, _z_low, _z_high, sign, _region, expected = spec
        matching = [p for p in mesh.polygons if belongs(mesh, p, spec)]
        assert len(matching) == expected and all(p.normal[axis] * sign < -.98 for p in matching), name
        assert not any(p.index in affected for p in matching)
        affected.update({p.index: (axis, sign) for p in matching})
        groups[name] = {"flipped_faces": len(matching), "face_indices": [p.index for p in matching],
                        "outward_normal_axis": axis, "outward_normal_sign": sign,
                        "surface_area_m2_counted_by_face": sum(p.area for p in matching)}
    if not affected:
        return {"groups": groups, "existing_custom_normals_preserved": bool(mesh.has_custom_normals)}

    retained = [face_attributes(mesh, p) for p in mesh.polygons]
    vertices = [tuple(v.co) for v in mesh.vertices]
    uses_custom = bool(mesh.has_custom_normals)
    normals = None
    if uses_custom:
        normals = { (p.index, mesh.loops[i].vertex_index): tuple(mesh.corner_normals[i].vector)
                  for p in mesh.polygons if p.index not in affected for i in p.loop_indices }
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    for index in affected:
        bm.faces[index].normal_flip()
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    assert [face_attributes(mesh, p) for p in mesh.polygons] == retained
    assert [tuple(v.co) for v in mesh.vertices] == vertices
    assert all(mesh.polygons[i].normal[axis] * sign > .98 for i, (axis, sign) in affected.items())
    max_normal_delta = None
    if normals is not None:
        adjusted = [None] * len(mesh.loops)
        for p in mesh.polygons:
            for loop in p.loop_indices:
                adjusted[loop] = (tuple(p.normal) if p.index in affected
                                  else normals[p.index, mesh.loops[loop].vertex_index])
        mesh.normals_split_custom_set(adjusted)
        mesh.update()
        max_normal_delta = max(abs(a - b)
                               for p in mesh.polygons if p.index not in affected for loop in p.loop_indices
                               for a, b in zip(adjusted[loop], mesh.corner_normals[loop].vector))
        assert max_normal_delta < .01
    return {"groups": groups, "existing_custom_normals_preserved": uses_custom,
            "unmodified_corner_normal_max_component_delta": max_normal_delta}


asset, source_name, destination, proof = sys.argv[sys.argv.index("--") + 1:]
source, output, report = [Path(value).resolve() for value in (source_name, destination, proof)]
assert sha256(source.read_bytes()).hexdigest() == HASHES[asset] and not output.exists()
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
results = {}
for suffix in ("", "_LOD1", "_LOD2"):
    obj = bpy.data.objects[asset + suffix]
    assert obj.matrix_world.is_identity
    results[suffix or "near"] = fix(obj.data, pane_groups(asset, suffix))
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
report.write_text(json.dumps({"source_sha256": HASHES[asset], "candidate_sha256": sha256(output.read_bytes()).hexdigest(),
                              "tiers": results}, indent=2) + "\n")
