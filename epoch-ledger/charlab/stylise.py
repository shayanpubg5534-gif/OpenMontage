"""Character lab (M2.3c): bespoke character geometry, procedural and headless (Blender bpy, no manual modelling).

Called by build_dressed.py when a spec has a "design" section; specs without one build exactly as before. Steps:

  face_morph   Face planes: a weighted Taubin smoothing of the face skin (volume-preserving), protecting the eyelids,
               lips and ears, so the profile line and the shadow shapes are cleaner, as in a drawing. It is added as one
               shape key on top of the designed MakeHuman face targets (listed in the spec's preset), then every proxy
               (eyes, teeth, clothes) is refitted to the new face before the targets are baked.
  hair         Original hair geometry: a shell grown from the scalp over a designed hairline, thickness from a designed
               volume map, sculpted into clumps that follow a designed flow (grooves converge at a part, a crown or a
               ponytail tie), with lock tips along the hairline. Optional ponytail: tapered locks that hang clear of
               the body and clothes, and a tie. Replaces the stock alpha-card hair.
  brows        Designed brows: a raised, tapered band drawn along a designed curve on the brow ridge (per character:
               thickness, arch, tail). Replaces the stock alpha-card brows.
  lash_lines   The upper lid line an illustrator draws: a solid band along the lid margin (from MakeHuman's eyelash
               helper geometry), thicker toward the outer corner with a short flick, plus a lighter partial lower line.
               Replaces the stock alpha-card lashes.
  attach       Every generated mesh gets skin weights and the expression shape keys from the nearest body vertices,
               so blinks close the lash line and brow expressions carry the brows; the rig is unchanged.
Lab code: no production asset is touched.
"""
from __future__ import annotations

import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree


# ── helpers ───────────────────────────────────────────────────────────────────────────────────────────────────────
def members(obj, name, thr=.5):
    gi = obj.vertex_groups.get(name)
    if gi is None:
        return []
    g = gi.index
    return [v.index for v in obj.data.vertices if any(x.group == g and x.weight > thr for x in v.groups)]


def weight_of(obj, name):
    gi = obj.vertex_groups.get(name)
    out = [0.0] * len(obj.data.vertices)
    if gi is None:
        return out
    for v in obj.data.vertices:
        for x in v.groups:
            if x.group == gi.index:
                out[v.index] = x.weight
    return out


def mixed_coords(body):
    """Vertex positions with every shape key mixed in (the shape MPFB fits proxies to)."""
    if not body.data.shape_keys:
        return [v.co.copy() for v in body.data.vertices]
    k = body.shape_key_add(name="_mix_probe", from_mix=True)
    co = [d.co.copy() for d in k.data]
    body.shape_key_remove(k)
    return co


def centre(co, idx):
    return sum((co[i] for i in idx), Vector()) / max(1, len(idx))


def body_bvh(body, co, keep):
    keep = set(keep)
    polys = [list(p.vertices) for p in body.data.polygons if all(i in keep for i in p.vertices)]
    return BVHTree.FromPolygons(co, polys, all_triangles=False, epsilon=0.0)


def lerp_table(table, x):
    """Piecewise-linear interpolation in a sorted [[x, y], ...] table (clamped)."""
    if x <= table[0][0]:
        return table[0][1]
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0 or 1)
    return table[-1][1]


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a or 1e-9)))
    return t * t * (3 - 2 * t)


def hash1(i):
    return (math.sin(i * 127.1 + 311.7) * 43758.5453) % 1.0


def material(name, rgb, rough=.8):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*[(c / 255) ** 2.2 for c in rgb], 1)
    bsdf.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*[(c / 255) ** 2.2 for c in rgb], 1)
    return m


def new_object(name, verts, faces, body, mat, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = body.matrix_world.copy()
    ob.data.materials.append(mat)
    return ob


# ── 1. face planes ────────────────────────────────────────────────────────────────────────────────────────────────
def face_morph(body, cfg, children, ClothesService, LOG):
    """Weighted Taubin smoothing of the face skin, as a shape key, then refit every proxy to the new face."""
    strength, iters = float(cfg.get("strength", .8)), int(cfg.get("iterations", 12))
    co = mixed_coords(body)
    skin = set(members(body, "body"))
    head = weight_of(body, "head")
    eyes = [centre(co, members(body, f"joint-{s}-eye")) for s in "lr"]
    lips, ears = set(members(body, "lips", .1)), set(members(body, "ears", .1))
    mouth = centre(co, members(body, "lips"))
    nbr = {i: [] for i in skin}
    for e in body.data.edges:
        a, b = e.vertices
        if a in skin and b in skin:
            nbr[a].append(b)
            nbr[b].append(a)
    w = {}
    for i in skin:
        if head[i] < .05 or i in ears:
            continue
        p = co[i]
        prot = max(1 - smoothstep(.019, .027, min((p - e).length for e in eyes)),          # eyelids keep their shape
                   1.0 if i in lips else 1 - smoothstep(.022, .034, (p - mouth).length))  # lips keep their line
        w[i] = min(1.0, head[i]) * (1 - prot) * strength
    pos = {i: co[i].copy() for i in skin}
    for it in range(iters * 2):
        f = .5 if it % 2 == 0 else -.53                                                     # Taubin λ / μ
        new = {}
        for i, wi in w.items():
            ns = nbr[i]
            if not ns:
                continue
            avg = sum((pos[j] for j in ns), Vector()) / len(ns)
            new[i] = pos[i] + (avg - pos[i]) * f * wi
        pos.update(new)
    sk = body.shape_key_add(name="m23c_face_planes", from_mix=False)
    basis = body.data.shape_keys.key_blocks[0]
    moved = 0
    for i in w:
        d = pos[i] - co[i]
        if d.length > 1e-6:
            sk.data[i].co = basis.data[i].co + d
            moved += 1
    sk.value = 1.0
    refit = []
    for ch in children:
        if ch is body:
            continue
        try:
            ClothesService.fit_clothes_to_human(ch, body)
            refit.append(ch.name)
        except Exception as ex:  # noqa: BLE001
            refit.append(f"{ch.name}: not refitted ({ex})")
    LOG["face_planes"] = {"strength": strength, "iterations": iters, "vertices_moved": moved, "refitted": refit}


# ── attach generated meshes to the rig and the expressions ────────────────────────────────────────────────────────
def attach(ob, body, rig, pool, k=4, rigid=None):
    """Skin weights and expression shape keys for a generated mesh, from its k nearest body vertices (in `pool`).
    rigid: a bone name to weight the whole mesh to that bone instead (hair: the head)."""
    keys = body.data.shape_keys.key_blocks
    basis = keys[0]
    bones = {b.name for b in rig.data.bones}
    kd = KDTree(len(pool))
    for n, i in enumerate(pool):
        kd.insert(basis.data[i].co, n)
    kd.balance()
    wmap = {}
    for g in body.vertex_groups:
        if g.name in bones:
            wmap[g.index] = g.name
    near = []
    for v in ob.data.vertices:
        hits = kd.find_n(v.co, k)
        ws = [(pool[n], 1.0 / (d + 1e-4)) for _, n, d in hits]
        s = sum(w for _, w in ws)
        near.append([(i, w / s) for i, w in ws])
    groups = {}
    if rigid:
        g = ob.vertex_groups.new(name=rigid)
        g.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
    else:
        for vi, ws in enumerate(near):
            acc = {}
            for i, w in ws:
                for x in body.data.vertices[i].groups:
                    if x.group in wmap:
                        acc[wmap[x.group]] = acc.get(wmap[x.group], 0) + x.weight * w
            tot = sum(acc.values()) or 1
            for name, w in acc.items():
                if w / tot > .01:
                    groups.setdefault(name, []).append((vi, w / tot))
        for name, lst in groups.items():
            g = ob.vertex_groups.new(name=name)
            for vi, w in lst:
                g.add([vi], w, "REPLACE")
    ob.parent = rig
    ob.matrix_parent_inverse = rig.matrix_world.inverted()
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = rig
    made = 0
    for kb in keys[1:]:
        offs = []
        for vi, ws in enumerate(near):
            o = sum(((kb.data[i].co - basis.data[i].co) * w for i, w in ws), Vector())
            offs.append(o)
        if max(o.length for o in offs) < 2e-5:
            continue
        if not ob.data.shape_keys:
            ob.shape_key_add(name="Basis", from_mix=False)
        sk = ob.shape_key_add(name=kb.name, from_mix=False)
        for vi, o in enumerate(offs):
            sk.data[vi].co = ob.data.vertices[vi].co + o
        made += 1
    return made


def remove(obj):
    bpy.data.objects.remove(obj, do_unlink=True)


# ── 2. designed brows ─────────────────────────────────────────────────────────────────────────────────────────────
def catmull(pts, n):
    """Sample a Catmull-Rom curve through pts (lists of floats) at n points."""
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    for s in range(n):
        t = s / (n - 1) * (len(pts) - 1)
        i = min(int(t), len(pts) - 2)
        u = t - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        out.append([.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u ** 3)
                    for a, b, c, d in zip(p0, p1, p2, p3)])
    return out


def ray_front(bvh, x, z, y0=-.5):
    hit = bvh.ray_cast(Vector((x, y0, z)), Vector((0, 1, 0)), 2.0)
    return (hit[0], hit[1]) if hit[0] is not None else (None, None)


def brows(body, rig, cfg, mat):
    """A designed brow per side: control points [x_out, z_up, half_width] (metres, from the eye centre)."""
    basis = body.data.shape_keys.key_blocks[0]
    co = [d.co.copy() for d in basis.data]
    skin = members(body, "body")
    bvh = body_bvh(body, co, skin)
    verts, faces = [], []
    lift, cushion = float(cfg.get("lift", .0005)), float(cfg.get("cushion", .0009))
    n = int(cfg.get("samples", 28))
    for side, s in (("l", 1), ("r", -1)):
        E = centre(co, members(body, f"joint-{side}-eye"))
        pts = catmull(cfg["curve"], n)
        rows = []
        for (xo, zu, hw) in pts:
            P, N = ray_front(bvh, E.x + s * xo, E.z + zu)
            if P is None:
                continue
            up = (Vector((0, 0, 1)) - N * N.z).normalized()
            rows.append((P, N, up, hw))
        base = len(verts)
        for P, N, up, hw in rows:
            verts += [P - up * hw + N * lift, P + N * (lift + cushion * min(1, hw / .0015)), P + up * hw + N * lift]
        for r in range(len(rows) - 1):
            a, b = base + 3 * r, base + 3 * (r + 1)
            q = [(a, b, b + 1, a + 1), (a + 1, b + 1, b + 2, a + 2)]
            faces += [f if s > 0 else f[::-1] for f in q]
    ob = new_object("Human.m23c_brows", verts, faces, body, mat)
    return ob, skin


# ── 3. lash lines ─────────────────────────────────────────────────────────────────────────────────────────────────
def lid_margin(co, helper, E, bins=14):
    """Root row of MakeHuman's eyelash helper fan: per angular bin around the eye, the vertex nearest the eye centre,
    plus the bin's lash direction (root → farthest vertex)."""
    import collections
    byb = collections.defaultdict(list)
    xs = [co[i].x for i in helper]
    lo, hi = min(xs), max(xs)
    for i in helper:
        b = min(bins - 1, int((co[i].x - lo) / (hi - lo + 1e-9) * bins))
        byb[b].append(i)
    out = []
    for b in sorted(byb):
        ids = byb[b]
        root = min(ids, key=lambda i: (co[i] - E).length)
        tip = max(ids, key=lambda i: (co[i] - E).length)
        out.append((root, (co[tip] - co[root]).normalized()))
    return out


def lash_lines(body, rig, cfg, mat_up, mat_low):
    basis = body.data.shape_keys.key_blocks[0]
    co = [d.co.copy() for d in basis.data]
    obs = []
    for which, mat, prof in (("2", mat_up, cfg.get("upper", [[0, .0004], [.5, .0009], [.85, .0016], [1, .0019]])),
                             ("1", mat_low, cfg.get("lower", [[0, 0], [.45, 0], [.7, .00035], [1, .0005]]))):
        verts, faces, pool = [], [], []
        flick = float(cfg.get("flick", .0026)) if which == "2" else 0.0
        for side, s in (("l", 1), ("r", -1)):
            E = centre(co, members(body, f"joint-{side}-eye"))
            helper = members(body, f"helper-{side}-eyelashes-{which}")
            pool += helper
            roots = lid_margin(co, helper, E)
            if s < 0:
                roots = roots[::-1]                                   # inner → outer on both sides
            if (co[roots[0][0]] - Vector((0, co[roots[0][0]].y, co[roots[0][0]].z))).length > \
               (co[roots[-1][0]] - Vector((0, co[roots[-1][0]].y, co[roots[-1][0]].z))).length:
                roots = roots[::-1]
            base = len(verts)
            m = len(roots)
            for k, (ri, d) in enumerate(roots):
                u = k / (m - 1)
                w = lerp_table(prof, u)
                r = (co[ri] - E).normalized()
                lid = (Vector((0, 0, 1 if which == "2" else -1)) - r * r.z).normalized()
                dd = (lid * .65 + d * .35).normalized()                    # mostly along the lid, a little lifted
                P = co[ri] + r * .0003
                verts += [P - dd * .0002, P + dd * max(w, .00005)]
            if flick:                                                  # outer flick: a short tapered wing
                ri, d = roots[-1]
                t = (co[roots[-1][0]] - co[roots[-2][0]]).normalized()
                P = co[ri] + (co[ri] - E).normalized() * .0002
                verts += [P + t * flick * .9 + d * flick * .25, P + t * flick + d * flick * .45]
                m += 1
            for k in range(m - 1):
                a, b = base + 2 * k, base + 2 * (k + 1)
                f = (a, b, b + 1, a + 1)
                faces.append(f if (s > 0) == (which == "2") else f[::-1])
        ob = new_object(f"Human.m23c_lashline_{'upper' if which == '2' else 'lower'}", verts, faces, body, mat)
        obs.append((ob, pool))
    return obs


# ── 4. designed hair ──────────────────────────────────────────────────────────────────────────────────────────────
class HeadFrame:
    def __init__(self, co, skin_head, eye_z):
        pts = [co[i] for i in skin_head if co[i].z > eye_z]
        ys = [p.y for p in pts]
        self.C = Vector((0.0, (min(ys) + max(ys)) / 2, eye_z + .025))

    def sph(self, p):
        d = p - self.C
        az = math.degrees(math.atan2(d.x, -d.y))                    # 0 = front, +90 = the character's left
        el = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
        return az, el, d.normalized()

    def dir(self, az, el):
        a, e = math.radians(az), math.radians(el)
        return Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))


def flow_coord(d, A, B1, B2):
    """(angle around the flow axis A in degrees, angle from A): grooves are lines of constant angle around A."""
    return math.degrees(math.atan2(d.dot(B1), d.dot(B2))), math.degrees(math.acos(max(-1, min(1, d.dot(A)))))


def hair(body, rig, cfg, mat, children, LOG):
    basis = body.data.shape_keys.key_blocks[0]
    co = [d.co.copy() for d in basis.data]
    skin = members(body, "body")
    head_w = weight_of(body, "head")
    ears = set(members(body, "ears", .05))
    eye_z = centre(co, members(body, "joint-l-eye")).z
    H = HeadFrame(co, [i for i in skin if head_w[i] > .5], eye_z)
    hl = cfg["hairline"]                                                  # [[az, el], ...] over -180..180
    vol = cfg.get("volume", {"top": .010, "side": .005, "back": .007})
    bumps = cfg.get("bumps", [])                                          # [{az, el, r, mm}]
    tips = cfg.get("tips", [[-180, 3], [180, 3]])                         # lock-tip length (degrees) along the hairline
    ax = cfg.get("flow_axis", [0, 0])                                     # [az, el] of the flow axis (grooves converge there)
    A = H.dir(*ax)
    B1 = A.cross(Vector((0, 0, 1)) if abs(A.z) < .9 else Vector((1, 0, 0))).normalized()
    B2 = A.cross(B1).normalized()
    clump = float(cfg.get("clump_deg", 11.0))
    groove = float(cfg.get("groove", .45))
    part = cfg.get("part")                                                # [az, el] of a point on the part line (or None)
    if part is not None:
        part = flow_coord(H.dir(*part), A, B1, B2)[0]
    soft = float(cfg.get("edge_soft_deg", 7.0))

    def field(p):
        az, el, d = H.sph(p)
        s, a = flow_coord(d, A, B1, B2)
        j = (s + 360) / clump + .37 * math.sin(s * .05)                  # irregular clump spacing
        idx = math.floor(j)
        u = j - idx
        tip = lerp_table(tips, az) * (1 - abs(2 * u - 1)) ** 1.4 * (.6 + .8 * hash1(idx))
        f = el - (lerp_table(hl, az) - tip)
        return f, az, el, s, a, u, idx

    neck_w = weight_of(body, "neck_01")
    region = [i for i in skin if (head_w[i] > .3 or (neck_w[i] > .3 and co[i].z > H.C.z - .12)) and i not in ears
              and field(co[i])[0] > -max(soft * 1.6, 12.0)]                # wide margin: the cut is made below
    rs = set(region)
    bm = bmesh.new()
    vmap = {}
    for i in region:
        vmap[i] = bm.verts.new(co[i])
    for p in body.data.polygons:
        if all(i in rs for i in p.vertices):
            try:
                bm.faces.new([vmap[i] for i in p.vertices])
            except ValueError:
                pass
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=int(cfg.get("cuts", 3)), use_grid_fill=True)
    bvh = body_bvh(body, co, skin)
    bm.verts.ensure_lookup_table()
    for v in bm.verts:                                                   # back onto the curved scalp
        hit = bvh.find_nearest(v.co)
        if hit[0] is not None:
            v.co = hit[0]
    bm.normal_update()
    F = {v: field(v.co) for v in bm.verts}
    # cut along the designed hairline: drop vertices fully outside; slide boundary ones onto the iso-line
    for v in list(bm.verts):
        if F[v][0] < 0 and all(F[e.other_vert(v)][0] < 0 for e in v.link_edges):
            bm.verts.remove(v)
    bm.verts.ensure_lookup_table()
    slide = {}
    for v in bm.verts:
        f0 = F[v][0]
        if f0 >= 0:
            continue
        acc, n = Vector(), 0
        for e in v.link_edges:
            u = e.other_vert(v)
            f1 = F[u][0]
            if f1 > 0:
                t = f0 / (f0 - f1)
                acc += v.co.lerp(u.co, t)
                n += 1
        if n:
            slide[v] = acc / n
    for v, p in slide.items():
        v.co = p
    bm.normal_update()
    normals = {v: v.normal.copy() for v in bm.verts}
    base_co = {v: v.co.copy() for v in bm.verts}
    edge_t = float(cfg.get("edge_thickness", 0.0))                       # >0: a solid edge with a wall to the scalp
    edge_w = {}
    for v in bm.verts:
        f, az, el, s, a, u, idx = F[v] if v not in slide else field(v.co)
        cov = smoothstep(0, soft, f) ** .7
        if edge_t:
            cov = edge_t + (1 - edge_t) * cov
        edge_w[v] = 1 - smoothstep(0, soft * 2.5, f)
        top = smoothstep(5, 55, el)
        back = smoothstep(100, 160, abs(az))
        t = vol["side"] + (vol["top"] - vol["side"]) * top
        t = t + (vol["back"] - t) * back * (1 - top * .5)
        for b in bumps:
            d = math.hypot((az - b["az"]) * math.cos(math.radians(el)), el - b["el"])
            t += b["mm"] / 1000 * math.exp(-(d / b["r"]) ** 2)
        fade = smoothstep(4, 22, min(a, 180 - a))                         # no grooves where the flow converges
        if not cfg.get("edge_grooves", True):                            # a clean hairline (pulled-back hair)
            fade *= smoothstep(soft, soft * 3.5, f)
        g = 1 - groove * fade * (1 - math.sin(math.pi * u)) ** 2.2
        if part is not None:
            dp = abs(((s - part + 180) % 360) - 180)
            g *= 1 - .75 * (1 - smoothstep(0, 3.5, dp)) * smoothstep(30, 60, el)
        h = .0007 + t * cov * g * (.88 + .24 * hash1(idx + 7))
        v.co = v.co + normals[v] * h
    for _ in range(2):                                                    # remove projection noise, keep the edge
        bmesh.ops.smooth_vert(bm, verts=[v for v in bm.verts if not v.is_boundary], factor=.5,
                              use_axis_x=True, use_axis_y=True, use_axis_z=True)
    if edge_t:                                                            # wall from the hairline down to the scalp
        walls = []
        for e in [e for e in bm.edges if e.is_boundary]:
            f0 = e.link_faces[0]
            lp = next(l for l in f0.loops if l.edge == e)
            a, b = lp.vert, lp.link_loop_next.vert
            walls.append((a, b))
        low = {}
        for a, b in walls:
            for v in (a, b):
                if v not in low:
                    low[v] = bm.verts.new(base_co[v] + normals[v] * .0003)
                    normals[low[v]] = normals[v]
                    edge_w[low[v]] = 0.0
        for a, b in walls:
            bm.faces.new([b, a, low[a], low[b]])
    bm.verts.ensure_lookup_table()
    scalp_n = [normals[v] for v in bm.verts]
    blend = [edge_w.get(v, 1.0) for v in bm.verts]
    zone = cfg.get("zone")                                                # {"rgb", "az": [a0, a1], "el_max"}: e.g. grey temples
    if zone:
        for f in bm.faces:
            c = f.calc_center_median()
            _, az, el, _, _, _, idx = field(c)
            inside = zone["az"][0] <= abs(az) <= zone["az"][1] and el < zone["el_max"] + 7 * (hash1(idx + 3) - .5)
            f.material_index = 1 if inside else 0
    me = bpy.data.meshes.new("Human.m23c_hair")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.update()
    # shading normals: toward the scalp normal along the hairline ramp, so the band edge follows the designed
    # hairline instead of the faces of the steep ramp
    me.normals_split_custom_set_from_vertices([v.normal.lerp(scalp_n[i], blend[i]).normalized() for i, v in enumerate(me.vertices)])
    ob = bpy.data.objects.new("Human.m23c_hair", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = body.matrix_world.copy()
    me.materials.append(mat)
    if zone:
        me.materials.append(material("m23c_hair_zone", zone["rgb"], .6))
    info = {"shell_triangles": sum(len(p.vertices) - 2 for p in me.polygons)}
    obs = [ob]
    if cfg.get("ponytail"):
        pt, n_tri = ponytail(body, co, skin, H, cfg["ponytail"], mat, children, cfg.get("tie_rgb", [40, 30, 30]))
        obs += pt
        info["ponytail_triangles"] = n_tri
    LOG["hair_design"] = info
    return obs


def tube(path, radii, segs, flat=1.0, up=Vector((0, 0, 1))):
    """A tapered tube along `path` (Vectors) with elliptical cross-sections; closed at the tip."""
    verts, faces = [], []
    n = len(path)
    prev = None
    for k, P in enumerate(path):
        T = (path[min(k + 1, n - 1)] - path[max(k - 1, 0)]).normalized()
        side = (prev or T.cross(up)).normalized()
        if side.length < .5:
            side = T.orthogonal().normalized()
        side = (side - T * side.dot(T)).normalized()
        prev = side
        nrm = T.cross(side).normalized()
        r = radii[k]
        for j in range(segs):
            a = 2 * math.pi * j / segs
            verts.append(P + side * math.cos(a) * r + nrm * math.sin(a) * r * flat)
    for k in range(n - 1):
        for j in range(segs):
            a, b = k * segs + j, k * segs + (j + 1) % segs
            faces.append((a, b, b + segs, a + segs))
    tip = len(verts)
    verts.append(path[-1] + (path[-1] - path[-2]).normalized() * radii[-1])
    for j in range(segs):
        a, b = (n - 1) * segs + j, (n - 1) * segs + (j + 1) % segs
        faces.append((a, b, tip))
    return verts, faces


def ponytail(body, co, skin, H, cfg, mat, children, tie_rgb):
    """Tapered locks from a tie at the back of the head, hanging clear of the body and the clothes."""
    dg = bpy.context.evaluated_depsgraph_get()
    vs, ps = list(co), [list(p.vertices) for p in body.data.polygons if all(i in set(skin) for i in p.vertices)]
    for ch in children:                                                   # clothes are obstacles too
        if ch is body or any(k in ch.name for k in ("eyebrow", "eyelash", "high-poly", "low-poly", "teeth", "tongue",
                                                     "short0", "ponytail", "bob0", "long0", "braid", "afro", "m23c_")):
            continue                                                      # only the body and the clothes are obstacles
        ev = ch.evaluated_get(dg)
        me = ev.to_mesh()
        off = len(vs)
        vs += [ch.matrix_world @ v.co for v in me.vertices]
        ps += [[off + i for i in p.vertices] for p in me.polygons]
        ev.to_mesh_clear()
    bvh = BVHTree.FromPolygons(vs, ps, all_triangles=False, epsilon=0.0)
    az, el = cfg.get("tie", [180, -8])
    d = H.dir(az, el)
    hit = bvh.ray_cast(H.C + d * .3, -d, .6)
    T = (hit[0] if hit[0] is not None else H.C + d * .1) + d * float(cfg.get("tie_lift", .012))
    L, n_locks, segs = float(cfg.get("length", .22)), int(cfg.get("locks", 9)), 8
    r0 = float(cfg.get("lock_radius", .0075))
    spread = float(cfg.get("spread", .016))
    clear = float(cfg.get("clearance", .012))
    back = Vector((d.x, d.y, 0)).normalized()
    side = Vector((0, 0, 1)).cross(back).normalized()
    verts, faces = [], []
    samples = 22
    for k in range(n_locks):
        ang = 2 * math.pi * k / n_locks + .4
        o = side * math.cos(ang) * spread * .5 + Vector((0, 0, 1)) * math.sin(ang) * spread * .35
        Lk = L * (.82 + .3 * hash1(k + 3))
        sway = (hash1(k + 11) - .5) * .03
        path = []
        for s in range(samples):
            t = s / (samples - 1)
            P = T + o * (1 + .6 * t) + back * (.025 * math.sin(math.pi * min(1, t * 1.6)) + .012) \
                - Vector((0, 0, 1)) * Lk * t ** 1.05 + side * sway * t * t + back * .02 * t ** 3
            for _ in range(4):                                            # keep the lock outside the body and clothes
                h = bvh.find_nearest(P)
                if h[0] is None:
                    break
                dv = P - h[0]
                inside = dv.dot(h[1]) < 0
                if inside or dv.length < clear:
                    P = h[0] + h[1] * clear
                else:
                    break
            path.append(P)
        radii = [r0 * (.65 + .55 * math.sin(math.pi * min(1, .15 + t * .9)) ** .6) * (1 - t ** 2.2) + .0004
                 for t in (s / (samples - 1) for s in range(samples))]
        v, f = tube(path, radii, segs, flat=.62)
        base = len(verts)
        verts += v
        faces += [tuple(base + i for i in q) for q in f]
    ob = new_object("Human.m23c_hair_ponytail", verts, faces, body, mat)
    tv, tf = tube([T - back * .004, T + back * .006], [spread * .62, spread * .62], 14, flat=.8)
    tie = new_object("Human.m23c_hair_tie", tv, tf, body, material("m23c_hair_tie", tie_rgb, .6))
    return [ob, tie], sum(len(p.vertices) - 2 for p in ob.data.polygons)


# ── 5. skirts that follow the legs (M3) ──────────────────────────────────────────────────────────────────────────
def cloth_follow_legs(body, rig, cfg, children, LOG):
    """MakeHuman skirts are weighted to the pelvis through the skirt helper, so seated thighs push through them.
    Below the hips, blend each listed garment's skin weights toward those of its nearest leg vertices (0 at the hip
    line, full at `depth` metres below it), so the skirt bends with the thighs."""
    names = cfg.get("objects", [])
    depth = float(cfg.get("depth", .16))
    basis = body.data.shape_keys.key_blocks[0] if body.data.shape_keys else None
    co = [d.co.copy() for d in basis.data] if basis else [v.co.copy() for v in body.data.vertices]
    hip = (rig.matrix_world @ rig.data.bones["thigh_l"].head_local).z
    legs = {"thigh_l", "thigh_r", "calf_l", "calf_r", "pelvis"}
    gid = {g.index: g.name for g in body.vertex_groups if g.name in {b.name for b in rig.data.bones}}
    pool = [i for i in members(body, "body") if co[i].z < hip + .03]
    kd = KDTree(len(pool))
    for n, i in enumerate(pool):
        kd.insert(co[i], n)
    kd.balance()
    done = {}
    for ob in children:
        if not any(k in ob.name for k in names):
            continue
        bones = {b.name for b in rig.data.bones}
        vg = {g.index: g.name for g in ob.vertex_groups if g.name in bones}
        changed = 0
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            f = smoothstep(hip + .02, hip - depth, p.z)
            if f <= 0:
                continue
            orig = {vg[x.group]: x.weight for x in v.groups if x.group in vg}
            near = {}
            hits = kd.find_n(p, 6)
            ws = [(pool[n], 1 / (d + 1e-4)) for _, n, d in hits]
            sw = sum(w for _, w in ws)
            for i, w in ws:
                for x in body.data.vertices[i].groups:
                    if x.group in gid and gid[x.group] in legs:
                        near[gid[x.group]] = near.get(gid[x.group], 0) + x.weight * w / sw
            tot_o, tot_n = sum(orig.values()) or 1, sum(near.values()) or 1
            new = {}
            for k in set(orig) | set(near):
                new[k] = (1 - f) * orig.get(k, 0) / tot_o + f * near.get(k, 0) / tot_n
            for k, w in new.items():
                g = ob.vertex_groups.get(k) or ob.vertex_groups.new(name=k)
                g.add([v.index], w, "REPLACE")
            changed += 1
        done[ob.name] = changed
    LOG["cloth_follow_legs"] = done


# ── entry points called from build_dressed.py ─────────────────────────────────────────────────────────────────────
def design_before_bake(body, rig, spec, children, ClothesService, LOG):
    d = spec.get("design") or {}
    if d.get("face_planes"):
        face_morph(body, d["face_planes"], children, ClothesService, LOG)


def design_after_expressions(body, rig, spec, children, LOG):
    """Generate the designed meshes (after the expression keys exist on the body, before masks remove helpers)."""
    d = spec.get("design") or {}
    made = {}
    stock = {c.name: c for c in children}
    if d.get("hair"):
        hcfg = d["hair"]
        mat = material("m23c_hair", hcfg.get("rgb", [52, 40, 34]), .6)
        for ob in hair(body, rig, hcfg, mat, children, LOG):
            made[ob.name] = attach(ob, body, rig, members(body, "body"), rigid="head")
        for n, c in stock.items():
            if any(h in n for h in ("short0", "ponytail", "bob0", "long0", "braid", "afro")):
                remove(c)
    if d.get("brows"):
        bcfg = d["brows"]
        ob, pool = brows(body, rig, bcfg, material("m23c_brows", bcfg.get("rgb", [48, 36, 30])))
        made[ob.name] = attach(ob, body, rig, pool)
        for n, c in stock.items():
            if "eyebrow" in n:
                remove(c)
    if d.get("lash_lines"):
        lcfg = d["lash_lines"]
        for ob, pool in lash_lines(body, rig, lcfg, material("m23c_lashline", lcfg.get("rgb", [30, 22, 22])),
                                   material("m23c_lashline_lower", lcfg.get("lower_rgb", [92, 66, 58]))):
            made[ob.name] = attach(ob, body, rig, pool, k=2)
        for n, c in stock.items():
            if "eyelash" in n:
                remove(c)
    if d.get("cloth_follow_legs"):
        live = [o for o in bpy.data.objects if o.parent == rig and o.type == "MESH"]
        cloth_follow_legs(body, rig, d["cloth_follow_legs"], live, LOG)
    LOG["design_meshes"] = {n: {"expression_keys": k, "vertices": len(bpy.data.objects[n].data.vertices)}
                            for n, k in made.items()}
