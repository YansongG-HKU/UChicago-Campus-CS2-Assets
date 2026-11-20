"""Recover exact candidate binary files in a separate directory."""
import argparse
import hashlib
import json
from pathlib import Path

import zstandard


def require_sha(data, expected, name):
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"SHA-256 mismatch: {name}")
    return data


def safe_child(directory, relative):
    target = (directory / relative).resolve()
    if not target.is_relative_to(directory):
        raise ValueError(f"Path is outside input directory: {relative}")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--patch-dir", type=Path)
    args = parser.parse_args()
    baseline = args.baseline.resolve(strict=True)
    output = args.destination.resolve()
    if output.exists() or output.is_relative_to(baseline) or baseline.is_relative_to(output):
        parser.error("Choose a new directory outside the baseline")
    patch_dir = (args.patch_dir or Path(__file__).parent / "patches").resolve(strict=True)
    manifest = json.loads((patch_dir / "manifest.json").read_text())
    recovered = {}
    for row in manifest:
        basis = safe_child(baseline, row["source"]).read_bytes()
        require_sha(basis, row["source_sha256"], row["source"])
        patch = safe_child(patch_dir, row["delta"]).read_bytes()
        require_sha(patch, row["delta_sha256"], row["delta"])
        if len(patch) != row["delta_bytes"]:
            raise ValueError(f"Wrong delta length: {row['delta']}")
        dictionary = zstandard.ZstdCompressionDict(basis, dict_type=zstandard.DICT_TYPE_RAWCONTENT)
        result = zstandard.ZstdDecompressor(dict_data=dictionary).decompress(
            patch, max_output_size=row["candidate_bytes"])
        if len(result) != row["candidate_bytes"]:
            raise ValueError(f"Wrong candidate length: {row['candidate']}")
        target = safe_child(output, row["candidate"])
        require_sha(result, row["candidate_sha256"], target.name)
        recovered[target] = result
    output.mkdir()
    for target, data in recovered.items():
        with target.open("xb") as stream:
            stream.write(data)
        print(target.name, len(data), hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
