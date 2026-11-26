"""Import a CharMorph base character headlessly (artistic-direction gate) and save it to a .blend for rendering.

    BLENDER_USER_RESOURCES=.runtime/charlab/cm_user .runtime/charlab/venv/bin/python \
        epoch-ledger/charlab/bstudio/charmorph_import.py BASE OUT.blend [--hair STYLE] [--morph name=value ...]
"""
import sys
import traceback

import bpy

argv = sys.argv[1:]
base, out = argv[0], argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module="charmorph")
from charmorph.lib import charlib  # noqa: E402
print("chars:", list(charlib.library.chars.keys()))
ui = bpy.context.window_manager.charmorph_ui
ui.base_model = base
for k in ("import_expressions", "import_morphs"):
    if hasattr(ui, k):
        try: setattr(ui, k, True)
        except Exception as e: print("ui", k, e)
r = bpy.ops.charmorph.import_char()
print("import:", r)
obj = next((o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("cm_", base))), None) or \
      max((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
bpy.context.view_layer.objects.active = obj
print("char obj:", obj.name, len(obj.data.vertices), "shape keys:", len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0)
preset = argv[argv.index("--preset") + 1] if "--preset" in argv else None
if preset:
    for o in bpy.context.selected_objects: o.select_set(False)
    obj.select_set(True)
    try: print("preset:", bpy.ops.charmorph.import_("EXEC_DEFAULT", filepath=preset) if hasattr(bpy.ops.charmorph, "import_") else getattr(bpy.ops.charmorph, "import")(filepath=preset))
    except Exception: traceback.print_exc()
hair = argv[argv.index("--hair") + 1] if "--hair" in argv else None
if hair:
    try:
        obj.select_set(True); bpy.context.view_layer.objects.active = obj
        ui.hair_style = hair
        print("hair:", bpy.ops.charmorph.hair_create())
    except Exception:
        traceback.print_exc()
try:
    print("hair styles available:", [i.identifier for i in ui.bl_rna.properties["hair_style"].enum_items])
except Exception as e:
    print("hair enum:", e)
bpy.ops.wm.save_as_mainfile(filepath=out)
print("saved", out)
