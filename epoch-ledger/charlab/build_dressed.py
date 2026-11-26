"""Character lab (M2.3, M2.3b, M2.3c): a fully dressed character from a preset (MPFB + MakeHuman system assets) → GLB.

    BLENDER_USER_RESOURCES=.runtime/charlab/user .runtime/charlab/venv/bin/python \
        epoch-ledger/charlab/build_dressed.py epoch-ledger/charlab/specs/amara.json OUT_DIR [--bvh idle=FILE:START:END]

The spec holds an MPFB human preset ("preset": eyes, eyebrows, eyelashes, hair, teeth, tongue, clothes, skin) plus
the lab's own fields (rig, expression units, finger poses). Steps:
  1. MPFB builds the human from the preset (phenotype, body parts, clothes, skin) with the game_engine rig; every
     proxy (clothes, hair, brows, lashes, eyes, teeth) is fitted and skinned to the same skeleton.
  2. Expression units are loaded as shape keys on the body and transferred to the brows, lashes and teeth through
     the MHCLO vertex correspondence (MPFB only transfers visemes and face units), so a blink also closes the lashes
     and raised brows carry the eyebrow hair.
  3. Masks are made real: body vertices hidden by helpers or under clothes ("Delete.*" groups) are deleted with
     the shape keys preserved, so nothing hidden in Blender can show through in three.js.
  4. Optional mocap clip (e.g. a relaxed idle stance) and a relaxed / grip finger action; GLB export.
  5. A report: objects, vertices, materials and textures, eye-alignment offsets, and timings.
Lab code: no production asset is touched.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_character as BC  # noqa: E402  (retarget, step timer, report)

LOG = BC.LOG


def mpfb():
    bpy.ops.preferences.addon_enable(module="bl_ext.user_default.mpfb")
    from bl_ext.user_default.mpfb.services.humanservice import HumanService
    from bl_ext.user_default.mpfb.services.targetservice import TargetService
    from bl_ext.user_default.mpfb.services.locationservice import LocationService
    from bl_ext.user_default.mpfb.services.clothesservice import ClothesService
    from bl_ext.user_default.mpfb.entities.clothes.mhclo import Mhclo
    return HumanService, TargetService, LocationService, ClothesService, Mhclo


@BC.step("human_from_preset")
def build(spec, HumanService):
    info = dict(spec["preset"])
    info["rig"] = spec.get("rig", "game_engine")
    settings = HumanService.get_default_deserialization_settings()
    settings.update({"subdiv_levels": 0, "override_rig": "PRESET", "override_skin_model": "PRESET"})
    body = HumanService.deserialize_from_dict(info, settings)
    rig = body.parent
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return body, rig


def children(rig):
    return [o for o in bpy.data.objects if o.parent == rig and o.type == "MESH"]


@BC.step("expressions")
def expressions(body, rig, TargetService, ClothesService, Mhclo):
    """Expression units on the body, then the same offsets on brows / lashes / teeth via MHCLO correspondence."""
    units = []
    for unit in BC.EXPRESSION_UNITS:
        p = TargetService.target_full_path(unit)
        if p:
            TargetService.load_target(body, p, weight=0.0, name=unit)
            units.append(unit)
    keys = body.data.shape_keys.key_blocks
    basis = [v.co.copy() for v in body.data.vertices]
    moved = {}
    for child in children(rig):
        if child == body:
            continue
        path = ClothesService.find_clothes_absolute_path(child)
        if not path:
            continue
        m = Mhclo()
        m.load(path)
        made = 0
        for unit in units:
            src = keys[unit]
            offs = {}
            for ci, mp in m.verts.items():
                if ci >= len(child.data.vertices):
                    continue
                (v0, v1, v2), (w0, w1, w2) = mp["verts"], mp["weights"]
                o = (src.data[v0].co - basis[v0]) * w0 + (src.data[v1].co - basis[v1]) * w1 + (src.data[v2].co - basis[v2]) * w2
                if o.length > 1e-5:
                    offs[ci] = o
            if not offs:
                continue
            if not child.data.shape_keys:
                child.shape_key_add(name="Basis", from_mix=False)
            sk = child.shape_key_add(name=unit, from_mix=False)
            for ci, o in offs.items():
                sk.data[ci].co = child.data.vertices[ci].co + o
            made += 1
        if made:
            moved[child.name] = made
    LOG["expression_shape_keys"] = units
    LOG["expression_keys_on_proxies"] = moved


@BC.step("apply_masks")
def apply_masks(rig):
    """Delete what MASK modifiers hide (helpers, body under clothes), preserving shape keys."""
    import bmesh
    report = {}
    for obj in children(rig):
        masks = [m for m in obj.modifiers if m.type == "MASK" and m.vertex_group in obj.vertex_groups]
        if not masks:
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        dl = bm.verts.layers.deform.active
        kill = set()
        for m in masks:
            gi = obj.vertex_groups[m.vertex_group].index
            for v in bm.verts:
                inside = dl is not None and gi in v[dl] and v[dl][gi] > 0.0
                if (inside and m.invert_vertex_group) or (not inside and not m.invert_vertex_group):
                    kill.add(v)
        n0 = len(bm.verts)
        bmesh.ops.delete(bm, geom=list(kill), context="VERTS")
        bm.to_mesh(obj.data)
        bm.free()
        for m in masks:
            obj.modifiers.remove(m)
        report[obj.name] = {"removed": len(kill), "kept": n0 - len(kill)}
    for obj in children(rig):
        for m in list(obj.modifiers):
            if m.type == "SUBSURF":
                obj.modifiers.remove(m)
    LOG["masks_applied"] = report


@BC.step("eye_check")
def eye_check(body, rig):
    """Eye alignment, before helpers are removed: each eyeball's centre against MPFB's anatomical eye joint
    (centroid of the joint-l-eye / joint-r-eye helper vertices, the point the eye is meant to rotate about)."""
    eyes = next((o for o in children(rig) if any("eye" in i["name"] if False else False for i in [])), None)
    for o in children(rig):
        imgs = [n.image.name.lower() for s_ in o.material_slots if s_.material and s_.material.node_tree
                for n in s_.material.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]
        if any("eye" in i and "eyebrow" not in i and "lash" not in i for i in imgs):
            eyes = o
    if not eyes:
        LOG["eye_check"] = "no eyes object"
        return
    def group_centre(obj, name):
        gi = obj.vertex_groups[name].index
        pts = [obj.matrix_world @ v.co for v in obj.data.vertices if any(g.group == gi and g.weight > 0 for g in v.groups)]
        return sum(pts, Vector()) / len(pts)
    vs = [eyes.matrix_world @ v.co for v in eyes.data.vertices]
    out = {}
    for side, sel in (("l", lambda v: v.x > 0), ("r", lambda v: v.x <= 0)):
        pts = [v for v in vs if sel(v)]
        c = sum(pts, Vector()) / len(pts)
        j = group_centre(body, f"joint-{side}-eye")
        out[side] = {"offset_from_eye_joint_mm": round((c - j).length * 1000, 2),
                     "offset_xyz_mm": [round(x * 1000, 2) for x in (c - j)],
                     "eyeball_radius_mm": round(max((p - c).length for p in pts) * 1000, 1)}
    LOG["eye_check"] = out


@BC.step("finger_actions")
def finger_actions(rig):
    """'relaxed' (natural slight curl, thumb in) and 'grip' (curl around a held object), each a 1-frame-to-16 action."""
    def fingers(pb):
        return any(f in pb.name for f in ("index", "middle", "ring", "pinky", "thumb"))
    poses = {"relaxed": {"index": 7, "middle": 11, "ring": 15, "pinky": 19, "thumb": 0},
             "grip": {"index": 62, "middle": 68, "ring": 72, "pinky": 76, "thumb": 34}}
    for name, deg in poses.items():
        act = bpy.data.actions.new(name)
        rig.animation_data_create()
        rig.animation_data.action = act
        for pb in rig.pose.bones:
            pb.matrix_basis = Matrix.Identity(4)
        for fr, amt in ((1, 1.0), (2, 1.0)):
            for pb in rig.pose.bones:
                if not fingers(pb):
                    continue
                f = next(k for k in deg if k in pb.name)
                seg = {"01": 1.0, "02": .8, "03": .6}[pb.name.split("_")[1]]
                ax = "Z" if f == "thumb" else "X"
                pb.rotation_quaternion = Matrix.Rotation(math.radians(deg[f] * amt * seg), 4, ax).to_quaternion()
                pb.keyframe_insert("rotation_quaternion", frame=fr)
        act.use_fake_user = True
        rig.animation_data.action = None


@BC.step("stand_pose")
def stand_pose(rig, aims):
    """A relaxed standing pose as an action ('stand'): each listed bone is aimed along a world direction, parents
    first, with the smallest rotation from where it points now (so bone roll and twist are kept)."""
    act = bpy.data.actions.new("stand")
    rig.animation_data_create()
    rig.animation_data.action = act
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    names = BC._order(rig, [k for k in aims if not k.startswith("_") and k in rig.pose.bones])
    for n in names:
        pb = rig.pose.bones[n]
        w = BC._world(rig, pb)
        cur = (w.to_3x3() @ Vector((0, 1, 0))).normalized()
        BC._set_world_rot(rig, pb, cur.rotation_difference(Vector(aims[n]).normalized()) @ w.to_quaternion())
    for fr in (1, 2):
        for n in names:
            rig.pose.bones[n].keyframe_insert("rotation_quaternion", frame=fr)
    act.use_fake_user = True
    rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    LOG["stand_bones"] = names


@BC.step("face_normals")
def face_normals(body, rig, strength, iterations=40):
    """Clean illustrated face shading (M2.3b): blend the head's shading normals toward those of a heavily smoothed
    copy of the body, weighted by the head bone's skin weights. Bands then follow the broad form of the head instead
    of every crease (no patchy, mask-like shadows); the silhouette and geometry are unchanged."""
    tmp = body.copy()
    tmp.data = body.data.copy()
    bpy.context.scene.collection.objects.link(tmp)
    tmp.shape_key_clear() if tmp.data.shape_keys else None
    for m in list(tmp.modifiers):
        tmp.modifiers.remove(m)
    sm = tmp.modifiers.new("smooth", "SMOOTH")
    sm.factor, sm.iterations = 1.0, iterations
    dg = bpy.context.evaluated_depsgraph_get()
    ev = tmp.evaluated_get(dg)
    me = ev.to_mesh()
    smooth = [v.normal.copy() for v in me.vertices]
    ev.to_mesh_clear()
    bpy.data.objects.remove(tmp, do_unlink=True)
    gi = {g.name: g.index for g in body.vertex_groups}
    head, neck = gi.get("head"), gi.get("neck_01")
    out, n_face = [], 0
    for v in body.data.vertices:
        w = 0.0
        for g in v.groups:
            if g.group == head:
                w += g.weight
            elif g.group == neck:
                w += g.weight * .35
        w = min(1.0, w) * strength
        n = v.normal.lerp(smooth[v.index], w).normalized()
        out.append(n)
        n_face += w > .05
    body.data.normals_split_custom_set_from_vertices(out)
    LOG["face_normals"] = {"strength": strength, "vertices_adjusted": n_face, "smooth_iterations": iterations}


@BC.step("export_textures")
def export_textures(rig, out: Path, ident: str):
    """Every material's images saved as PNG, with a manifest (material → images), for build-time palette processing."""
    d = out / f"{ident}_tex"
    d.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for o in children(rig):
        for s_ in o.material_slots:
            m = s_.material
            if not m or not m.node_tree:
                continue
            for n in m.node_tree.nodes:
                if n.type == "TEX_IMAGE" and n.image:
                    name = Path(n.image.name).stem + ".png"
                    n.image.save_render(str(d / name)) if not n.image.filepath else n.image.save(filepath=str(d / name))
                    manifest.setdefault(o.name.replace(".", ""), []).append(name)
    (d / "manifest.json").write_text(json.dumps(manifest, indent=1))
    LOG["textures"] = str(d)


@BC.step("export_lod")
def export_lod(rig, out: Path, ident: str, ratio: float):
    """A wide-shot level of detail: shape keys dropped (faces are unreadable at that size) and every mesh decimated."""
    tris = {}
    for o in children(rig):
        if o.data.shape_keys:
            o.shape_key_clear()
        d = o.modifiers.new("lod", "DECIMATE")
        d.ratio = ratio
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=d.name)
        tris[o.name] = sum(len(p.vertices) - 2 for p in o.data.polygons)
    path = out / f"{ident}_lod.glb"
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", export_skins=True, export_morph=False,
                              export_animations=True, export_animation_mode="ACTIONS", export_apply=False, export_yup=True,
                              export_force_sampling=True, export_frame_range=False)
    LOG["lod"] = {"glb": str(path), "bytes": path.stat().st_size, "ratio": ratio, "triangles": tris}


@BC.step("inventory")
def inventory(rig):
    objs = {}
    for o in children(rig):
        mats = []
        for s in o.material_slots:
            m = s.material
            if not m:
                continue
            imgs = sorted({n.image.name for n in (m.node_tree.nodes if m.node_tree else []) if n.type == "TEX_IMAGE" and n.image})
            mats.append({"name": m.name, "images": imgs})
        objs[o.name] = {"vertices": len(o.data.vertices), "shape_keys": len(o.data.shape_keys.key_blocks) - 1 if o.data.shape_keys else 0,
                        "materials": mats}
    LOG["objects"] = objs


def main(argv):
    spec_path, out = Path(argv[0]), Path(argv[1])
    clips = {}
    i = 2
    while i < len(argv):
        if argv[i] == "--bvh":
            k, v = argv[i + 1].split("=", 1)
            clips[k] = v
            i += 2
        else:
            raise SystemExit(f"unknown argument {argv[i]}")
    out.mkdir(parents=True, exist_ok=True)
    spec = json.loads(spec_path.read_text())
    LOG.update(spec=spec["id"], blender=bpy.app.version_string)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    HumanService, TargetService, LocationService, ClothesService, Mhclo = mpfb()
    import bl_ext.user_default.mpfb as M
    LOG["mpfb"] = ".".join(map(str, M.VERSION))
    body, rig = build(spec, HumanService)
    LOG["rig"] = rig.name
    LOG["bones"] = len(rig.data.bones)
    if spec.get("design"):                    # M2.3c bespoke geometry (opt-in): face planes, then proxies refitted
        import stylise as ST
        t = time.time()
        ST.design_before_bake(body, rig, spec, children(rig), ClothesService, LOG)
        LOG.setdefault("timings", {})["design_face"] = round(time.time() - t, 2)
    TargetService.bake_targets(body)          # phenotype becomes the base shape: only expression keys are exported
    eye_check(body, rig)                      # needs the joint helpers, so before the masks are applied
    expressions(body, rig, TargetService, ClothesService, Mhclo)
    if spec.get("design"):                    # M2.3c: designed hair, brows, lash lines (need the helpers and the keys)
        t = time.time()
        ST.design_after_expressions(body, rig, spec, children(rig), LOG)
        LOG.setdefault("timings", {})["design_meshes"] = round(time.time() - t, 2)
    apply_masks(rig)
    if clips:
        BC.retarget(rig, clips)
    if spec.get("stand"):
        stand_pose(rig, spec["stand"])
    finger_actions(rig)
    if spec.get("face_normals"):
        face_normals(body, rig, float(spec["face_normals"]))
    inventory(rig)
    BC.export(out, spec["id"])
    LOG["triangles"] = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in children(rig)}
    export_textures(rig, out, spec["id"])
    if spec.get("lod_ratio"):
        export_lod(rig, out, spec["id"], float(spec["lod_ratio"]))
    LOG["total_seconds"] = round(time.time() - BC.T0, 2)
    (out / f"{spec['id']}.report.json").write_text(json.dumps(LOG, indent=2))
    print(json.dumps({k: LOG[k] for k in LOG if k != "objects"}, indent=2))


if __name__ == "__main__":
    code = 0
    try:
        main(sys.argv[1:])
    except BaseException:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
