"""Rain → mature adult professional, a restrained study using only her own rig controls (no sculpting, no neck change).
Anatomical cues of adulthood in stylized design: a longer lower face relative to the cranium, relatively smaller eyes.
Styling: hairband and scarf removed, top recoloured. Writes a .blend for render_views.py.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/rain_mature.py RAIN.blend OUT.blend [--lower 1.08] [--upper .96] [--eyes .9]
"""
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
src, out = argv[0], argv[1]
opt = lambda k, d: float(argv[argv.index(k) + 1]) if k in argv else d
bpy.ops.wm.open_mainfile(filepath=src, load_ui=False)
rig = bpy.data.objects["RIG-rain"]
rig.pose.bones["MSTR-Head_Lower"].scale = (1, opt("--lower", 1.08), 1)
u = opt("--upper", .96); rig.pose.bones["MSTR-Head_Upper"].scale = (u, u, u)
e = opt("--eyes", .9)
for s in ("L", "R"): rig.pose.bones[f"MSTR-Eye.{s}"].scale = (e, e, e)
for n in ("GEO-rain-hairband", "GEO-rain-scarf"):
    o = bpy.data.objects.get(n)
    if o: o.hide_render = True; o.hide_viewport = True
m = bpy.data.materials.get("MAT-rain.top")
if m and m.use_nodes:
    nt = m.node_tree; p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"); bc = p.inputs["Base Color"]
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1.0
    mix.inputs[7].default_value = (.08, .11, .22, 1)                      # B: deep navy
    if bc.is_linked: nt.links.new(bc.links[0].from_socket, mix.inputs[6])
    else: mix.inputs[6].default_value = bc.default_value
    nt.links.new(mix.outputs[2], bc)
bpy.ops.wm.save_as_mainfile(filepath=out)
print("saved", out)
