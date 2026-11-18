#!/usr/bin/env python3
"""Lossless content-addressed source delivery. Never deletes or overwrites inputs."""
import argparse,hashlib,json,pathlib,shutil,zipfile

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def safe_path(s):
 p=pathlib.PurePosixPath(s)
 if not s or p.is_absolute() or '..' in p.parts or '\\' in s or ':' in s or p.as_posix()!=s:raise ValueError('Unsafe path: '+s)
 return p

def pack(root,target):
 root=root.resolve();target=target.absolute()
 if target.exists() or root==target or root in target.parents:raise ValueError('New archive must be outside source tree')
 paths=sorted(root.rglob('*'))
 if any(p.is_symlink() for p in paths):raise ValueError('Symlinks are not supported')
 rows=[];objects={}
 for p in paths:
  if not p.is_file():continue
  rel=p.relative_to(root).as_posix();safe_path(rel);sha=digest(p);rows.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha});objects.setdefault(sha,p)
 manifest={'format':'cs2-source-content-bundle-v1','scope':'Source working files only; not a compiled game package. Byte/path preservation; not timestamps or filesystem permissions. Empty directories omitted.','files':rows}
 with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,separators=(',',':')))
  for sha,p in objects.items():
   if digest(p)!=sha:raise ValueError('Source changed during packing: '+str(p))
   z.write(p,'objects/'+sha)
 print(json.dumps({'files':len(rows),'unique_objects':len(objects),'source_bytes':sum(r['bytes'] for r in rows),'archive_bytes':target.stat().st_size,'archive_sha256':digest(target)}))

def unpack(archive,target):
 target=target.absolute()
 if target.exists():raise ValueError('Destination must not exist')
 with zipfile.ZipFile(archive) as z:
  names=z.namelist()
  if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP entries')
  m=json.loads(z.read('manifest.json'))
  if m['format']!='cs2-source-content-bundle-v1':raise ValueError('Unknown format')
  rows=m['files'];seen=set();objects={}
  for r in rows:
   p=safe_path(r['path']);sha=r['sha256']
   if len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha) or not isinstance(r['bytes'],int) or r['bytes']<0:raise ValueError('Invalid object')
   if str(p).casefold() in seen:raise ValueError('Duplicate/case-colliding paths')
   seen.add(str(p).casefold())
   if sha in objects and objects[sha]!=r['bytes']:raise ValueError('Inconsistent sizes')
   objects[sha]=r['bytes']
  if set(names)!={'manifest.json',*('objects/'+h for h in objects)}:raise ValueError('Unexpected/missing ZIP entries')
  # Validate every object before creating output. Never use extractall.
  for sha,size in objects.items():
   h=hashlib.sha256();n=0
   with z.open('objects/'+sha) as f:
    for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
   if n!=size or h.hexdigest()!=sha:raise ValueError('Object checksum mismatch')
  needed=sum(r['bytes'] for r in rows)
  parent=target.parent
  while not parent.exists():parent=parent.parent
  if shutil.disk_usage(parent).free < needed+64*1024*1024:raise ValueError('Insufficient free disk space for complete restored tree')
  target.mkdir(parents=True,exist_ok=False)
  for r in rows:
   p=target.joinpath(*safe_path(r['path']).parts);p.parent.mkdir(parents=True,exist_ok=True)
   with z.open('objects/'+r['sha256']) as f,p.open('xb') as out:shutil.copyfileobj(f,out)
   if p.stat().st_size!=r['bytes'] or digest(p)!=r['sha256']:raise ValueError('Restored file mismatch')
 print(json.dumps({'restored_files':len(rows),'verified':True}))

if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('operation',choices=['pack','unpack']);a.add_argument('source',type=pathlib.Path);a.add_argument('output',type=pathlib.Path);v=a.parse_args();(pack if v.operation=='pack' else unpack)(v.source,v.output)
