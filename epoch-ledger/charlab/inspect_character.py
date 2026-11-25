"""Character lab (M2.3): geometric inspection of an exported character GLB, in the isolated Blender Python.

    BLENDER_USER_RESOURCES=.runtime/charlab/user .runtime/charlab/venv/bin/python \
        epoch-ledger/charlab/inspect_character.py CHAR.glb OUT.json [--poses stand:1 walk:10 walk:30 ...]

For each pose (action:frame) the skinned meshes are evaluated and:
  * clothing intersections — every body vertex within 3 cm of a garment is tested against the garment's nearest
    surface; a body vertex on the *outside* of the garment shell (positive side of its normal) by more than 1 mm is a
    poke-through. Reported: count, worst depth, and where (bone the vertex follows most).
  * hair attachment — the same test of scalp vertices against the hair shell (scalp through hair), plus the gap
    between the hair's inner surface and the scalp (hair floating off the head).
  * eye alignment — eyeball centres vs. each other (symmetry) and their forward depth inside the eyelid opening.
Shapes are measured as exported (what three.js renders), not as authored in MPFB.
"""
from __future__ import annotations

import json
import os
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def kind(name):
    n = name.lower()
    if "eyebrow" in n: return "brow"
    if "eyelash" in n: return "lash"
    if "high-poly" in n or "low-poly" in n: return "eye"
    if "teeth" in n or "tongue" in n: return "mouth"
    if any(h in n for h in ("hair", "bob0", "short0", "long0", "ponytail", "braid", "afro")): return "hair"
    if any(c in n for c in ("suit", "shoes", "dress", "shirt", "fedora")): return "cloth"
    return "body"


NORMALS = {}


def evaluated(obj, dg):
    e = obj.evaluated_get(dg)
    m = e.to_mesh()
    rot = e.matrix_world.to_3x3()
    verts = [e.matrix_world @ v.co for v in m.vertices]
    NORMALS[obj.name] = [(rot @ v.normal).normalized() for v in m.vertices]
    polys = [tuple(p.vertices) for p in m.polygons]
    groups = [max(v.groups, key=lambda g: g.weight).group if len(v.groups) else -1 for v in m.vertices]
    names = [g.name for g in obj.vertex_groups]
    e.to_mesh_clear()
    return verts, polys, [names[g] if g >= 0 else "" for g in groups]


def outside(tree, verts, normals, inward=0.02, outward=0.03, tol=0.001):
    """Poke-through: the garment surface lies just *inside* the skin (a ray into the body meets it within 2 cm) and
    nothing of it lies outside (a ray out of the skin meets nothing within 3 cm). Covered skin has the garment
    outside; exposed skin (face, hands, neck above the collar) has the garment on neither side."""
    hits = []
    for i, (v, n) in enumerate(zip(verts, normals)):
        hin = tree.ray_cast(v - n * 1e-4, -n, inward)
        if hin[0] is None or hin[3] < tol:
            continue
        hout = tree.ray_cast(v + n * 1e-4, n, outward)
        if hout[0] is None:
            hits.append((i, hin[3]))
    return hits


def main(argv):
    glb, out = argv[0], argv[1]
    poses = argv[argv.index("--poses") + 1:] if "--poses" in argv else ["stand:1", "walk:10", "walk:25", "walk:40", "walk:55", "walk:70"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    by = {}
    for o in meshes:
        by.setdefault(kind(o.name), []).append(o)
    report = {"glb": os.path.basename(glb), "objects": {o.name: kind(o.name) for o in meshes}, "poses": {}}
    rig.animation_data_create()
    for p in poses:
        act_name, frame = p.split(":")
        act = bpy.data.actions.get(act_name) or next((a for a in bpy.data.actions if a.name.startswith(act_name)), None)
        if act is None:
            report["poses"][p] = "no such action"
            continue
        rig.animation_data.action = act
        if hasattr(act, "slots") and len(act.slots):
            rig.animation_data.action_slot = act.slots[0]
        bpy.context.scene.frame_set(int(frame))
        dg = bpy.context.evaluated_depsgraph_get()
        body_v, _, body_g = evaluated(by["body"][0], dg)
        r = {}
        for o in by.get("cloth", []) + by.get("hair", []):
            v, f, _ = evaluated(o, dg)
            tree = BVHTree.FromPolygons(v, f)
            hits = outside(tree, body_v, NORMALS[by['body'][0].name])
            where = {}
            for i, d in hits:
                where[body_g[i]] = where.get(body_g[i], 0) + 1
            entry = {"poke_vertices": len(hits), "worst_mm": round(max((d for _, d in hits), default=0) * 1000, 1),
                     "where": dict(sorted(where.items(), key=lambda x: -x[1])[:6])}
            if kind(o.name) == "hair":                       # gap: hair inner surface to scalp
                btree = BVHTree.FromPolygons(body_v, [tuple(x) for x in evaluated(by["body"][0], dg)[1]])
                gaps = []
                for hv in v:
                    loc, nrm, idx, dist = btree.find_nearest(hv, 0.08)
                    if loc is not None:
                        gaps.append(dist)
                gaps.sort()
                entry["hair_to_scalp_mm"] = {"min": round(gaps[0] * 1000, 1) if gaps else None,
                                             "p10": round(gaps[len(gaps) // 10] * 1000, 1) if gaps else None,
                                             "vertices_within_8cm": len(gaps), "hair_vertices": len(v)}
            r[o.name] = entry
        report["poses"][p] = r
    eyes = by.get("eye", [])
    if eyes:
        rig.animation_data.action = bpy.data.actions.get("stand")
        bpy.context.scene.frame_set(1)
        dg = bpy.context.evaluated_depsgraph_get()
        v, _, _ = evaluated(eyes[0], dg)
        L = [x for x in v if x.x > 0]
        R = [x for x in v if x.x <= 0]
        cl, cr = sum(L, Vector()) / len(L), sum(R, Vector()) / len(R)
        report["eyes"] = {"symmetry_x_mm": round((cl.x + cr.x) * 1000, 2), "height_diff_mm": round((cl.z - cr.z) * 1000, 2),
                          "depth_diff_mm": round((cl.y - cr.y) * 1000, 2), "interocular_mm": round((cl - cr).length * 1000, 1)}
    json.dump(report, open(out, "w"), indent=1)
    print(json.dumps(report, indent=1)[:6000])


if __name__ == "__main__":
    code = 0
    try:
        main(sys.argv[1:])
    except BaseException:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    os._exit(code)
