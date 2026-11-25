"""Character lab (M2.1): build a rigged, expressive GLB character headlessly from a JSON spec, on the CPU.

Runs inside the isolated Blender-as-a-module environment (never the production Python):

    BLENDER_USER_RESOURCES=.runtime/charlab/user .runtime/charlab/venv/bin/python \
        epoch-ledger/charlab/build_character.py epoch-ledger/charlab/specs/test_adult.json OUT_DIR \
        [--bvh walk=.runtime/charlab/mocap/02_01.bvh] [--bvh sit=.runtime/charlab/mocap/13_01.bvh:0:12]

Steps (each timed and reported in OUT_DIR/<id>.report.json):
  1. MPFB human from macro sliders (+ optional named shape targets).
  2. Identity targets baked into the mesh, so a character's identity cannot drift between shots.
  3. A built-in MPFB rig (default: "game_engine": 53 bones, five three-bone fingers per hand, Unreal-mannequin names),
     fitted to MPFB's joint helpers.
  4. Expression units loaded as shape keys (blink, brows, mouth; at 0, animated per shot); helper geometry removed
     with the shape keys preserved.
  5. Optional BVH clips retargeted onto the rig (rest poses matched by bone direction, rotations transferred as
     deltas from the matched rest pose, root motion scaled by leg length) and baked to actions.
  6. A finger "grip" action (curl of all finger joints) to test finger articulation downstream.
  7. GLB export with skins, shape keys and every action.

This is lab code for compatibility testing. It does not touch the production kit or any approved asset.
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

T0 = time.time()
LOG: dict = {"steps": {}}


def step(name):
    def deco(fn):
        def run(*a, **k):
            t = time.time()
            r = fn(*a, **k)
            LOG["steps"][name] = round(time.time() - t, 2)
            return r
        return run
    return deco


# CMU (cgspeed MotionBuilder BVH) → MPFB "game_engine" rig (Unreal-mannequin names)
CMU_TO_GAME_ENGINE = {
    "Hips": "pelvis", "LowerBack": "spine_01", "Spine": "spine_02", "Spine1": "spine_03", "Neck": "neck_01", "Head": "head",
    "LeftShoulder": "clavicle_l", "LeftArm": "upperarm_l", "LeftForeArm": "lowerarm_l", "LeftHand": "hand_l",
    "RightShoulder": "clavicle_r", "RightArm": "upperarm_r", "RightForeArm": "lowerarm_r", "RightHand": "hand_r",
    "LeftUpLeg": "thigh_l", "LeftLeg": "calf_l", "LeftFoot": "foot_l", "LeftToeBase": "ball_l",
    "RightUpLeg": "thigh_r", "RightLeg": "calf_r", "RightFoot": "foot_r", "RightToeBase": "ball_r",
}
EXPRESSION_UNITS = ["eye-left-closure", "eye-right-closure", "eyebrows-left-inner-up", "eyebrows-right-inner-up",
                    "eyebrows-left-down", "eyebrows-right-down", "mouth-corner-puller", "mouth-depression", "mouth-open",
                    "mouth-compression", "eye-left-opened-up", "eye-right-opened-up"]


def mpfb():
    bpy.ops.preferences.addon_enable(module="bl_ext.user_default.mpfb")
    from bl_ext.user_default.mpfb.services.humanservice import HumanService
    from bl_ext.user_default.mpfb.services.targetservice import TargetService
    from bl_ext.user_default.mpfb.services.rigservice import RigService
    return HumanService, TargetService, RigService


@step("human")
def make_human(spec, HumanService, TargetService):
    macro = TargetService.get_default_macro_info_dict()
    for k, v in spec.get("macro", {}).items():
        if k == "race":
            macro["race"].update(v)
        else:
            macro[k] = v
    body = HumanService.create_human(macro_detail_dict=macro, feet_on_ground=True)
    for name, w in spec.get("targets", {}).items():
        path = TargetService.target_full_path(name)
        if not path:
            raise SystemExit(f"target not found: {name}")
        TargetService.load_target(body, path, weight=w, name=name)
    return body


@step("bake_identity")
def bake_identity(body, TargetService):
    TargetService.bake_targets(body)          # macro + identity targets become the base shape
    n = len(body.data.shape_keys.key_blocks) if body.data.shape_keys else 0
    LOG["shape_keys_after_bake"] = n


@step("remove_helpers")
def remove_helpers(body):
    import bmesh
    for m in list(body.modifiers):
        if m.type == "MASK":
            body.modifiers.remove(m)
    gi = body.vertex_groups["body"].index
    bm = bmesh.new()
    bm.from_mesh(body.data)
    deform = bm.verts.layers.deform.active
    kill = [v for v in bm.verts if gi not in v[deform]]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bm.to_mesh(body.data)
    bm.free()
    LOG["vertices"] = len(body.data.vertices)
    LOG["helper_vertices_removed"] = len(kill)


@step("expressions")
def add_expressions(body, TargetService):
    added = []
    for unit in EXPRESSION_UNITS:
        path = TargetService.target_full_path(unit)
        if path:
            TargetService.load_target(body, path, weight=0.0, name=unit)
            added.append(unit)
    LOG["expression_shape_keys"] = added


@step("rig")
def add_rig(body, rig_name, HumanService):
    rig = HumanService.add_builtin_rig(body, rig_name)
    bones = [b.name for b in rig.data.bones]
    LOG["rig"] = rig_name
    LOG["bones"] = len(bones)
    LOG["finger_bones"] = len([b for b in bones if any(f in b.lower() for f in ("thumb", "index", "middle", "ring", "pinky", "finger"))])
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return rig


def _world(obj, pb):
    return obj.matrix_world @ pb.matrix


def _order(rig, names):
    """Mapped target bones, parents before children."""
    depth = {b.name: len(b.parent_recursive) for b in rig.data.bones}
    return sorted(names, key=lambda n: depth[n])


def _set_world_rot(rig, pb, rot_q, head_world=None):
    mw = rig.matrix_world
    cur = _world(rig, pb)
    head = head_world if head_world is not None else cur.to_translation()
    sc = cur.to_scale()
    m = Matrix.Translation(head) @ rot_q.to_matrix().to_4x4() @ Matrix.Diagonal((*sc, 1.0))
    pb.matrix = mw.inverted() @ m
    bpy.context.view_layer.update()


@step("retarget")
def retarget(rig, clips, mapping=CMU_TO_GAME_ENGINE, fps=30):
    scene = bpy.context.scene
    scene.render.fps = fps
    report = {}
    for name, src_spec in clips.items():
        path, a, b = (src_spec.split(":") + ["", ""])[:3]
        before = set(bpy.data.objects)
        bpy.ops.import_anim.bvh(filepath=path, axis_forward="-Z", axis_up="Y", rotate_mode="NATIVE", use_fps_scale=True,
                                update_scene_fps=False, update_scene_duration=False, global_scale=1.0)
        src = next(o for o in bpy.data.objects if o not in before and o.type == "ARMATURE")
        src_act = src.animation_data.action
        f0, f1 = (int(x) for x in src_act.frame_range)
        f0 += 1                                   # cgspeed CMU conversions begin with a setup pose frame
        if a:
            f0 = max(f0, int(float(a) * fps) + 1)
        if b:
            f1 = min(f1, int(float(b) * fps) + 1)
        pairs = [(s, t) for s, t in mapping.items() if s in src.pose.bones and t in rig.pose.bones]
        tgt_names = _order(rig, [t for _, t in pairs])
        s_of = {t: s for s, t in pairs}

        # scale: leg length ratio (hip to ankle), measured in the rest poses
        def leg(arm, up, ank):
            return (arm.matrix_world @ arm.data.bones[ank].head_local - arm.matrix_world @ arm.data.bones[up].head_local).length
        k = leg(rig, "thigh_l", "foot_l") / leg(src, "LeftUpLeg", "LeftFoot")
        src.scale = (k, k, k)
        bpy.context.view_layer.update()

        # 1. match rest poses by bone direction (works for T-pose, A-pose, splayed legs)
        src.data.pose_position = "REST"
        for pb in rig.pose.bones:
            pb.matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()
        offset = {}
        for t in tgt_names:
            spb, tpb = src.pose.bones[s_of[t]], rig.pose.bones[t]
            sw = _world(src, spb)
            if t != "pelvis" and spb.length > 1e-4:
                sdir = (src.matrix_world @ spb.tail - src.matrix_world @ spb.head).normalized()
                tw = _world(rig, tpb)
                tdir = (tw.to_3x3() @ Vector((0, 1, 0))).normalized()
                _set_world_rot(rig, tpb, tdir.rotation_difference(sdir) @ tw.to_quaternion())
            offset[t] = sw.to_quaternion().inverted() @ _world(rig, tpb).to_quaternion()
        aligned = {t: rig.pose.bones[t].matrix_basis.copy() for t in tgt_names}
        pelvis_rest = _world(rig, rig.pose.bones["pelvis"]).to_translation().copy()
        src.data.pose_position = "POSE"
        scene.frame_set(f0)
        bpy.context.view_layer.update()
        hips_start = (src.matrix_world @ src.pose.bones["Hips"].head).copy()   # root motion is relative to the first frame

        # 2. transfer, frame by frame, parents first; root motion from the hips
        act = bpy.data.actions.new(name)
        rig.animation_data_create()
        rig.animation_data.action = act
        n = 0
        for f in range(f0, f1 + 1):
            scene.frame_set(f)
            for t in tgt_names:
                rig.pose.bones[t].matrix_basis = aligned[t]
            bpy.context.view_layer.update()
            for t in tgt_names:
                spb, tpb = src.pose.bones[s_of[t]], rig.pose.bones[t]
                q = _world(src, spb).to_quaternion() @ offset[t]
                head = None
                if t == "pelvis":
                    head = pelvis_rest + ((src.matrix_world @ spb.head) - hips_start)
                _set_world_rot(rig, tpb, q, head)
            fr = f - f0 + 1
            for t in tgt_names:
                pb = rig.pose.bones[t]
                pb.keyframe_insert("rotation_quaternion", frame=fr)
                if t == "pelvis":
                    pb.keyframe_insert("location", frame=fr)
            n += 1
        # Blender 5 layered actions: make sure the action is assigned to a slot and kept for export
        act.use_fake_user = True
        report[name] = {"source": os.path.basename(path), "frames": n, "seconds": round(n / fps, 2), "bones": len(tgt_names),
                        "scale": round(k, 4)}
        rig.animation_data.action = None
        bpy.data.actions.remove(src_act)          # the imported source clip must not be exported
        bpy.data.objects.remove(src, do_unlink=True)
        scene.frame_set(1)
    LOG["clips"] = report


@step("grip_action")
def grip_action(rig, fps=30):
    """A test action: all finger joints of both hands curl from open (frame 1) to a grip (frame 16)."""
    fingers = [pb for pb in rig.pose.bones if any(f in pb.name for f in ("index", "middle", "ring", "pinky", "thumb"))]
    act = bpy.data.actions.new("grip")
    rig.animation_data_create()
    rig.animation_data.action = act
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    for fr, amt in ((1, 0.0), (16, 1.0)):
        for pb in fingers:
            ang = math.radians((55 if "thumb" not in pb.name else 30) * amt)
            pb.rotation_quaternion = Matrix.Rotation(ang, 4, "X").to_quaternion() if "thumb" not in pb.name else Matrix.Rotation(ang, 4, "Z").to_quaternion()
            pb.keyframe_insert("rotation_quaternion", frame=fr)
    act.use_fake_user = True
    rig.animation_data.action = None
    LOG["grip_bones"] = len(fingers)


@step("material")
def material(body, spec):
    m = bpy.data.materials.new("skin")
    if m.node_tree is None:          # Blender 4.x needs use_nodes; 5.x creates the tree and deprecates the flag
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*[c / 255 for c in spec.get("skin_rgb", [196, 140, 105])], 1)
        bsdf.inputs["Roughness"].default_value = 0.7
    body.data.materials.clear()
    body.data.materials.append(m)


@step("export")
def export(out: Path, ident: str):
    path = out / f"{ident}.glb"
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", export_skins=True, export_morph=True,
                              export_morph_normal=False, export_animations=True, export_animation_mode="ACTIONS",
                              export_apply=False, export_yup=True, export_force_sampling=True, export_frame_range=False)
    LOG["glb"] = str(path)
    LOG["glb_bytes"] = path.stat().st_size


def main(argv):
    spec_path, out = Path(argv[0]), Path(argv[1])
    clips = {}
    i = 2
    while i < len(argv):
        if argv[i] == "--bvh":
            name, src = argv[i + 1].split("=", 1)
            clips[name] = src
            i += 2
        else:
            raise SystemExit(f"unknown argument {argv[i]}")
    out.mkdir(parents=True, exist_ok=True)
    spec = json.loads(spec_path.read_text())
    LOG.update(spec=spec["id"], blender=bpy.app.version_string)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    HumanService, TargetService, RigService = mpfb()
    import bl_ext.user_default.mpfb as M
    LOG["mpfb"] = ".".join(map(str, M.VERSION))
    body = make_human(spec, HumanService, TargetService)
    bake_identity(body, TargetService)
    rig = add_rig(body, spec.get("rig", "game_engine"), HumanService)   # fitted to the helper joints, so before removal
    add_expressions(body, TargetService)
    remove_helpers(body)
    material(body, spec)
    if clips:
        retarget(rig, clips)
    grip_action(rig)
    export(out, spec["id"])
    LOG["total_seconds"] = round(time.time() - T0, 2)
    (out / f"{spec['id']}.report.json").write_text(json.dumps(LOG, indent=2))
    print(json.dumps(LOG, indent=2))


if __name__ == "__main__":
    code = 0
    try:
        main(sys.argv[1:])
    except BaseException:                 # noqa: BLE001 — report, then exit without the interpreter shutdown below
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)       # bpy 4.5 (as a Python module) can hang during interpreter shutdown
