"""Restore hash-locked replacement FBXs into separate copies of the original packages."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import zstandard


def sha(data):
    return hashlib.sha256(data).hexdigest()


def child(root, name):
    p = (root/name).resolve()
    if not p.is_relative_to(root):
        raise ValueError(f"Unsafe path: {name}")
    return p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--patch-dir", type=Path, default=Path(__file__).resolve().parent / "export-overlay")
    args = parser.parse_args()
    baseline = args.baseline.resolve(strict=True)
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(baseline) or baseline.is_relative_to(output):
        parser.error("Choose a new output outside the baseline")
    changes = args.patch_dir.resolve(strict=True)
    packages = json.loads((changes/"manifest.json").read_text())
    pending = []
    for entry in packages:
        package = child(baseline,entry["baseline_package"])
        target = child(output,entry["asset"])
        for name, digest in entry["original_files"].items():
            if sha(child(package,name).read_bytes()) != digest:
                raise ValueError(f"Baseline file hash mismatch: {name}")
        writes = {}
        for fix in entry["replace"]:
            old = child(package,fix["name"]).read_bytes()
            patch = child(changes,fix["patch"]).read_bytes()
            if sha(old)!=fix["before_sha256"] or sha(patch)!=fix["patch_sha256"]:
                raise ValueError(f"Patch input mismatch: {fix['name']}")
            dictionary = zstandard.ZstdCompressionDict(old,dict_type=zstandard.DICT_TYPE_RAWCONTENT)
            new = zstandard.ZstdDecompressor(dict_data=dictionary).decompress(
                    patch,max_output_size=fix["bytes"])
            if len(new)!=fix["bytes"] or sha(new)!=fix["after_sha256"]:
                raise ValueError(f"Patch output mismatch: {fix['name']}")
            writes[fix["name"]] = new
        for fix in entry["add_references"]:
            new = child(changes,fix["blob"]).read_bytes()
            if sha(new)!=fix["sha256"] or child(package,fix["name"]).exists():
                raise ValueError(f"Conflicting new texture: {fix['name']}")
            writes[fix["name"]] = new
        pending.append((package,target,writes))
    output.mkdir()
    for package,target,writes in pending:
        shutil.copytree(package,target)
        for filename, data in writes.items():
            dest = child(target,filename)
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(data)
        print(target.name,"patched files:",len(writes))


if __name__=="__main__":
    main()
