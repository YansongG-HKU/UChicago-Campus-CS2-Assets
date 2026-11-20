"""Remove only non-renderable zero area triangles from five legacy split FBXs."""
import array
import json
from pathlib import Path
import shutil
import sys

import bpy
import numpy as np
from io_scene_fbx import parse_fbx, encode_bin
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable_readback import encode_node, sha, typed_tree_hash, visit

FILES = {
    'ButlerLibrary': {'NA_ButlerLibrary_11x7.fbx': 10},
    'LowMemorialLibrary': {'NA_ColumbiaLowLibrary_13x10.fbx': 8},
    'MathematicsHall': {'NA_MathematicsHall_7x5.fbx': 4},
    'StPaulsChapel': {'NA_StPaulsChapel_4x6.fbx': 2, 'NA_StPaulsChapel_4x6_LOD1.fbx': 2},
}
TYPES = {
    b'Normals': 3, b'Binormals': 3, b'Tangents': 3, b'UV': 2,
    b'NormalsIndex': 1, b'UVIndex': 1, b'Materials': 1, b'Smoothing': 1,
}
VIEWS = ((1, -1, .8), (-1, 1, .7), (1, 1, .2), (-1, -1, .1), (0, 0, 1))

def child(root, name):
    return next(e for e in root.elems if e.id == name)

def rewrite(original, output, expected_removed):
    root, version = parse_fbx.parse(str(original))
    geometries = [n for n in visit(root) if n.id == b'Geometry']
    assert len(geometries) == 1
    geo = geometries[0]
    vertex_node = child(geo, b'Vertices')
    polygon_node = child(geo, b'PolygonVertexIndex')
    positions = np.asarray(vertex_node.props[0]).reshape(-1, 3)
    polygon_index = np.asarray(polygon_node.props[0]).reshape(-1, 3)
    assert np.all(polygon_index[:, :2] >= 0) and np.all(polygon_index[:, 2] < 0)
    indices = polygon_index.copy()
    indices[:, 2] = ~indices[:, 2]
    corners = positions[indices]
    lengths = np.linalg.norm(np.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0]), axis=1)
    # Require exact degeneracy from the source binary, before any Blender rounding.
    keep = lengths == 0
    assert int(keep.sum()) == expected_removed, (original, int(keep.sum()), expected_removed)
    keep = ~keep
    loop_keep = np.repeat(keep, 3)
    polygon_node.props[0] = array.array(polygon_node.props[0].typecode, polygon_index[keep].flatten())
    edge_node = child(geo, b'Edges')
    retained_edges = {}
    new_indices = indices[keep]
    for face, (a,b,c) in enumerate(new_indices.tolist()):
        for offset, ends in enumerate(((a,b), (b,c), (c,a))):
            retained_edges.setdefault(tuple(sorted(ends)), face * 3 + offset)
    rebuilt = array.array(edge_node.props[0].typecode)
    edge_keys = set()
    for value in edge_node.props[0]:
        face, offset = divmod(value, 3)
        key = tuple(sorted((indices[face, offset], indices[face, (offset + 1) % 3])))
        if key in retained_edges and key not in edge_keys:
            rebuilt.append(retained_edges[key])
            edge_keys.add(key)
    assert edge_keys == set(retained_edges), original
    edge_node.props[0] = rebuilt

    for layer in (n for n in geo.elems if n.id.startswith(b'LayerElement')):
        mapping = child(layer, b'MappingInformationType').props[0]
        reference = child(layer, b'ReferenceInformationType').props[0]
        if mapping in (b'AllSame', b'ByVertice', b'ByVertex'):
            continue
        mask = {b'ByPolygonVertex': loop_keep, b'ByPolygon': keep}[mapping]
        assert reference in (b'Direct', b'IndexToDirect')
        for node in layer.elems:
            if not node.props or not isinstance(node.props[0], array.array):
                continue
            if reference == b'IndexToDirect' and (node.id not in (b'Materials',) and not node.id.endswith(b'Index')):
                continue
            chunk = TYPES[node.id]
            data = node.props[0]
            assert len(data) == len(mask) * chunk, (node.id, mapping, len(data), len(mask), chunk)
            node.props[0] = array.array(data.typecode, np.asarray(data).reshape(-1, chunk)[mask].flatten())
    normalized = typed_tree_hash(root)
    with encode_bin.FBXElem.enable_multithreading_cm():
        encoded = encode_node(root)
    encode_bin.write(str(output), encoded, version)
    adjusted, adjusted_version = parse_fbx.parse(str(output))
    assert adjusted_version == version and typed_tree_hash(adjusted) == normalized
    return version

def snapshot(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path), use_image_search=False)
    models = [o for o in bpy.data.objects if o.type == 'MESH']
    assert len(models) == 1, path
    mesh = models[0].data
    mesh.calc_loop_triangles()
    positions = [tuple(models[0].matrix_world @ v.co) for v in mesh.vertices]
    faces = [tuple(t.vertices) for t in mesh.loop_triangles if t.area > 1e-10]
    mask = [t for t in mesh.loop_triangles if t.area > 1e-10]
    uv = np.array([[tuple(layer.uv[l].vector) for t in mask for l in t.loops] for layer in mesh.uv_layers])
    normals = np.array([tuple(mesh.corner_normals[l].vector) for t in mask for l in t.loops])
    mat = [mesh.materials[mesh.polygons[t.polygon_index].material_index].name for t in mask]
    images = sorted((i.name, sha(Path(bpy.path.abspath(i.filepath)))) for i in bpy.data.images if i.source == 'FILE')
    return np.array(positions), faces, uv, normals, mat, images, len(mesh.loop_triangles)

def image(points, faces, scene_bounds):
    tree = BVHTree.FromPolygons(points, faces, all_triangles=True)
    center, span = scene_bounds
    canvas = np.zeros((124, 124*len(VIEWS), 3), dtype=np.uint8)
    for index,direction in enumerate(VIEWS):
        direction = Vector(direction).normalized()
        right = Vector((0, 0, 1)).cross(direction)
        right = right.normalized() if right.length > .01 else Vector((1, 0, 0))
        up = direction.cross(right).normalized()
        start = center + direction*span
        light = (direction*.8 + up*.55 - right*.24).normalized()
        for y in range(124):
            scan = start + up * ((.5 - (y+.5)/124)*span)
            for x in range(124):
                p, n, face, _ = tree.ray_cast(scan + right * (((x+.5)/124 - .5)*span),
                                               -direction,3*span)
                rgb = (25,31,39) if face is None else (np.array([224,228,234]) *
                        (.48 + .46*max(0, n.dot(light)))).astype(np.uint8)
                canvas[y,124*index+x] = rgb
    return canvas

def png(path, a):
    image = bpy.data.images.new(path.stem, a.shape[1], a.shape[0], alpha=True)
    rgba = np.ones((*a.shape[:2],4), dtype=np.float32)
    rgba[:,:,:3] = a / 255
    image.pixels.foreach_set(rgba[::-1].flatten())
    image.filepath_raw = str(path)
    image.file_format = 'PNG'
    image.save()
    bpy.data.images.remove(image)

base, target = map(lambda p: Path(p).resolve(), sys.argv[sys.argv.index('--')+1:])
target.mkdir()
records = {}
for asset, filenames in FILES.items():
    initial = base / asset
    published = target / asset
    shutil.copytree(initial, published)
    records[asset] = []
    for name, expected in filenames.items():
        source = initial / name
        output = published / name
        version = rewrite(source, output, expected)
        a,b = snapshot(source), snapshot(output)
        assert a[1] == b[1] and np.array_equal(a[2],b[2]) and a[4:6] == b[4:6], name
        assert np.array_equal(a[0],b[0]) and a[-1] - b[-1] == expected and len(b[1]) == b[-1], name
        delta = float(np.max(np.abs(a[3]-b[3])))
        assert delta < 1e-5, (name, delta)
        bbox = a[0].min(axis=0), a[0].max(axis=0)
        bounds = (Vector((bbox[0]+bbox[1])/2), float(np.linalg.norm(bbox[1]-bbox[0]))*1.05)
        before_view = image(a[0], a[1], bounds)
        after_view = image(b[0], b[1], bounds)
        assert np.array_equal(before_view, after_view), name
        png(target / (name + '-same-view.png'), np.concatenate([before_view,after_view],axis=0))
        records[asset].append({
            'fbx': name, 'version': version,
            'old_sha256': sha(source), 'new_sha256': sha(output),
            'old_bytes': source.stat().st_size, 'new_bytes': output.stat().st_size,
            'old_triangles': a[-1], 'new_triangles': b[-1], 'removed_zero_area_triangles': expected,
            'five_same_camera_view_different_pixels': 0, 'max_corner_normal_component_delta': delta,
            'nondegenerate_topology_uv_bounds_materials_and_images_equal': True,
        })
        print(asset,name,expected,'verified',flush=True)
(target / 'zero-area-readback.json').write_text(json.dumps(records, indent=2) + '\n')
