"""P6 proportion silhouettes: orthographic front and side views at one fixed scale (2.1 m frame, 1000 px tall).

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/p6/ortho_p6.py VARIANT.blend OUTDIR [--nude]
--nude hides wardrobe and hair (proportions of the body itself, as the standard measures them).
"""
import json
import math
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
src, out = argv[0], argv[1]; os.makedirs(out, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=src, load_ui=False); sc = bpy.context.scene
if "--nude" in argv:
    for o in sc.objects:
        if o.type == "MESH" and o.name != "p6_body": o.hide_render = True
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
sc.render.resolution_x, sc.render.resolution_y = 560, 1000
cd = bpy.data.cameras.new("o"); cd.type = "ORTHO"; cd.ortho_scale = 2.1
cam = bpy.data.objects.new("o", cd); sc.collection.objects.link(cam); sc.camera = cam
for name, pos, rot in (("ortho_front", (0, -10, 1.05), (math.pi / 2, 0, 0)), ("ortho_side", (10, 0.03, 1.05), (math.pi / 2, 0, math.pi / 2))):
    cam.location = pos; cam.rotation_euler = rot; sc.render.filepath = os.path.join(out, name + ".png"); bpy.ops.render.render(write_still=True)
json.dump({"ortho_scale": 2.1, "px_per_m": 1000 / 2.1, "z_bottom": 0.0}, open(os.path.join(out, "ortho.json"), "w"))
