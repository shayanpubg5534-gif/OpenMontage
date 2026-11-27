"""P6: export a P6 character .blend to a static GLB for the three.js runtime (bank still; experimental).

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/p6/export_glb.py VARIANT.blend OUT.glb

The skin's painted zones (warm cheeks, lips, stubble, scalp) are baked from the Cycles shader into a 2048 px texture; cloth and hair keep their base colours (the Cycles-only cavity tint is not exported).
Modifiers (subdivision, thickness) are applied. Static: no rig, no shape keys (the gate is visual).
"""
import sys

import bpy
import numpy as np

src, out = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=src, load_ui=False)
body = bpy.data.objects["p6_body"]; me = body.data
import bmesh  # noqa: E402
ci = [i for i, m in enumerate(me.materials) if m and m.name == "cornea"]
bm = bmesh.new(); bm.from_mesh(me)                       # the cornea is a Cycles mix shader (no glTF equivalent): drop it
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in ci], context="FACES"); bm.to_mesh(me); bm.free()
# bake the skin shader's painted colour to a 2048 px texture (the glTF exporter writes no usable vertex colours here)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = 1; sc.cycles.device = "CPU"
img = bpy.data.images.new("skin_paint", 2048, 2048)
skin = bpy.data.materials["skin"]; tn = skin.node_tree.nodes.new("ShaderNodeTexImage"); tn.image = img; skin.node_tree.nodes.active = tn
for o in bpy.data.objects: o.select_set(o is body)
bpy.context.view_layer.objects.active = body
for md in body.modifiers: md.show_render = False
sc.render.bake.use_pass_direct = False; sc.render.bake.use_pass_indirect = False; sc.render.bake.use_pass_color = True; sc.render.bake.margin = 8
bpy.ops.object.bake(type="DIFFUSE")
for md in body.modifiers: md.show_render = True
for m in bpy.data.materials:
    if not m.use_nodes: continue
    nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    if not b: continue
    for k in ("Sheen Weight", "Subsurface Weight", "Coat Weight", "Anisotropic", "Transmission Weight"):   # no runtime equivalent:
        if k in b.inputs: b.inputs[k].default_value = 0.0                                                     # glTF extensions render far too bright
    lk = b.inputs["Base Color"].links
    if m.name == "skin":
        for l in list(lk): nt.links.remove(l)
        nt.links.new(tn.outputs["Color"], b.inputs["Base Color"])
    elif lk and lk[0].from_node.type == "VALTORGB":
        colr = lk[0].from_node.color_ramp.elements[1].color; nt.links.remove(lk[0]); b.inputs["Base Color"].default_value = colr
for o in bpy.data.objects: o.select_set(o.type == "MESH")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=True, export_vertex_color="ACTIVE",
                          export_all_vertex_colors=False, export_materials="EXPORT")
print("exported", out)
