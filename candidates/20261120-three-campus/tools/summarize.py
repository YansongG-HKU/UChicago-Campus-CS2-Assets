"""Measure and archive each candidate independently, with per-asset verification."""
from concurrent.futures import ThreadPoolExecutor
import collections
import csv
import hashlib
import json
from pathlib import Path
import statistics
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

ROOT = Path.cwd()
EVIDENCE = ROOT / 'final-readback'
OUTPUT = ROOT / 'handoff'
OUTPUT.mkdir(exist_ok=False)
CANDIDATES = ROOT / 'import-candidates-v2'
LOCKED = {
    'Chicago': 'ada4b6cafa5d010e2bbd814e77331e3e878878c5',
    'Columbia': '98587eeddab6ddf83a0c562efbf449207d633582',
    'Penn': '3a7097a0ef154f454e0ce67da0b26c37c26bfed4',
}
PNG = json.loads((ROOT/'png-verify/png-verified.json').read_text())
COL = json.loads((ROOT/'columbia-geometry-fix/zero-area-readback.json').read_text())
GLASS = json.loads((ROOT/'glass-uv-repair.json').read_text())

def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def lod_parts(row):
    counts = [0, 0, 0]
    xyz = [[], [], []]
    for name, artifact in row['fbx'].items():
        tier = 2 if '_LOD2' in name else 1 if '_LOD1' in name else 0
        for mesh in artifact['meshes']:
            assert mesh.get('finite') and mesh.get('zero_area') == 0
            assert all(uv['finite'] for uv in mesh['uv'])
            assert mesh['uv'], (row['asset'], mesh['name'])
            counts[tier] += mesh['triangles']
            xyz[tier].append(mesh['bounds_m'])
    assert all(xyz), row['asset']
    bounds = [[[f(box[end][axis] for box in tier) for axis in range(3)]
                for end,f in enumerate((min,max))] for tier in xyz]
    return counts, bounds

def zip_package(row):
    campus, name = row['campus'], row['asset']
    folder = CANDIDATES / campus / name
    archive = OUTPUT / 'per-asset-zip' / campus / (name + '.zip')
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive,'x',compression=ZIP_DEFLATED,compresslevel=3) as z:
        for relative, value in row['files'].items():
            p = folder / relative
            assert sha(p) == value['sha256'], p
            z.write(p, name + '/' + relative,
                    compress_type=ZIP_STORED if p.suffix == '.png' else ZIP_DEFLATED)
    with ZipFile(archive) as z:
        assert z.testzip() is None
        for relative, value in row['files'].items():
            assert hashlib.sha256(z.read(name + '/' + relative)).hexdigest() == value['sha256']
    return {'relative':archive.relative_to(OUTPUT).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive)}

all_rows = [json.loads(p.read_text()) for p in sorted(EVIDENCE.glob('*/*.json'))]
assert len(all_rows) == 153 and all('error' not in r for r in all_rows)
with ThreadPoolExecutor(max_workers=3) as executor:
    archives = list(executor.map(zip_package, all_rows))

campus_rows = collections.defaultdict(list)
for row, archive in zip(all_rows,archives):
    counts,bounds = lod_parts(row)
    ground = [b[0][2] for b in bounds]
    high = [b[1][2] for b in bounds]
    campus, asset = row['campus'], row['asset']
    flags = []
    if row['empty_glass_placeholders_retained_only_in_baseline']:
        flags.append('empty_glass_placeholders_removed')
    if max(high)-min(high)>2:
        flags.append('high_point_changes_over_2m_review_in_editor')
    if max(ground)-min(ground) > .25:
        flags.append('bounds_z_min_changes_over_0.25m_review_in_editor')
    if not counts[0] > counts[1] > counts[2]:
        flags.append('nondecreasing_lod_triangles')
    if campus == 'Columbia' and asset in COL:
        flags.append('legacy_zero_area_triangles_repaired')
    if row.get('glass_uv_repair'):
        flags.append('repaired_zero_area_glass_uv')
    if asset in ('LernerHall','QuadMcClelland','BakerDining'):
        flags.append('known_architectural_defect_remains')
    add = {
        'campus': campus, 'asset': asset, 'type': 'Quad segment' if campus=='Penn' and asset.startswith('Quad') else 'asset',
        'before_bytes': row['before_bytes'], 'after_bytes': row['after_bytes'], 'saved_bytes': row['before_bytes']-row['after_bytes'],
        'zip_bytes': archive['bytes'], 'zip_sha256': archive['sha256'], 'lod0_triangles': counts[0],
        'lod1_triangles':counts[1], 'lod2_triangles':counts[2],
        'lod0_span_m': [round(b-a,4) for a,b in zip(*bounds[0])], 'max_lod_ground_bound_delta_m': round(max(ground)-min(ground),6),
        'max_lod_top_bound_delta_m': round(max(high)-min(high),6),
        'fbx_files':len(row['fbx']), 'same_byte_png_copies_removed':len(row['removed_exact_duplicates']),
        'empty_glass_fbx_removed':len(row['empty_glass_placeholders_retained_only_in_baseline']),
        'special_fbx_preview_material_removed':len(row.get('special_shader_material_bindings_removed', [])),
        'glass_uv_triangles_repaired':sum(x['corner_uv_triangles_repaired'] for x in row.get('glass_uv_repair',[])),
        'archive_source_sha256':row['source_sha256'], 'editor':'pending', 'flags':';'.join(flags),
    }
    row['archive'] = archive
    campus_rows[campus].append(add)
    row['summary'] = add
    row['lod_bounds_m'] = bounds

metrics = {}
all_summaries = []
for campus, summaries in campus_rows.items():
    all_summaries += summaries
    rows = [r for r in all_rows if r['campus'] == campus]
    stats = sorted(s['after_bytes'] for s in summaries)
    metrics[campus] = {
        'basis': LOCKED[campus], 'units':len(rows),
        'fbx':sum(s['fbx_files'] for s in summaries),
        'before_bytes':sum(s['before_bytes'] for s in summaries),
        'after_bytes':sum(s['after_bytes'] for s in summaries),
        'min_asset_bytes': min(stats), 'median_asset_bytes': statistics.median(stats),
        'max_asset':max(summaries,key=lambda s:s['after_bytes'])['asset'], 'max_asset_bytes':max(stats),
        'min_zip_bytes':min(s['zip_bytes'] for s in summaries),'max_zip_bytes':max(s['zip_bytes'] for s in summaries),
        'exact_png_duplicates_removed':sum(s['same_byte_png_copies_removed'] for s in summaries),
        'empty_glass_fbx_removed':sum(s['empty_glass_fbx_removed'] for s in summaries),
        'special_fbx_preview_material_removed':sum(s['special_fbx_preview_material_removed'] for s in summaries),
        'glass_uv_fbx_repaired':sum(bool('corner_uv_triangles_repaired' in r) for path,r in GLASS.items() if path.startswith(campus+'/')),
        'glass_uv_triangles_repaired':sum(s['glass_uv_triangles_repaired'] for s in summaries),
        'large_lod_peak_delta_flags':sum(s['max_lod_top_bound_delta_m']>2 for s in summaries),
        'png_files':sum(p['path'].startswith(campus+'/') for p in PNG),
        'lossless_png_idat_savings':sum(p['before_bytes']-p['after_bytes'] for p in PNG if p['path'].startswith(campus+'/')),
    }
    with (OUTPUT / f'{campus}-asset-audit.csv').open('w') as handle:
        writer = csv.DictWriter(handle,fieldnames=summaries[0].keys(),lineterminator="\n")
        writer.writeheader()
        writer.writerows(summaries)
    manifest = {'baseline_revision':LOCKED[campus], 'assets':{r['asset']:{
        'files':r['files'], 'zip':r['archive'], 'fbx':{n:{
           'axis_and_unit':f['fbx_unit_and_axis_metadata'],'references':sorted(f['texture_refs'])
        } for n,f in r['fbx'].items()}} for r in rows}}
    (OUTPUT / f'{campus}-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
(OUTPUT/'summary.json').write_text(json.dumps(metrics,indent=2)+'\n')
with (OUTPUT/'asset-audit.csv').open('w') as handle:
    writer=csv.DictWriter(handle,fieldnames=all_summaries[0].keys(),lineterminator="\n")
    writer.writeheader()
    writer.writerows(all_summaries)
print(json.dumps(metrics,indent=2))
