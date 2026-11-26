"""Retarget the lab's mocap clip set onto a converted character and export the runtime GLB with animations.
Reuses build_character.retarget (bone-direction matching onto the lab's bone names) unchanged.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/add_clips.py IN.glb OUT.glb --bvh name=FILE:a:b ...
"""
import json
import os
import sys
import time

import bpy

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
src, out = argv[0], argv[1]
clips = {}
for i, a in enumerate(argv):
    if a == "--bvh":
        k, v = argv[i + 1].split("=", 1); clips[k] = v
import build_character as BC   # noqa: E402

t0 = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
for pb in rig.pose.bones: pb.rotation_mode = "QUATERNION"
for o in bpy.data.objects:          # shape keys at rest
    if o.type == "MESH" and o.data.shape_keys:
        for k in o.data.shape_keys.key_blocks[1:]: k.value = 0.0
BC.retarget(rig, clips)
if "--no-grip" not in argv: BC.grip_action(rig)   # finger curl reference clip used by the runtime's hand poses
for o in bpy.data.objects: o.select_set(o.type in ("MESH", "ARMATURE"))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_skins=True, export_morph=True,
                          export_morph_normal=True, export_animations=True, export_animation_mode="ACTIONS", export_yup=True,
                          export_image_format="JPEG", export_jpeg_quality=90, export_force_sampling=True)
rep = {"clips": BC.LOG.get("clips"), "seconds": round(time.time() - t0, 1), "glb_mb": round(os.path.getsize(out) / 1e6, 2)}
json.dump(rep, open(out + ".json", "w"), indent=1)
print("CLIPS", json.dumps(rep))
