"""Artistic-direction gate: a Blender Studio character inside our documentary set (exported from the runtime), Cycles.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/bstudio/render_in_set.py CHAR.blend SET.glb OUT_PREFIX \
        [--at X,Y] [--yaw DEG] [--acts "A,B"] [--samples 32]
Reuses render_views.py's posing (arms relaxed, pose-library actions). Writes OUT_PREFIX_medium.png and _close.png.
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
char, setglb, outp = argv[0], argv[1], argv[2]
opt = lambda k, d: type(d)(argv[argv.index(k) + 1]) if k in argv else d
at = [float(v) for v in opt("--at", "-1.2,-0.3").split(",")]
yaw = opt("--yaw", 15.0)
SAMPLES = opt("--samples", 32)
bpy.ops.wm.open_mainfile(filepath=char, load_ui=False)
sc = bpy.context.scene
# pose with the same helper code as render_views.py (arms relaxed + bundled expressions)
src = open(os.path.join(os.path.dirname(__file__), "render_views.py")).read()
pose_code = src[src.index("# ── pose:"):src.index("# only what renders")]
pose_ns = {"bpy": bpy, "math": math, "sc": sc, "argv": ["--arms", "--acts", opt("--acts", "")], "opt": lambda k, d: (opt("--acts", "") if k == "--acts" else d)}
exec(pose_code, pose_ns)
rig = pose_ns.get("rig0")
# move the character: everything parented to the rig follows it
roots = [o for o in sc.objects if o.parent is None and o.type in ("ARMATURE", "MESH", "EMPTY", "CURVES")]
for o in roots:
    o.location.x += at[0]; o.location.y += at[1]
    o.rotation_euler.z += math.radians(yaw)
# set
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): o.hide_render = True
bpy.ops.import_scene.gltf(filepath=setglb)
bpy.context.view_layer.update()
head = None
if rig:
    for bn in ("DEF-head", "DEF-Head", "head", "Head", "DEF-neck"):
        b = rig.pose.bones.get(bn)
        if b: head = rig.matrix_world @ ((b.head + b.tail) / 2); break
head = head or Vector((at[0], at[1], 1.6))
# light: warm sun through the window (three.js back wall is Blender +Y), cool fill, dim world
def light(kind, name, loc, energy, color, size=1.0, rot=None):
    L = bpy.data.lights.new(name, kind); L.energy = energy; L.color = color
    if kind == "AREA": L.size = size
    if kind == "SUN": L.angle = math.radians(6)
    o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
    tgt = Vector((at[0], at[1], 1.0)); o.rotation_euler = (tgt - Vector(loc)).to_track_quat("-Z", "Y").to_euler() if rot is None else rot
light("SUN", "set_sun", (-2.5, 4.0, 4.5), 3.2, (1, .9, .78))
light("AREA", "set_fill", (2.5, -3.0, 2.2), 260, (.82, .88, 1), 3.0)
light("AREA", "set_key", (-1.8, -2.4, 2.6), 380, (1, .95, .88), 1.6)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (.55, .52, .48, 1); w.node_tree.nodes["Background"].inputs[1].default_value = .5
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
try: sc.view_settings.view_transform = "AgX"
except Exception: pass
try: sc.render.image_settings.media_type = "IMAGE"
except Exception: pass
sc.render.image_settings.file_format = "PNG"
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
times = {}
for name, pos, look, lens in (("medium", (head.x + .9, head.y - 3.3, 1.45), (head.x - .1, head.y, 1.15), 40),
                              ("close", (head.x + .35, head.y - 1.25, head.z + .02), (head.x, head.y, head.z - .05), 70)):
    cam.location = pos; cd.lens = lens
    cam.rotation_euler = (Vector(look) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{outp}_{name}.png"; t = time.time(); bpy.ops.render.render(write_still=True); times[name] = round(time.time() - t, 1)
print("DONE", times)
