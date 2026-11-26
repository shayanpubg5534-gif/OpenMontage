"""Does camera perspective exaggerate the head? Renders the converted character (Workbench) through the P2 test camera
(30° vertical fov, 2.1 m away, eye height) and through a long lens with the same framing, and reports the projected head
height relative to the projected chin-to-pelvis length in both, against the orthographic (true) ratio.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/perspective_check.py CHAR.glb PROPS.json OUT_DIR
"""
import json
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
glb, props, out = argv[0], json.load(open(argv[1])), argv[2]; os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
sc = bpy.context.scene
for o in sc.objects:
    if o.type == "MESH" and o.data.shape_keys:
        for k in o.data.shape_keys.key_blocks[1:]: k.value = 0.0
arm = next(o for o in sc.objects if o.type == "ARMATURE")
pelvis_z = (arm.matrix_world @ arm.data.bones["pelvis"].head_local).z
L = props["landmarks_z"]; crown, chin = Vector((0, 0, L["crown"])), Vector((0, 0, L["chin"])); pelvis = Vector((0, 0, pelvis_z))
true_ratio = (L["crown"] - L["chin"]) / (L["chin"] - pelvis_z)
sc.render.engine = "BLENDER_WORKBENCH"; sc.render.resolution_x, sc.render.resolution_y = 1080, 1080
try: sc.render.image_settings.media_type = "IMAGE"
except Exception: pass
sc.render.image_settings.file_format = "PNG"
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.sensor_fit = "VERTICAL"
res = {"true_head_over_torso": round(true_ratio, 3)}
target = Vector((0, 0, 1.15))
for name, dist, fov in (("test_camera_30deg_2.1m", 2.1, 30), ("long_lens_10deg_6.4m", 6.4, 10)):
    d = Vector((0.27, -1, (1.5 - 1.15) / 2.1)).normalized()       # same direction as the test camera (slightly right, eye height)
    cam.location = target + d * dist; cd.angle = math.radians(fov)
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    p = {k: world_to_camera_view(sc, cam, v) for k, v in (("crown", crown), ("chin", chin), ("pelvis", pelvis))}
    r = (p["crown"].y - p["chin"].y) / (p["chin"].y - p["pelvis"].y)
    res[name] = {"head_over_torso": round(r, 3), "exaggeration_pct": round((r / true_ratio - 1) * 100, 1)}
    sc.render.filepath = os.path.join(out, name + ".png"); bpy.ops.render.render(write_still=True)
json.dump(res, open(os.path.join(out, "perspective.json"), "w"), indent=1)
print("PERSPECTIVE", json.dumps(res))
