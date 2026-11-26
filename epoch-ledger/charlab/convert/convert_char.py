"""Character conversion prototype: a professionally made Blender character (CloudRig, Blender Studio "Snow family") →
runtime GLB for the character lab (three.js / HyperFrames). Experimental; production untouched.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/convert_char.py PROFILE.json OUT_DIR [--tex 2048] [--subsurf 1]

What it does (each step keeps the *visible result*, not Blender's internal machinery):
1. Geometry: every render-visible mesh is evaluated at rest with its whole modifier stack (mirror, masks, lattices,
   corrective smooth, surface deform, subdivision at --subsurf) and baked to a plain mesh. Weights survive evaluation.
2. Skeleton: a clean deform skeleton with the lab's bone names (pelvis, spine_01…, upperarm_l…, eye_l…) is built from
   the character's deform bones: two-segment limbs are merged, face bones are folded into `head`, eye bones are kept.
   Vertex weights are merged by the same map, normalised and limited to 4 influences.
3. Face: the character's own pose library (and a few face controls) is posed, the fully deformed face (bones, drivers,
   shape keys, lattices) is evaluated, and the difference from rest is stored as a morph target named after the lab's
   expression units (mouth-open, eye-left-closure, eyebrows-left-inner-up, …), split left/right where needed. So the
   existing blink, expression and lip-sync code drives it unchanged.
4. Materials: each object's shaders are baked to a colour texture (Cycles, diffuse colour), then replaced with simple
   PBR materials (corneas: clear glossy; highlights: emissive).
5. Export: GLB with skin and morph targets, plus report.json (sizes, counts, timings, what was dropped).
"""
import json
import math
import os
import sys
import time


import bpy
import numpy as np
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
prof = json.load(open(argv[0])); OUT = argv[1]; os.makedirs(OUT, exist_ok=True)
opt = lambda k, d: type(d)(argv[argv.index(k) + 1]) if k in argv else d
TEX, SUBS = opt("--tex", 2048), opt("--subsurf", 1)
T0 = time.time(); REP = {"profile": argv[0], "timings": {}}
def tick(k, t): REP["timings"][k] = round(time.time() - t, 1)

bpy.ops.wm.open_mainfile(filepath=prof["blend"], load_ui=False)
sc = bpy.context.scene
rig = bpy.data.objects[prof["rig"]]
# render visibility (not viewport visibility: e.g. Snow's eyeballs are hidden in the viewport but render)
_vl = bpy.context.view_layer
def _excluded(o):
    def walk(lc):
        if o.name in lc.collection.objects and (lc.exclude or lc.collection.hide_render): return True
        return any(walk(c) for c in lc.children)
    return walk(_vl.layer_collection) if any(c.hide_render for c in o.users_collection) is False else True
VIS = [o for o in sc.objects if o.type == "MESH" and not o.hide_render and o.name in _vl.objects and not _excluded(o)
       and o.name not in prof.get("skip_meshes", [])]
REP["source_meshes"] = [o.name for o in VIS]

# ── rest pose: clear any animation, controls at identity ─────────────────────────────────────────────────────────────
def rest():
    if rig.animation_data:
        for tr in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(tr)
        rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)
    sc.frame_set(1); bpy.context.view_layer.update()
rest()
DRV = 0
for o in VIS:   # quality drivers (e.g. a rig 'Quality' property) would override modifier settings
    if o.animation_data:
        for fc in list(o.animation_data.drivers):
            if fc.data_path.startswith("modifiers["):
                mn = fc.data_path.split('"')[1]
                if o.modifiers.get(mn) and o.modifiers[mn].type == "SUBSURF": o.animation_data.drivers.remove(fc); DRV += 1
REP["modifier_drivers_removed"] = DRV
for o in VIS:
    for m in o.modifiers:
        if m.type == "SUBSURF": m.show_viewport = True; m.levels = SUBS
        elif m.type in ("MASK", "MIRROR", "LATTICE", "CORRECTIVE_SMOOTH", "SURFACE_DEFORM", "ARMATURE", "SHRINKWRAP", "DISPLACE"): m.show_viewport = True

def evaluate(o):
    dg = bpy.context.evaluated_depsgraph_get()
    return bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)

def coords(me):
    a = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", a); return a.reshape(-1, 3)

# ── 1. geometry at rest ─────────────────────────────────────────────────────────────────────────────────────────────
t = time.time()
BASE = {}
for o in VIS:
    me = evaluate(o); me.name = "CV-" + o.name
    # object-level material slots become mesh materials
    me.materials.clear()
    for s in o.material_slots: me.materials.append(s.material)
    BASE[o.name] = (me, o.matrix_world.copy())
tick("bake_geometry", t)
REP["polys"] = {k: len(v[0].polygons) for k, v in BASE.items()}; REP["polys_total"] = sum(REP["polys"].values())

# ── 3. face poses → morph deltas (evaluated before the scene is rebuilt) ─────────────────────────────────────────────
def pose_actions(names, frame=1):
    rest(); rig.animation_data_create()
    for an in names:
        act = bpy.data.actions.get(an)
        if not act: print("missing action", an); continue
        tr = rig.animation_data.nla_tracks.new(); st = tr.strips.new(an, frame, act)
        try:
            if act.slots: st.action_slot = act.slots[0]
        except Exception: pass
    sc.frame_set(frame); bpy.context.view_layer.update()

def pose_bones(spec):
    rest()
    for bn, ax, val in spec:      # ax "X"/"Y"/"Z": rotation in degrees; "locX"/"locY"/"locZ": translation in metres
        pb = rig.pose.bones[bn]
        if ax.startswith("loc"):
            l = list(pb.location); l["XYZ".index(ax[3])] += val; pb.location = l
        else:
            pb.rotation_mode = "XYZ"; e = list(pb.rotation_euler); e["XYZ".index(ax)] += math.radians(val); pb.rotation_euler = e
    bpy.context.view_layer.update()

FACE = [n for n in prof["face_meshes"] if n in BASE]
t = time.time()
MORPH = {}            # morph name → {mesh: delta}
for m in prof["morphs"]:
    if "actions" in m: pose_actions(m["actions"])
    else: pose_bones(m["bones"])
    for on in FACE:
        d = coords(evaluate(bpy.data.objects[on])) - coords(BASE[on][0])
        if np.abs(d).max() < 1e-6: continue
        d *= m.get("gain", 1.0)
        for name, side in ((m["name"].replace("{s}", "left"), 1), (m["name"].replace("{s}", "right"), -1)) if "{s}" in m["name"] else ((m["name"], 0),):
            dd = d.copy()
            if side:   # character's left is +X in Blender object space; smooth split over the midline
                x = coords(BASE[on][0])[:, 0]; w = np.clip(.5 + side * x / .012, 0, 1); dd *= w[:, None]
            MORPH.setdefault(name, {})[on] = dd
rest()
tick("bake_face_morphs", t)
REP["morphs"] = {k: sorted(v) for k, v in MORPH.items()}

# ── 2. clean skeleton with the lab's names ──────────────────────────────────────────────────────────────────────────
t = time.time()
BM = prof["bones"]                       # target → [source deform bones]; first source gives head/roll, last gives tail
PARENT = prof["parents"]                  # target → parent target
src_w = {b.name: (rig.matrix_world @ b.head_local, rig.matrix_world @ b.tail_local, b) for b in rig.data.bones}
arm_d = bpy.data.armatures.new("CV-skeleton"); arm = bpy.data.objects.new("rig", arm_d); sc.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
for o in sc.objects: o.select_set(False)
arm.select_set(True); bpy.ops.object.mode_set(mode="EDIT")
for tname, srcs in BM.items():
    h, _, b0 = src_w[srcs[0]]; _, tl, _ = src_w[srcs[-1]]
    eb = arm_d.edit_bones.new(tname); eb.head = h; eb.tail = tl if (tl - h).length > 1e-4 else h + Vector((0, 0, .05))
    z = (rig.matrix_world.to_3x3() @ b0.matrix_local.to_3x3()) @ Vector((0, 0, 1)); eb.align_roll(z)
for tname, p in PARENT.items():
    if p: arm_d.edit_bones[tname].parent = arm_d.edit_bones[p]
if prof.get("root_bone"):   # the lab runtime expects a root above the pelvis (MakeHuman game skeleton convention)
    rb = arm_d.edit_bones.new(prof["root_bone"]); rb.head = Vector((0, 0, 0)); rb.tail = Vector((0, 0, .1))
    arm_d.edit_bones["pelvis"].parent = rb
bpy.ops.object.mode_set(mode="OBJECT")
tick("skeleton", t)
# every source deform bone → a target (explicit map first, then face rules, then nearest mapped ancestor by position)
src2t = {s: tn for tn, ss in BM.items() for s in ss}
fold_head = prof.get("fold_into_head_patterns", [])
def target_of(g):
    if g in src2t: return src2t[g]
    if any(p in g for p in fold_head): return "head"
    if g in src_w:   # nearest target bone head
        p = src_w[g][0]; return min(BM, key=lambda tn: (src_w[BM[tn][0]][0] - p).length)
    return None
UNMAPPED = {}

# ── rebuild objects: baked mesh + merged weights + morphs, parented to the clean skeleton ────────────────────────────
t = time.time()
NEW = []
for on, (me, mw) in BASE.items():
    ob = bpy.data.objects.new(on.replace("GEO-", ""), me); sc.collection.objects.link(ob); ob.matrix_world = mw
    src_groups = {g.index: g.name for g in bpy.data.objects[on].vertex_groups}
    # merged weights
    acc = [dict() for _ in me.vertices]
    for v in me.vertices:
        for g in v.groups:
            gn = src_groups.get(g.group)
            if gn is None or g.weight <= 0: continue
            if gn in rig.data.bones and not rig.data.bones[gn].use_deform: continue
            tn = target_of(gn)
            if tn is None: UNMAPPED[gn] = UNMAPPED.get(gn, 0) + 1; continue   # helper / mask groups, not bones
            acc[v.index][tn] = acc[v.index].get(tn, 0) + g.weight
    for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
    groups = {tn: ob.vertex_groups.new(name=tn) for tn in BM}
    orphan = 0
    for i, a in enumerate(acc):
        if not a: a = {"head" if on in FACE else "pelvis": 1.0}; orphan += 1
        top = sorted(a.items(), key=lambda kv: -kv[1])[:4]; s = sum(w for _, w in top) or 1
        for tn, w in top: groups[tn].add([i], w / s, "REPLACE")
    if orphan: REP.setdefault("orphan_vertices", {})[on] = orphan
    # morph targets
    if any(on in v for v in MORPH.values()):
        ob.shape_key_add(name="Basis", from_mix=False)
        base = coords(me)
        for mn, per in MORPH.items():
            if on not in per: continue
            k = ob.shape_key_add(name=mn, from_mix=False); k.data.foreach_set("co", (base + per[on]).ravel()); k.value = 0.0
    ob.parent = arm; ob.matrix_parent_inverse = arm.matrix_world.inverted()
    mod = ob.modifiers.new("Armature", "ARMATURE"); mod.object = arm
    NEW.append(ob)
REP["non_bone_groups_ignored"] = len(UNMAPPED)
tick("rebuild_objects", t)

# ── 4. bake materials to colour textures ────────────────────────────────────────────────────────────────────────────
t = time.time()
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 1; sc.cycles.bake_type = "DIFFUSE"
sc.render.bake.use_pass_direct = False; sc.render.bake.use_pass_indirect = False; sc.render.bake.use_pass_color = True
sc.render.bake.margin = 8
SPECIAL = prof.get("special_materials", {})
for im in bpy.data.images:          # tiled (UDIM) textures must be loaded before baking, or the bake sees empty tiles
    if im.source in ("TILED", "FILE") and im.filepath:
        im.filepath = bpy.path.abspath(im.filepath)
        try: im.reload()
        except Exception: pass
        try: _ = im.pixels[0] if im.source == "FILE" else None
        except Exception: pass
REP["tiled_images"] = [im.name for im in bpy.data.images if im.source == "TILED"]
texdir = os.path.join(OUT, "tex"); os.makedirs(texdir, exist_ok=True)

def albedo_as_emission(nt):
    """route every output's surface through an Emission shader fed by its Principled BSDF's Base Color input, so an EMIT
    bake yields the true albedo (a DIFFUSE bake returns black for metallic areas, e.g. irises, and alters SSS skin)"""
    for out in [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"]:
        surf = out.inputs["Surface"]
        if not surf.is_linked: continue
        sh = surf.links[0].from_node
        bsdf = sh if sh.type == "BSDF_PRINCIPLED" else next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
        if bsdf is not None:
            bc = bsdf.inputs["Base Color"]
            if bc.is_linked: nt.links.new(bc.links[0].from_socket, em.inputs["Color"])
            else: em.inputs["Color"].default_value = bc.default_value
        nt.links.new(em.outputs["Emission"], surf)
for ob in NEW:
    me = ob.data
    if not me.uv_layers: REP.setdefault("no_uv", []).append(ob.name); continue
    ar = next((i for i, u in enumerate(me.uv_layers) if u.active_render), 0)
    src_uv = me.uv_layers[ar]; src_name = src_uv.name
    uv = np.empty(len(src_uv.data) * 2, np.float32); src_uv.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    # UDIM: tiles beyond 0–1 are laid side by side in one bake layout (full resolution per tile)
    u0, v0 = math.floor(uv[:, 0].min() + 1e-4), math.floor(uv[:, 1].min() + 1e-4)
    ntu, ntv = max(1, math.ceil(uv[:, 0].max() - 1e-4) - u0), max(1, math.ceil(uv[:, 1].max() - 1e-4) - v0)
    bake_uv = me.uv_layers.new(name="BAKE"); bake_uv.data.foreach_set("uv", np.stack([(uv[:, 0] - u0) / ntu, (uv[:, 1] - v0) / ntv], 1).ravel())
    me.uv_layers[src_name].active_render = True; me.uv_layers.active = bake_uv      # materials read the source UVs; the bake writes BAKE
    mats = [m for m in me.materials if m]
    if not mats or all(m.name in SPECIAL for m in mats): continue
    size = TEX if len(me.polygons) > 3000 else TEX // 2
    img = bpy.data.images.new(f"{ob.name}_albedo", min(4096, size * ntu), min(4096, size * ntv), alpha=False)
    REP.setdefault("uv_tiles", {})[ob.name] = [ntu, ntv]
    copies = []
    for i, m in enumerate(list(me.materials)):
        if not m or m.name in SPECIAL: copies.append(m); continue
        c = m.copy(); me.materials[i] = c; copies.append(c)
        albedo_as_emission(c.node_tree)
        n = c.node_tree.nodes.new("ShaderNodeTexImage"); n.image = img; c.node_tree.nodes.active = n
    for o in sc.objects: o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    try:
        bpy.ops.object.bake(type="EMIT", margin=8, use_clear=True)
    except Exception as e:
        REP.setdefault("bake_errors", {})[ob.name] = str(e); continue
    mag = prof.get("iris_magnify", {}).get(ob.name.replace("snow-", "GEO-snow-")) or prof.get("iris_magnify", {}).get("GEO-" + ob.name)
    if mag:   # cornea refraction magnifies the iris; approximate it by a radial warp around the darkest disc (the pupil)
        W_, H_ = img.size; px = np.array(img.pixels[:], np.float32).reshape(H_, W_, 4)
        lum = px[..., :3].mean(2); inside = lum > .01; dark = inside & (lum < np.percentile(lum[inside], 3))
        yy, xx = np.nonzero(dark); cy, cx = yy.mean(), xx.mean(); rp = math.sqrt(dark.sum() / math.pi)
        R = rp * mag["radius_in_pupils"]; Y, X = np.mgrid[0:H_, 0:W_].astype(np.float32); dy, dx = Y - cy, X - cx; r = np.sqrt(dx * dx + dy * dy) + 1e-6
        k = np.where(r < R, 1 / mag["scale"] + (1 - 1 / mag["scale"]) * (r / R) ** 2, 1.0)   # smooth back to identity at R
        sx = np.clip(cx + dx * k, 0, W_ - 1).astype(np.int32); sy = np.clip(cy + dy * k, 0, H_ - 1).astype(np.int32)
        img.pixels[:] = px[sy, sx].ravel(); REP.setdefault("iris_magnified", {})[ob.name] = {"centre": [round(float(cx)), round(float(cy))], "pupil_px": round(rp, 1)}
    img.filepath_raw = os.path.join(texdir, f"{ob.name}_albedo.png"); img.file_format = "PNG"; img.save()
    ob["albedo"] = img.name
tick("bake_materials", t)

# keep only the bake layout as the runtime UV map
for ob in NEW:
    me = ob.data
    if "BAKE" not in me.uv_layers: continue
    for u in [u.name for u in me.uv_layers if u.name != "BAKE"]: me.uv_layers.remove(me.uv_layers[u])
    me.uv_layers["BAKE"].name = "UVMap"; me.uv_layers["UVMap"].active_render = True

# runtime materials: one PBR material per object (baked albedo), special cases by source material
def pbr(name, img=None, color=(1, 1, 1, 1), rough=.6, alpha=1.0, emit=None, spec=.4):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    try: p.inputs["Specular IOR Level"].default_value = spec
    except Exception: pass
    if img:
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img; nt.links.new(tx.outputs["Color"], p.inputs["Base Color"])
    else: p.inputs["Base Color"].default_value = color
    if alpha < 1: p.inputs["Alpha"].default_value = alpha; m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    if emit: p.inputs["Emission Color"].default_value = emit; p.inputs["Emission Strength"].default_value = 1.0
    return m
ROUGH = prof.get("roughness", {})
for ob in NEW:
    me = ob.data; src = [m.name.split(".0")[0] if m else "" for m in me.materials]
    special = next((SPECIAL[s] for s in src if s in SPECIAL), None)
    if special:
        k = special["kind"]
        m = pbr(f"{ob.name}_{k}", color=tuple(special.get("color", (1, 1, 1, 1))), rough=special.get("rough", .05),
                alpha=special.get("alpha", 1.0), emit=tuple(special["emit"]) if "emit" in special else None)
    else:
        img = bpy.data.images.get(ob.get("albedo", ""))
        r = next((ROUGH[k] for k in ROUGH if any(k in s for s in src)), .6)
        sp = next((prof.get("specular", {})[k] for k in prof.get("specular", {}) if any(k in s for s in src)), .4)
        m = pbr(f"{ob.name}_mat", img=img, rough=r, spec=sp)
    me.materials.clear(); me.materials.append(m)
    idx = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_set("material_index", idx)   # every face → the baked material

# ── 5. export ────────────────────────────────────────────────────────────────────────────────────────────────────────
t = time.time()
for o in sc.objects: o.select_set(False)
for o in NEW: o.select_set(True)
arm.select_set(True)
glb = os.path.join(OUT, prof["id"] + ".glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_apply=False, export_skins=True,
                          export_morph=True, export_morph_normal=True, export_animations=False, export_yup=True,
                          export_all_influences=False, export_image_format="JPEG", export_jpeg_quality=90)
tick("export", t)
REP["glb_mb"] = round(os.path.getsize(glb) / 1e6, 2); REP["bones"] = list(BM); REP["total_s"] = round(time.time() - T0, 1)
REP["licence"] = prof.get("licence"); REP["credit"] = prof.get("credit")
json.dump(REP, open(os.path.join(OUT, "report.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, prof["id"] + "_converted.blend"))
print("CONVERTED", json.dumps({k: REP[k] for k in ("glb_mb", "polys_total", "total_s")}), "morphs", len(MORPH), "non-bone groups ignored", len(UNMAPPED))
