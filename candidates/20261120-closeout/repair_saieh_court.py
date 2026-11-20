"""Correct the courtyard-facing side of the northwest Saieh window rows."""
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "20261120-completion"))
from tower_window_winding import fix, GLASS


SOURCE_SHA = "32629cb0e64fe8fb73e747a9107a200aa2c1df6022c119aca0b5b7b5b0bb8195"
CENTERS = (-32.14, -27.64, -23.14, -18.64, -14.14)
CLOISTER_CENTERS = (-33.14, -28.64, -24.14, -19.64, -15.14)
DORMER_CENTERS = (-29.14, -19.14)


def rules(arch_triangles):
    # Geometry from the existing five northwest-range window bays. The
    # original generator faces these two rows toward the south courtyard.
    for index, x in enumerate(CENTERS, start=1):
        for row, radius, bottom, top, triangles in (
            ("arch", 1.3751, 7.2, 13.6, arch_triangles),
            ("upper", 1.0501, 14.8, 16.8, 2),
        ):
            yield (f"northwest_court_bay_{index}_{row}", 1, 3.44, x - radius, x + radius,
                   bottom, top, -1, GLASS, triangles)
    for index, x in enumerate(CLOISTER_CENTERS, start=1):
        yield (f"cloister_bay_{index}", 1, 1.195, x - 1.6501, x + 1.6501,
               .45, 4.85, -1, GLASS, arch_triangles)
    for index, x in enumerate(DORMER_CENTERS, start=1):
        yield (f"south_dormer_{index}", 1, 4.51, x - .6801, x + .6801,
               19.1, 21.1, -1, GLASS, 2)


source, target, report = (Path(arg).resolve() for arg in sys.argv[sys.argv.index("--") + 1:])
if sha256(source.read_bytes()).hexdigest() != SOURCE_SHA or target.exists() or target.suffix != ".blend":
    raise ValueError("Select the audited Saieh source and a new Blender output")
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
proof = {}
for label, suffix, count in (("near", "", 13), ("mid", "_LOD1", 11)):
    obj = bpy.data.objects["SaiehHall" + suffix]
    assert obj.matrix_world.is_identity
    proof[label] = fix(obj.data, rules(count))
bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
report.write_text(json.dumps({"source_sha256": SOURCE_SHA, "candidate_sha256": sha256(target.read_bytes()).hexdigest(),
                              "tiers": proof}, indent=2) + "\n")
