#!/usr/bin/env python3
"""Apply exact material-name and microscopic topology binary patches to a new full candidate tree."""
import argparse,hashlib,json,pathlib,shutil,tempfile

def sha(data):return hashlib.sha256(data).hexdigest()
def safe(root,relative):
 p=pathlib.PurePosixPath(relative)
 if p.is_absolute() or '..' in p.parts or '\\' in relative:raise ValueError('Unsafe path')
 t=root.joinpath(*p.parts)
 if any(x.is_symlink() for x in [t,*t.parents]):raise ValueError('Symlink forbidden')
 return t

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base',type=pathlib.Path,required=True);ap.add_argument('--output',type=pathlib.Path,required=True);a=ap.parse_args();base=a.base.resolve();out=a.output.absolute()
 if out.exists() or base in out.parents or out in base.parents:ap.error('Output must be new and outside baseline')
 try:import zstandard as zstd
 except ImportError:ap.error('Install the official PyPI package first: python -m pip install zstandard==0.25.0')
 root=pathlib.Path(__file__).resolve().parent;changes=json.loads((root/'material-patches/manifest.json').read_text())
 # Require the full-source receipt, including all hashes, rather than accepting an arbitrary folder.
 previous=json.loads((base/'CANDIDATE_SOURCE_MANIFEST_20261118.json').read_text());expected={r['path']:r for r in previous['assets']};actual={p.relative_to(base).as_posix() for p in (base/'assets').rglob('*') if p.is_file()}
 if actual!=set(expected):raise ValueError('Base asset inventory mismatch')
 for r in previous['assets']:
  p=safe(base,r['path']);data=p.read_bytes()
  if len(data)!=r['bytes'] or sha(data)!=r['sha256']:raise ValueError('Base checksum mismatch: '+r['path'])
 with tempfile.TemporaryDirectory(prefix='campus-material-',dir=out.parent) as temp:
  staging=pathlib.Path(temp)
  for c in changes:
   old=safe(base,c['source']).read_bytes();patch=safe(root/'material-patches',c['patch']).read_bytes()
   if sha(old)!=c['before_sha256'] or sha(patch)!=c['patch_sha256']:raise ValueError('Patch input mismatch: '+c['source'])
   dictionary=zstd.ZstdCompressionDict(old,dict_type=zstd.DICT_TYPE_RAWCONTENT)
   result=zstd.ZstdDecompressor(dict_data=dictionary,max_window_size=1024*1024).decompress(patch,max_output_size=c['result_bytes'])
   if len(result)!=c['result_bytes'] or sha(result)!=c['after_sha256']:raise ValueError('Patch output mismatch')
   target=safe(staging,c['source']);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(result)
  shutil.copytree(base,out)
  for c in changes:shutil.copy2(safe(staging,c['source']),safe(out,c['source']))
 final=[]
 for r in previous['assets']:
  p=safe(out,r['path']);data=p.read_bytes();final.append({'path':r['path'],'bytes':len(data),'sha256':sha(data)})
 previous.update({'stage':'technical-normalized','warning':'Existing baseline FBX exports remain historical; this script patches source scenes only. Regenerate and validate exports separately.','changed_source_count':previous['changed_source_count']+sum(not c['already_changed_in_previous_11'] for c in changes),'unchanged_asset_count':previous['base_asset_count']-previous['changed_source_count']-sum(not c['already_changed_in_previous_11'] for c in changes),'material_scene_repairs':len(changes),'material_name_repairs':sum(len(c['changes']) for c in changes),'goodspeed_micron_weld':True,'assets':final,'game_editor_verified':False})
 (out/'CANDIDATE_SOURCE_MANIFEST_20261118.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2));print('Verified exact binary reconstruction of 8 scene repairs / 24 material names / Goodspeed microscopic weld. Game acceptance remains unverified.')
if __name__=='__main__':main()
