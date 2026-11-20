"""Trace roof and underside grids without including scene presentation objects."""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


UP = Vector((0, 0, 1))
SUFFIXES = ("", "_LOD1", "_LOD2")
PALEVSKY_POINTS = {
    # Each pair includes a representative wing and an adjacent open court
    # or setback, using the individual source's local metre coordinates.
    "MaxPalevskyWest": {"west_wing": (-13, 0), "north_wing": (5, 20), "open_court": (0, 5)},
    "MaxPalevskyCentral": {"central_bar": (0, 0), "south_projection": (0, -11),
                           "north_west_stair": (-28, 10), "north_east_stair": (29, 10), "setback": (0, 11)},
    "MaxPalevskyEast": {"east_wing": (18, 0), "south_wing": (-10, -26),
                        "north_wing": (-10, 26), "open_court": (0, 0)},
}


def data(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
    bounds = [(min(v[i] for v in vertices), max(v[i] for v in vertices)) for i in range(3)]
    triangles = [tuple(p.vertices) for p in mesh.loop_triangles]
    on_ground = {i for i, v in enumerate(vertices) if abs(v.z) <= .002}
    ground_edges = {tuple(sorted((tuple(round(x, 5) for x in vertices[a]),
                                  tuple(round(x, 5) for x in vertices[b]))))
                    for edge in mesh.edges for a, b in [tuple(edge.vertices)] if a in on_ground and b in on_ground}
    edge_length = sum((Vector(a) - Vector(b)).length for a, b in sorted(ground_edges))
    return bounds, len(triangles), BVHTree.FromPolygons(vertices, triangles, all_triangles=True), round(edge_length, 3)


def shoot(tree, bounds, x, y):
    low, high = bounds[2]
    depth = high - low + 2
    roof, *_ = tree.ray_cast(Vector((x, y, high + 1)), -UP, depth)
    floor, *_ = tree.ray_cast(Vector((x, y, low - 1)), UP, depth)
    return [round(roof.z, 5) if roof is not None else None, round(floor.z, 5) if floor is not None else None]


def family(name, size):
    meshes = [bpy.data.objects[name + suffix] for suffix in SUFFIXES]
    probes = [data(mesh) for mesh in meshes]
    common = [(min(bounds[i][0] for bounds, *_ in probes), max(bounds[i][1] for bounds, *_ in probes))
              for i in range(2)]
    xs, ys = [[low + (high - low) * (i + .5) / size for i in range(size)] for low, high in common]
    result = {"grid_size": size, "grid_xy_m": common, "tiers": {}}
    footprints = []
    for suffix, (bounds, triangles, tree, edge_length) in zip(SUFFIXES, probes):
        samples = [shoot(tree, bounds, x, y) for y in ys for x in xs]
        footprint = {i for i, (roof, floor) in enumerate(samples) if roof is not None or floor is not None}
        footprints.append(footprint)
        near = footprints[0]
        if not suffix:
            near_samples = samples
        visible_ground = sum(floor is not None and abs(floor - bounds[2][0]) <= .02 for _, floor in samples)
        result["tiers"][suffix or "near"] = {
            "bounds_m": [[round(p, 5) for p in axis] for axis in bounds],
            "opaque_triangles": triangles,
            "covered_columns": len(footprint),
            "columns_touching_lowest_datum_within_20mm": visible_ground,
            "unique_edge_length_with_both_endpoints_at_z0_m": edge_length,
            "lost_columns_from_near": len(near - footprint),
            "added_columns_from_near": len(footprint - near),
            "lost_columns_near_roof_range_m": [
                fn(near_samples[i][0] for i in near - footprint if near_samples[i][0] is not None)
                for fn in (min, max)
            ] if any(near_samples[i][0] is not None for i in near - footprint) else [],
            "named_columns": {feature: {"xy_m": [x, y], "roof_and_underside_m": shoot(tree, bounds, x, y)}
                              for feature, (x, y) in PALEVSKY_POINTS.get(name, {}).items()},
        }
        if name == "CobbGate":
            ymin, ymax = bounds[1]
            through = {}
            for z in (1, 2, 3.9, 4.75, 5.2, 5.5):
                clear = []
                for x in (-2.5, -2, -1, 0, 1, 2, 2.5):
                    hit, *_ = tree.ray_cast(Vector((x, ymin - 1, z)), Vector((0, 1, 0)), ymax - ymin + 2)
                    if hit is None:
                        clear.append(x)
                through[str(z)] = clear
            result["tiers"][suffix or "near"]["cobb_gate_through_passage_clear_x_m_by_z_m"] = through
    return result


parser = argparse.ArgumentParser()
parser.add_argument("root", type=Path)
parser.add_argument("register", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--size", type=int, default=41)
parser.add_argument("--families", nargs="+")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
result = {}
current_source = None
with args.register.open() as stream:
    for row in csv.DictReader(stream):
        name = row["asset"]
        if args.families and name not in args.families:
            continue
        path = (args.root / row["source_relpath"]).resolve()
        if path != current_source:
            checksum = sha256()
            with path.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    checksum.update(block)
            if checksum.hexdigest() != row["source_sha256"]:
                raise ValueError(f"Source hash changed for {path}")
            bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
            current_source = path
        result[name] = {"source_sha256": row["source_sha256"], **family(name, args.size)}
        print(name, flush=True)
args.output.write_text(json.dumps(result, indent=2) + "\n")
