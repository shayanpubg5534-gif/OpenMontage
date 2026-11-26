"""Load a converted GLB into an empty Blender scene, relax the arms like render_views.py, save a .blend (for comparison
renders of the conversion in the same renderer as the original).

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/glb_to_blend.py IN.glb OUT.blend [--morphs "name=w,..."]
"""
import math
import sys

import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
glb, out = argv[0], argv[1]
morphs = dict((kv.split("=")[0], float(kv.split("=")[1])) for kv in (argv[argv.index("--morphs") + 1].split(",") if "--morphs" in argv else []) if kv)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
arm.name = "RIG-converted"
bpy.context.view_layer.update()
# arms down: rotate each upper arm about the character's forward axis (-Y) so the hand drops ~68°
for side, sgn in (("l", 1), ("r", -1)):
    pb = arm.pose.bones.get(f"upperarm_{side}")
    if not pb: continue
    R = Matrix.Rotation(math.radians(-68 * sgn), 4, Vector((0, -1, 0)))
    M = arm.matrix_world @ pb.matrix
    loc = M.to_translation()
    W = Matrix.Translation(loc) @ R @ Matrix.Translation(-loc) @ M
    pb.matrix = arm.matrix_world.inverted() @ W
    bpy.context.view_layer.update()
for o in bpy.data.objects:
    if o.type == "MESH" and o.data.shape_keys:
        for k in o.data.shape_keys.key_blocks:
            k.value = morphs.get(k.name, 0.0) if k.name != "Basis" else k.value
bpy.ops.wm.save_as_mainfile(filepath=out)
print("saved", out)
