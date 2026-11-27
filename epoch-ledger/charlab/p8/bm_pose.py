"""P8: pose the free Fab "businessman" (Daydreams Creative Studios; MPFB/MakeHuman-built, Rigify rig) with its own rig.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/p8/bm_pose.py SRC.blend OUT.blend POSE [--face FACE] [--glb OUT.glb]
POSE: rest | stand | point | walk | sit        FACE: neutral | blink | smile | open
Uses only the asset's own Rigify controls (FK arms/legs, spine, head; face controls for lids, lips and jaw). The
character is not modified otherwise. Writes OUT.blend + OUT.json (framing and measurements for render_p6.py) and, with
--glb, a static posed GLB (modifiers applied, subdivision off) for the three.js runtime. Raw asset files stay in
.runtime (not committed: Fab Standard License).
"""
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
src, out, pose = argv[0], argv[1], argv[2]
opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
face = opt("--face", "neutral")
bpy.ops.wm.open_mainfile(filepath=src, load_ui=False)
A = bpy.data.objects["Human.rigify"]; P = A.pose.bones
for o in list(bpy.data.objects):                      # drop widget meshes and annotations (rig display helpers only)
    if o.name.startswith("WGT-") or o.type == "GREASEPENCIL": bpy.data.objects.remove(o)


def upd(): bpy.context.view_layer.update()


def aim(name, direction, roll_ref=None):
    """rotate a pose bone (armature space, about its head) so it points along `direction`"""
    pb = P[name]; upd(); M = pb.matrix.copy(); head = M.to_translation()
    cur = (pb.tail - pb.head).normalized(); tgt = Vector(direction).normalized()
    R = cur.rotation_difference(tgt).to_matrix().to_4x4()
    pb.matrix = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ M; upd()


def rot(name, axis, deg):
    """rotate a pose bone about an armature-space axis through its head"""
    pb = P[name]; upd(); M = pb.matrix.copy(); head = M.to_translation()
    R = Matrix.Rotation(math.radians(deg), 4, Vector(axis))
    pb.matrix = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ M; upd()


def curl(side, fingers, deg):
    for f in fingers:
        for seg in ("01", "02", "03"):
            n = f"f_{f}.{seg}.{side}" if f != "thumb" else f"thumb.{seg}.{side}"
            if n in P:
                pb = P[n]; pb.rotation_mode = "XYZ"; pb.rotation_euler.x += math.radians(deg if f != "thumb" else deg * 0.4)
    upd()


for side in ("L", "R"):                                # FK on limbs (the rig's own switch)
    P[f"upper_arm_parent.{side}"]["IK_FK"] = 1.0; P[f"thigh_parent.{side}"]["IK_FK"] = 1.0
upd()
sx = {"L": 1, "R": -1}
if pose != "rest":
    for s in ("L", "R"):                               # relaxed arms: down, slight elbow bend, palms in
        aim(f"upper_arm_fk.{s}", (sx[s] * 0.10, 0.03, -1.0))
        aim(f"forearm_fk.{s}", (sx[s] * 0.06, -0.18, -1.0))
        curl(s, ("index", "middle", "ring", "pinky"), 18)
        aim(f"thigh_fk.{s}", (sx[s] * 0.05, 0.0, -1.0)); aim(f"shin_fk.{s}", (sx[s] * 0.01, 0.02, -1.0))
if pose == "point":                                    # right hand points forward and across, left relaxed
    aim("upper_arm_fk.R", (-0.35, -0.80, -0.35)); aim("forearm_fk.R", (-0.25, -0.95, 0.05))
    curl("R", ("middle", "ring", "pinky"), 55); curl("R", ("index",), -18)
    rot("head", (0, 0, 1), -12); rot("chest", (0, 0, 1), -6)
if pose == "walk":                                     # contact pose
    aim("thigh_fk.L", (0.02, -0.42, -1.0)); aim("shin_fk.L", (0.0, -0.10, -1.0))
    aim("thigh_fk.R", (-0.02, 0.38, -1.0)); aim("shin_fk.R", (0.0, 0.55, -1.0))
    aim("upper_arm_fk.L", (0.10, 0.30, -1.0)); aim("upper_arm_fk.R", (-0.10, -0.32, -1.0))
    aim("forearm_fk.R", (-0.05, -0.55, -1.0))
if pose == "sit":                                      # seated on a 0.47 m seat: thighs forward, shins down
    for s in ("L", "R"):
        aim(f"thigh_fk.{s}", (sx[s] * 0.10, -1.0, -0.06)); aim(f"shin_fk.{s}", (0.0, 0.05, -1.0))
        aim(f"forearm_fk.{s}", (sx[s] * 0.05, -1.0, -0.25))
    P["torso"].location.z -= 0.0; upd()
# face, with the rig's face controls only (there are no shape keys)
if face == "blink":                                    # lid controls moved along their own local axis that points
    for s in ("L", "R"):                               # most downward in world space (top lids down, bottom lids up)
        for n in [x for x in P.keys() if x.startswith(f"lid.") and x.endswith(s) or (x.startswith("lid.") and f".{s}." in x)]:
            pb = P[n]; M = (A.matrix_world @ pb.bone.matrix_local).to_3x3()
            ax = [M.col[i].normalized() for i in range(3)]; k = max(range(3), key=lambda i: abs(ax[i].z))
            top = ".T." in n; amt = {"": 0.6, ".001": 0.9, ".002": 1.0, ".003": 0.9}.get(n[len("lid.T." + s):] if False else "", 1.0)
            d = (-1 if top else 1) * (0.0095 if top else 0.0025) * (1 if ax[k].z > 0 else -1)
            v = [0.0, 0.0, 0.0]; v[k] = d; pb.location = Vector(v) + pb.location
    upd()
if face == "smile":
    for s in ("L", "R"):
        P[f"lip_end.{s}.001"].location.x += sx[s] * 0.004; P[f"lip_end.{s}.001"].location.y += 0.004
if face == "open":
    P["jaw_master"].rotation_mode = "XYZ"; P["jaw_master"].rotation_euler.x += math.radians(10)
upd()

# seated: bring the hips down to seat height (the set's chair or a stool)
dg = bpy.context.evaluated_depsgraph_get()
meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.hide_render]
pts = []
for o in meshes:
    e = o.evaluated_get(dg); m = e.to_mesh(); pts.append(np.array([(e.matrix_world @ v.co)[:] for v in m.vertices])); e.to_mesh_clear()
allp = np.concatenate(pts)
if pose == "sit":
    A.location.z -= allp[:, 2].min() - 0.0 + 0.0
    hip = A.matrix_world @ P["DEF-thigh.L"].head
    A.location.z += 0.47 - hip.z + 0.05; upd()
else:
    A.location.z -= allp[:, 2].min(); upd()

# framing + measurements (definitions as convert/measure_props.py)
dg = bpy.context.evaluated_depsgraph_get()
def pts_of(o):
    e = o.evaluated_get(dg); m = e.to_mesh(); a = np.array([(e.matrix_world @ v.co)[:] for v in m.vertices]); e.to_mesh_clear(); return a
H = pts_of(bpy.data.objects["Human"]); allp = np.concatenate([pts_of(o) for o in meshes])
crown = H[:, 2].max(); mid = H[np.abs(H[:, 0]) < .006]; fc = mid[mid[:, 2] > crown - .32]; nose = fc[np.argmin(fc[:, 1])]
frt = mid[(mid[:, 2] < nose[2] - .03) & (mid[:, 2] > nose[2] - .15) & (mid[:, 1] < nose[1] + .08)]; chin = frt[:, 2].min()
hh = crown - chin; floor = allp[:, 2].min()
biac = abs((A.matrix_world @ P["DEF-upper_arm.L"].head).x - (A.matrix_world @ P["DEF-upper_arm.R"].head).x)
cr = H[(H[:, 2] > nose[2]) & (H[:, 2] < nose[2] + .07) & (H[:, 1] > nose[1] + .04)]
cr = cr[np.abs(cr[:, 0]) < np.percentile(np.abs(cr[:, 0]), 92)]; head_w = cr[:, 0].max() - cr[:, 0].min()
eyes = [bpy.data.objects[n] for n in ("Default Simple", "Default Simple.001")]
E = np.concatenate([pts_of(o) for o in eyes]); EL = E[E[:, 0] > 0]
lid = [A.matrix_world @ P[n].head for n in ("lid.T.L", "lid.B.L.002") if n in P]
res = {"asset": "Businessman (Daydreams Creative Studios, Fab, Standard License)", "pose": pose, "face": face,
       "height_m": round(float(crown - floor), 4) if pose != "sit" else None, "head_height_m": round(float(hh), 4),
       "heads_tall": round(float((crown - floor) / hh), 2) if pose != "sit" else None,
       "biacromial_m": round(float(biac), 4), "shoulder_width_hh": round(float(biac / hh), 2),
       "eyeball_width_m": round(float(EL[:, 0].max() - EL[:, 0].min()), 4), "head_width_m": round(float(head_w), 4),
       "frame": {"crown_z": float(crown), "chin_z": float(chin), "eye": [float(x) for x in E.mean(0)], "head_y": float(H[H[:, 2] > chin, 1].mean())}}
res["height_m"] = res["height_m"] or round(float(allp[:, 2].max() - floor), 4)
bpy.context.scene.render.engine = "CYCLES"
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(out))
json.dump(res, open(os.path.splitext(out)[0] + ".json", "w"), indent=1)
print("P8POSE", json.dumps({k: v for k, v in res.items() if k != "frame"}))
glb = opt("--glb", None)
if glb:
    import bmesh
    for o in meshes:                                   # the eyeball shell is opaque in glTF (its cornea was a shader):
        if not o.name.startswith("Default Simple"): continue   # remove the front cap so the iris shows
        si = [i for i, m in enumerate(o.data.materials) if m and "Sclera" in m.name]
        bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
        cen = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
        r = max((v.co - cen).length for v in bm.verts)
        dead = [f for f in bm.faces if f.material_index in si and (f.calc_center_median() - cen).normalized().y < -0.82]
        bmesh.ops.delete(bm, geom=dead, context="FACES"); bm.to_mesh(o.data); bm.free()
    A.rotation_euler.z += math.radians(float(opt("--yaw", "0"))); upd()     # facing baked in (static prop)
    for o in meshes:                                   # eyes hang from bones (no skin): keep their world placement
        if o.parent_type == "BONE":
            mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    upd()
    for o in bpy.data.objects:
        for m in o.modifiers:
            if m.type == "SUBSURF": m.levels = 0
        o.select_set(o in meshes)
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_apply=True, export_skins=False,
                              export_morph=False, export_materials="EXPORT")      # the pose is baked into the static mesh
    # runtime materials: opaque cloth and skin (spec/alpha maps made the suit render see-through), cards stay masked
    import struct
    b = open(glb, "rb").read(); n = struct.unpack("<I", b[12:16])[0]; j = json.loads(b[20:20 + n]); rest = b[20 + n:]
    for m in j.get("materials", []):
        name = m.get("name", "")
        m["alphaMode"] = "MASK" if any(k in name for k in ("eyebrow", "eyelash", "afro")) else "OPAQUE"
        if m["alphaMode"] == "MASK": m["alphaCutoff"] = 0.5
        m.pop("extensions", None); pbr = m.setdefault("pbrMetallicRoughness", {}); pbr["metallicFactor"] = 0.0
        pbr["roughnessFactor"] = 0.9 if "suit" in name or "shoes" in name else max(pbr.get("roughnessFactor", 1.0), 0.6)
        if "suit" in name: m.pop("normalTexture", None); pbr.pop("metallicRoughnessTexture", None); pbr["roughnessFactor"] = 1.0       # wool, not satin
        if "Iris" in name: pbr["baseColorFactor"] = [0.09, 0.05, 0.03, 1]           # node-group colours do not export
        if "Sclera" in name: pbr["baseColorFactor"] = [0.78, 0.75, 0.71, 1]
    j.pop("extensionsUsed", None)
    js = json.dumps(j).encode(); js += b" " * (-len(js) % 4)
    out_b = b[:12] + struct.pack("<I", len(js)) + b"JSON" + js + rest
    out_b = out_b[:8] + struct.pack("<I", len(out_b)) + out_b[12:]
    open(glb, "wb").write(out_b)
    print("exported", glb)
