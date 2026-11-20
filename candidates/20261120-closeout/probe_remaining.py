"""Check the Tower outlier and topology of the leading Harper backface hits."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


TOWER_PARTS = ("ReynoldsClubhouse", "MandelHall", "MitchellTower", "HutchinsonCommons")
HARPER_FACES = {
    "": (88497, 28339, 113018, 52772, 99340, 115319, 26729, 55042, 55041, 99341, 115320, 26728),
    "_LOD1": (16753, 25108, 38779, 29768, 32723, 39399, 10358, 38807, 34698, 34697, 39361, 39360),
}


def make_bvh(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    return BVHTree.FromPolygons(
        [obj.matrix_world @ v.co for v in mesh.vertices],
        [tuple(tri.vertices) for tri in mesh.loop_triangles], all_triangles=True,
    )


def read(path, expected_sha):
    digest = sha256(path.read_bytes()).hexdigest()
    if digest != expected_sha:
        raise ValueError(f"Unexpected source bytes: {path}")
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)


def tower(path, expected_sha):
    read(path, expected_sha)
    tiers = {}
    for suffix in ("", "_LOD1", "_LOD2"):
        trees = {name: make_bvh(bpy.data.objects[name + suffix]) for name in TOWER_PARTS}
        x = 13.707499504
        rows = []
        offsets = [i / 10 for i in range(-3, 4)]
        for dx in offsets:
            for dz in offsets:
                for label, origin, ray in (
                    ("north", (x + dx, 75, 2 + dz), (0, -1, 0)),
                    ("south", (x + dx, -75, 2 + dz), (0, 1, 0)),
                    ("west", (-80, -4 + dx, 2 + dz), (1, 0, 0)),
                    ("east", (80, -4 + dx, 2 + dz), (-1, 0, 0)),
                ):
                    direction = Vector(ray)
                    hits = []
                    for name, tree in trees.items():
                        pos, n, _, distance = tree.ray_cast(Vector(origin), direction, 160)
                        if pos is not None:
                            hits.append((distance, name, tuple(round(v, 5) for v in pos), round(n.dot(-direction), 5)))
                    first = min(hits)[1:] if hits else None
                    rows.append([label, dx, dz, first])
        tiers[suffix or "near"] = rows
    return {"source_sha256": expected_sha, "tiers": tiers}


def harper(path, expected_sha):
    read(path, expected_sha)
    tiers = {}
    for suffix, samples in HARPER_FACES.items():
        mesh = bpy.data.objects["HarperMemorialLibrary" + suffix].data
        edges = defaultdict(list)
        for p in mesh.polygons:
            for key in p.edge_keys:
                edges[key].append(p.index)
        rows = []
        for index in samples:
            stack, component = [index], {index}
            while stack:
                for key in mesh.polygons[stack.pop()].edge_keys:
                    for other in edges[key]:
                        if other not in component:
                            component.add(other)
                            stack.append(other)
            used = Counter(key for f in component for key in mesh.polygons[f].edge_keys)
            affected = [mesh.vertices[i].co for f in component for i in mesh.polygons[f].vertices]
            rows.append({
                "face": index, "component_polygons": len(component),
                "open_boundary_edges": sum(count == 1 for count in used.values()),
                "seed_normal": [round(v, 5) for v in mesh.polygons[index].normal],
                "bounds_m": [[round(min(v[a] for v in affected), 5), round(max(v[a] for v in affected), 5)]
                             for a in range(3)],
            })
        tiers[suffix or "near"] = rows
    return {"source_sha256": expected_sha, "tiers": tiers}


old, new, library, destination = (Path(v).resolve() for v in sys.argv[sys.argv.index("--") + 1:])
data = {
    "tower_original": tower(old, "be0ac5a6c9914ccc9db2a667ad9c84ed53730ab8c4c6d2fef839f29a5864c1cf"),
    "tower_candidate": tower(new, "06f75668c992665e3b274eafd435be8101a780d2109891c6ebe4455a9ee1c095"),
    "harper_candidate": harper(library, "06934d07b62e3b96195bd1df22688bf04b0f3484fe40fa4a3edf382ed849fe48"),
}
destination.write_text(json.dumps(data, separators=(",", ":")) + "\n")
