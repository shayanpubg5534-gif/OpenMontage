"""Proportion measurement (P3): heads tall, shoulder width, head width, eye size, from evaluated meshes; plus orthographic
front and side silhouettes (Workbench) for a comparison sheet.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/measure_props.py FILE(.blend|.glb) OUT_DIR --head NAME_SUBSTR
        [--exclude hair,brow,lash] [--rig RIGNAME] [--arms]

Landmarks (metres): floor = lowest point of the character; crown = highest point of the head mesh (hair excluded);
chin = lowest point of the front facial midline before the profile turns back into the neck; shoulders = outermost
points of the upper torso at 82% of height (deltoid width); head width = widest cranium point between brow and ear level
(ears excluded by a midline-distance cap); eye width = horizontal extent of one eye opening.
"""
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
src, out = argv[0], argv[1]; os.makedirs(out, exist_ok=True)
opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
HEAD = opt("--head", "head"); EXCL = [e for e in opt("--exclude", "hair,brow,lash,eye_dots,cornea,widget,wgt").split(",") if e]
if src.endswith(".glb"):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=src)
else:
    bpy.ops.wm.open_mainfile(filepath=src, load_ui=False)
sc = bpy.context.scene; vl = bpy.context.view_layer
for o in sc.objects:
    if o.type == "MESH" and o.data.shape_keys:
        for k in o.data.shape_keys.key_blocks[1:]: k.value = 0.0
dg = bpy.context.evaluated_depsgraph_get()
def pts(o):
    e = o.evaluated_get(dg); me = e.to_mesh(); a = np.array([(e.matrix_world @ v.co)[:] for v in me.vertices]).reshape(-1, 3); e.to_mesh_clear(); return a
vis = [o for o in sc.objects if o.type == "MESH" and not o.hide_render and o.name in vl.objects and not any(c.hide_render for c in o.users_collection)
       and not any(x in o.name.lower() for x in EXCL)]
allp = np.concatenate([pts(o) for o in vis]); floor = max(allp[:, 2].min(), -.02)   # characters stand at z=0; props below ground are ignored
heads = [o for o in vis if HEAD.lower() in o.name.lower()]
H = pts(heads[0]) if heads else allp
crown = H[:, 2].max()
# front facial midline: Blender characters face -Y
mid = H[np.abs(H[:, 0]) < .006]
face = mid[mid[:, 2] > crown - .32]
nose = face[np.argmin(face[:, 1])]
# chin: the lowest midline point still within 8 cm of the nose-tip plane (the neck lies 10 cm or more behind it)
front = mid[(mid[:, 2] < nose[2] - .03) & (mid[:, 2] > nose[2] - .15) & (mid[:, 1] < nose[1] + .08)]
chin_z = front[:, 2].min()
head_h = crown - chin_z; height = crown - floor
# shoulders: biacromial width between the upper-arm joint centres (anthropometric standard), from the skeleton
import re
arm = next((o for o in sc.objects if o.type == "ARMATURE" and o.name.startswith("RIG")), None) or next((o for o in sc.objects if o.type == "ARMATURE"), None)
shoulder_w = None
if arm:
    ua = [b for b in arm.data.bones if b.use_deform and re.search(r"(?i)upper_?arm_?1?[._-]?(l|r)$", b.name)]
    if len(ua) < 2: ua = [b for b in arm.data.bones if re.fullmatch(r"(?i)upper_?arm[._-]?(l|r)", b.name)]
    xs = sorted({round((arm.matrix_world @ b.head_local).x, 4) for b in ua})
    if len(xs) >= 2: shoulder_w = xs[-1] - xs[0]
cr = H[(H[:, 2] > nose[2]) & (H[:, 2] < nose[2] + .07) & (H[:, 1] > nose[1] + .04)]
cr = cr[np.abs(cr[:, 0]) < np.percentile(np.abs(cr[:, 0]), 92)]          # drop the ears
head_w = cr[:, 0].max() - cr[:, 0].min()
eye = [o for o in vis if "eye" in o.name.lower() and "brow" not in o.name.lower() and "lash" not in o.name.lower()]
eye_w = None
if eye:
    E = np.concatenate([pts(o) for o in eye]); L = E[E[:, 0] > 0]
    if len(L): eye_w = L[:, 0].max() - L[:, 0].min()
m = {"file": src, "height_m": round(height, 3), "head_h_m": round(head_h, 3), "heads_tall": round(height / head_h, 2),
     "biacromial_m": round(shoulder_w, 3) if shoulder_w else None, "biacromial_in_head_heights": round(shoulder_w / head_h, 2) if shoulder_w else None,
     "head_w_m": round(head_w, 3), 
     "eye_w_m": round(eye_w, 3) if eye_w else None, "eye_w_over_head_w": round(eye_w / head_w, 3) if eye_w else None,
     "landmarks_z": {"floor": round(floor, 3), "chin": round(chin_z, 3), "crown": round(crown, 3)}}
# orthographic silhouettes, same pixel scale per metre of height
for o in sc.objects:
    if o.type in ("LIGHT", "CAMERA"): o.hide_render = True
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
try: sc.render.image_settings.media_type = "IMAGE"
except Exception: pass
sc.render.image_settings.file_format = "PNG"
sc.render.resolution_x, sc.render.resolution_y = 500, 1000
cd = bpy.data.cameras.new("o"); cd.type = "ORTHO"; cd.ortho_scale = height * 1.1
cam = bpy.data.objects.new("o", cd); sc.collection.objects.link(cam); sc.camera = cam
cx = (allp[:, 0].max() + allp[:, 0].min()) / 2; cy = (allp[:, 1].max() + allp[:, 1].min()) / 2; zc = floor + height / 2
for name, pos, rot in (("ortho_front", (cx, cy - 10, zc), (math.pi / 2, 0, 0)), ("ortho_side", (cx + 10, cy, zc), (math.pi / 2, 0, math.pi / 2))):
    cam.location = pos; cam.rotation_euler = rot; sc.render.filepath = os.path.join(out, name + ".png"); bpy.ops.render.render(write_still=True)
m["ortho"] = {"ortho_scale": cd.ortho_scale, "z_centre": zc, "px_per_m": 1000 / cd.ortho_scale}
json.dump(m, open(os.path.join(out, "props.json"), "w"), indent=1)
print("PROPS", json.dumps({k: m[k] for k in ("heads_tall", "biacromial_in_head_heights", "eye_w_over_head_w", "height_m")}))
