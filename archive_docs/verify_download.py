"""Verify the files in downloaded complete asset groups. Python 3 standard library only."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'release_manifest/file_manifest.json').read_text(encoding='utf-8'))
groups={p.name for p in (root/'assets').iterdir() if p.is_dir()}
errors=[];checked=0
for row in manifest:
 path=Path(row['path'])
 if path.parts[1] not in groups:continue
 p=root/path
 if not p.is_file():errors.append('Missing: '+row['path']);continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 if p.stat().st_size!=row['bytes'] or h.hexdigest()!=row['sha256']:errors.append('Mismatch: '+row['path'])
 checked+=1
print(f'Checked {checked} files in {len(groups)} downloaded asset groups; {len(errors)} errors.')
for error in errors:print(error)
sys.exit(1 if errors else 0)
