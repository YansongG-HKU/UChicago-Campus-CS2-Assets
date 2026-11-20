"""Set FBX texture links to byte-identical textures already in the original package."""
import hashlib
import importlib.util
from pathlib import Path, PurePosixPath
import sys
from io_scene_fbx import encode_bin, parse_fbx

source, package, destination, converter = [Path(s).resolve() for s in sys.argv[sys.argv.index('--')+1:]]
if destination.exists():
    raise FileExistsError(destination)
spec = importlib.util.spec_from_file_location("project_fbx_converter",converter)
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
root, version = parse_fbx.parse(str(source))
if version != 7500:
    raise ValueError("Expected the verified Blender-generated FBX 7500")

remap = {}
for packed in source.parent.glob("*.png"):
    canonical = package/"textures"/packed.name
    if canonical.is_file() and hashlib.sha256(canonical.read_bytes()).digest()==hashlib.sha256(packed.read_bytes()).digest():
        remap[packed.name] = canonical.relative_to(package).as_posix().encode()
changes = set()
path_nodes = {b"RelativeFilename",b"Filename",b"FileName"}


def clone(element):
    out = encode_bin.FBXElem(element.id)
    for kind,value in zip(element.props_type,element.props):
        if element.id in path_nodes and isinstance(value,bytes) and value:
            name = PurePosixPath(value.decode().replace("\\","/")).name
            if name in remap:
                value = remap[name]
                if element.id==b"RelativeFilename":
                    changes.add(name)
        getattr(out,codec.METHODS[kind])(value)
    out.elems = [clone(child) for child in element.elems]
    return out


with encode_bin.FBXElem.enable_multithreading_cm():
    result = clone(root)
if not changes:
    raise ValueError("No eligible relative texture link changed")
encode_bin.write(str(destination),result,version)
print("Reused exact PNG hashes:",sorted(changes))
