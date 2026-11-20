"""Validate final texture bytes, write true 7500 and compare Blender results."""
import argparse
import json
import shutil
import sys
from pathlib import Path

from io_scene_fbx import encode_bin, parse_fbx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable_readback import PATH_IDS, encode_node, read_blender, sha, typed_tree_hash, visit

def unit_metadata(root):
    global_settings = next(n for n in root.elems if n.id == b'GlobalSettings')
    props = next(n for n in global_settings.elems if n.id == b'Properties70')
    names = {b'UnitScaleFactor', b'OriginalUnitScaleFactor', b'UpAxis', b'UpAxisSign',
             b'FrontAxis', b'FrontAxisSign', b'CoordAxis', b'CoordAxisSign'}
    return {e.props[0].decode(): e.props[-1] for e in props.elems if e.props[0] in names}

def finalize(row, geometry, folder, png):
    name = row['asset']
    final = folder / name
    originals = {v['fbx']: v for v in geometry.get(name, [])} if row['campus'] == 'Columbia' else {}
    data = {}
    empty = []
    settings = json.loads((final / 'settings.json').read_text())
    visible_texture_refs = {
        ref for item in row['fbx'].values() if any(m['triangles'] for m in item['meshes'])
        for ref in item['resolved_texture_sha256']
    }
    for filename, item in row['fbx'].items():
        path = final / filename
        source = path
        record = originals.get(filename)
        if record:
            source = Path('columbia-geometry-fix', name, filename).resolve()
            assert sha(source) == record['new_sha256']
        refs = item['resolved_texture_sha256']
        for ref, before in refs.items():
            rel = (path.parent / ref).relative_to(folder.parent).as_posix()
            texture = png[rel]
            assert texture['before_sha256'] == before and sha(path.parent / ref) == texture['after_sha256']
        assert not item['unresolved_fbx_paths'] and not item['paths_not_loaded_by_blender']
        if not record:
            assert sha(path) == item['sha256']
        if (filename.endswith('_Gls.fbx') and len(item['meshes']) == 1 and item['meshes'][0].get('empty')
                and set(refs) <= visible_texture_refs and set(settings) == {'sharedAssets'}):
            # The zero-vertex export has no unique resources or explicit settings binding.
            empty.append({'file': filename, 'sha256': sha(path), 'bytes': path.stat().st_size,
                          'references_also_on_nonempty_meshes': sorted(refs)})
            path.unlink()
            continue
        root, version = parse_fbx.parse(str(source))
        if record:
            edits = {old.encode(): new.encode() for old, new in item['path_edits']}
            for node in visit(root):
                if node.id in PATH_IDS:
                    for index, value in enumerate(node.props):
                        node.props[index] = edits.get(value, value)
        source_tree = typed_tree_hash(root)
        if version != 7500 or source != path:
            temp = path.with_suffix('.pending.fbx')
            with encode_bin.FBXElem.enable_multithreading_cm():
                encoded = encode_node(root)
            encode_bin.write(str(temp), encoded, 7500)
            loaded_root, loaded_version = parse_fbx.parse(str(temp))
            assert loaded_version == 7500 and typed_tree_hash(loaded_root) == source_tree, filename
            temp.replace(path)
        check = read_blender(path, refs)
        assert check['finished'] and not check['paths_not_loaded_by_blender']
        assert check['images'] == item['images'], filename
        if not record:
            assert check['meshes'] == item['meshes'], filename
        else:
            assert all(m['zero_area'] == 0 for m in check['meshes'])
            assert sum(m['triangles'] for m in check['meshes']) == record['new_triangles']
        data[filename] = {'version': 7500, 'source_version': version, 'sha256': sha(path),
                          'bytes': path.stat().st_size,'fbx_unit_and_axis_metadata': unit_metadata(root),
                          'geometry_uv_tree_sha256': source_tree, 'path_edits': len(item['path_edits']),
                          'texture_refs': refs, **check}
    files = {p.relative_to(final).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
             for p in sorted(final.rglob('*')) if p.is_file()}
    return {**{k: row[k] for k in ('campus','asset','source_sha256','before_bytes','removed_exact_duplicates','issues')},
            'after_bytes': sum(f['bytes'] for f in files.values()),
            'files': files, 'fbx': data, 'empty_glass_placeholders_retained_only_in_baseline': empty}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('campus')
    p.add_argument('png', type=Path)
    p.add_argument('geometry', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('--offset', type=int, default=0)
    p.add_argument('--stride', type=int, default=1)
    a = p.parse_args(sys.argv[sys.argv.index('--')+1:])
    folder = a.root.resolve() / a.campus
    png = {r['path']:r for r in json.loads(a.png.read_text())}
    geometry = json.loads(a.geometry.read_text())
    output = a.out / a.campus
    output.mkdir(exist_ok=True, parents=True)
    for p in sorted((folder / '_readback').glob('*.json'))[a.offset::a.stride]:
        row = json.loads(p.read_text())
        try:
            result = finalize(row, geometry, folder, png)
        except Exception as error:
            import traceback
            result = {'asset':row['asset'],'error':str(error),'traceback':traceback.format_exc()}
        (output / p.name).write_text(json.dumps(result, indent=2) + '\n')
        print('ERROR' if 'error' in result else 'VERIFIED', a.campus, row['asset'],
              result.get('traceback', result.get('after_bytes')), flush=True)

if __name__ == '__main__':
    main()
