"""P6 mature stylised character prototype: a documentary financial professional built from the CharMorph Reom base.

    .runtime/charlab/venv/bin/python epoch-ledger/charlab/p6/build_p6.py VARIANT OUT.blend [--db DIR]
        VARIANT: A (subtle mature) | B (balanced editorial) | C (stronger cinematic illustrated) | raw (unchanged base)

Everything is geometry made here, deterministic, on the CC-BY Reom mesh (CharMorph database, `--db`, default
$CHARMORPH_DB or /home/user/upliner/charmorph-db). No shading-only stylisation: the variants differ in mesh.
 1. Base: Reom's basis mesh + anatomical morphs from the database (age, jaw, zygomatic, chin, nose, brow ridge,
    shoulders, trapezius, neck) toward a 35–45-year-old man.
 2. Geometric stylisation (per variant):
    • form simplification: Laplacian low-pass of the face's small-scale relief (soft-tissue noise, realistic creases)
    • plane accentuation: band-pass "unsharp masking" of the head's mid-frequency forms (jaw line, cheekbone, brow,
      nose bridge become crisper planes), weighted by a face mask
    • proportion: head scaled about the neck with a smooth falloff (the standard's 7.5 heads), never the eyes alone
 3. Pose: arms lowered from the base A-pose and relaxed fingers, by linear-blend skinning with the database's Rigify
    weights and joints (no armature needed for a static gate; the same weights drive the real rig later).
 4. Wardrobe on the posed body (offset shells, low-pass + collision push, procedural folds): shirt with collar, cuffs
    and placket; tie; trousers with straight legs and a break; belt; derby shoes. Separate meshes, reusable topology.
 5. Mesh hair (no particles): a scalp shell from the base's own scalp mask, shaped into a short side-parted cut with
    flow-aligned clumps and strands; brows, lash line and stubble are painted into the skin, restrained.
 6. Materials: restrained, illustrated (flat painted skin with warm/cool zones, no pore maps; cavity-tinted cloth).
Writes OUT.blend and OUT.json (measurements and parameters).
"""
import json
import math
import os
import sys

import bpy  # noqa: I001  (bpy first: it provides bmesh and mathutils)
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR, OUT = argv[0], argv[1]
DB = argv[argv.index("--db") + 1] if "--db" in argv else os.environ.get("CHARMORPH_DB", "/home/user/upliner/charmorph-db")
CH = os.path.join(DB, "characters/reom")

# ── variant parameters (wardrobe, hair, lighting are identical across variants) ──────────────────────────────────────
MATURE = {  # anatomical morphs shared by every variant (a 35–45-year-old man; chosen from a morph study, see P6 report)
    "Body_Age": 0.45, "Body_ReomMuscle": 0.1, "Body_ReomFat": 0.08, "Body_Height": 0.3, "Shoulders_ShoulderWidth": 1.8,
    "Shoulders_ShoulderBladeWidth": 2.8, "Shoulders_TrapeziusSize": 0.6, "Neck_Girth": 0.55, "Jaw_Mandible": 2.0, "Jaw_Mandible_GonialAngle": 0.6,
    "Chin_AnteriorMandibleWidth": 0.7, "Chin_Mentalis_Portrusion": 0.3, "Cheeks_Zygomatic_Bone": 1.0,
    "Nose_NasalBone": 0.4, "Face_FrontalBone_BrowRidge": -0.1, "Head_TemporalBone": 0.4, "Pelvis_CrotchVolume": -1.0,
}
VARIANTS = {
    "raw": dict(morphs={}, smooth=0, accent=0.0, head=1.0, extra={}),
    "A": dict(morphs=MATURE, smooth=2, accent=0.35, head=0.975, extra={}),
    "B": dict(morphs=MATURE, smooth=4, accent=0.7, head=0.96,
              extra={"Jaw_Mandible": 2.4, "Cheeks_Zygomatic_Bone": 1.4, "Generic_Stylized": 0.35}),
    "C": dict(morphs=MATURE, smooth=8, accent=1.6, head=0.945,
              extra={"Jaw_Mandible": 2.9, "Cheeks_Zygomatic_Bone": 1.9, "Chin_Mentalis_Portrusion": 0.5,
                     "Face_FrontalBone_BrowRidge": 0.15, "Generic_Stylized": 1.0}),
}
P = VARIANTS[VAR]


def sstep(x, a, b):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)


def npz_groups(path):
    z = np.load(path); names = z["names"].tobytes().decode().split("\0")
    off = np.concatenate([[0], np.cumsum(z["cnt"].astype(int))]); idx = z["idx"].astype(int); w = z["weights"].astype(float)
    return {names[i]: (idx[off[i]:off[i + 1]], w[off[i]:off[i + 1]]) for i in range(len(names))}


# ── 1. base mesh + morphs ────────────────────────────────────────────────────────────────────────────────────────────
bpy.ops.wm.open_mainfile(filepath=os.path.join(CH, "char.blend"), load_ui=False)
for o in list(bpy.data.objects):
    if o.name != "cm_reom": bpy.data.objects.remove(o)
body = bpy.data.objects["cm_reom"]; body.name = "p6_body"; me = body.data
co = np.load(os.path.join(CH, "morphs/L1/Default.npy")).astype(float)
morphs = dict(P["morphs"]); morphs.update(P["extra"])
morphs.update(json.loads(os.environ.get("P6_MORPHS", "{}")))     # exploration override (not used by the variants)
for name, val in sorted(morphs.items()):
    z = np.load(os.path.join(CH, "morphs/L2", name + ".npz")); co[z["idx"].astype(int)] += val * z["delta"].astype(float)
N = len(co)
mat_idx = np.zeros(len(me.polygons), int); me.polygons.foreach_get("material_index", mat_idx)
me.materials.clear()   # our own materials are appended later (indices are re-assigned then)
faces = [tuple(p.vertices) for p in me.polygons]
vmat = np.full(N, -1)
for f, m in zip(faces, mat_idx):
    for v in f: vmat[v] = m if vmat[v] < 0 or m in (3,) else vmat[v]
EYE = np.isin(vmat, [0, 1, 2]); MOUTH_IN = np.isin(vmat, [7, 8, 9, 10])
edges = np.array([tuple(e.vertices) for e in me.edges])
nbr = [[] for _ in range(N)]
for a, b in edges: nbr[a].append(b); nbr[b].append(a)


def joints(c):
    J = {}
    for k, (i, w) in npz_groups(os.path.join(CH, "joints/rigify.npz")).items(): J[k[6:]] = (c[i] * w[:, None]).sum(0) / w.sum()
    return J


def laplace(c, mask, it, lam=0.5, nb=nbr):
    c = c.copy()
    for _ in range(it):
        avg = np.array([c[n].mean(0) if n else c[i] for i, n in enumerate(nb)])
        c[mask] += lam * (avg[mask] - c[mask])
    return c


J = joints(co)
# head mask: soft weight 1 above the jaw/neck junction, 0 below the neck base; never eyes or mouth interior (they ride along)
z_chin, z_neck = J["chin_head"][2], J["spine.004_tail"][2]
head_w = np.clip((co[:, 2] - (z_neck + 0.01)) / max(z_chin - z_neck - 0.01, 1e-3), 0, 1)
face_front = np.clip((-(co[:, 1]) + 0.02) / 0.06, 0, 1) * head_w                       # the face, fading toward the back
soft = (~EYE) & (~MOUTH_IN)

# ── 2. geometric stylisation ────────────────────────────────────────────────────────────────────────────────────────
base = co.copy()
if P["smooth"]:     # simplify small relief on face and neck (only displacement relative to a band-limited version)
    low = laplace(co, soft, P["smooth"], 0.5)
    co[soft] = co[soft] + (low[soft] - co[soft]) * (0.6 * head_w[soft, None] + 0.25 * (1 - head_w[soft, None]))
if P["accent"]:     # plane accentuation: v += k (v − L(v)), L a mid-frequency low-pass over the head
    low = laplace(co, soft, 16, 0.5); mid = laplace(co, soft, 3, 0.5)
    d = mid - low
    co[soft] += P["accent"] * d[soft] * (0.35 + 0.65 * face_front[soft, None]) * head_w[soft, None]
# eyeballs and mouth interior: move rigidly with the surrounding skin (mean displacement of their neighbourhood)
disp = co - base
for side in (1, -1):
    eye = EYE & (np.sign(base[:, 0]) == side)
    if not eye.any(): continue
    ctr = base[eye].mean(0); near = soft & (np.linalg.norm(base - ctr, axis=1) < 0.03)
    co[eye] = base[eye] + disp[near].mean(0)
inner = MOUTH_IN; ctr = base[inner].mean(0); near = soft & (np.linalg.norm(base - ctr, axis=1) < 0.035)
co[inner] = base[inner] + disp[near].mean(0)
# head proportion about the neck (smooth falloff through the neck so nothing shears)
if P["head"] != 1.0:
    piv = np.array([0, J["spine.004_tail"][1], z_neck + 0.03])
    s = 1 + (P["head"] - 1) * np.clip((co[:, 2] - (z_neck - 0.02)) / 0.07, 0, 1)
    co = piv + (co - piv) * s[:, None]
# natural asymmetry (small, deterministic): the character's left brow sits 1 mm higher, the right mouth corner and
# right side of the jaw a little fuller; nothing large enough to read as a deformity
Jt = joints(co)
def bump(c, r, d):
    w = np.clip(1 - np.linalg.norm(co - c, axis=1) / r, 0, 1) ** 2 * soft
    return w[:, None] * np.asarray(d)
if VAR != "raw": co += bump(Jt["brow.T.L.001_head"], 0.025, [0, 0, 0.0010])
if VAR != "raw": co += bump(Jt["lip.T.R.001_tail"] if "lip.T.R.001_tail" in Jt else Jt["lip.T.R_tail"], 0.018, [-0.0006, -0.0004, 0.0004])
if VAR != "raw": co += bump(Jt["jaw.R.001_tail"] if "jaw.R.001_tail" in Jt else Jt["jaw.R_tail"], 0.03, [-0.0010, 0, 0])
J = joints(co)

# ── 3. pose (LBS with Rigify weights): arms down and relaxed, fingers softly curled ─────────────────────────────────
W = npz_groups(os.path.join(CH, "weights/rigify.npz"))


def rot(axis, ang, piv):
    R = np.array(Matrix.Rotation(ang, 3, Vector(axis).normalized()))
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = piv - R @ piv
    return T


def tr(T, p): return p @ T[:3, :3].T + T[:3, 3]


bone_T = {}
for side, sx in (("L", 1), ("R", -1)):
    ua_h, ua_t, fa_t = J[f"upper_arm.{side}_head"], J[f"upper_arm.{side}_tail"], J[f"forearm.{side}_tail"]
    up = ua_t - ua_h; tgt = np.array([sx * -0.02, -0.05, -1.0]); tgt /= np.linalg.norm(tgt)
    ax = np.cross(up / np.linalg.norm(up), tgt); ang = math.asin(min(1, np.linalg.norm(ax)))
    T_up = rot(ax, ang, ua_h)
    el = tr(T_up, ua_t)
    T_fa = rot(np.array([sx, 0, 0]), -math.radians(14), el) @ T_up   # slight elbow flex forward
    wr = tr(T_fa, fa_t); T_fa = rot(wr - el, sx * math.radians(60), el) @ T_fa   # pronation: palms toward the thighs
    T_sh = rot(np.array([0, 1.0, 0]), sx * math.radians(4), J[f"shoulder.{side}_head"])                  # shoulders settle
    bone_T[f"DEF-shoulder.{side}"] = T_sh
    for b in (f"DEF-upper_arm.{side}", f"DEF-upper_arm.{side}.001"): bone_T[b] = T_up
    for b in (f"DEF-forearm.{side}", f"DEF-forearm.{side}.001", f"DEF-hand.{side}"): bone_T[b] = T_fa
    # fingers: a relaxed curl per segment about the knuckle line, composed with the hand
    palm = {"index": "palm.01", "middle": "palm.02", "ring": "palm.03", "pinky": "palm.04"}
    knuckles = J[f"palm.01.{side}_tail"] - J[f"palm.04.{side}_tail"]; knuckles /= np.linalg.norm(knuckles)
    for f, curl in (("index", 14), ("middle", 18), ("ring", 21), ("pinky", 24), ("thumb", 8)):
        T_prev = T_fa
        for seg in ("01", "02", "03"):
            stem = "thumb" if f == "thumb" else "f_" + f; nm = f"{stem}.{seg}.{side}"
            h = J.get(nm + "_head")
            if h is None: h = J[f"{stem}.{int(seg) - 1:02d}.{side}_tail"] if seg != "01" else J[f"{palm[f]}.{side}_tail"]
            a = knuckles if f != "thumb" else (J[f"thumb.01.{side}_tail"] - J[f"thumb.01.{side}_head"])
            if f == "thumb": a = np.cross(a, knuckles)
            T_prev = T_prev @ rot(a, sx * math.radians(curl), h)
            bone_T[f"DEF-{nm}"] = T_prev
    for b in (f"DEF-palm.01.{side}", f"DEF-palm.02.{side}", f"DEF-palm.03.{side}", f"DEF-palm.04.{side}"): bone_T[b] = T_fa
Wm = np.zeros((N, len(W))); names = list(W)
for j, nm in enumerate(names):
    i, w = W[nm]; Wm[i, j] = w
tot = Wm.sum(1); tot[tot == 0] = 1; Wm /= tot[:, None]
posed = np.zeros_like(co); unc = 1 - Wm.sum(1)
for j, nm in enumerate(names):
    T = bone_T.get(nm)
    posed += Wm[:, j:j + 1] * (tr(T, co) if T is not None else co)
posed += unc[:, None] * co
co_rest = co; co = posed
co[:, 2] -= co[:, 2].min()                                                    # stand on the floor
me.vertices.foreach_set("co", co.ravel().astype(np.float32)); me.update()
J = joints(co)
bpy.context.view_layer.update()

# vertex-paint layers used by the skin shader (scalp, beard, lips from the base's own masks; brows/lashes from joints)
def load_img(path):
    im = bpy.data.images.load(path); im.colorspace_settings.name = "Non-Color"; w, h = im.size
    a = np.zeros(w * h * 4, np.float32); im.pixels.foreach_get(a); bpy.data.images.remove(im)
    return a.reshape(h, w, 4)[::-1]          # Blender pixels start at the bottom row
masks = load_img(os.path.join(CH, "textures/Head_ScalpBeardShadowMask.png"))
lipm = load_img(os.path.join(CH, "textures/ReomLipMask.png"))[..., 0]
uv = np.zeros(len(me.loops) * 2); me.uv_layers[0].data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
lv = np.zeros(len(me.loops), int); me.loops.foreach_get("vertex_index", lv)
def sample(img, u):
    h, w = img.shape[:2]; x = np.clip((u[:, 0] % 1) * (w - 1), 0, w - 1).astype(int); y = np.clip((1 - u[:, 1] % 1) * (h - 1), 0, h - 1).astype(int)
    return img[y, x]
head_v = vmat == 3
scalp = np.zeros(N); beard = np.zeros(N); lips = np.zeros(N)
s = sample(masks, uv); l = sample(lipm, uv)
for k in range(len(lv)):
    v = lv[k]
    if head_v[v]: scalp[v] = max(scalp[v], s[k, 1]); beard[v] = max(beard[v], s[k, 2]); lips[v] = max(lips[v], l[k])


def polyline_dist(pts, P_):
    best = np.full(len(P_), 9.0); tpar = np.zeros(len(P_))
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]); L /= L[-1]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; ab = b - a; t = np.clip(((P_ - a) @ ab) / (ab @ ab), 0, 1)
        d = np.linalg.norm(P_ - (a + t[:, None] * ab), axis=1); m = d < best; best[m] = d[m]; tpar[m] = L[i] + t[m] * (L[i + 1] - L[i])
    return best, tpar


brow = np.zeros(N); lash = np.zeros(N)
for side in ("L", "R"):
    pts = np.array([J[f"brow.T.{side}.003_tail"], J[f"brow.T.{side}.003_head"], J[f"brow.T.{side}.001_tail"], J[f"brow.T.{side}.001_head"], J[f"brow.T.{side}_head"]])
    pts[:, 2] -= 0.002
    d, t = polyline_dist(pts, co)
    width = 0.0042 * (1 - 0.55 * t) + 0.0012                                  # tapered: fuller inside, fine at the tail
    brow = np.maximum(brow, np.clip(1 - d / width, 0, 1) * head_v * (co[:, 1] < 0.03))
    lp = np.array([J[f"lid.T.{side}_head"], J[f"lid.T.{side}_tail"], J[f"lid.T.{side}.001_tail"] if f"lid.T.{side}.001_tail" in J else J[f"lid.T.{side}_tail"],
                   J[f"lid.T.{side}.002_tail"], J[f"lid.B.{side}_head"]])
    d, t = polyline_dist(lp, co)
    lash = np.maximum(lash, np.clip(1 - d / 0.0016, 0, 1) * (1 - np.abs(t - 0.45) * 1.2).clip(0, 1) * head_v)


def add_attr(name, vals):
    a = me.color_attributes.new(name, "FLOAT_COLOR", "POINT"); c = np.zeros((N, 4)); c[:, :3] = np.asarray(vals).reshape(N, -1)[:, :3] if np.ndim(vals) > 1 else np.repeat(np.asarray(vals)[:, None], 3, 1); c[:, 3] = 1
    a.data.foreach_set("color", c.ravel().astype(np.float32))


# warm zones of a painted face: cheeks, nose tip, ears, knuckles (distance to landmarks)
def blob(ctrs, r):
    out = np.zeros(N)
    for c in ctrs: out = np.maximum(out, np.clip(1 - np.linalg.norm(co - c, axis=1) / r, 0, 1) ** 1.5)
    return out


cheeks = blob([J["cheek.T.L_head"] + np.array([0, -0.01, -0.012]), J["cheek.T.R_head"] + np.array([0, -0.01, -0.012])], 0.035)
nose_tip = blob([J["nose.002_tail"] if "nose.002_tail" in J else J["nose_tail"]], 0.018)
ears = blob([J["ear.L_head"], J["ear.R_head"]], 0.04)
add_attr("paint_a", np.stack([scalp, beard, lips], 1))
add_attr("paint_b", np.stack([brow, lash, np.clip(cheeks + 0.8 * nose_tip + 0.7 * ears, 0, 1)], 1))

# ── helpers for garments ────────────────────────────────────────────────────────────────────────────────────────────
dg = bpy.context.evaluated_depsgraph_get()
body_bvh = BVHTree.FromObject(body, dg)
bm_b = bmesh.new(); bm_b.from_mesh(me); bm_b.normal_update()
vnorm = np.array([v.normal for v in bm_b.verts])


def make_obj(name, verts, fcs, mat=None):
    m = bpy.data.meshes.new(name); m.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in fcs]); m.update()
    o = bpy.data.objects.new(name, m); bpy.context.scene.collection.objects.link(o)
    if mat: m.materials.append(mat)
    for p in m.polygons: p.use_smooth = True
    return o


def sub_mesh(vsel):
    """faces whose vertices are all selected → (verts, faces, original vertex index)."""
    keep = [f for f in faces if all(vsel[v] for v in f)]
    used = sorted({v for f in keep for v in f}); rm = {v: i for i, v in enumerate(used)}
    return co[used].copy(), [[rm[v] for v in f] for f in keep], np.array(used)


def subdivide(o, levels):
    m = o.modifiers.new("sub", "SUBSURF"); m.levels = levels; m.render_levels = levels
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=m.name)


def arrays(o):
    m = o.data; v = np.zeros(len(m.vertices) * 3); m.vertices.foreach_get("co", v); v = v.reshape(-1, 3)
    nb = [[] for _ in range(len(v))]
    for e in m.edges: a, b = e.vertices; nb[a].append(b); nb[b].append(a)
    bnd = np.zeros(len(v), bool)
    bm = bmesh.new(); bm.from_mesh(m)
    for e in bm.edges:
        if e.is_boundary: bnd[e.verts[0].index] = bnd[e.verts[1].index] = True
    bm.free()
    return v, nb, bnd


def setco(o, v): o.data.vertices.foreach_set("co", v.ravel().astype(np.float32)); o.data.update()


def push_out(v, gap, keep_mask=None):
    """move points to at least `gap` outside the body surface (along the body normal)."""
    for i in range(len(v)):
        if keep_mask is not None and not keep_mask[i]: continue
        loc, n, _, d = body_bvh.find_nearest(Vector(v[i]))
        if loc is None: continue
        n = Vector(n); off = Vector(v[i]) - loc
        s = off.dot(n)
        if s < gap: v[i] = np.array(loc + n * gap)
    return v


def vnormals(o):
    o.data.update(); m = o.data; n = np.zeros(len(m.vertices) * 3); m.vertices.foreach_get("normal", n); return n.reshape(-1, 3)


def shell(name, vsel, offset, smooth_it, mat, gap=0.004, levels=1):
    v, f, orig = sub_mesh(vsel)
    v = v + vnorm[orig] * (offset[orig][:, None] if np.ndim(offset) else offset)
    o = make_obj(name, v, f, mat)
    bm = bmesh.new(); bm.from_mesh(o.data)                    # the base mesh is split along UV seams (inner legs, arms):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)    # weld, or the shell opens along them when smoothed
    bm.to_mesh(o.data); bm.free(); subdivide(o, levels)
    v, nb, bnd = arrays(o)
    bnb = [[j for j in nb[i] if bnd[j]] if bnd[i] else [] for i in range(len(v))]
    for _ in range(3):
        v = laplace(v, ~bnd, smooth_it, 0.6, nb); v = laplace(v, bnd, 8, 0.5, bnb); v = push_out(v, gap)
    setco(o, v)
    return o


# landmarks
z_belt = J["spine_tail"][2] + 0.005                          # belt line (just below the navel)
z_ank = J["foot.L_head"][2] + 0.035 if "foot.L_head" in J else J["shin.L_tail"][2] + 0.035
z_wrist_L = J["hand.L_head"][2] if "hand.L_head" in J else J["forearm.L_tail"][2]
handw = sum(Wm[:, names.index(n)] for n in names if any(k in n for k in ("hand", "f_", "thumb", "palm")))
neckw = sum(Wm[:, names.index(n)] for n in names if n in ("DEF-spine.004", "DEF-spine.005", "DEF-spine.006"))


def mat(name, col, rough=0.6, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    for k, val in kw.items(): b.inputs[k].default_value = val
    return m


def cavity_cloth(name, col, dark, rough=0.75, sheen=0.25):
    """cloth: colour darkened in folds and cavities (pointiness), a soft sheen: illustrated, not plastic."""
    m = mat(name, col, rough); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry"); ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.40; ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.56; ramp.color_ramp.elements[1].color = (*col, 1)
    nt.links.new(geo.outputs["Pointiness"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Sheen Weight"].default_value = sheen; b.inputs["Sheen Roughness"].default_value = 0.5
    return m


M_SHIRT = cavity_cloth("shirt", (0.62, 0.68, 0.76), (0.42, 0.47, 0.56))        # pale blue poplin
M_TROUS = cavity_cloth("trousers", (0.075, 0.085, 0.11), (0.035, 0.04, 0.055), 0.8)   # charcoal navy wool
M_TIE = cavity_cloth("tie", (0.16, 0.03, 0.04), (0.08, 0.015, 0.02), 0.5, 0.4)   # deep burgundy silk
M_BELT = mat("belt", (0.04, 0.025, 0.02), 0.4)
M_SHOE = mat("shoe", (0.07, 0.035, 0.022), 0.32, **{"Coat Weight": 0.25, "Coat Roughness": 0.25})
M_SOLE = mat("sole", (0.025, 0.02, 0.018), 0.7)
M_BTN = mat("button", (0.85, 0.84, 0.8), 0.35)

# ── 4. wardrobe ─────────────────────────────────────────────────────────────────────────────────────────────────────
# shirt: torso and arms, from just below the belt (tucked) to the wrist; ends at the neck base (collar added below)
z_collar = J["spine.004_tail"][2] - 0.035
sel = np.isin(vmat, [3, 4, 5]) & (co[:, 2] > z_belt - 0.02) & (handw < 0.25) & (co[:, 2] < z_collar + 0.018 + 0.03 * np.clip((co[:, 1] - 0.0) / 0.06, 0, 1)) & ~EYE & ~MOUTH_IN
for side in (1, -1):        # cuffs stop 2 cm short of the wrist crease
    arm = (np.sign(co[:, 0]) == side) & (np.abs(co[:, 0]) > 0.17)
    zw = J["hand.L_head" if side > 0 else "hand.R_head"][2] if "hand.L_head" in J else z_wrist_L
    sel &= ~(arm & (co[:, 2] < zw + 0.03))
off = (np.full(N, 0.006) + 0.010 * np.clip((co[:, 2] - z_belt) / 0.12, 0, 1) * (np.abs(co[:, 0]) < 0.17)) * (1 - 0.6 * sstep(co[:, 2], z_collar - 0.07, z_collar))
shirt = shell("p6_shirt", sel, off, 12, M_SHIRT, gap=0.006, levels=2)
sv, snb, sbnd = arrays(shirt); sn = vnormals(shirt)
# torso volume: a shirt hangs from the chest; fill the abdominal concavity (per height slice: radius ≥ chest profile)
cz = J["spine.003_tail"][2] - 0.06
torso = np.abs(sv[:, 0]) < 0.16
for i in np.where(torso & (sv[:, 2] < cz) & (sv[:, 2] > z_belt))[0]:
    r = sv[i, :2] - np.array([0, J["spine.002_tail"][1] - 0.005])
    if r[1] < 0: sv[i, 1] -= 0.012 * math.sin(math.pi * (sv[i, 2] - z_belt) / (cz - z_belt))   # front fullness
# drape: cloth spans the chest and abdomen instead of following them; per vertical column the shirt front is moved out
# to its convex front envelope (the line a shirt takes from the chest down to the tuck)
spy = J["spine.002_tail"][1]
fr = (sv[:, 1] < spy - 0.02) & (np.abs(sv[:, 0]) < 0.15) & (sv[:, 2] > z_belt + 0.01) & (sv[:, 2] < J["spine.003_tail"][2] + 0.02)
for x0 in np.arange(-0.15, 0.15, 0.008):
    m = np.where(fr & (np.abs(sv[:, 0] - x0) < 0.006))[0]
    if len(m) < 4: continue
    pts = sorted(zip(sv[m, 2], sv[m, 1]))
    hull = []
    for p_ in pts:                         # lower hull in (z, y): the forward-most envelope (y is negative forward)
        while len(hull) >= 2 and (hull[-1][0] - hull[-2][0]) * (p_[1] - hull[-2][1]) - (hull[-1][1] - hull[-2][1]) * (p_[0] - hull[-2][0]) >= 0:
            hull.pop()
        hull.append(p_)
    hz_, hy_ = np.array(hull).T
    sv[m, 1] = np.minimum(sv[m, 1], np.interp(sv[m, 2], hz_, hy_) - 0.001)
sv = laplace(sv, fr & ~sbnd, 3, 0.5, snb)
# folds: tuck blousing above the belt, elbow crease rings, a drape fold from the armpit
ang = np.arctan2(sv[:, 1] - 0.06, sv[:, 0])
d = np.zeros(len(sv))
band = np.clip(1 - np.abs(sv[:, 2] - (z_belt + 0.035)) / 0.04, 0, 1) * torso
d += 0.0045 * band * np.sin(ang * 23 + 2.0 * np.sin(ang * 5))
for side, nm in ((1, "L"), (-1, "R")):
    el = tr(bone_T[f"DEF-upper_arm.{nm}"], J[f"upper_arm.{nm}_tail"])
    dist = np.linalg.norm(sv - el, axis=1); w = np.clip(1 - dist / 0.09, 0, 1) * (np.sign(sv[:, 0]) == side)
    d += 0.0035 * w * np.sin((sv[:, 2] - el[2]) / 0.012 * math.pi + 1.4 * np.sin(ang * 3))
    ap = J[f"upper_arm.{nm}_head"] - np.array([side * 0.02, 0, 0.07])
    w = np.clip(1 - np.linalg.norm(sv - ap, axis=1) / 0.08, 0, 1)
    d += 0.0025 * w * np.sin(((sv[:, 2] - ap[2]) + side * 0.6 * (sv[:, 0] - ap[0])) / 0.018 * math.pi)
sv += sn * d[:, None]; setco(shirt, sv)
sol = shirt.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.0022; sol.offset = -1

# collar: a separate stand and turned-down leaf, built around the shirt's neck opening (open only under the knot)
cv, cnb, cbnd = arrays(shirt)
nk = cbnd & (cv[:, 2] > z_collar - 0.05) & (np.abs(cv[:, 0]) < 0.12)
nc = cv[nk]; ctr = np.array([0.0, (nc[:, 1].max() + nc[:, 1].min()) / 2, 0])
nsk = (vmat == 3) & (np.abs(co[:, 2] - (z_collar + 0.03)) < 0.008) & (np.abs(co[:, 0]) < 0.09)
ctr = np.array([0.0, (co[nsk, 1].max() + co[nsk, 1].min()) / 2, 0])
ea, eb = (co[nsk, 0].max() - co[nsk, 0].min()) / 2 + 0.006, (co[nsk, 1].max() - co[nsk, 1].min()) / 2 + 0.006
nth = np.arctan2(nc[:, 1] - ctr[1], nc[:, 0])
# the shirt's neckline is drawn in to the collar base (no gap between the shoulders' slope and the stand)
bm = bmesh.new(); bm.from_mesh(shirt.data); bm.verts.ensure_lookup_table()
bverts = {v.index for e in bm.edges if e.is_boundary for v in e.verts}; comp = {}
for v0 in bverts:                                          # boundary loops; the neckline is the highest one
    if v0 in comp: continue
    stack = [v0]; comp[v0] = v0
    while stack:
        v = bm.verts[stack.pop()]
        for e in v.link_edges:
            if not e.is_boundary: continue
            u = e.other_vert(v).index
            if u not in comp: comp[u] = v0; stack.append(u)
bm.free()
loops = {}
for v, r in comp.items(): loops.setdefault(r, []).append(v)
nidx = np.array(max(loops.values(), key=lambda L: cv[L, 2].mean()))
for i in nidx:
    th = math.atan2(cv[i, 1] - ctr[1], cv[i, 0]); phi = (th + math.pi / 2) % (2 * math.pi)
    back = max(0.0, -math.cos(phi)); z0 = z_collar + 0.012 - 0.012 * max(0.0, math.cos(phi)) ** 2 - 0.045 * back ** 1.5
    cv[i] = [ctr[0] + (ea + 0.001) * math.cos(th), ctr[1] + (eb + 0.001) * math.sin(th), z0 + 0.006]
near = np.zeros(len(cv), bool)
for i in nidx: near |= np.linalg.norm(cv - cv[i], axis=1) < 0.07
cv = laplace(cv, near & ~cbnd, 10, 0.5, cnb); cv = push_out(cv, 0.008, ~cbnd | near); setco(shirt, cv)   # final clearance (subdivision and thickness shrink convex areas)
COLS, cvs, cfs = 72, [], []
phis = np.linspace(0.16, 2 * math.pi - 0.16, COLS)           # angle from the front centre (the gap is under the knot)
rows = []
for phi in phis:
    th = -math.pi / 2 + phi; dirn = np.array([math.cos(th), math.sin(th), 0])
    back = max(0.0, -math.cos(phi)); z0 = z_collar + 0.012 - 0.012 * max(0.0, math.cos(phi)) ** 2 - 0.045 * back ** 1.5
    base = np.array([ctr[0] + ea * dirn[0], ctr[1] + eb * dirn[1], z0])
    front = max(0.0, math.cos(phi)) ** 2; tip = max(0.0, math.cos(phi)) ** 10
    col = []
    for s_ in np.linspace(0, 1, 5):                              # the stand: up and slightly in toward the neck
        col.append(base + np.array([0, 0, (0.032 + 0.045 * back ** 1.5) * s_]) - dirn * (0.004 - 0.012 * back ** 1.5 * (1 - s_)) * s_)
    topp = col[-1] + dirn * 0.0045 + np.array([0, 0, 0.003])
    for t in np.linspace(0, 1, 7):                               # the leaf: over and down, spreading to points in front
        out = 0.003 + (0.008 + 0.012 * front + 0.022 * tip + 0.012 * back) * t ** 0.8
        down = (0.040 + 0.012 * front + 0.03 * tip + 0.035 * back ** 1.5) * t
        col.append(topp + dirn * out - np.array([0, 0, down]) - np.array([0, 0, 0.004 * math.sin(math.pi * t)]))
    rows.append(col)
R = len(rows[0])
for i, col in enumerate(rows):
    cvs += [list(p) for p in col]
    if i: cfs += [[(i - 1) * R + r, (i - 1) * R + r + 1, i * R + r + 1, i * R + r] for r in range(R - 1)]
collar = make_obj("p6_collar", np.array(cvs), cfs, M_SHIRT)
s_ = collar.modifiers.new("thick", "SOLIDIFY"); s_.thickness = 0.0018
s_ = collar.modifiers.new("sub", "SUBSURF"); s_.levels = 1; s_.render_levels = 2

# tie: a tapered blade on the shirt front, from a knot at the collar to the belt
front_pts = []
for zz in np.linspace(z_collar + 0.012, z_belt + 0.01, 24):
    loc, n, _, _ = BVHTree.FromObject(shirt, bpy.context.evaluated_depsgraph_get()).ray_cast(Vector((0, -0.5, zz)), Vector((0, 1, 0)))
    if loc: front_pts.append((np.array(loc), np.array(n)))
tv, tf = [], []
for k, (p, n) in enumerate(front_pts):
    t = k / (len(front_pts) - 1); w = 0.016 + 0.026 * t ** 0.8 if k > 1 else 0.019
    side = np.array([1.0, 0, 0]); lift = n * (0.006 + 0.004 * t)
    tip = -0.03 if k == len(front_pts) - 1 else 0
    tv += [p + lift - side * w, p + lift + n * 0.002, p + lift + side * w]
    if k == len(front_pts) - 1: tv[-2] = tv[-2] + np.array([0, 0, tip])
    if k: b0 = 3 * (k - 1); tf += [[b0, b0 + 1, b0 + 4, b0 + 3], [b0 + 1, b0 + 2, b0 + 5, b0 + 4]]
tie = make_obj("p6_tie", tv, tf, M_TIE); s_ = tie.modifiers.new("thick", "SOLIDIFY"); s_.thickness = 0.004
s_ = tie.modifiers.new("sub", "SUBSURF"); s_.levels = s_.render_levels = 2
kn = front_pts[1][0] + front_pts[1][1] * 0.010 + np.array([0, 0, 0.004])
bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(kn)); knot = bpy.context.object; knot.name = "p6_tie_knot"
for v in knot.data.vertices:                                # a four-in-hand knot: an inverted, rounded trapezoid
    v.co.x *= 0.036 * (1.0 if v.co.z > 0 else 0.62); v.co.y *= 0.016; v.co.z *= 0.034
knot.rotation_euler.x = math.radians(-12); knot.data.materials.append(M_TIE)
bv_ = knot.modifiers.new("bev", "BEVEL"); bv_.width = 0.006; bv_.segments = 4
sb_ = knot.modifiers.new("sub", "SUBSURF"); sb_.levels = sb_.render_levels = 2
bpy.ops.object.shade_smooth()

# trousers: a shell over hips and thighs; below it each leg is lofted as clean rings that hang straight to a hem
#           resting on the shoe (shorter at the front), then folds: the break, behind the knee, a pressed crease
legb = vmat == 6
def leg_centre(side, z):
    m = legb & (np.sign(co[:, 0]) == side) & (np.abs(co[:, 2] - z) < 0.02)
    return np.array([(co[m, 0].max() + co[m, 0].min()) / 2, (co[m, 1].max() + co[m, 1].min()) / 2])
z_cut = J["thigh.L_tail"][2] + 0.10
selt = np.isin(vmat, [4, 6]) & (co[:, 2] < z_belt + 0.025) & (co[:, 2] > z_cut) & ~EYE
trous = shell("p6_trousers", selt, np.full(N, 0.011) + 0.006 * (co[:, 2] > z_belt - 0.08), 6, M_TROUS, gap=0.009, levels=2)
z_hem = 0.045
bm = bmesh.new(); bm.from_mesh(trous.data); bm.verts.ensure_lookup_table()
for side in (1, -1):
    loop = [e for e in bm.edges if e.is_boundary and max(v.co.z for v in e.verts) < z_cut + 0.04 and np.sign(e.verts[0].co.x) == side]
    lv0 = {v for e in loop for v in e.verts}
    deg = {}
    for e in loop:
        for v in e.verts: deg[v] = deg.get(v, 0) + 1
    ends = [v for v, d_ in deg.items() if d_ == 1]
    if len(ends) == 2:                                            # close a ring left open by a notch in the shell's edge
        e_new = bm.edges.get(ends) or bm.edges.new(ends); loop.append(e_new)
    ck = leg_centre(side, J["thigh.L_tail"][2]); ch = leg_centre(side, z_ank + 0.03); ch[1] = ck[1] + 0.3 * (ch[1] - ck[1]); ch[0] = ck[0] + 0.6 * (ch[0] - ck[0])
    c0 = np.array([np.mean([v.co.x for v in lv0]), np.mean([v.co.y for v in lv0])])
    info_ = {v: (math.atan2(v.co.y - c0[1], v.co.x - c0[0]), math.hypot(v.co.x - c0[0], v.co.y - c0[1]), v.co.z) for v in lv0}
    edges_ = loop; prev = {v: v for v in lv0}
    STEPS = 22
    for k in range(1, STEPS + 1):
        t = k / STEPS
        r = bmesh.ops.extrude_edge_only(bm, edges=edges_)
        newv = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
        edges_ = [g for g in r["geom"] if isinstance(g, bmesh.types.BMEdge) and all(v in newv for v in g.verts)]
        # extrude_edge_only duplicates verts at the same location: match each to its previous-ring vertex
        cur = {}
        prv = list(prev.values()); P_ = np.array([u.co for u in prv])
        for v in newv:
            j = int(np.argmin(((P_ - np.array(v.co)) ** 2).sum(1))); root = [o for o, u in prev.items() if u is prv[j]][0]; cur[root] = v
        for root, v in cur.items():
            ang, r0, z0 = info_[root]
            front = max(0.0, -math.sin(ang))
            zh = z_hem + 0.028 * front ** 2
            c = c0 + (ch - c0) * t; R_ = r0 + (0.069 - r0) * float(sstep(t, 0, 0.35))
            v.co.x, v.co.y = c[0] + R_ * math.cos(ang), c[1] + R_ * math.sin(ang); v.co.z = z0 + (zh - z0) * t
        prev = cur
bm.to_mesh(trous.data); bm.free(); trous.data.update()
for p_ in trous.data.polygons: p_.use_smooth = True
tv_, tnb, tbnd = arrays(trous)
tv_ = laplace(tv_, ~tbnd & (tv_[:, 2] < z_cut + 0.05) & (tv_[:, 2] > z_cut - 0.08), 4, 0.5, tnb)   # blend the join
for _ in range(3):         # calves and knees stay inside the hanging leg (collision), then relax
    tv_ = push_out(tv_, 0.016, tv_[:, 2] < z_cut + 0.02); tv_ = laplace(tv_, ~tbnd & (tv_[:, 2] < z_cut + 0.02), 3, 0.5, tnb)
tv_ = push_out(tv_, 0.008, tv_[:, 2] < z_cut + 0.02)
setco(trous, tv_); tn = vnormals(trous)
for side, nm in ((1, "L"), (-1, "R")):
    kne = J[f"thigh.{nm}_tail"]; m = (np.sign(tv_[:, 0]) == side); hz = tv_[:, 2] - z_hem
    w = np.clip(1 - hz / 0.13, 0, 1) * m
    tv_ += tn * (0.0045 * w * np.sin(hz / 0.035 * math.pi + 2.5 * tv_[:, 0] * side))[:, None]       # the break
    w = np.clip(1 - np.abs(tv_[:, 2] - kne[2] + 0.02) / 0.07, 0, 1) * m * (tv_[:, 1] > kne[1])
    tv_ += tn * (0.0022 * w * np.sin((tv_[:, 2] - kne[2]) / 0.022 * math.pi))[:, None]             # behind the knee
    cx = leg_centre(side, kne[2])[0]; mm = m & (tv_[:, 2] < J[f"thigh.{nm}_head"][2] - 0.08) & (tv_[:, 1] < kne[1])
    tv_[:, 1] -= 0.0025 * np.clip(1 - np.abs(tv_[:, 0] - cx) / 0.01, 0, 1) * mm                    # pressed front crease
setco(trous, tv_)
s_ = trous.modifiers.new("thick", "SOLIDIFY"); s_.thickness = 0.0025; s_.offset = -1

# belt: a band fitted to the trousers' waist (per-angle outer radius), and a buckle
tw = tv_[np.abs(tv_[:, 2] - (z_belt + 0.005)) < 0.014]; bc = np.array([0, (tw[:, 1].max() + tw[:, 1].min()) / 2])
ta = np.arctan2(tw[:, 1] - bc[1], tw[:, 0]); trr = np.linalg.norm(tw[:, :2] - bc, axis=1)
bins = np.linspace(-math.pi, math.pi, 49); rad = np.array([trr[(ta >= bins[i]) & (ta < bins[i + 1])].max() if ((ta >= bins[i]) & (ta < bins[i + 1])).any() else np.nan for i in range(48)])
ok = ~np.isnan(rad); rad = np.interp(np.arange(48), np.arange(48)[ok], rad[ok], period=48)
rad = np.convolve(np.concatenate([rad[-2:], rad, rad[:2]]), np.ones(5) / 5, "valid")
bvs, bfs = [], []
for i in range(48):
    a_ = (bins[i] + bins[i + 1]) / 2; d = np.array([math.cos(a_), math.sin(a_)])
    for zz in (z_belt - 0.011, z_belt + 0.021):
        bvs.append([*(bc + d * (rad[i] + 0.0035)), zz])
for i in range(48):
    j = (i + 1) % 48; bfs.append([2 * i, 2 * j, 2 * j + 1, 2 * i + 1])
belt = make_obj("p6_belt", np.array(bvs), bfs, M_BELT)
s_ = belt.modifiers.new("thick", "SOLIDIFY"); s_.thickness = 0.004; s_ = belt.modifiers.new("sub", "SUBSURF"); s_.levels = 1; s_.render_levels = 2
fy = min(v[1] for v in bvs)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, fy - 0.004, z_belt + 0.005))
bk = bpy.context.object; bk.name = "p6_buckle"; bk.scale = (0.036, 0.005, 0.028); bk.data.materials.append(mat("buckle", (0.55, 0.5, 0.42), 0.3, Metallic=1.0))
bev = bk.modifiers.new("bev", "BEVEL"); bev.width = 0.002; bev.segments = 3

# shoes: a procedural last per foot (superelliptic sections sized from the foot's own outline: no toes), a welted
#        sole following the same outline, a slightly longer toe; dark brown derby leather
def shoe_for(side):
    F = co[(vmat == 6) & (np.sign(co[:, 0]) == side) & (co[:, 2] < z_ank + 0.01)]
    yt, yh = F[:, 1].min(), F[:, 1].max(); NS, NR = 44, 40
    ys = np.linspace(yh + 0.006, yt - 0.016, NS)                                  # heel → toe (toe 1.6 cm longer)
    prof = []
    for y in ys:
        m = np.abs(F[:, 1] - np.clip(y, yt + 0.004, yh - 0.004)) < 0.012
        prof.append([F[m, 0].min(), F[m, 0].max(), F[m, 2].max()])
    prof = np.array(prof)
    for k in range(10): prof = np.vstack([prof[:1], (prof[:-2] + 2 * prof[1:-1] + prof[2:]) / 4, prof[-1:]])
    s_ = np.linspace(0, 1, NS)
    endw = np.sqrt(np.clip(np.minimum(s_ / 0.10, (1 - s_) / 0.16), 0, 1)) * 0.9 + 0.1   # rounded heel and toe
    cx = (prof[:, 0] + prof[:, 1]) / 2; a_ = ((prof[:, 1] - prof[:, 0]) / 2 + 0.007) * endw
    zb = 0.022; zt = np.minimum(np.maximum(prof[:, 2] + 0.008, zb + 0.03), 0.085)
    zt = zb + (zt - zb) * (0.35 + 0.65 * np.sqrt(np.clip((1 - s_) / 0.22, 0, 1)))       # the toe box lowers to the tip
    zt = np.where(s_ < 0.4, 0.078, np.minimum(zt, 0.078))                                  # heel counter; instep below the hem
    V, Fc = [], []
    for i in range(NS):
        for j in range(NR):
            th = 2 * math.pi * j / NR; c, sn = math.cos(th), math.sin(th)
            n_ = 2.6 if sn > 0 else 6.0                                                    # rounder top, flat bottom
            x = cx[i] + a_[i] * np.sign(c) * abs(c) ** (2 / n_)
            zc = (zt[i] + zb) / 2; hz = (zt[i] - zb) / 2 * (endw[i] ** 0.5)
            V.append([x, ys[i], zc + hz * np.sign(sn) * abs(sn) ** (2 / n_)])
    for i in range(NS - 1):
        for j in range(NR):
            Fc.append([i * NR + j, i * NR + (j + 1) % NR, (i + 1) * NR + (j + 1) % NR, (i + 1) * NR + j])
    V.append([cx[0], ys[0] + 0.002, (zt[0] + zb) / 2]); V.append([cx[-1], ys[-1] - 0.002, (zt[-1] + zb) / 2])
    for j in range(NR):
        Fc.append([len(V) - 2, (j + 1) % NR, j]); Fc.append([len(V) - 1, (NS - 1) * NR + j, (NS - 1) * NR + (j + 1) % NR])
    o = make_obj(f"p6_shoe_{'L' if side > 0 else 'R'}", np.array(V), Fc, M_SHOE)
    m_ = o.modifiers.new("sub", "SUBSURF"); m_.levels = 1; m_.render_levels = 2
    # sole: the outline at the widest section, extruded 0 → zb
    out = [[cx[i] - a_[i] - 0.003, ys[i]] for i in range(NS)] + [[cx[i] + a_[i] + 0.003, ys[i]] for i in reversed(range(NS))]
    sv_ = [[x, y, 0.0] for x, y in out] + [[x, y, zb + 0.001] for x, y in out]; n2 = len(out)
    sf = [[i, (i + 1) % n2, n2 + (i + 1) % n2, n2 + i] for i in range(n2)] + [list(range(n2))[::-1], list(range(n2, 2 * n2))]
    so = make_obj(f"p6_sole_{'L' if side > 0 else 'R'}", np.array(sv_), sf, M_SOLE)
    bv_ = so.modifiers.new("bev", "BEVEL"); bv_.width = 0.002; bv_.segments = 2; bv_.limit_method = "ANGLE"
    return o


shoes = [shoe_for(1), shoe_for(-1)]

# ── 5. mesh hair: short, side-parted, flow-aligned clumps (geodesic feathering to a natural hairline) ──────────────
import heapq  # noqa: E402
M_HAIR = bpy.data.materials.new("hair"); M_HAIR.use_nodes = True
selh = (scalp > 0.2) & head_v
zb_ = J["brow.T.L.001_head"][2]
for _ in range(3):        # a fuller, lower hairline at the front and temples (dilate 3 rings, then erode 1: a smooth line)
    grow = selh.copy()
    for i in np.where(selh)[0]:
        for j in nbr[i]:
            if head_v[j] and co[j, 1] < 0.05 and co[j, 2] > zb_ + 0.03 and abs(co[j, 0]) < 0.075: grow[j] = True
    selh = grow
shrink = selh.copy()
for i in np.where(selh)[0]:
    if any(not selh[j] for j in nbr[i]) and co[i, 1] < 0.05: shrink[i] = False
selh = shrink
crown = J["spine.006_tail"]; fh = J["forehead.L_head"]
hv, hf, horig = sub_mesh(selh)
hair = make_obj("p6_hair", hv + vnorm[horig] * 0.0008, hf, M_HAIR); subdivide(hair, 3)
hv, hnb, hbnd = arrays(hair); hn = vnormals(hair)
dist = np.full(len(hv), 9.0); pq = [(0.0, i) for i in np.where(hbnd)[0]]
for _, i in pq: dist[i] = 0
heapq.heapify(pq)
while pq:                                   # geodesic distance from the hairline (Dijkstra on mesh edges)
    d0, i = heapq.heappop(pq)
    if d0 > dist[i]: continue
    for j in hnb[i]:
        nd = d0 + float(np.linalg.norm(hv[i] - hv[j]))
        if nd < dist[j]: dist[j] = nd; heapq.heappush(pq, (nd, j))
top = sstep(hv[:, 2], fh[2] - 0.035, fh[2] + 0.045)
front = sstep(-hv[:, 1], -0.03, 0.06)
side_part = sstep(-(hv[:, 0] - 0.035), -0.04, 0.06)                     # more volume on the side the hair sweeps to
T = (0.003 + 0.010 * top + 0.006 * top * front + 0.003 * top * side_part)
T *= sstep(dist, 0.0, 0.03)   # tapered hairline; a lifted front
hv = hv + hn * (T + 0.0008)[:, None]
for _ in range(2): hv = laplace(hv, ~hbnd, 6, 0.5, hnb); hv = push_out(hv, 0.0009)
setco(hair, hv); hn = vnormals(hair)
part_x = 0.035
lat = hv[:, 0] - part_x
u_top = lat * (1 + 0.5 * sstep(-hv[:, 1], -0.02, 0.08)) + 0.22 * (hv[:, 1] - crown[1])
ang = np.arctan2(hv[:, 1] - crown[1], hv[:, 0])
u_side = ang * 0.085 + 0.2 * (hv[:, 2] - crown[2])
wt = sstep(hv[:, 2], fh[2] - 0.02, fh[2] + 0.04)
u = wt * u_top + (1 - wt) * u_side
rng = np.random.default_rng(7); ph = np.zeros(len(hv))
for k in range(5): ph += 0.55 * np.sin(hv @ rng.normal(size=3) * (25 + 10 * k) + rng.uniform(0, 6.3))
clump = 0.5 + 0.5 * np.cos(2 * math.pi * u / 0.02 + 1.6 * ph)
strand = 0.5 + 0.5 * np.cos(2 * math.pi * u / 0.0045 + 2.3 * ph)
fine = 0.5 + 0.5 * np.cos(2 * math.pi * u / 0.0019 + 3.1 * ph)
fade = sstep(dist, 0.002, 0.018)
gro = -(0.0013 * clump ** 2 + 0.0005 * strand + 0.0002 * fine) * fade
partline = np.clip(1 - np.abs(lat) / 0.0035, 0, 1) * wt * sstep(-(hv[:, 1] - crown[1]), -0.02, 0.06)
gro -= 0.0025 * partline
hv += hn * gro[:, None]; setco(hair, hv)
s_ = hair.modifiers.new("thick", "SOLIDIFY"); s_.thickness = 0.0015; s_.offset = -1
nt = M_HAIR.node_tree; b = nt.nodes["Principled BSDF"]
geo = nt.nodes.new("ShaderNodeNewGeometry"); ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.44; ramp.color_ramp.elements[0].color = (0.016, 0.010, 0.007, 1)
ramp.color_ramp.elements[1].position = 0.56; ramp.color_ramp.elements[1].color = (0.075, 0.048, 0.033, 1)
nt.links.new(geo.outputs["Pointiness"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
b.inputs["Roughness"].default_value = 0.45; b.inputs["Specular IOR Level"].default_value = 0.4
b.inputs["Anisotropic"].default_value = 0.5

# brows: sculpted mesh brows on the skin (tapered, restrained, strand grooves), not particles and not cartoon blocks
bvs, bfs = [], []
for side in ("L", "R"):
    pts = np.array([J[f"brow.T.{side}.003_tail"], J[f"brow.T.{side}.003_head"], J[f"brow.T.{side}.001_tail"], J[f"brow.T.{side}.001_head"], J[f"brow.T.{side}_head"]])
    pts = pts[1:]                                                            # start just off the midline (no unibrow)
    xs = np.linspace(pts[0, 0], pts[-1, 0], 8); fy = np.polyfit(pts[:, 0], pts[:, 1], 2); fz = np.polyfit(pts[:, 0], pts[:, 2], 2)
    zl = np.interp(xs, [xs[0], xs[-1]], [np.polyval(fz, xs[0]), np.polyval(fz, xs[-1])])
    pts = np.stack([xs, np.polyval(fy, xs), 0.6 * np.polyval(fz, xs) + 0.4 * zl], 1)   # a softened arch
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    NA, NC = 36, 7; base0 = len(bvs)
    for i in range(NA):
        t = i / (NA - 1); p = np.array([np.interp(t * L[-1], L, pts[:, k]) for k in range(3)])
        p[2] -= 0.0030 + 0.0012 * math.sin(math.pi * t) + 0.002 * t            # low, nearly straight: a man's brow
        hw = 0.0034 * (1 - t) ** 0.6 + 0.0010                                # full at the head, fine at the tail
        loc, n, _, _ = body_bvh.find_nearest(Vector(p)); n = np.array(n); loc = np.array(loc)
        tang = pts[min(int(np.searchsorted(L, t * L[-1])), len(pts) - 1)] - pts[max(int(np.searchsorted(L, t * L[-1])) - 1, 0)]
        tang = tang / (np.linalg.norm(tang) + 1e-9); up = np.cross(n, tang); up /= np.linalg.norm(up) + 1e-9
        if up[2] < 0: up = -up
        for j in range(NC):
            u = j / (NC - 1) * 2 - 1; q = loc + up * u * hw
            l2, n2, _, _ = body_bvh.find_nearest(Vector(q)); h = 0.0007 * (1 - u * u) * (1 - 0.6 * t) + 0.0002
            bvs.append(list(np.array(l2) + np.array(n2) * h))
    for i in range(NA - 1):
        for j in range(NC - 1):
            a0 = base0 + i * NC + j; bfs.append([a0, a0 + 1, a0 + NC + 1, a0 + NC])
brows = make_obj("p6_brows", np.array(bvs), bfs, M_HAIR)
s_ = brows.modifiers.new("sub", "SUBSURF"); s_.levels = 1; s_.render_levels = 2

# ── 6. body materials: painted skin, eyes, mouth ────────────────────────────────────────────────────────────────────
def skin_material(variant):
    m = bpy.data.materials.new("skin"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    base = (0.34, 0.19, 0.12); warm = (0.40, 0.16, 0.11); stub = (0.24, 0.19, 0.17); hairc = (0.05, 0.032, 0.024); lip = (0.42, 0.20, 0.16)
    A = nt.nodes.new("ShaderNodeAttribute"); A.attribute_name = "paint_a"; Bn = nt.nodes.new("ShaderNodeAttribute"); Bn.attribute_name = "paint_b"
    sa = nt.nodes.new("ShaderNodeSeparateColor"); sb = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(A.outputs["Color"], sa.inputs[0]); nt.links.new(Bn.outputs["Color"], sb.inputs[0])
    def mix(c_in, col, fac_socket, k):
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = k
        nt.links.new(fac_socket, mul.inputs[0]); nt.links.new(mul.outputs[0], mx.inputs["Factor"])
        if isinstance(c_in, tuple): mx.inputs["A"].default_value = (*c_in, 1)
        else: nt.links.new(c_in, mx.inputs["A"])
        mx.inputs["B"].default_value = (*col, 1); return mx.outputs["Result"]
    k = {"A": 1.0, "B": 1.15, "C": 1.3}.get(variant, 1.0)
    c = mix(base, warm, sb.outputs[2], 0.45 * k)          # warm cheeks, nose, ears
    c = mix(c, lip, sa.outputs[2], 0.55)                  # lips (the base's own lip mask)
    c = mix(c, stub, sa.outputs[1], 0.34 * k)             # shaved beard shadow
    c = mix(c, (0.38, 0.30, 0.26), sa.outputs[0], 0.35)  # scalp under the hair
    c = mix(c, hairc, sb.outputs[0], 0.85)                # brows (painted, restrained)
    c = mix(c, (0.09, 0.06, 0.05), sb.outputs[1], 0.7)    # lash line
    nt.links.new(c, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.52; b.inputs["Subsurface Weight"].default_value = 0.12
    b.inputs["Subsurface Radius"].default_value = (0.9, 0.45, 0.3); b.inputs["Subsurface Scale"].default_value = 0.01
    b.inputs["Specular IOR Level"].default_value = 0.35
    return m


M_SKIN = skin_material(VAR)
M_SCLERA = mat("sclera", (0.78, 0.74, 0.70), 0.3)
M_IRIS = mat("iris", (0.16, 0.09, 0.05), 0.35); M_PUPIL = mat("pupil", (0.005, 0.005, 0.005), 0.3)
M_CORNEA = bpy.data.materials.new("cornea"); M_CORNEA.use_nodes = True; _nt = M_CORNEA.node_tree
_nt.nodes.remove(_nt.nodes["Principled BSDF"]); _mx = _nt.nodes.new("ShaderNodeMixShader"); _fr = _nt.nodes.new("ShaderNodeFresnel"); _fr.inputs[0].default_value = 1.45
_tr = _nt.nodes.new("ShaderNodeBsdfTransparent"); _gl = _nt.nodes.new("ShaderNodeBsdfGlossy"); _gl.inputs["Roughness"].default_value = 0.03
_nt.links.new(_fr.outputs[0], _mx.inputs[0]); _nt.links.new(_tr.outputs[0], _mx.inputs[1]); _nt.links.new(_gl.outputs[0], _mx.inputs[2])
_nt.links.new(_mx.outputs[0], _nt.nodes["Material Output"].inputs["Surface"])
M_MOUTH = mat("mouth", (0.18, 0.06, 0.06), 0.5); M_TEETH = mat("teeth", (0.75, 0.72, 0.64), 0.35)
for m_ in (M_SKIN, M_SCLERA, M_IRIS, M_PUPIL, M_MOUTH, M_TEETH, M_CORNEA): me.materials.append(m_)
remap = {0: 1, 1: 2, 2: 3, 3: 0, 4: 0, 5: 0, 6: 0, 7: 4, 8: 4, 9: 4, 10: 5}
iris_c = {s: co[(vmat == 1) & (np.sign(co[:, 0]) == s)].mean(0) for s in (1, -1)}
iris_r = {s: np.linalg.norm(co[(vmat == 1) & (np.sign(co[:, 0]) == s)][:, [0, 2]] - iris_c[s][[0, 2]], axis=1).max() for s in (1, -1)}
new_idx = []
for p, m in zip(me.polygons, mat_idx):
    k = remap[int(m)]
    if m == 0:      # the cornea: sclera faces in front of the iris
        c = np.array(p.center); s = 1 if c[0] > 0 else -1
        if np.linalg.norm(c[[0, 2]] - iris_c[s][[0, 2]]) < iris_r[s] * 1.05 and c[1] < iris_c[s][1]: k = 6
    new_idx.append(k)
me.polygons.foreach_set("material_index", new_idx)
for p in me.polygons: p.use_smooth = True
sm = body.modifiers.new("sub", "SUBSURF"); sm.levels = 1; sm.render_levels = 2
for o in (shirt, trous, hair):
    s_ = o.modifiers.new("sub", "SUBSURF"); s_.levels = 0; s_.render_levels = 1

# ── measurements on the posed, unclothed body (crown/chin from the skin, as measure_props) ───────────────────────────
# definitions identical to convert/measure_props.py (P3–P5 numbers are comparable): crown = top of the head skin; chin =
# lowest front-midline point within 8 cm of the nose-tip plane; biacromial = distance between the upper-arm joints;
# head width = cranium between nose level and 7 cm above, behind the nose, ears dropped (92nd percentile); eye width =
# horizontal extent of one eye opening (lid corners)
skin = ~EYE & ~MOUTH_IN
H = co[skin & head_v]; crown_z = H[:, 2].max()
mid = H[np.abs(H[:, 0]) < .006]; face = mid[mid[:, 2] > crown_z - .32]; nose = face[np.argmin(face[:, 1])]
frt = mid[(mid[:, 2] < nose[2] - .03) & (mid[:, 2] > nose[2] - .15) & (mid[:, 1] < nose[1] + .08)]; chin_z = frt[:, 2].min()
hh = crown_z - chin_z; height = crown_z - co[:, 2].min()
cr = H[(H[:, 2] > nose[2]) & (H[:, 2] < nose[2] + .07) & (H[:, 1] > nose[1] + .04)]
cr = cr[np.abs(cr[:, 0]) < np.percentile(np.abs(cr[:, 0]), 92)]; head_w = cr[:, 0].max() - cr[:, 0].min()
biac = abs(J["upper_arm.L_head"][0] - J["upper_arm.R_head"][0])
lidL = [J[k][0] for k in J if k.startswith("lid.") and ".L" in k]; eye_w = max(lidL) - min(lidL)
res = {"variant": VAR, "morphs": morphs, "smooth": P["smooth"], "accent": P["accent"], "head_scale": P["head"],
       "height_m": round(float(height), 4), "head_height_m": round(float(hh), 4), "heads_tall": round(float(height / hh), 2),
       "biacromial_m": round(float(biac), 4), "shoulder_width_hh": round(float(biac / hh), 2),
       "head_width_m": round(float(head_w), 4), "eye_width_m": round(float(eye_w), 4), "eye_w_over_head_w": round(float(eye_w / head_w), 3),
       "frame": {"crown_z": float(crown_z), "chin_z": float(chin_z), "eye": [float(x) for x in (co[EYE].mean(0))],
                 "head_y": float(co[skin & head_v, 1].mean())}}
bpy.context.scene.render.engine = "CYCLES"
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(OUT))
with open(os.path.splitext(OUT)[0] + ".json", "w") as f: json.dump(res, f, indent=1)
print("P6RESULT", json.dumps(res))
