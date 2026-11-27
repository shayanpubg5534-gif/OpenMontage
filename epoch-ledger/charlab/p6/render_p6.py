"""P6 comparison views: one neutral studio for every variant (same lights, cameras, background, exposure).

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/p6/render_p6.py VARIANT.blend OUTDIR [--samples 64] [--res 1000]

Views: full_front, full_side (85 mm-equivalent long lens, camera at mid-height: no flattering low angle),
face_front, face_34, face_side (100 mm-equivalent). Neutral grey cyclorama, a soft key, fill and rim.
"""
import json
import math
import os
import sys
import time

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
src, out = argv[0], argv[1]; os.makedirs(out, exist_ok=True)
opt = lambda k, d: type(d)(argv[argv.index(k) + 1]) if k in argv else d
SAMPLES, RES = opt("--samples", 64), opt("--res", 1000)
ONLY = opt("--only", "")
bpy.ops.wm.open_mainfile(filepath=src, load_ui=False)
info = json.load(open(os.path.splitext(src)[0] + ".json"))
F = info["frame"]; sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.film_transparent = False
w = sc.world or bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.32, 0.33, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.35
# cyclorama
bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 1.5, 0)); cyc = bpy.context.object
m = bpy.data.materials.new("cyc"); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.36, 0.36, 0.37, 1)
m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9; cyc.data.materials.append(m)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.subdivide(number_cuts=30); bpy.ops.object.mode_set(mode="OBJECT")
for v in cyc.data.vertices:     # curve up behind the subject
    wy = v.co.y + 1.5
    if wy > 2.2: v.co.z = (wy - 2.2) ** 1.6 * 1.2
cyc.modifiers.new("s", "SUBSURF").levels = 1; bpy.ops.object.shade_smooth()


def area(name, loc, size, energy, col=(1, 1, 1), target=(0, 0, 1.1)):
    L = bpy.data.lights.new(name, "AREA"); L.size = size; L.energy = energy; L.color = col
    o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


area("key", (-2.2, -2.6, 2.6), 2.2, 260, (1.0, 0.95, 0.88))
area("fill", (2.6, -2.2, 1.4), 3.0, 80, (0.88, 0.93, 1.0))
area("rim", (1.2, 2.6, 2.4), 1.2, 160, (1.0, 0.97, 0.92))
area("face_key", (-0.9, -1.3, 1.95), 0.6, 10, (1.0, 0.95, 0.88), target=(0, 0, F["eye"][2]))

cam = bpy.data.cameras.new("cam"); co_ = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co_); sc.camera = co_
H = info["height_m"]; hh = F["crown_z"] - F["chin_z"]; eye = Vector(F["eye"]); hc = Vector((0, F["head_y"], (F["crown_z"] + F["chin_z"]) / 2 - 0.005))
views = {
    "full_front": dict(lens=85, dist=None, dirn=(0, -1, 0), tgt=Vector((0, 0, H / 2)), w=0.62 * RES, h=RES, fit=H * 1.08),
    "full_side": dict(lens=85, dist=None, dirn=(1, 0, 0), tgt=Vector((0, 0.03, H / 2)), w=0.62 * RES, h=RES, fit=H * 1.08),
    "face_front": dict(lens=100, dist=None, dirn=(0, -1, 0), tgt=hc, w=0.85 * RES, h=RES, fit=hh * 1.75),
    "face_34": dict(lens=100, dist=None, dirn=(math.sin(math.radians(-35)) * -1, -math.cos(math.radians(35)), 0), tgt=hc, w=0.85 * RES, h=RES, fit=hh * 1.75),
    "face_side": dict(lens=100, dist=None, dirn=(1, 0, 0), tgt=hc + Vector((0, 0.01, 0)), w=0.85 * RES, h=RES, fit=hh * 1.75),
}
times = {}
for name, v in views.items():
    if ONLY and name not in ONLY.split(","): continue
    sc.render.resolution_x, sc.render.resolution_y = int(v["w"]), int(v["h"])
    cam.lens = v["lens"]; cam.sensor_fit = "VERTICAL"; cam.sensor_height = 24
    dist = v["fit"] / 2 / math.tan(math.atan(12 / v["lens"]))
    d = Vector(v["dirn"]).normalized(); co_.location = v["tgt"] + d * dist
    co_.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.clip_start = 0.05; cam.clip_end = 100
    t = time.time(); sc.render.filepath = os.path.join(out, name + ".png"); bpy.ops.render.render(write_still=True)
    times[name] = round(time.time() - t, 1); print("rendered", name, times[name])
json.dump(times, open(os.path.join(out, "timings.json"), "w"))
