"""Character lab (M2.3c): checks that the designed meshes are driven by the existing rig and expressions.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/verify_design.py CHARACTER.glb OUT.json

Imports the exported GLB and reports, for every designed mesh (stylise.py: hair, ponytail, tie, brows, lash lines):
  * skinning: armature modifier, which bones weight it, and how far it moves when the head bone turns 20 degrees;
  * expressions: each shape key's largest displacement (mm);
  * blink: the gap between the upper and lower lash lines at the eye centre, open and at full closure;
  * brow raise: how far the brow's inner end rises with eyebrows-*-inner-up.
Also counts bones and clips, so a broken rig shows up here too.
"""
from __future__ import annotations

import json
import math
import os
import sys

import bpy
from mathutils import Quaternion, Vector


def keyed(ob, key, w):
    kb = ob.data.shape_keys.key_blocks if ob.data.shape_keys else {}
    for k in kb[1:] if kb else []:
        k.value = 0.0
    if key and key in kb:
        kb[key].value = w


def world(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    out = [ob.matrix_world @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    return out


def main(glb, out):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    rig.animation_data_clear() if rig.animation_data else None
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    designed = [o for o in meshes if "m23c_" in o.name]
    R = {"glb": os.path.basename(glb), "bones": len(rig.data.bones), "actions": sorted(a.name for a in bpy.data.actions),
         "meshes": len(meshes), "designed": {}}
    head = rig.pose.bones["head"]
    for ob in designed:
        mod = next((m for m in ob.modifiers if m.type == "ARMATURE"), None)
        used = {x.group for v in ob.data.vertices for x in v.groups if x.weight > .01}
        groups = sorted(g.name for g in ob.vertex_groups if g.index in used)
        keyed(ob, None, 0)
        a = world(ob)
        head.rotation_mode = "QUATERNION"
        head.rotation_quaternion = Quaternion(Vector((0, 0, 1)), math.radians(20))
        bpy.context.view_layer.update()
        b = world(ob)
        head.rotation_quaternion = Quaternion()
        bpy.context.view_layer.update()
        e = {"armature": bool(mod and mod.object == rig), "bones_weighting": groups[:8],
             "moves_with_head_mm": round(max((p - q).length for p, q in zip(a, b)) * 1000, 1), "vertices": len(a),
             "shape_keys": {}}
        kb = ob.data.shape_keys.key_blocks if ob.data.shape_keys else []
        for k in list(kb)[1:]:
            keyed(ob, k.name, 1.0)
            c = world(ob)
            e["shape_keys"][k.name] = round(max((p - q).length for p, q in zip(a, c)) * 1000, 2)
        keyed(ob, None, 0)
        R["designed"][ob.name] = e
    # blink: upper vs lower lash line, left eye (x > 0), the vertices nearest the lid centre
    up = next((o for o in designed if "lashline_upper" in o.name), None)
    lo = next((o for o in designed if "lashline_lower" in o.name), None)
    if up and lo:
        def lid_gap(w):
            keyed(up, "eye-left-closure", w)
            keyed(lo, "eye-left-closure", w)
            U = [p for p in world(up) if p.x > 0]
            L = [p for p in world(lo) if p.x > 0]
            cx = sum(p.x for p in U) / len(U)
            u = min(U, key=lambda p: abs(p.x - cx))
            lw = min(L, key=lambda p: abs(p.x - cx))
            return round((u.z - lw.z) * 1000, 2)
        R["blink_lid_gap_mm"] = {"open": lid_gap(0), "half": lid_gap(.5), "closed": lid_gap(1)}
        keyed(up, None, 0)
        keyed(lo, None, 0)
    br = next((o for o in designed if "brows" in o.name), None)
    if br:
        a = world(br)
        keyed(br, "eyebrows-left-inner-up", 1)
        b = world(br)
        keyed(br, None, 0)
        inner = min((i for i, p in enumerate(a) if p.x > 0), key=lambda i: a[i].x)
        R["brow_inner_raise_mm"] = round((b[inner].z - a[inner].z) * 1000, 2)
    with open(out, "w") as f:
        json.dump(R, f, indent=2)
    print(json.dumps(R, indent=1))


if __name__ == "__main__":
    code = 0
    try:
        main(*sys.argv[1:3])
    except BaseException:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    os._exit(code)
