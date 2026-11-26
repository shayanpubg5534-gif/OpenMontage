"""Integration test (artistic-direction gate): export a Blender Studio character to glTF for the three.js runtime.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/bstudio/export_gltf.py FILE.blend OUT.glb [--apply]

Exports visible meshes + the deform skeleton + shape keys. Without --apply, modifiers other than the armature are
dropped (subdivision, lattices, corrective smooth, surface deform), which is how a skinned, shape-keyed runtime
character has to be shipped. With --apply, modifiers are baked into the mesh, which removes shape keys.
Reports what survives (polys, bones, shape keys, materials, hair) as JSON next to the output.
"""
import json
import os
import sys
import time

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
src, out = argv[0], argv[1]
apply_mods = "--apply" in argv
bpy.ops.wm.open_mainfile(filepath=src, load_ui=False)
sc = bpy.context.scene
vis = [o for o in sc.objects if o.type == "MESH" and not o.hide_render and o.visible_get()]
dropped = {}
for o in vis:
    for m in o.modifiers:
        if m.type != "ARMATURE":
            dropped[m.type] = dropped.get(m.type, 0) + 1
for o in sc.objects: o.select_set(False)
for o in vis: o.select_set(True)
rigs = [o for o in sc.objects if o.type == "ARMATURE" and o.name.startswith("RIG")]
for r in rigs: r.select_set(True)
t = time.time()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=apply_mods,
                          export_def_bones=True, export_morph=True, export_morph_normal=False, export_skins=True,
                          export_animations=False, export_yup=True)
rep = {"source": src, "out": out, "apply_modifiers": apply_mods, "export_s": round(time.time() - t, 1),
       "size_mb": round(os.path.getsize(out) / 1e6, 1), "meshes_exported": len(vis),
       "polys_base_cage": sum(len(o.data.polygons) for o in vis),
       "shape_keys": {o.name: len(o.data.shape_keys.key_blocks) for o in vis if o.data.shape_keys},
       "modifiers_not_in_gltf": dropped if not apply_mods else {},
       "particle_hair_not_exported": [p.name for p in bpy.data.particles],
       "deform_bones": sum(b.use_deform for r in rigs for b in r.data.bones)}
json.dump(rep, open(out + ".json", "w"), indent=1)
print(json.dumps({k: rep[k] for k in ("size_mb", "meshes_exported", "polys_base_cage", "deform_bones", "modifiers_not_in_gltf")}))
