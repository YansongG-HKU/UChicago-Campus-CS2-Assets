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
    return bounds, len(triangles), BVHTree.FromPolygons(vertices, triangles, all_triangles=True)


def shoot(tree, bounds, x, y):
    low, high = bounds[2]
    depth = high - low + 2
    roof, *_ = tree.ray_cast(Vector((x, y, high + 1)), -UP, depth)
    floor, *_ = tree.ray_cast(Vector((x, y, low - 1)), UP, depth)
    return [round(roof.z, 5) if roof is not None else None, round(floor.z, 5) if floor is not None else None]


def family(name, size):
    meshes = [bpy.data.objects[name + suffix] for suffix in SUFFIXES]
    probes = [data(mesh) for mesh in meshes]
    common = [(min(bounds[i][0] for bounds, _, _ in probes), max(bounds[i][1] for bounds, _, _ in probes))
              for i in range(2)]
    xs, ys = [[low + (high - low) * (i + .5) / size for i in range(size)] for low, high in common]
    result = {"grid_size": size, "grid_xy_m": common, "tiers": {}}
    footprints = []
    for suffix, (bounds, triangles, tree) in zip(SUFFIXES, probes):
        samples = [shoot(tree, bounds, x, y) for y in ys for x in xs]
        footprint = {i for i, (roof, floor) in enumerate(samples) if roof is not None or floor is not None}
        footprints.append(footprint)
        near = footprints[0]
        visible_ground = sum(floor is not None and abs(floor - bounds[2][0]) <= .02 for _, floor in samples)
        result["tiers"][suffix or "near"] = {
            "bounds_m": [[round(p, 5) for p in axis] for axis in bounds],
            "opaque_triangles": triangles,
            "covered_columns": len(footprint),
            "columns_touching_lowest_datum_within_20mm": visible_ground,
            "lost_columns_from_near": len(near - footprint),
            "added_columns_from_near": len(footprint - near),
            "named_columns": {feature: {"xy_m": [x, y], "roof_and_underside_m": shoot(tree, bounds, x, y)}
                              for feature, (x, y) in PALEVSKY_POINTS.get(name, {}).items()},
        }
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
