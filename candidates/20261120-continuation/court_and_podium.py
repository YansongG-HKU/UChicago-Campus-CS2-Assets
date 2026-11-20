"""Measure Hull Court lab envelopes and the paired Woodlawn podium in Blender."""
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


UP = Vector((0, 0, 1))
TIERS = ("", "_LOD1", "_LOD2")


class MeshProbe:
    def __init__(self, obj):
        mesh = obj.data
        mesh.calc_loop_triangles()
        points = [obj.matrix_world @ v.co for v in mesh.vertices]
        faces = [tuple(p.vertices) for p in mesh.loop_triangles]
        self.tree = BVHTree.FromPolygons(points, faces, all_triangles=True)
        self.bounds = [[round(min(v[i] for v in points), 6), round(max(v[i] for v in points), 6)]
                       for i in range(3)]
        self.triangles = len(faces)

    def height(self, x, y, start, end):
        direction = UP if end > start else -UP
        point, _, _, _ = self.tree.ray_cast(Vector((x, y, start)), direction, abs(end - start))
        return round(point.z, 6) if point is not None else None

    def wall(self, x, y, z, direction, distance):
        point, _, _, _ = self.tree.ray_cast(Vector((x, y, z)), direction, distance)
        return round(point.y, 6) if point is not None else None

    def envelope(self):
        return {"bounds_m": self.bounds, "triangles": self.triangles}


def load_source(path):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    return sha256(path.read_bytes()).hexdigest()


def hull_court(assets):
    group = assets / "HullCourt_v0.1/HullCourt"
    model = group / "source/HullCourtAssembly.blend"
    doc = json.loads((group / "documentation/assembly_coordinates.json").read_text())
    answer = {"assembly_sha256": load_source(model), "components": {}, "loggias": {}}
    in_assembly = {
        comp["asset"] + suffix: MeshProbe(bpy.data.objects[comp["asset"] + suffix]).envelope()
        for comp in doc["components"] for suffix in TIERS
    }
    for joint in doc["joints"][:2]:
        left, right = joint["owning_component"], joint["counterpart"]
        x, seam_y, _ = joint["authored_position_xyz_m"]
        loggia_name = {"CulverHall": "Culver", "ErmanBiologyCenter": "Erman"}[left]
        loggia = MeshProbe(bpy.data.objects[f"{loggia_name} optional lab-side loggia shell"])
        samples = {}
        for suffix in TIERS:
            southern = MeshProbe(bpy.data.objects[left + suffix])
            northern = MeshProbe(bpy.data.objects[right + suffix])
            rows = []
            for dx in (-1.2, -.8, 0, .8, 1.2):
                for z in (.1, 1.1, 2.9, 4.75):
                    row = {"x": x + dx, "z": z}
                    row["south_lab_end"] = southern.wall(x + dx, seam_y + 1, z, Vector((0, -1, 0)), 5)
                    row["north_lab_end"] = northern.wall(x + dx, seam_y + 8, z, Vector((0, 1, 0)), 7)
                    for key, y, direction in (("south_proxy", seam_y - 1, 1), ("north_proxy", seam_y + 12, -1)):
                        row[key] = loggia.wall(x + dx, y, z, Vector((0, direction, 0)), 8)
                    rows.append(row)
            samples[suffix or "near"] = rows
        answer["loggias"][joint["id"]] = {"proxy": loggia.envelope(), "samples": samples}
    answer["gate_markers"] = [o.name for o in bpy.context.scene.objects if o.type == "EMPTY" and "Cobb Gate" in o.name]

    for comp in doc["components"]:
        name = comp["asset"]
        source = group / "source" / f"{name}.blend"
        entry = {"sha256": load_source(source), "documented_model_body_xy_m": comp["body_xy_m"],
                 "body_measurement_basis": comp["body_basis"], "tiers": {}}
        footprint = comp["footprint_shared_frame_xy_m"]
        center = [sum(p[i] for p in footprint) / len(footprint) for i in range(2)]
        x, y = center
        long_x = comp["body_xy_m"][0] > comp["body_xy_m"][1]
        for suffix in TIERS:
            key = name + suffix
            model_probe = MeshProbe(bpy.data.objects[key])
            stations = [(x + offset if long_x else x, y if long_x else y + offset)
                        for offset in (-6, -3, 0, 3, 6)]
            entry["tiers"][suffix or "near"] = {
                **model_probe.envelope(),
                "assembly_envelope": in_assembly[key],
                "centerline": [{"xy_m": (px, py), "roof_z_m": model_probe.height(px, py, 60, 0),
                                "underside_z_m": model_probe.height(px, py, -.1, 5)}
                               for px, py in stations],
            }
        answer["components"][name] = entry
    return answer


def woodlawn(assets):
    document = assets / "WoodlawnDining/WoodlawnDining/documentation/assembly_contract.json"
    contract = json.loads(document.read_text())
    source = assets / "WoodlawnCommonsAssembly/WoodlawnCommonsAssembly/source/WoodlawnCommonsAssembly.blend"
    result = {"assembly_sha256": load_source(source), "nominal_podium_roof_z_m": contract["podium_roof_z_m"], "tiers": {}}
    names = ("WoodlawnDining", "WoodlawnResidential")
    for suffix in TIERS:
        models = {name: MeshProbe(bpy.data.objects[name + suffix]) for name in names}
        patches = []
        for i, joint in enumerate(contract["joint_segments"], 1):
            samples = []
            tangent = Vector(joint["tangent_xyz"])
            normal = Vector(joint["outward_normal_xyz"])
            anchor = Vector(joint["anchor_common_m"])
            for section in (-.4, -.2, 0, .2, .4):
                for off in (-.05, -.015, 0, .015, .05):
                    point = anchor + tangent * section * joint["width_m"] + normal * off
                    samples.append({"along_fraction": section, "signed_offset_m": off,
                                    "xy_m": [round(point.x, 6), round(point.y, 6)],
                                    "roof_first_hit_m": {n: g.height(point.x, point.y, 7, 3.8) for n, g in models.items()},
                                    "underside_first_hit_m": {n: g.height(point.x, point.y, -.1, .5) for n, g in models.items()}})
            patches.append({"segment": i, "samples": samples})
        result["tiers"][suffix or "near"] = {"components": {n: g.envelope() for n, g in models.items()},
                                             "podium_sections": patches}
    return result


assets, output = [Path(v).resolve() for v in sys.argv[sys.argv.index("--") + 1:]]
output.mkdir()
for name, job in (("HullCourt", hull_court), ("Woodlawn", woodlawn)):
    (output / f"{name}.json").write_text(json.dumps(job(assets), indent=2) + "\n")
