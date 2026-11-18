#!/usr/bin/env python3
"""Verify candidate package hashes and extract into a NEW output directory."""
import argparse, hashlib, io, json, pathlib, zipfile

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=pathlib.Path)
    args=parser.parse_args()
    root=pathlib.Path(__file__).resolve().parent
    if args.output.exists():
        parser.error('Output must not exist; original and edited copies are never overwritten.')
    rows=json.loads((root/'manifest.json').read_text())
    fbx=json.loads((root/'fbx_manifest.json').read_text())
    checked=[]
    seen=set()
    for kind,records in [('models',rows),('fbx-check-only',fbx)]:
        for record in records:
            directory=root/kind
            name=record['zip'] if kind=='models' else record['path'].split('/')[-1]
            if record.get('parts'):
                data=[]
                for part in record['parts']:
                    chunk=(directory/part['name']).read_bytes()
                    if len(chunk)!=part['bytes'] or digest(chunk)!=part['sha256']:
                        raise ValueError('Part hash mismatch: '+part['name'])
                    data.append(chunk)
                data=b''.join(data)
            else:
                data=(directory/name).read_bytes()
            expected=record['zip_sha256'] if kind=='models' else record['sha256']
            if digest(data)!=expected:
                raise ValueError('ZIP hash mismatch: '+name)
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if archive.testzip() is not None: raise ValueError('ZIP CRC mismatch')
                for info in archive.infolist():
                    p=pathlib.PurePosixPath(info.filename)
                    if p.is_absolute() or '..' in p.parts or '\\' in info.filename:
                        raise ValueError('Unsafe archive path')
                    if info.is_dir():continue
                    output=p if kind=='models' else pathlib.PurePosixPath('fbx-check-only')/p
                    if str(output) in seen:raise ValueError('Duplicate output path')
                    seen.add(str(output));raw=archive.read(info)
                    if kind=='models' and (str(p)!=record['path'] or len(raw)!=record['bytes'] or digest(raw)!=record['sha256']):
                        raise ValueError('Model hash mismatch')
                    checked.append((output,raw))
    args.output.mkdir(parents=True)
    for relative,data in checked:
        target=args.output/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print(f'Verified/extracted {len(rows)} Blender scene candidates and {len(fbx)} check-only FBX files; no game acceptance implied.')
if __name__=='__main__':main()
