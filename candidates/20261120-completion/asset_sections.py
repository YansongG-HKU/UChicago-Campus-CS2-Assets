"""Audit roof profiles, street sections and ground contact in the three authored tiers."""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


SUFFIXES = ("", "_LOD1", "_LOD2")
STATIONS = (.1, .2, .3, .4, .5, .6, .7, .8, .9)
UP = Vector((0, 0, 1))


def hit(tree, point, direction, depth):
    location, normal, _, _ = tree.ray_cast(Vector(point), direction, depth)
    if location is None:
        return None
    return ([round(n, 5) for n in location], round(normal.dot(-direction), 5))


def building(tree, roof_grid, low, high, basis, points):
    """Keep sample coordinates identical between all three tiers."""
    roof = []
    for y in roof_grid[1]:
        row = []
        for x in roof_grid[0]:
            above = hit(tree, (x, y, high[2] + 1), -UP, high[2] - low[2] + 2)
            below = hit(tree, (x, y, low[2] - 1), UP, high[2] - low[2] + 2)
            row.append([above[0][2] if above else None, below[0][2] if below else None])
        roof.append(row)
    faces = {}
    for axis, tag in ((0, "x"), (1, "y")):
        stations = roof_grid[1 - axis]
        for direction in (-1, 1):
            vector = Vector((0, 0, 0))
            vector[axis] = direction
            start = low[axis] - 1 if direction == 1 else high[axis] + 1
            section = []
            for orthogonal in stations:
                heights = (.1, 1.5, .2 * basis, .4 * basis, .65 * basis, .82 * basis)
                profile = []
                for z in heights:
                    xyz = [0., 0., z]
                    xyz[axis] = start
                    xyz[1 - axis] = orthogonal
                    profile.append(hit(tree, xyz, vector, high[axis] - low[axis] + 2))
                section.append(profile)
            faces[tag + ("_positive" if direction < 0 else "_negative")] = section
    features = {}
    for key, (x, y) in points.items():
        above = hit(tree, (x, y, high[2] + 1), -UP, high[2] - low[2] + 2)
        below = hit(tree, (x, y, low[2] - 1), UP, high[2] - low[2] + 2)
        features[key] = {"xy_m": [x, y], "roof": above, "underside": below}
    return {"roof_grid_z_m": roof, "cardinal_sections": faces, "landmarks": features}


def snapshot(family, landmarks):
    items = {}
    for suffix in SUFFIXES:
        obj = bpy.data.objects[family + suffix]
        surface = obj.data
        surface.calc_loop_triangles()
        vertices = [obj.matrix_world @ vertex.co for vertex in surface.vertices]
        axes = [[min(v[i] for v in vertices), max(v[i] for v in vertices)] for i in range(3)]
        tree = BVHTree.FromPolygons(vertices, [tuple(t.vertices) for t in surface.loop_triangles], all_triangles=True)
        feet = {idx for idx, p in enumerate(vertices) if abs(p.z) <= .002}
        edge = sum(1 for e in surface.edges if all(i in feet for i in e.vertices))
        items[suffix] = (axes, tree, len(surface.loop_triangles), edge)
    low = [min(a[0][i][0] for a in items.values()) for i in range(3)]
    high = [max(a[0][i][1] for a in items.values()) for i in range(3)]
    grid = [[round(low[i] + f * (high[i] - low[i]), 5) for f in STATIONS] for i in range(2)]
    data = {"roof_grid_xy_m": grid, "section_z_m": [.1, 1.5, *[high[2] * f for f in (.2, .4, .65, .82)]],
            "tiers": {}}
    for suffix, (axes, tree, faces, feet) in items.items():
        data["tiers"][suffix or "near"] = {
            "world_bounds_m": axes, "triangles": faces, "ground_edge_count_with_duplicates": feet,
            **building(tree, grid, low, high, high[2], landmarks),
        }
    return data


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("baseline", type=Path)
parser.add_argument("register", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--landmarks", type=Path)
parser.add_argument("--families", nargs="+")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
config = json.loads(args.landmarks.read_text()) if args.landmarks else {}
out = {}
with args.register.open(newline="") as handle:
    for row in csv.DictReader(handle):
        name = row["asset"]
        selected = name in args.families if args.families else row["first_pass_origin"] == "static_only"
        if not selected:
            continue
        source = args.baseline / row["source_relpath"]
        digest = sha256(source.read_bytes()).hexdigest()
        assert digest == row["source_sha256"], source
        bpy.ops.wm.open_mainfile(filepath=str(source.resolve()), load_ui=False)
        out[name] = {"source_sha256": digest, "source": row["source_relpath"],
                     **snapshot(name, config.get(name, {}))}
        print(name, flush=True)
args.output.write_text(json.dumps(out, indent=2) + "\n")
