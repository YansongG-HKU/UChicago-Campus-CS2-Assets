"""Export and reimport new tiers, or compare packaged FBXs to their Blender source."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import sys
import time

import bpy
import numpy as np
from io_scene_fbx import parse_fbx
from mathutils import kdtree


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    points = np.array([tuple(obj.matrix_world @ v.co) for v in mesh.vertices])
    local_points = np.array([tuple(v.co) for v in mesh.vertices])
    vertices = np.array([list(t.vertices) for t in mesh.loop_triangles])
    loops = np.array([list(t.loops) for t in mesh.loop_triangles])
    uv = [np.array([list(item.uv) for item in layer.data])[loops] for layer in mesh.uv_layers]
    normal_transform = obj.matrix_world.to_3x3().inverted().transposed()
    normals = np.array([list((normal_transform @ n.vector).normalized()) for n in mesh.corner_normals])[loops]
    return {
        'points': points, 'local_points': local_points, 'vertices': vertices, 'uv': uv, 'normals': normals,
        'materials': [m.name for m in mesh.materials if m],
        'degenerate': sum(t.area <= 1e-10 for t in mesh.loop_triangles),
        'bounds': np.array([points.min(axis=0), points.max(axis=0)]),
    }


def canonical(record, ids):
    indices = ids[record['vertices']]
    corners = (indices.argmin(axis=1)[:, None] + np.arange(3)) % 3
    rows = np.arange(len(indices))[:, None]
    oriented = indices[rows, corners]
    order = np.lexsort(oriented.T[::-1])
    return oriented[order], [layer[rows, corners][order] for layer in record['uv']], record['normals'][rows, corners][order]


def match_coordinates(source, target):
    original, inverse = np.unique(source, axis=0, return_inverse=True)
    tree = kdtree.KDTree(len(original))
    for i, point in enumerate(original):
        tree.insert(point, i)
    tree.balance()
    nearest = [tree.find(point) for point in target]
    target_ids = np.array([item[1] for item in nearest])
    return inverse, target_ids, max(item[2] for item in nearest), len(original) - len(set(target_ids))


def compare(before, after):
    inverse, target_ids, vertex_delta, missing = match_coordinates(before['points'], after['points'])
    # FBX axis conversion can add several microns to the world transform.
    # Match in local mesh coordinates for near-coincident corners when the
    # files use the same local axes. Report the world deltas independently.
    local_src, local_dst, local_delta, local_missing = match_coordinates(before['local_points'], after['local_points'])
    if local_delta < 1e-4 and local_missing < missing:
        inverse, target_ids, missing = local_src, local_dst, local_missing
    source_triangles, source_uv, source_normals = canonical(before, inverse)
    target_triangles, target_uv, target_normals = canonical(after, target_ids)
    same_triangles = np.array_equal(source_triangles, target_triangles)
    uv_delta = None
    normal_delta = None
    if same_triangles and len(source_uv) == len(target_uv):
        uv_delta = max((float(np.max(np.abs(s-t))) for s,t in zip(source_uv, target_uv)), default=0)
        cosines = np.sum(source_normals * target_normals, axis=2)
        normal_delta = float(np.degrees(np.arccos(np.clip(cosines, -1, 1))).max())
    bounds_delta = float(np.abs(before['bounds'] - after['bounds']).max())
    return {
        'source_triangles': len(source_triangles), 'reimport_triangles': len(target_triangles),
        'oriented_triangles_match': same_triangles, 'corner_uv_max_delta': uv_delta,
        'corner_normal_max_delta_degrees': normal_delta, 'bounds_max_delta_m': bounds_delta,
        'vertex_max_delta_m': vertex_delta, 'local_vertex_max_delta_m': local_delta,
        'missing_source_positions': missing,
        'source_uv_layers': len(source_uv), 'reimport_uv_layers': len(target_uv),
        'source_materials': before['materials'], 'reimport_materials': after['materials'],
        'source_bounds': before['bounds'].tolist(), 'reimport_bounds': after['bounds'].tolist(),
        'zero_triangles': after['degenerate'],
    }


def filenames(path):
    root, version = parse_fbx.parse(str(path))
    todo = [root]
    references = set()
    while todo:
        elem = todo.pop()
        if elem.id == b'RelativeFilename':
            references.update(value.decode('utf8').replace('\\', '/') for value in elem.props if value)
        todo.extend(elem.elems)
    return version, sorted(references)


def stage_images(objects, location, canonical):
    """Use an existing canonical filename when its bytes match the packed image."""
    names_by_digest = {}
    if canonical:
        for path in sorted(canonical.glob('*.png'), key=lambda p: ('_LOD1_' in p.name, p.name)):
            names_by_digest.setdefault(digest(path.read_bytes()), path.name)
    images = {
        node.image for obj in objects for mat in obj.data.materials if mat and mat.node_tree
        for node in mat.node_tree.nodes if node.type == 'TEX_IMAGE' and node.image
    }
    for img in images:
        if not img.packed_file:
            raise ValueError(f'Missing packed bytes for {img.name}')
        data = img.packed_file.data
        sha = digest(data)
        name = names_by_digest.get(sha, f'{sha}.png')
        path = location / name
        if path.exists() and path.read_bytes() != data:
            raise ValueError(f'Texture filename collision at {name}')
        if not path.exists():
            path.write_bytes(data)
        img.filepath_raw = str(path)


parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('result', type=Path)
parser.add_argument('objects', nargs='+')
modes = parser.add_mutually_exclusive_group(required=True)
modes.add_argument('--packaged', type=Path)
modes.add_argument('--export', type=Path)
parser.add_argument('--textures', type=Path)
parser.add_argument('--converter', type=Path)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
source = args.source.resolve()
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
objects = [bpy.data.objects[name] for name in args.objects]
snapshots = {obj.name: snapshot(obj) for obj in objects}
package = args.packaged or args.export
if args.export:
    package.mkdir(parents=True)
    stage_images(objects, package, args.textures)
    if args.textures and (args.textures / 'settings.json').is_file():
        settings = args.textures / 'settings.json'
        mappings = json.loads(settings.read_text())['sharedAssets']
        for alias, target_name in mappings.items():
            if not (package / target_name).exists():
                raise ValueError(f'Shared map target is missing: {target_name}')
            alias_path = args.textures / alias
            if alias_path.exists() and alias_path.read_bytes() != (package / target_name).read_bytes():
                raise ValueError(f'Shared map bytes differ: {alias}')
        shutil.copyfile(settings, package / 'settings.json')
    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)
    converter = None
    if args.converter:
        spec = importlib.util.spec_from_file_location('project_fbx_converter', args.converter)
        converter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(converter)
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        obj_path = package / (obj.name + '.fbx')
        export_path = obj_path if not converter else package / (obj.name + '_7400.fbx')
        bpy.ops.export_scene.fbx(
            filepath=str(export_path), use_selection=True, object_types={'MESH'},
            use_mesh_modifiers=True, use_triangles=True, bake_anim=False,
            add_leaf_bones=False, path_mode='RELATIVE', axis_forward='-Z', axis_up='Y',
            mesh_smooth_type='FACE', use_tspace=True,
        )
        if converter:
            converter.convert(str(export_path), str(obj_path))
            export_path.unlink()
        obj.select_set(False)

records = []
for name, before in snapshots.items():
    path = (package / (name + '.fbx')).resolve()
    version, references = filenames(path)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    start = time.monotonic()
    bpy.ops.import_scene.fbx(filepath=str(path), use_image_search=False)
    import_seconds = time.monotonic() - start
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    assert len(meshes) == 1, [obj.name for obj in meshes]
    after = snapshot(meshes[0])
    texture_checks = {}
    for reference in references:
        resolved = (path.parent / reference).resolve()
        valid = not os.path.isabs(reference) and resolved.is_relative_to(path.parent) and resolved.is_file()
        texture_checks[reference] = digest(resolved.read_bytes()) if valid else None
    row = {
        'name': name, 'file_sha256': digest(path.read_bytes()), 'bytes': path.stat().st_size,
        'version': version, 'import_seconds': import_seconds,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'texture_reference_hashes': texture_checks,
        'imported_image_sizes': {im.name: list(im.size) for im in bpy.data.images if im.source == 'FILE'},
        **compare(before, after),
    }
    records.append(row)
    print(name, row['oriented_triangles_match'], row['corner_uv_max_delta'], texture_checks, flush=True)

args.result.write_text(json.dumps({
    'source': source.name, 'source_sha256': digest(source.read_bytes()),
    'blender': bpy.app.version_string, 'records': records,
}, indent=2) + '\n')
