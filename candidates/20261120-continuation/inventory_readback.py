"""Read back the actual historical deliverable FBXs against 88 registered source families."""
import argparse
import collections
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("root", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--jobs", type=int, default=3)
parser.add_argument("--skip-import", action="store_true")
args = parser.parse_args()
repo = Path(__file__).resolve().parents[2]
output = args.output.absolute()
output.mkdir(parents=True, exist_ok=True)
audited = json.loads((repo/"candidates/20261118-technical/evidence/source_audit.json").read_text())

sources = collections.defaultdict(list)
for scene in audited:
    for family in scene["families"]:
        name = family["family"]
        if not name.startswith("__"):
            sources[name].append((scene, family))

by_group = {}
plan = {}
for name, choices in sorted(sources.items()):
    def source_rank(entry):
        path = Path(entry[0]["source"])
        return (path.stem != name, path.parts[1] == "RockefellerChapel_v02",
                len(entry[0]["families"]), path.as_posix())
    scene, family = min(choices, key=source_rank)
    grouping = Path(scene["source"]).parts[1]
    group = by_group.setdefault(grouping, collections.defaultdict(list))
    if not group:
        for path in (args.root/"assets"/grouping).rglob("*.fbx"):
            rel = path.relative_to(args.root)
            if "historical_evidence" in rel.parts:
                continue
            stem = path.stem.casefold()
            group[stem].append(path)
    exact = {}
    missing = []
    for mesh in family["meshes"]:
        mesh_name = mesh["name"]
        matches = group.get(mesh_name.casefold(), [])
        if mesh_name == name:
            matches = matches + group.get((name+"_Main").casefold(), [])
        if not matches:
            missing.append(mesh_name)
            continue
        def rank(path):
            return ("ProjectFiles" not in path.parts, path.parent.name != name,
                    "repair_20261007" in path.parts, len(path.parts), str(path))
        exact[mesh_name] = str(min(matches, key=rank).resolve())
    plan[name] = {"source":scene["source"], "source_sha256":scene["source_sha256"],
                  "fbx":exact,"unmapped":missing}
assert len(plan)==88, len(plan)
(output/"plan.json").write_text(json.dumps(plan,indent=2)+"\n")
if args.skip_import:
    raise SystemExit(0)


def verify(job):
    name, entry = job
    source = args.root/entry["source"]
    checksum = hashlib.sha256()
    with source.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            checksum.update(block)
    if checksum.hexdigest() != entry["source_sha256"]:
        raise ValueError(f"Source hash changed for {source}")
    report = output/f"{name}.json"
    fbx_paths = output/f"{name}.paths.json"
    fbx_paths.write_text(json.dumps(entry["fbx"])+"\n")
    if not entry["fbx"]:
        return name, {"state":"unmapped","unmapped":entry["unmapped"]}
    command = ["blender","-b","-t","1","--factory-startup","--disable-autoexec","--python-exit-code","1","--python",
               str(repo/"candidates/20261120-cloud/fbx_review.py"),"--",
               str(source),str(report),*entry["fbx"],"--packaged-map",str(fbx_paths)]
    with (output/f"{name}.log").open("w") as log:
        check = subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    if check.returncode:
        return name, {"state":"import_error","returncode":check.returncode,"unmapped":entry["unmapped"]}
    actual = json.loads(report.read_text())
    revision = []
    for row in actual["records"]:
        if not row["oriented_triangles_match"] or row["corner_uv_max_delta"] != 0:
            revision.append({"mesh":row["name"],"source":row["source_triangles"],"delivered":row["reimport_triangles"],
                             "delta_m":row["vertex_max_delta_m"],"uv_delta":row["corner_uv_max_delta"]})
    missing_references = [{"mesh":row["name"],"path":p} for row in actual["records"]
                          for p,sha in row["texture_reference_hashes"].items() if sha is None]
    return name, {"state":"readback","readback_meshes":len(actual["records"]),
                  "geometry_or_uv_differences":revision,"unmapped":entry["unmapped"],
                  "invalid_or_missing_relative_references":missing_references}


results = {}
with ThreadPoolExecutor(max_workers=args.jobs) as queue:
    jobs = [queue.submit(verify,job) for job in plan.items()]
    for finished in as_completed(jobs):
        name, result = finished.result()
        results[name] = result
        (output/"summary.json").write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
        print(name,result["state"],flush=True)
