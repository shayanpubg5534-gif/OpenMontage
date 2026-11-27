"""Static views of a character file for the artistic-direction gate (Cycles, CPU). Read-only on the source file.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/bstudio/render_views.py FILE.blend OUTDIR [--samples 48] [--res 900]

Options: --illustrated (P5: Workbench texture colour + cavity + outline, a shading-only stylisation test).
Renders, with one neutral light rig for every candidate (so designs are compared, not lighting):
full body front / three-quarter / profile, and head close-ups front / three-quarter / profile.
Framing comes from the rig's head bone and the visible meshes' bounds. timings.json records seconds per image.
"""
import json
import math
import os
import sys
import time

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
path, out = argv[0], argv[1]
opt = lambda k, d: type(d)(argv[argv.index(k) + 1]) if k in argv else d
SAMPLES, RES = opt("--samples", 48), opt("--res", 900)
os.makedirs(out, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=path, load_ui=False)
sc = bpy.context.scene

# ── pose: arms relaxed (FK), optional bundled expression actions (pose library) ─────────────────────────────────────
import re
POSE_ARMS = "--arms" in argv
ACTS = [a for a in opt("--acts", "").split(",") if a]
rig0 = next((o for o in sc.objects if o.type == "ARMATURE" and o.name.startswith("RIG")), None)
def hand_z(rig, side):
    bpy.context.view_layer.update()
    for pat in (r"DEF-(Hand|Wrist|hand|wrist)[._]?" + side, r"(?i)DEF-.*(hand|wrist|palm).*[._]" + side, r"(?i)DEF-.*forearm.*2[._]" + side, r"(?i).*(hand|wrist).*[._]" + side):
        hb = [b for b in rig.pose.bones if re.fullmatch(pat, b.name)]
        if hb: return rig.matrix_world @ hb[0].tail
    return None
if rig0 is not None and ACTS:
    rig0.animation_data_create()
    for an in ACTS:                                  # stack bundled pose-library actions as NLA strips at frame 1
        act = bpy.data.actions.get(an)
        if not act: print("no action", an); continue
        tr = rig0.animation_data.nla_tracks.new(); st = tr.strips.new(an, 1, act)
        try:
            if act.slots: st.action_slot = act.slots[0]
        except Exception: pass
        st.blend_type = "COMBINE" if False else "REPLACE"
    sc.frame_set(1)
if rig0 is not None and POSE_ARMS:
    for b in rig0.pose.bones:                        # FK arms
        for k in list(b.keys()):
            if re.match(r"ik_(left|right)_(upper)?arm$", k): b[k] = 0.0
    for side in ("L", "R"):
        ua = next((rig0.pose.bones.get(n) for n in (f"FK-UpperArm.{side}", f"UpperArm.{side}", f"FK-upper_arm.{side}", f"upper_arm_fk.{side}") if rig0.pose.bones.get(n)), None)
        fa = next((rig0.pose.bones.get(n) for n in (f"FK-Forearm.{side}", f"Forearm.{side}", f"FK-forearm.{side}") if rig0.pose.bones.get(n)), None)
        if not ua: print("no upper arm control", side); continue
        ua.rotation_mode = "XYZ"; best = None
        z0 = hand_z(rig0, side)
        for ax in (0, 2):
            for sg in (1, -1):
                ua.rotation_euler = (0, 0, 0); ua.rotation_euler[ax] = sg * math.radians(68)
                z = hand_z(rig0, side)
                if z is not None and (best is None or z.z < best[0]): best = (z.z, ax, sg)
        ua.rotation_euler = (0, 0, 0)
        if best: ua.rotation_euler[best[1]] = best[2] * math.radians(68)
        print("arm", side, ua.name, best, z0)
    bpy.context.view_layer.update()

# only what renders: visible meshes in the view layer
def visible_meshes():
    return [o for o in sc.objects if o.type in ("MESH", "CURVES") and not o.hide_render and o.visible_get()]

dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in visible_meshes():
    try:
        e = o.evaluated_get(dg)
        for c in e.bound_box: pts.append(e.matrix_world @ Vector(c))
    except Exception:
        pass
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
# robust height: use the rig's head bone when there is one
rig = next((o for o in sc.objects if o.type == "ARMATURE" and o.name.startswith("RIG")), None) or \
      next((o for o in sc.objects if o.type == "ARMATURE"), None)
head = None
if rig:
    for bn in ("DEF-head", "DEF-Head", "head", "Head", "DEF-spine.006", "ORG-head", "MCH-head", "DEF-neck"):
        b = rig.pose.bones.get(bn)
        if b: head = rig.matrix_world @ ((b.head + b.tail) / 2); break
floor = lo.z
top = hi.z
cx, cy = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
if head is None: head = Vector((cx, cy, top - (top - floor) * .07))
H = top - floor
info = {"file": path, "bounds": [list(lo), list(hi)], "height": H, "head": list(head), "rig": rig.name if rig else None}

# neutral studio: backdrop, key / fill / rim area lights, filmic-like view
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): o.hide_render = True
world = bpy.data.worlds.new("eval_world"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.32, .30, .28, 1); world.node_tree.nodes["Background"].inputs[1].default_value = .35
def area(name, loc, energy, size, color=(1, 1, 1)):
    L = bpy.data.lights.new(name, "AREA"); L.energy = energy; L.size = size; L.color = color
    o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
    d = Vector((cx, cy, floor + H * .62)) - Vector(loc); o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler(); return o
s = H / 1.75
area("eval_key", (cx - 2.2 * s, cy - 2.6 * s, floor + 2.3 * s), 900 * s * s, 2.2 * s, (1, .93, .84))
area("eval_fill", (cx + 2.8 * s, cy - 1.6 * s, floor + 1.4 * s), 260 * s * s, 3.0 * s, (.85, .9, 1))
area("eval_rim", (cx + 1.2 * s, cy + 2.6 * s, floor + 2.4 * s), 650 * s * s, 1.6 * s, (1, .95, .9))
bpy.ops.mesh.primitive_plane_add(size=40 * s, location=(cx, cy, floor))
gm = bpy.data.materials.new("eval_floor"); gm.use_nodes = True; gm.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (.36, .34, .32, 1)
bpy.context.object.data.materials.append(gm)

cam_d = bpy.data.cameras.new("eval_cam"); cam = bpy.data.objects.new("eval_cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
try: sc.cycles.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
sc.render.film_transparent = False
try: sc.render.image_settings.media_type = "IMAGE"
except Exception: pass
sc.render.image_settings.file_format = "PNG"
try: sc.view_settings.view_transform = "AgX"
except Exception: sc.view_settings.view_transform = "Filmic"
sc.view_settings.look = "None"
sc.cycles.max_bounces = 6; sc.render.threads_mode = "AUTO"
if "--illustrated" in argv:   # P5 adaptation test: shading-only stylisation (no geometry/rig change), same cameras
    sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading
    sh.light = "STUDIO"; sh.color_type = "TEXTURE"; sh.show_cavity = True; sh.cavity_type = "BOTH"
    sh.cavity_ridge_factor, sh.cavity_valley_factor = 1.2, 1.6; sh.show_object_outline = True; sh.object_outline_color = (.12, .09, .08)
    sh.show_shadows = True; sh.shadow_intensity = .35; sh.show_specular_highlight = False
    sc.display.render_aa = "16"

# character faces -Y in Blender Studio files (front view from -Y)
def shot(name, yaw_deg, target, dist, lens, w, h):
    sc.render.resolution_x, sc.render.resolution_y = w, h
    a = math.radians(yaw_deg)
    pos = Vector((target.x + math.sin(a) * dist, target.y - math.cos(a) * dist, target.z))
    cam.location = pos; cam_d.lens = lens
    cam.rotation_euler = (target - pos).to_track_quat("-Z", "Y").to_euler()
    t = time.time(); sc.render.filepath = os.path.join(out, name + ".png"); bpy.ops.render.render(write_still=True)
    return round(time.time() - t, 1)

times = {}
ONLY = [x for x in opt("--only", "").split(",") if x]; SUF = opt("--suffix", "")
_shot = shot
def shot(name, *a):
    if ONLY and name not in ONLY: return None
    return _shot(name + SUF, *a)
body_t = Vector((cx, cy, floor + H * .5))
for nm, yaw in (("body_front", 0), ("body_34", 35), ("body_profile", 90)):
    times[nm] = shot(nm, yaw, body_t, H * 2.15, 50, int(RES * .62), RES)
face_t = head.copy(); face_t.z -= H * .01
for nm, yaw in (("head_front", 0), ("head_34", 35), ("head_profile", 90)):
    times[nm] = shot(nm, yaw, face_t, H * .62, 85, RES, RES)
info["seconds"] = times
json.dump(info, open(os.path.join(out, f"timings{SUF}.json"), "w"), indent=1)
print("DONE", json.dumps(times))
