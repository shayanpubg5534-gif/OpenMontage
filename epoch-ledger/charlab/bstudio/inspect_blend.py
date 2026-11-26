"""Inspect a Blender Studio character file (artistic-direction gate). Read-only: prints a JSON summary.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/bstudio/inspect_blend.py FILE.blend [OUT.json]
"""
import json
import sys
import time

import bpy

t0 = time.time()
path = sys.argv[1]
bpy.ops.wm.open_mainfile(filepath=path, load_ui=False)
D = bpy.data
out = {"file": path, "load_s": round(time.time() - t0, 1), "blender": bpy.app.version_string,
       "scenes": [s.name for s in D.scenes], "collections": [c.name for c in D.collections][:40]}
meshes = []
for o in D.objects:
    if o.type == "MESH":
        me = o.data
        sk = [k.name for k in me.shape_keys.key_blocks] if me.shape_keys else []
        meshes.append({"name": o.name, "polys": len(me.polygons), "verts": len(me.vertices), "shape_keys": len(sk),
                       "sk_sample": sk[:12], "mods": [m.type for m in o.modifiers], "mats": [m.name for m in me.materials if m][:6],
                       "parent": o.parent.name if o.parent else None, "hidden": o.hide_render})
out["meshes"] = sorted(meshes, key=lambda m: -m["polys"])[:40]
out["n_mesh_objects"] = len(meshes)
out["total_polys"] = sum(m["polys"] for m in meshes if not m["hidden"])
out["armatures"] = [{"name": o.name, "bones": len(o.data.bones), "deform": sum(b.use_deform for b in o.data.bones)} for o in D.objects if o.type == "ARMATURE"]
out["curves_hair"] = [{"name": o.name, "curves": len(o.data.curves)} for o in D.objects if o.type == "CURVES"]
out["particle_hair"] = [p.name for p in D.particles]
out["node_groups"] = [g.name for g in D.node_groups][:40]
out["materials"] = {m.name: sorted({n.type for n in m.node_tree.nodes}) for m in D.materials if m.use_nodes and m.node_tree}
out["drivers"] = sum(len(o.animation_data.drivers) for o in D.objects if o.animation_data)
out["texts"] = [t.name for t in D.texts]
out["images"] = [(i.name, list(i.size)) for i in D.images][:30]
out["actions"] = [a.name for a in D.actions][:40]
out["libraries"] = [l.filepath for l in D.libraries]
json.dump(out, open(sys.argv[2], "w") if len(sys.argv) > 2 else sys.stdout, indent=1)
print("\nOK", path)
