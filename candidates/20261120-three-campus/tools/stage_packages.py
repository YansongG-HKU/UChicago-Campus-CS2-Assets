"""Build isolated import-only candidates and inventory the source artifacts in use."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--workspace', type=Path, default=Path.cwd())
parser.add_argument('--campuses', nargs='+', choices=('Chicago','Columbia','Penn'),
                    default=('Chicago','Columbia','Penn'))
args = parser.parse_args()
HERE = args.workspace.resolve()
REVIEW = HERE.parent / 'Review_20261120'
TECHNICAL = HERE.parent / 'Campus_20261120_Technical'
overlays = {
    'BakerDining': REVIEW / 'BakerDiningPackageVerified',
    'BillingsHospital': REVIEW / 'BillingsPackageVerified',
    'BoothHarperCenter': REVIEW / 'BoothHarperCenterPackageVerified',
    'HenryHindsLaboratory': REVIEW / 'continuation/Hinds_Armillary_Package',
}
if 'Chicago' in args.campuses:
    for group in ['continuation/VerifiedAllGroundedOverlay', 'completion/PackageOverlay', 'closeout/ReplayedPacks']:
        overlays.update({p.name: p for p in (REVIEW / group).iterdir() if p.is_dir()})

def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def deployed_files(asset, package, mesh_names):
    return {p.relative_to(package).as_posix(): p for p in package.rglob('*')
            if p.is_file() and (p.suffix.lower() == '.png' or p.name == 'settings.json'
                                or p.name in mesh_names and p.suffix == '.fbx')}


def stage(result, campus, asset, root, source, files, alternate=None):
    target = HERE / 'import-candidates-v1' / campus / asset
    target.mkdir(parents=True, exist_ok=False)
    meta = {}
    for relative, path in sorted(files.items()):
        if path.stat().st_size < 135 and path.read_bytes().startswith(b'version https://git-lfs'):
            raise ValueError(f'LFS pointer: {path}')
        out = target / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, out)
        meta[relative] = {'bytes': out.stat().st_size, 'sha256': sha(out)}
    assert (target / 'settings.json').is_file(), target
    result.append({'campus': campus, 'asset': asset, 'root': str(root), 'source': str(source),
                   'source_sha256': sha(source), 'files': meta,
                   'before_bytes': sum(f['bytes'] for f in meta.values()), 'folder': str(target),
                   'other_export_set_bytes': alternate})


rows = []
chicago_plan = (
    json.loads((REVIEW / 'continuation/inventory/plan.json').read_text()) if 'Chicago' in args.campuses else {}
)
for asset, entry in chicago_plan.items():
    paths = []
    for p in entry['fbx'].values():
        relative = Path(p).parts[Path(p).parts.index('assets'):]
        paths.append(TECHNICAL.joinpath(*relative))
    root = overlays.get(asset, paths[0].parent)
    names = {p.name for p in paths}
    files = deployed_files(asset, root, names)
    assert {Path(n).name for n in files if n.endswith('.fbx')} == names, (asset, set(files), names)
    stage(rows, 'Chicago', asset, root, TECHNICAL / entry['source'], files)

for campus in (c for c in args.campuses if c != 'Chicago'):
    repo = HERE / (campus + '-CS2-Assets')
    for setting in sorted(repo.glob('*/settings.json')):
        asset = setting.parent
        split = {p.name: p for p in (asset / 'fbx/split').glob('*.fbx')}
        combined = list((asset / 'fbx').glob('*.fbx'))
        assert len(combined) == 3 and len(split) in (6, 7, 8), (asset, split)
        textures = {p.name: p for p in (asset / 'textures').glob('*.png')}
        assert len(textures) in (10, 15), asset
        files = {'settings.json': setting, **textures, **split}
        stage(rows, campus, asset.name, asset, next(asset.glob('*.blend')), files,
              sum(p.stat().st_size for p in combined))
assert len(rows) == sum({"Chicago":88, "Columbia":19, "Penn":46}[c] for c in args.campuses)
(HERE / 'staged-packages-v1.json').write_text(json.dumps(rows, indent=2) + '\n')
for campus in args.campuses:
    group = [r for r in rows if r['campus'] == campus]
    samples = sorted((r['before_bytes'], r['asset']) for r in group)
    print(campus, len(group), sum(n for n, _ in samples), samples[0], samples[-5:], flush=True)
