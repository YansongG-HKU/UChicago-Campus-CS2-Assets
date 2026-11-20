"""Same-camera Blender workbench previews at the Hinds armillary pedestal."""
from pathlib import Path
import sys
import bpy
from mathutils import Vector

before, after, output = [Path(s) for s in sys.argv[sys.argv.index('--')+1:]]
output.mkdir()
for stage,path in [("before",before),("after",after)]:
    bpy.ops.wm.open_mainfile(filepath=str(path.resolve()),load_ui=False)
    scene=bpy.context.scene
    scene.render.engine="BLENDER_WORKBENCH"
    scene.use_nodes=False
    scene.render.resolution_x=900
    scene.render.resolution_y=650
    scene.render.resolution_percentage=100
    scene.display.shading.color_type="SINGLE"
    scene.display.shading.single_color=(.69,.72,.68)
    scene.display.shading.show_cavity=True
    camera=bpy.data.objects.new("Armillary review",bpy.data.cameras.new("Armillary review"))
    scene.collection.objects.link(camera)
    scene.camera=camera
    camera.data.type="ORTHO"
    camera.data.ortho_scale=1.55
    target=Vector((16.5,-3,2.4))
    camera.location=target+Vector((8,2.2,.18))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    for suffix in ("","_LOD1"):
        for obj in bpy.data.objects:
            if obj.type=="MESH":
                obj.hide_render=obj.name!="HenryHindsLaboratory"+suffix
        scene.render.filepath=str(output/(stage+(suffix or "_near")+".png"))
        bpy.ops.render.render(write_still=True)
