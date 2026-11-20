"""Make one deployable file set per asset and verify it with Blender 4.3."""
import argparse
import array
import hashlib
import json
import math
import re
import shutil
import struct
import sys
from pathlib import Path, PurePosixPath

import bpy
import numpy
from io_scene_fbx import encode_bin, parse_fbx

METHODS = {
    'B': 'add_bool', 'C': 'add_char', 'Z': 'add_int8', 'Y': 'add_int16',
    'I': 'add_int32', 'L': 'add_int64', 'F': 'add_float32', 'D': 'add_float64',
    'R': 'add_bytes', 'S': 'add_string', 'i': 'add_int32_array', 'l': 'add_int64_array',
    'f': 'add_float32_array', 'd': 'add_float64_array', 'b': 'add_bool_array', 'c': 'add_byte_array',
}
PATH_IDS = {b'Filename', b'FileName', b'RelativeFilename'}

def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def visit(node):
    yield node
    for child in node.elems:
        yield from visit(child)

def typed_tree_hash(root):
    result = hashlib.sha256()
    for node in visit(root):
        result.update(struct.pack('<III', len(node.id), len(node.elems), len(node.props)) + node.id)
        for tag, value in zip(node.props_type, node.props):
            data = (value.typecode.encode() + value.tobytes() if isinstance(value, array.array)
                    else value if isinstance(value, bytes) else repr(value).encode())
            result.update(struct.pack('<BQ', tag, len(data)))
            result.update(data)
    return result.hexdigest()

def encode_node(node):
    new = encode_bin.FBXElem(node.id)
    for tag, value in zip(node.props_type, node.props):
        getattr(new, METHODS[chr(tag)])(value)
    new.elems = [encode_node(child) for child in node.elems]
    return new

def resolve_map(old, files, aliases):
    text = old.decode('utf-8').replace(chr(92), '/')
    rel = PurePosixPath(text)
    if rel.as_posix() in files:
        return rel.as_posix()
    if rel.name in files:
        return rel.name
    if rel.name in aliases and aliases[rel.name] in files:
        return aliases[rel.name]
    matches = [name for name in files if name.endswith('/' + rel.name)]
    if len(matches) == 1:
        return matches[0]
    return None

def mesh_details(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    if not len(mesh.vertices):
        return {'name': obj.name, 'triangles': 0, 'empty': True}
    points = numpy.empty(len(mesh.vertices) * 3, dtype=numpy.float32)
    mesh.vertices.foreach_get('co', points)
    transform = numpy.array(obj.matrix_world, dtype=numpy.float64)
    world = points.reshape(-1, 3) @ transform[:3, :3].T + transform[:3, 3]
    minimum = world.min(axis=0)
    maximum = world.max(axis=0)
    geometry = hashlib.sha256()
    for prop, count, dtype in ((mesh.vertices, len(mesh.vertices) * 3, 'f4'),
                               (mesh.loops, len(mesh.loops), 'i4')):
        values = numpy.empty(count, dtype=dtype)
        prop.foreach_get('co' if prop == mesh.vertices else 'vertex_index', values)
        geometry.update(values.tobytes())
    uv = []
    for layer in mesh.uv_layers:
        values = numpy.empty(len(layer.uv) * 2, dtype=numpy.float32)
        layer.uv.foreach_get('vector', values)
        uv.append({'name': layer.name, 'finite': bool(numpy.isfinite(values).all()),
                   'sha256': hashlib.sha256(values.tobytes()).hexdigest(),
                   'outside_unit_components': int(((values < -0.00001) | (values > 1.00001)).sum())})
    return {'name': obj.name, 'triangles': len(mesh.loop_triangles),
            'zero_area': sum(t.area <= 1e-10 for t in mesh.loop_triangles),
            'vertices': len(mesh.vertices), 'bounds_m': [minimum.round(6).tolist(), maximum.round(6).tolist()],
            'finite': bool(numpy.isfinite(world).all()), 'geometry_sha256': geometry.hexdigest(),
            'uv': uv, 'materials': [m.name if m else None for m in mesh.materials]}

def read_blender(path, expected_relpaths):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    result = bpy.ops.import_scene.fbx(filepath=str(path), use_image_search=False)
    meshes = sorted((mesh_details(o) for o in bpy.data.objects if o.type == 'MESH'), key=lambda r: r['name'])
    images = {}
    for image in bpy.data.images:
        if image.source != 'FILE':
            continue
        file = Path(bpy.path.abspath(image.filepath)).resolve()
        local = file.is_relative_to(path.parent.resolve()) and file.is_file()
        if local:
            # Reading size after reload makes Blender test decoding as well as existence.
            image.reload()
        size = list(image.size) if local else []
        images[image.name] = {'local': local, 'size': size,
                              'path': str(file.relative_to(path.parent)) if local else None}
    missing = sorted(set(expected_relpaths) - {im['path'] for im in images.values() if all(im['size'])})
    return {'finished': 'FINISHED' in result, 'meshes': meshes, 'images': images,
            'paths_not_loaded_by_blender': missing}

def audit(row, dest):
    asset = row['asset']
    source = Path(row['folder'])
    dest = dest / asset
    dest.mkdir(parents=True, exist_ok=False)
    files = row['files']
    settings = json.loads((source / 'settings.json').read_text())
    aliases = settings.get('sharedAssets', {})
    duplicate = {}
    for alias, canonical in aliases.items():
        canonical_entry = files.get(canonical)
        if alias in files and canonical_entry and files[alias]['sha256'] == canonical_entry['sha256']:
            duplicate[alias] = canonical
    named = {v['sha256']: k for k,v in files.items() if '/' not in k and k.endswith('.png') and k not in duplicate}
    for name, meta in files.items():
        if re.fullmatch(r'textures/[0-9a-f]{64}\.png', name) and meta['sha256'] in named:
            duplicate[name] = named[meta['sha256']]
    issues = []
    for alias, canonical in aliases.items():
        if canonical not in files:
            issues.append(['missing_alias_target', alias, canonical])
        elif alias in files and alias not in duplicate:
            issues.append(['different_alias_bytes', alias, canonical])

    for name in files:
        if name in duplicate or name.endswith('.fbx'):
            continue
        out = dest / name
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, out)

    records = {}
    for name in (n for n in files if n.endswith('.fbx')):
        original = source / name
        output = dest / name
        root, version = parse_fbx.parse(str(original))
        refs = set()
        changed = []
        unresolved = set()
        for node in visit(root):
            if node.id not in PATH_IDS:
                continue
            for i, old in enumerate(node.props):
                if not isinstance(old, bytes) or not old:
                    continue
                match = resolve_map(old, files, aliases)
                if not match:
                    unresolved.add(old.decode('utf-8', errors='replace'))
                    continue
                rel = duplicate.get(match, match)
                refs.add(rel)
                assert files[rel]['sha256'] == files[match]['sha256'], (name, rel, match)
                if rel.encode() != old:
                    node.props[i] = rel.encode()
                    changed.append([old.decode(), rel])
        stable_tree = typed_tree_hash(root)
        if changed:
            with encode_bin.FBXElem.enable_multithreading_cm():
                encoded = encode_node(root)
            encode_bin.write(str(output), encoded, version)
            reread, output_version = parse_fbx.parse(str(output))
            assert version == output_version and stable_tree == typed_tree_hash(reread), name
        else:
            shutil.copyfile(original, output)
        for ref in refs:
            assert sha(dest / ref) == files[ref]['sha256'], (name, ref)
        after = read_blender(output, refs)
        records[name] = {'version': version, 'sha256': sha(output), 'bytes': output.stat().st_size,
                         'path_edits': changed, 'unresolved_fbx_paths': sorted(unresolved),
                         'resolved_texture_sha256': {r: files[r]['sha256'] for r in sorted(refs)},
                         'typed_tree_sha256_after_path_edits': stable_tree, **after}
    output = {p.relative_to(dest).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size}
              for p in sorted(dest.rglob('*')) if p.is_file()}
    return {'campus': row['campus'], 'asset': asset, 'source_sha256': row['source_sha256'],
            'before_bytes': row['before_bytes'], 'after_bytes': sum(f['bytes'] for f in output.values()),
            'removed_exact_duplicates': duplicate, 'issues': issues, 'fbx': records, 'files': output}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inventory', type=Path)
    parser.add_argument('campus')
    parser.add_argument('output', type=Path)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--stride', type=int, default=1)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    records = [r for r in json.loads(args.inventory.read_text()) if r['campus'] == args.campus]
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    evidence = args.output / '_readback'
    evidence.mkdir(exist_ok=True)
    for row in records[args.offset::args.stride]:
        asset = row['asset']
        result_path = evidence / (asset + '.json')
        try:
            result = audit(row, args.output)
            print('PASS', args.campus, asset, len(result['fbx']), result['before_bytes'], result['after_bytes'], flush=True)
        except Exception as error:
            import traceback
            result = {'campus': args.campus, 'asset': asset, 'error': str(error), 'traceback': traceback.format_exc()}
            print('ERROR', args.campus, asset, result['traceback'], flush=True)
        result_path.write_text(json.dumps(result, indent=2) + '\n')

if __name__ == '__main__':
    main()
