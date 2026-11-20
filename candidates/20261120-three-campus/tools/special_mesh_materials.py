"""Clear legacy preview materials from the project's special-shader meshes."""
import argparse
import json
import sys
from pathlib import Path

import bpy
from io_scene_fbx import parse_fbx, encode_bin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable_readback import encode_node, read_blender, sha, typed_tree_hash, visit

STRIP = {b'Material', b'Texture', b'Video'}

def child(root, name):
    return next(e for e in root.elems if e.id == name)

def rewrite(path, before):
    root, version = parse_fbx.parse(str(path))
    assert version == 7500
    assert sha(path) == before['sha256']
    objects = child(root, b'Objects')
    assert sum(n.id == b'Geometry' for n in objects.elems) == 1
    assert all(n.id in STRIP | {b'Geometry',b'Model'} for n in objects.elems)
    removed = {item.props[0] for item in objects.elems if item.id in STRIP}
    if not removed:
        return None
    objects.elems[:] = [e for e in objects.elems if e.props[0] not in removed]
    geo = child(objects,b'Geometry')
    geo.elems[:] = [e for e in geo.elems if e.id != b'LayerElementMaterial']
    for layer in (e for e in geo.elems if e.id == b'Layer'):
        layer.elems[:] = [e for e in layer.elems if not (
            e.id == b'LayerElement' and child(e,b'Type').props[0] == b'LayerElementMaterial')]
    connections = child(root,b'Connections')
    connections.elems[:] = [e for e in connections.elems if not (removed & set(e.props[1:3]))]
    definitions = child(root,b'Definitions')
    definitions.elems[:] = [e for e in definitions.elems if not (e.id == b'ObjectType' and e.props[0] in STRIP)]
    child(definitions,b'Count').props[0] = sum(child(e,b'Count').props[0] for e in definitions.elems if e.id == b'ObjectType')
    checked = typed_tree_hash(root)
    temp = path.with_suffix('.shader.pending.fbx')
    with encode_bin.FBXElem.enable_multithreading_cm():
        output = encode_node(root)
    encode_bin.write(str(temp),output,version)
    actual, new_version = parse_fbx.parse(str(temp))
    assert typed_tree_hash(actual) == checked and new_version == version
    check = read_blender(temp, [])
    assert check['finished'] and not check['images']
    assert check['meshes'] == [{**m,'materials':[]} for m in before['meshes']],path
    path_before = before['sha256']
    temp.replace(path)
    replacement = {**before, **check, 'bytes':path.stat().st_size,'sha256':sha(path),
                   'geometry_uv_tree_sha256':checked,'texture_refs':{},
                   'prior_preview_material_export_sha256':path_before}
    return replacement

def run(stage, results, name):
    folder = stage/name
    for result in sorted((results/name).glob('*.json')):
        row = json.loads(result.read_text())
        changed=[]
        for asset, readback in row['fbx'].items():
            if not asset.endswith(('_Win.fbx','_Gls.fbx','_Wat.fbx')) or not any(
                    part.get('materials') for part in readback['meshes']):
                continue
            actual = folder / row['asset'] / asset
            revised = rewrite(actual, readback)
            assert revised is not None
            row['fbx'][asset] = revised
            row['files'][asset] = {'bytes':revised['bytes'],'sha256':revised['sha256']}
            changed.append({'file':asset,'before_sha256':revised['prior_preview_material_export_sha256'],
                            'after_sha256':revised['sha256']})
        row['special_shader_material_bindings_removed'] = changed
        row['after_bytes'] = sum(f['bytes'] for f in row['files'].values())
        result.write_text(json.dumps(row,indent=2)+'\n')
        print(name, row['asset'],len(changed),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('candidates',type=Path)
    parser.add_argument('records',type=Path)
    parser.add_argument('campus')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(args.candidates.resolve(),args.records.resolve(),args.campus)

if __name__=='__main__':
    main()
