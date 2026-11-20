"""Render the same assembled exterior and isolated end walls for both far LODs."""
from pathlib import Path
import sys

import bpy
from mathutils import Vector


before, after, output = [Path(s).resolve() for s in sys.argv[sys.argv.index("--") + 1:]]
output.mkdir()
members = ("MitchellTower", "HutchinsonCommons", "ReynoldsClubhouse", "MandelHall")
views = {
    "assembly": (members, (1, 17, 15), (60, 65, 49), 132),
    "hutchinson": (("HutchinsonCommons",), (12.71, 30, 9), (65, -13, 19), 43),
    "reynolds": (("ReynoldsClubhouse",), (15, 13, 8), (-36, -38, 20), 51),
}
for stage, path in (("before", before), ("after", after)):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.use_nodes = False
    scene.render.resolution_x = 820
    scene.render.resolution_y = 620
    scene.render.resolution_percentage = 100
    shading = scene.display.shading
    shading.color_type = "OBJECT"
    shading.show_cavity = True
    for name, color in zip(members, ((.66, .7, .73, 1), (.8, .7, .53, 1),
                                     (.55, .66, .6, 1), (.71, .58, .58, 1))):
        bpy.data.objects[name + "_LOD2"].color = color
    camera = bpy.data.objects.new("Contact review", bpy.data.cameras.new("Contact review"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = "ORTHO"
    for key, (visible, center, offset, scale) in views.items():
        names = {name + "_LOD2" for name in visible}
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                obj.hide_render = obj.name not in names
        target = Vector(center)
        camera.location = target + Vector(offset)
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.ortho_scale = scale
        scene.render.filepath = str(output / f"{stage}-{key}.png")
        bpy.ops.render.render(write_still=True)
