"""Compare fixed views by ray-testing the two saved Blender scenes."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


VIEWS = ((1, -1, .75), (-1, 1, .65), (0, 0, 1), (1, 1, .55), (-1, -1, .55))
MEMBERS = ("MitchellTower", "HutchinsonCommons", "ReynoldsClubhouse", "MandelHall")
FOCUS = {
    "HarperMemorialLibrary": ((22.4112, 6, 27.8), (-1, .075, .015), 7.8, 12),
    "SaiehHall": ((-3.21852, -1.48, 29.1), (1, -.16, .045), 29, 18),
    "TowerGroup": ((17.7075, 30, 5.2), (-.13, -1, .18), 17, 15),
}


def read(path, name):
    bpy.ops.wm.open_mainfile(filepath=str(path.resolve()), load_ui=False)
    result = {}
    for suffix in ("", "_LOD1", "_LOD2"):
        verts, faces = [], []
        for family in MEMBERS if name == "TowerGroup" else (name,):
            obj = bpy.data.objects[family + suffix]
            obj.data.calc_loop_triangles()
            first = len(verts)
            verts.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
            faces.extend(tuple(first + i for i in t.vertices) for t in obj.data.loop_triangles)
        result[suffix or "near"] = (verts, BVHTree.FromPolygons(verts, faces, all_triangles=True))
    return result


def raster(tree, center, direction, width, depth, size):
    axis = Vector(direction).normalized()
    right = Vector((0, 0, 1)).cross(axis)
    right = right.normalized() if right.length > .01 else Vector((1, 0, 0))
    up = axis.cross(right).normalized()
    offsets = [(index + .5 - size / 2) * width / size for index in range(size)]
    positions = [right * delta for delta in offsets]
    layers = np.zeros((size, size, 2), dtype=np.float32)
    for y, height in enumerate(reversed(offsets)):
        origin = center + axis * depth + up * height
        for x, step in enumerate(positions):
            _, normal, index, distance = tree.ray_cast(origin + step, -axis, 2 * depth)
            if index is not None:
                layers[y, x] = (distance, normal.dot(axis))
    return layers


def save_image(data, path):
    back = data[:, :, 1] < -.001
    value = np.clip(.55 + .25 * abs(data[:, :, 1]), 0, 1)
    base = np.where(back[:, :, None], (238, 122, 79), (169, 193, 179))
    rgb = np.where((data[:, :, 0] > 0)[:, :, None], base * value[:, :, None], (29, 34, 42))
    with path.open("wb") as handle:
        handle.write(f"P6\n{data.shape[1]} {data.shape[0]}\n255\n".encode())
        handle.write(rgb.astype(np.uint8).tobytes())


def measures(before, after):
    have_before, have_after = before[:, :, 0] > 0, after[:, :, 0] > 0
    both = have_before & have_after
    distance = abs(before[:, :, 0][both] - after[:, :, 0][both])
    return {
        "covered_before": int(have_before.sum()), "covered_after": int(have_after.sum()),
        "coverage_changed_pixels": int(np.count_nonzero(have_before ^ have_after)),
        "covered_distance_delta_over_2mm_pixels": int(np.count_nonzero(distance > .002)),
        "first_hit_backfacing_before": int(np.count_nonzero(before[:, :, 1] < -.001)),
        "first_hit_backfacing_after": int(np.count_nonzero(after[:, :, 1] < -.001)),
    }


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("family", choices=FOCUS)
parser.add_argument("before", type=Path)
parser.add_argument("after", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--size", type=int, default=192)
parser.add_argument("--focus", type=float, nargs=8,
                    metavar=("X", "Y", "Z", "DX", "DY", "DZ", "WIDTH", "DEPTH"))
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
args.output.mkdir()
before, after = read(args.before, args.family), read(args.after, args.family)
focus, focus_direction, width, depth = ((args.focus[:3], args.focus[3:6], *args.focus[6:])
                                        if args.focus else FOCUS[args.family])
result = {}
for tier, (verts, tree) in before.items():
    bounds = [(min(vertex[i] for vertex in verts), max(vertex[i] for vertex in verts)) for i in range(3)]
    center = Vector(tuple((start + end) / 2 for start, end in bounds))
    span = (Vector(tuple(end for _, end in bounds)) - Vector(tuple(start for start, _ in bounds))).length
    rows = {}
    for i, direction in enumerate(VIEWS):
        a = raster(tree, center, direction, span * 1.1, span, args.size)
        b = raster(after[tier][1], center, direction, span * 1.1, span, args.size)
        rows[str(direction)] = measures(a, b)
        if i in (0, 1):
            save_image(a, args.output / f"{tier}-overview{i}-before.ppm")
            save_image(b, args.output / f"{tier}-overview{i}-after.ppm")
    a = raster(tree, Vector(focus), focus_direction, width, depth, args.size)
    b = raster(after[tier][1], Vector(focus), focus_direction, width, depth, args.size)
    rows["focus"] = measures(a, b)
    save_image(a, args.output / f"{tier}-focus-before.ppm")
    save_image(b, args.output / f"{tier}-focus-after.ppm")
    result[tier] = rows
(args.output / "report.json").write_text(json.dumps({
    "pixels_per_side": args.size, "source_sha256": sha256(args.before.read_bytes()).hexdigest(),
    "candidate_sha256": sha256(args.after.read_bytes()).hexdigest(), "tiers": result,
}, indent=2) + "\n")
