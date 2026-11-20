"""Stage six exact, hash-checked Chicago packages for an authorized Editor host."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

from io_scene_fbx import parse_fbx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from finalize_import import unit_metadata
from portable_readback import PATH_IDS, visit

BASE = Path.cwd()
REPO = BASE.parent / 'UChicago-Campus-CS2-Assets'
PLAN = BASE.parent / 'Review_20261120/continuation/inventory/plan.json'
REGISTER = json.loads(PLAN.read_text())
COMPLETION = REPO / 'candidates/20261120-completion'
CLOSEOUT = REPO / 'candidates/20261120-closeout'
TOWER = {x['name']: x for x in json.loads((COMPLETION / 'evidence/TowerGroup-packages-final.json').read_text())['records']}
CASE = {
    'MitchellTower': None, 'MandelHall': None, 'HutchinsonCommons': 'completion',
    'ReynoldsClubhouse': 'completion', 'HarperMemorialLibrary': 'completion', 'SaiehHall': 'closeout',
}
OUTPUT = BASE / 'editor-trial-exact'
OUTPUT.mkdir()
OVERLAYS = {k: {e['asset']: e for e in json.loads((v / 'export-overlay/manifest.json').read_text())}
            for k,v in [('completion',COMPLETION), ('closeout',CLOSEOUT)]}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

versions = {}
for asset, overlay in CASE.items():
    raw = [Path(p) for p in REGISTER[asset]['fbx'].values()]
    folder = raw[0].parent if overlay is None else BASE / ('editor-replay-' + overlay) / asset
    target = OUTPUT / 'ProjectFiles' / asset
    target.mkdir(parents=True)
    spec = OVERLAYS[overlay][asset] if overlay else None
    hashes = {}
    if spec:
        hashes.update(spec['original_files'])
        hashes.update({f['name']:f['after_sha256'] for f in spec['replace']})
        hashes.update({f['name']:f['sha256'] for f in spec['add_references']})
    included = {}
    fbx = {}
    stem = set(REGISTER[asset]['fbx'])
    for file in sorted(folder.rglob('*')):
        if not file.is_file() or file.name != 'settings.json' and file.suffix != '.png' and file.stem not in stem:
            continue
        relative = file.relative_to(folder).as_posix()
        content_hash = digest(file)
        if relative in hashes:
            assert content_hash == hashes[relative]
        out = target / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file,out)
        assert digest(out) == content_hash
        included[relative] = {'sha256': content_hash, 'bytes': out.stat().st_size}
        if file.suffix != '.fbx':
            continue
        if file.stem in TOWER:
            control = TOWER[file.stem]
            assert content_hash == control['file_sha256'], (asset,file)
        root, version = parse_fbx.parse(str(out))
        paths = {}
        for n in visit(root):
            if n.id == b'RelativeFilename':
                for item in n.props:
                    if item:
                        ref = item.decode().replace(chr(92),'/')
                        resolved = (file.parent / ref).resolve()
                        assert resolved.is_relative_to(folder.resolve()) and resolved.is_file(), ref
                        paths[ref] = digest(resolved)
        if file.stem in TOWER:
            assert paths == TOWER[file.stem]['texture_reference_hashes'], file
        fbx[relative] = {'version': version,'unit_and_axes': unit_metadata(root), 'references_sha256': paths}
    assert len(fbx) == len(raw)
    settings = json.loads((target / 'settings.json').read_text())
    assert all((target / destination).is_file() for destination in settings['sharedAssets'].values())
    versions[asset] = {'location':'ProjectFiles/' + asset,'exact_baseline':overlay or 'technical-tree',
                       'files':included,'fbx':fbx,'settings':settings}
(OUTPUT/'exact-sha256.json').write_text(json.dumps({'commit':'ada4b6cafa5d010e2bbd814e77331e3e878878c5',
                                                   'runtime_accepted':0, 'assets':versions},indent=2)+'\n')
print('EXACT_EDITOR_SET', len(versions), sum(len(v['fbx']) for v in versions.values()),
      sum(f['bytes'] for v in versions.values() for f in v['files'].values()), flush=True)
