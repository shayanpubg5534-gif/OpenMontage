"""Epoch Ledger character rig v3 — natural proportions, detailed faces, hands, clothing, soft shading.

Three-quarter view facing right (flip with scaleX(-1)). 7.5-head figure in a 400×1000 box (feet at y≈990).
Hierarchical joint groups compatible with kit/rig.js naming, so poses can be animated with svgOrigin:
  {p}-upper (hip) › {p}-torso, {p}-head (neck), {p}-uarm-{front|back} (shoulder) › {p}-farm-… (elbow) › {p}-hand-…
  {p}-thigh-{front|back} (hip) › {p}-shin-… (knee) › foot
Static poses are written as rotate() transforms (forward kinematics), so stills need no JavaScript.
Original implementation.
"""
from __future__ import annotations

import math

VIEWBOX = "0 0 400 1000"
ASPECT = 0.4
O = "#1b1410"            # ink
SH = "#2a1420"           # shadow tint (multiplied at low opacity)

# joints (authoring space)
J = dict(neck=(203, 178), sh_f=(246, 222), sh_b=(166, 218), hip_f=(220, 520), hip_b=(186, 516), waist=(203, 470))
L = dict(uarm=168, farm=150, hand=86, thigh=238, shin=228)

SKINS = [("#f1c9a5", "#d9a882", "#ffe4cc"), ("#c98f63", "#a86f48", "#e8b088"), ("#8d5a3b", "#6e4329", "#b07a56"),
         ("#e8b48c", "#c8946e", "#ffd2ae"), ("#5e3a26", "#46291a", "#8a5a3e"), ("#f4d3b5", "#dcb08e", "#fff0de")]
HAIR = ["#1f1712", "#3a2a1e", "#6a4a2a", "#a87a4a", "#d8c09a", "#7a7a7a", "#2a1a2a"]

COSTUMES = {
    #           jacket / top      jacket shade   shirt       tie         trousers     trouser sh   shoes     style
    "suit":    ("#2c3442", "#1c2230", "#eef2f6", "#7a1f2a", "#262c38", "#181c26", "#141416", "suit"),
    "suit_w":  ("#3a2a3a", "#26182a", "#f4eee6", None, "#2a2030", "#1a1420", "#1a1416", "suit"),
    "trader":  (None, None, "#dfe8f2", "#1f3a7a", "#3a3a44", "#24242c", "#1a1414", "shirt"),
    "casual":  ("#4a6a8a", "#34506c", "#e8e2d4", None, "#c9b48a", "#a8946c", "#5a3a22", "polo"),
    "casual2": ("#8a4a3a", "#6a3426", "#f0e6d4", None, "#3a4a6a", "#28344e", "#2a2420", "sweater"),
    "founder": (None, None, "#f4f0e8", None, "#3a3a44", "#26262e", "#2a2018", "shirt_open"),
}


def _limb(x, y, length, w0, w1, bulge=0.12, color="#888", shade=None, ink=O, sw=3.2):
    """Tapered limb hanging straight down from (x, y) with a soft muscle bulge; shading on the back side."""
    b = length * bulge
    path = (f"M{x - w0 / 2:.1f} {y:.1f} C{x - w0 / 2 - b * .35:.1f} {y + length * .35:.1f} {x - w1 / 2 - b * .1:.1f} {y + length * .75:.1f} {x - w1 / 2:.1f} {y + length:.1f} "
            f"L{x + w1 / 2:.1f} {y + length:.1f} C{x + w1 / 2 + b * .2:.1f} {y + length * .7:.1f} {x + w0 / 2 + b * .45:.1f} {y + length * .3:.1f} {x + w0 / 2:.1f} {y:.1f}Z")
    sh = (f'<path d="M{x - w0 / 2:.1f} {y:.1f} C{x - w0 / 2 - b * .35:.1f} {y + length * .35:.1f} {x - w1 / 2 - b * .1:.1f} {y + length * .75:.1f} {x - w1 / 2:.1f} {y + length:.1f} '
          f'L{x - w1 * .1:.1f} {y + length:.1f} C{x - w0 * .15:.1f} {y + length * .6:.1f} {x - w0 * .2:.1f} {y + length * .3:.1f} {x - w0 * .1:.1f} {y:.1f}Z" fill="{shade}" opacity=".85"/>') if shade else ""
    return f'<path d="{path}" fill="{color}" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"/>{sh}'


def _hand(x, y, skin, shade, kind="relaxed", s=1.0):
    """Hand hanging from the wrist at (x, y), fingers pointing down (+y). kinds: relaxed, grip, point, open, phone, fist."""
    k = s
    palm = (f'<path d="M{x - 17 * k:.1f} {y:.1f} C{x - 22 * k:.1f} {y + 22 * k:.1f} {x - 20 * k:.1f} {y + 44 * k:.1f} {x - 12 * k:.1f} {y + 52 * k:.1f} '
            f'L{x + 14 * k:.1f} {y + 52 * k:.1f} C{x + 20 * k:.1f} {y + 40 * k:.1f} {x + 19 * k:.1f} {y + 20 * k:.1f} {x + 15 * k:.1f} {y:.1f}Z" fill="{skin}" stroke="{O}" stroke-width="2.6"/>')
    fingers = ""
    if kind in ("relaxed", "open", "point"):
        spread = 1.4 if kind == "open" else 1.0
        for i, (dx, ln) in enumerate([(-11, 30), (-3, 36), (5, 34), (12, 27)]):
            if kind == "point" and i > 0:
                fingers += f'<path d="M{x + dx * k:.1f} {y + 50 * k:.1f} q{3 * k:.1f} {12 * k:.1f} {8 * k:.1f} {6 * k:.1f}" fill="{skin}" stroke="{O}" stroke-width="2.4"/>'
                continue
            fx = x + dx * k * spread
            curl = 0 if kind != "relaxed" else (i * 2.5)
            fingers += (f'<path d="M{fx - 4 * k:.1f} {y + 48 * k:.1f} L{fx - 5 * k + curl:.1f} {y + (48 + ln) * k:.1f} Q{fx + curl:.1f} {y + (54 + ln) * k:.1f} {fx + 5 * k + curl:.1f} {y + (48 + ln) * k:.1f} '
                        f'L{fx + 5 * k:.1f} {y + 48 * k:.1f}Z" fill="{skin}" stroke="{O}" stroke-width="2.2"/>')
        thumb = f'<path d="M{x + 13 * k:.1f} {y + 14 * k:.1f} C{x + 26 * k:.1f} {y + 22 * k:.1f} {x + 28 * k:.1f} {y + 34 * k:.1f} {x + 22 * k:.1f} {y + 44 * k:.1f} C{x + 18 * k:.1f} {y + 40 * k:.1f} {x + 16 * k:.1f} {y + 30 * k:.1f} {x + 10 * k:.1f} {y + 26 * k:.1f}Z" fill="{skin}" stroke="{O}" stroke-width="2.2"/>'
    else:   # grip / fist / phone: curled knuckles
        fingers = "".join(f'<path d="M{x + (dx - 5) * k:.1f} {y + 46 * k:.1f} q{5 * k:.1f} {16 * k:.1f} {10 * k:.1f} 0" fill="{skin}" stroke="{O}" stroke-width="2.2"/>' for dx in (-10, -2, 6, 13))
        thumb = f'<path d="M{x + 12 * k:.1f} {y + 16 * k:.1f} C{x + 22 * k:.1f} {y + 26 * k:.1f} {x + 18 * k:.1f} {y + 40 * k:.1f} {x + 8 * k:.1f} {y + 44 * k:.1f}" fill="{skin}" stroke="{O}" stroke-width="2.4"/>'
    prop = ""
    if kind == "phone":
        prop = f'<rect x="{x - 12 * k:.1f}" y="{y + 18 * k:.1f}" width="{26 * k:.1f}" height="{58 * k:.1f}" rx="{5 * k:.1f}" fill="#2a2a30" stroke="{O}" stroke-width="2.4"/><rect x="{x - 8 * k:.1f}" y="{y + 26 * k:.1f}" width="{18 * k:.1f}" height="{20 * k:.1f}" fill="#4a7a5a"/>'
    shade_p = f'<path d="M{x - 17 * k:.1f} {y:.1f} C{x - 22 * k:.1f} {y + 22 * k:.1f} {x - 20 * k:.1f} {y + 44 * k:.1f} {x - 12 * k:.1f} {y + 52 * k:.1f} L{x - 4 * k:.1f} {y + 52 * k:.1f} C{x - 10 * k:.1f} {y + 30 * k:.1f} {x - 8 * k:.1f} {y + 12 * k:.1f} {x - 6 * k:.1f} {y:.1f}Z" fill="{shade}" opacity=".7"/>'
    return (prop + palm + shade_p + fingers + thumb) if kind == "phone" else (palm + shade_p + fingers + thumb + prop)


def _face(p, skin, sh, hi, hair, style, expr="neutral", glasses=False, beard=False, female=False):
    """Three-quarter head facing right; centre (203, 98)."""
    cx, cy = 203, 98
    brows = {"neutral": ("M196 74 Q212 68 228 73", "M164 76 Q174 72 184 75"),
             "worried": ("M197 70 Q212 72 228 80", "M164 80 Q174 72 184 70"),
             "raised": ("M196 66 Q212 60 228 66", "M164 70 Q174 64 184 68"),
             "angry": ("M196 78 Q212 76 228 70", "M164 72 Q174 76 184 79")}[expr if expr in ("worried", "raised", "angry") else "neutral"]
    mouth = {"neutral": "M196 136 Q210 140 224 135", "smile": "M194 132 Q210 146 226 131", "worried": "M196 140 Q210 133 224 141",
             "talk": "M196 134 Q210 148 224 134 Q210 140 196 134Z", "grim": "M195 138 L225 137"}.get(expr, "M196 136 Q210 140 224 135")
    mouth_fill = 'fill="#6a2a2a"' if expr == "talk" else 'fill="none"'
    hair_back, hair_front = _hair3(style, hair)
    lash = 2.6 if female else 2.0
    eye = lambda ex, ey, w, h, iris_dx: (
        f'<path d="M{ex - w} {ey} Q{ex} {ey - h} {ex + w} {ey - 1} Q{ex} {ey + h * .7} {ex - w} {ey}Z" fill="#fbf7f2" stroke="{O}" stroke-width="1.6"/>'
        f'<circle cx="{ex + iris_dx}" cy="{ey - .5}" r="{h * .78:.1f}" fill="#5a3a22"/><circle cx="{ex + iris_dx}" cy="{ey - .5}" r="{h * .42:.1f}" fill="#120a06"/>'
        f'<circle cx="{ex + iris_dx + h * .3:.1f}" cy="{ey - h * .4:.1f}" r="{h * .2:.1f}" fill="#fff"/>'
        f'<path class="lid" d="M{ex - w - 1} {ey} Q{ex} {ey - h - 1.5} {ex + w + 1} {ey - 1}" fill="none" stroke="{O}" stroke-width="{lash + 1}" stroke-linecap="round"/>'
        f'<path d="M{ex - w + 2} {ey - h - 4} Q{ex} {ey - h - 7} {ex + w} {ey - h - 3}" fill="none" stroke="{sh}" stroke-width="1.6" opacity=".7"/>'
        f'<path d="M{ex - w + 3} {ey + h * .55:.1f} Q{ex} {ey + h * .9:.1f} {ex + w - 2} {ey + h * .5:.1f}" fill="none" stroke="{sh}" stroke-width="1.4" opacity=".6"/>')
    glass = (f'<rect x="195" y="82" width="36" height="26" rx="8" fill="#dff0ff" fill-opacity=".18" stroke="#1e1a1a" stroke-width="3"/>'
             f'<rect x="160" y="84" width="27" height="24" rx="7" fill="#dff0ff" fill-opacity=".18" stroke="#1e1a1a" stroke-width="3"/><path d="M187 92 L195 91" stroke="#1e1a1a" stroke-width="3"/>') if glasses else ""
    stubble = f'<path d="M168 120 C172 150 194 166 214 160 C230 154 238 138 238 126 C226 146 196 152 176 124Z" fill="{sh}" opacity=".28"/>' if beard else ""
    return f"""<g id="{p}-head">
  {hair_back}
  <path d="M182 150 L184 192 L222 192 L224 150Z" fill="{skin}" stroke="{O}" stroke-width="3"/>
  <path d="M184 160 L223 168 L222 192 L184 190Z" fill="{sh}" opacity=".55"/>
  <path d="M146 92 C144 46 182 22 214 26 C246 30 256 62 254 94 C256 112 250 130 240 146 C230 162 214 170 200 170 C184 170 168 160 160 146 C150 132 147 112 146 92Z" fill="{skin}" stroke="{O}" stroke-width="3.2"/>
  <path d="M150 96 C150 126 160 152 186 166 C168 150 160 128 160 100Z" fill="{sh}" opacity=".45"/>
  <path d="M246 62 C254 84 254 112 244 138" fill="none" stroke="{hi}" stroke-width="5" opacity=".8" stroke-linecap="round"/>
  <ellipse cx="152" cy="104" rx="11" ry="17" fill="{skin}" stroke="{O}" stroke-width="2.8"/><path d="M150 96 Q156 104 150 114" fill="none" stroke="{sh}" stroke-width="2.4"/>
  {stubble}
  <g id="{p}-eyes">{eye(212, 96, 13, 8, 2.5)}{eye(173, 97, 9, 7, 2)}</g>
  <path id="{p}-brows" d="{brows[0]} M{brows[1][1:]}" fill="none" stroke="{hair if style != 'bald' else sh}" stroke-width="{5 if not female else 3.6}" stroke-linecap="round"/>
  <path d="M220 98 C226 110 232 118 234 124 C232 128 226 130 220 128" fill="none" stroke="{O}" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M218 128 Q222 131 226 129" fill="none" stroke="{sh}" stroke-width="2"/>
  <ellipse cx="236" cy="118" rx="7" ry="4" fill="{hi}" opacity=".5"/>
  <ellipse cx="222" cy="120" rx="12" ry="7" fill="#e08a7a" opacity="{.22 if female else .12}"/>
  <path id="{p}-mouth" d="{mouth}" {mouth_fill} stroke="#5a2420" stroke-width="3" stroke-linecap="round"/>
  {'<path d="M198 137 Q210 133 222 137" fill="none" stroke="#b05a5a" stroke-width="3" opacity=".7"/>' if female else ''}
  {glass}
  {hair_front}
 </g>"""


def _hair3(style, c):
    hl = "#ffffff"
    if style == "short":
        back = f'<path d="M150 90 C138 48 170 18 212 20 C248 22 262 50 256 80 C248 62 232 52 206 52 C186 54 168 64 160 92Z" fill="{c}" stroke="{O}" stroke-width="3"/>'
        front = f'<path d="M156 66 C176 40 226 34 252 66 C236 52 210 46 188 54 C176 58 166 64 156 72Z" fill="{c}"/><path d="M178 44 C200 34 226 36 244 50" fill="none" stroke="{hl}" stroke-width="3" opacity=".25"/>'
    elif style == "parted":
        back = f'<path d="M148 96 C136 44 176 14 216 18 C252 22 266 52 258 86 C250 66 236 54 210 54 C188 56 168 66 158 98Z" fill="{c}" stroke="{O}" stroke-width="3"/>'
        front = f'<path d="M160 70 C170 42 210 26 248 48 C252 58 254 66 254 74 C240 56 222 52 206 56 C190 60 174 66 160 76Z" fill="{c}"/><path d="M204 30 C214 40 222 48 238 52" fill="none" stroke="{O}" stroke-width="2" opacity=".6"/><path d="M182 40 C200 30 224 32 240 42" fill="none" stroke="{hl}" stroke-width="3" opacity=".22"/>'
    elif style == "bun":
        back = f'<circle cx="150" cy="58" r="30" fill="{c}" stroke="{O}" stroke-width="3"/><path d="M148 100 C136 46 176 16 216 20 C250 24 264 54 256 86 C246 64 230 52 206 54 C184 56 166 68 158 100Z" fill="{c}" stroke="{O}" stroke-width="3"/>'
        front = f'<path d="M158 70 C176 42 222 36 252 64 C238 54 212 48 190 56 C176 60 166 66 158 76Z" fill="{c}"/><path d="M186 40 C204 32 226 36 240 46" fill="none" stroke="{hl}" stroke-width="3" opacity=".25"/>'
    elif style == "long":
        back = f'<path d="M146 98 C130 40 178 12 218 18 C256 24 270 60 260 110 C266 160 262 200 250 236 C220 248 176 246 150 230 C156 190 150 150 146 98Z" fill="{c}" stroke="{O}" stroke-width="3"/>'
        front = f'<path d="M158 74 C170 42 214 28 252 54 C256 64 258 74 256 86 C244 62 222 54 200 58 C182 62 168 70 158 82Z" fill="{c}"/><path d="M246 70 C254 120 254 170 246 214" fill="none" stroke="{hl}" stroke-width="3" opacity=".2"/>'
    elif style == "curly":
        back = "".join(f'<circle cx="{150 + (i * 23) % 110}" cy="{40 + (i * 17) % 50}" r="{20 + i % 3 * 3}" fill="{c}" stroke="{O}" stroke-width="2.6"/>' for i in range(12))
        front = "".join(f'<circle cx="{164 + i * 18}" cy="{52 - (i % 2) * 6}" r="14" fill="{c}"/>' for i in range(5))
    elif style == "bald":
        back = ""
        front = f'<path d="M160 60 C180 36 230 34 250 60" fill="none" stroke="#ffffff" stroke-width="5" opacity=".25"/>'
    else:  # buzz
        back = f'<path d="M150 90 C140 50 172 24 212 24 C246 26 258 52 254 80 C244 62 228 54 206 54 C186 56 168 66 160 92Z" fill="{c}" opacity=".85" stroke="{O}" stroke-width="2.6"/>'
        front = ""
    return back, front


def _ang(dx, dy):
    """SVG rotation (deg) that turns a limb drawn pointing down (+y) toward direction (dx, dy)."""
    return math.degrees(math.atan2(-dx, dy))


def ik(shoulder, target, l1=None, l2=None, bend=1):
    """Two-bone IK for an arm (or leg): returns (upper_rot, lower_rel_rot) so the wrist reaches `target`.
    bend=+1 puts the elbow below/outside (natural for arms in front), -1 the other way."""
    l1 = l1 or L["uarm"]; l2 = l2 or L["farm"]
    sx, sy = shoulder; tx, ty = target
    dx, dy = tx - sx, ty - sy; d = min(math.hypot(dx, dy), l1 + l2 - 1e-3); d = max(d, abs(l1 - l2) + 1e-3)
    base = math.atan2(dy, dx); a = math.acos((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))
    ua = base + a * bend
    ex, ey = sx + l1 * math.cos(ua), sy + l1 * math.sin(ua)
    th_u = _ang(ex - sx, ey - sy); th_f = _ang(tx - ex, ty - ey)
    return th_u, th_f - th_u


# hand targets in authoring space (wrist position) for IK poses; None = use the angle table
REACH = {
    "phone": {"front": ((250, 176), 1)},
    "worry": {"front": ((238, 96), 1)},
    "type": {"front": ((330, 440), 1), "back": ((304, 446), 1)},
    "carry": {"front": ((300, 400), 1), "back": ((282, 405), 1)},
    "talk": {"front": ((326, 340), 1)},
    "fold": {"front": ((190, 352), 1), "back": ((236, 344), 1)},
}

POSES = {
    #          torso  head   uarm_f farm_f hand_f   uarm_b farm_b hand_b   thigh_f shin_f thigh_b shin_b
    "stand":   (0, 0, -4, -6, "relaxed", 6, -4, "relaxed", 0, 0, 0, 0),
    "walk":    (2, 2, -22, -18, "relaxed", 20, -10, "relaxed", -18, 8, 16, 26),
    "walk_l":  (2, 2, 18, -16, "relaxed", -20, -12, "relaxed", 16, 24, -18, 6),
    "phone":   (-2, -6, -78, -142, "phone", 8, -6, "relaxed", 0, 0, 4, 2),
    "talk":    (-2, -4, -48, -62, "open", 6, -8, "relaxed", 2, 0, -2, 2),
    "point":   (-3, -8, -112, -14, "point", 6, -6, "relaxed", 0, 0, 3, 0),
    "type":    (6, 6, -50, -56, "relaxed", -44, -58, "relaxed", -80, 84, -80, 84),
    "worry":   (8, 10, -150, -128, "open", 10, -6, "relaxed", 0, 0, 2, 2),
    "fold":    (0, 2, -18, -112, "fist", -12, -108, "fist", 0, 0, 0, 0),
    "carry":   (3, 4, -56, -38, "grip", -50, -44, "grip", 0, 0, 0, 0),
}


JOINTS = ("upper", "neck", "uarm-front", "farm-front", "uarm-back", "farm-back", "thigh-front", "shin-front", "thigh-back", "shin-back")


def pose_angles(pose: str) -> dict:
    """Joint angles (deg) of a named pose after IK, keyed by joint id suffix — feeds kit/rig3.js R3.pose()."""
    tor, hd, uf, ff, hf, ub, fb, hb, tf, sf, tb, sb = POSES.get(pose, POSES["stand"])
    for side, (tgt, bend) in REACH.get(pose, {}).items():
        a, b = ik(J["sh_f"] if side == "front" else J["sh_b"], tgt, L["uarm"], L["farm"] - 10, bend)
        if side == "front":
            uf, ff = a, b
        else:
            ub, fb = a, b
    wrap = lambda a: ((a + 180) % 360) - 180      # shortest-arc angles so blends never spin the long way round
    return {k: round(wrap(v), 2) for k, v in zip(JOINTS, (tor, hd, uf, ff, ub, fb, tf, sf, tb, sb))}


def figure_svg(p: str, costume: str = "suit", skin: int = 0, hair: int = 0, style: str = "short", pose: str = "stand",
               expr: str = "neutral", glasses: bool = False, beard: bool = False, female: bool | None = None, inner: bool = False,
               angles: dict | None = None, shadow: bool = True) -> str:
    """Full figure. inner=True returns only the group (for embedding as a scene3d sprite with VIEWBOX).
    angles: explicit joint angles (pose_angles format, e.g. from reach()) overriding the pose table."""
    jk, jks, shirt, tie, tr, trs, shoe, kind = COSTUMES[costume]
    female = costume == "suit_w" if female is None else female
    if female and style == "short":
        style = "bun"
    sk, sks, skh = SKINS[skin % len(SKINS)]
    hc = HAIR[hair % len(HAIR)]
    tor, hd, uf, ff, hf, ub, fb, hb, tf, sf, tb, sb = POSES.get(pose, POSES["stand"])
    for side, (tgt, bend) in REACH.get(pose, {}).items():
        a, b = ik(J["sh_f"] if side == "front" else J["sh_b"], tgt, L["uarm"], L["farm"] - 10, bend)
        if side == "front":
            uf, ff = a, b
        else:
            ub, fb = a, b
    if angles:
        tor, hd, uf, ff, ub, fb, tf, sf, tb, sb = (angles.get(k, v) for k, v in zip(JOINTS, (tor, hd, uf, ff, ub, fb, tf, sf, tb, sb)))
    top, top_s = (jk, jks) if jk else (shirt, "#b8c4d0")
    (nx, ny), (sfx, sfy), (sbx, sby), (hfx, hfy), (hbx, hby) = J["neck"], J["sh_f"], J["sh_b"], J["hip_f"], J["hip_b"]

    def arm(side, ua, fa, hand_kind):
        sx, sy = (sfx, sfy) if side == "front" else (sbx, sby)
        col, scol = (top, top_s) if side == "front" else (top_s, top_s)
        sleeve_end = shirt if jk else sk
        cuff = (f'<rect x="{sx - 15}" y="{sy + L["uarm"] + L["farm"] - 16}" width="30" height="16" rx="4" fill="{shirt}" stroke="{O}" stroke-width="2.4"/>' if jk else "")
        fold = f'<path d="M{sx - 10} {sy + L["uarm"] - 10} q10 8 20 0" fill="none" stroke="{scol}" stroke-width="3" opacity=".8"/>'
        short_sleeve = kind in ("polo",)
        farm_col = sk if short_sleeve or kind == "shirt_open" and side == "front" else col
        farm_sh = sks if farm_col == sk else scol
        return (f'<g id="{p}-uarm-{side}" transform="rotate({ua} {sx} {sy})">'
                + _limb(sx, sy - 6, L["uarm"] + 10, 46, 36, .14, col, scol)
                + fold
                + f'<g id="{p}-farm-{side}" transform="rotate({fa} {sx} {sy + L["uarm"]})">'
                + _limb(sx, sy + L["uarm"] - 8, L["farm"] + 6, 36, 28, .1, farm_col, farm_sh)
                + (f'<path d="M{sx - 17} {sy + L["uarm"] - 4} L{sx + 17} {sy + L["uarm"] - 4}" stroke="{O}" stroke-width="2.4"/>' if short_sleeve else "")
                + cuff
                + f'<g id="{p}-hand-{side}">{_hand(sx, sy + L["uarm"] + L["farm"] - 2, sk, sks, hand_kind, .95)}</g>'
                + "</g></g>")

    def leg(side, ta, sa):
        hx, hy = (hfx, hfy) if side == "front" else (hbx, hby)
        col, scol = (tr, trs) if side == "front" else (trs, trs)
        foot = (f'<path d="M{hx - 18} {hy + L["thigh"] + L["shin"] - 8} L{hx + 20} {hy + L["thigh"] + L["shin"] - 8} C{hx + 52} {hy + L["thigh"] + L["shin"] - 4} {hx + 60} {hy + L["thigh"] + L["shin"] + 12} {hx + 56} {hy + L["thigh"] + L["shin"] + 22} '
                f'L{hx - 20} {hy + L["thigh"] + L["shin"] + 22}Z" fill="{shoe}" stroke="{O}" stroke-width="3"/>'
                f'<path d="M{hx + 6} {hy + L["thigh"] + L["shin"]} C{hx + 30} {hy + L["thigh"] + L["shin"]} {hx + 44} {hy + L["thigh"] + L["shin"] + 4} {hx + 50} {hy + L["thigh"] + L["shin"] + 10}" fill="none" stroke="#ffffff" stroke-width="2.4" opacity=".25"/>')
        crease = f'<path d="M{hx + 4} {hy + 30} L{hx + 6} {hy + L["thigh"] + L["shin"] - 20}" stroke="{scol}" stroke-width="2.4" opacity=".7"/>'
        return (f'<g id="{p}-thigh-{side}" transform="rotate({ta} {hx} {hy})">'
                + _limb(hx, hy - 10, L["thigh"] + 14, 64, 44, .12, col, scol)
                + f'<g id="{p}-shin-{side}" transform="rotate({sa} {hx} {hy + L["thigh"]})">'
                + _limb(hx, hy + L["thigh"] - 6, L["shin"], 44, 36, .1, col, scol) + crease + foot
                + "</g></g>")

    # torso with costume detail
    lapel = ""
    if kind == "suit":
        lapel = (f'<path d="M190 196 L203 262 L212 196Z" fill="{shirt}" stroke="{O}" stroke-width="2.4"/>'
                 + (f'<path d="M199 202 L207 202 L210 226 L204 300 L198 226Z" fill="{tie}" stroke="{O}" stroke-width="2"/>' if tie else "")
                 + f'<path d="M190 196 L203 262 L196 300 L170 210Z" fill="{jks}" stroke="{O}" stroke-width="2.6"/>'
                   f'<path d="M212 196 L203 262 L214 300 L236 210Z" fill="{jk}" stroke="{O}" stroke-width="2.6"/>'
                   f'<circle cx="208" cy="356" r="4.5" fill="#0e0e12"/><circle cx="208" cy="404" r="4.5" fill="#0e0e12"/>'
                   f'<path d="M226 330 L250 326" stroke="{jks}" stroke-width="3"/><path d="M203 300 L208 470" stroke="{jks}" stroke-width="2.4"/>')
    elif kind in ("shirt", "shirt_open"):
        lapel = (f'<path d="M188 194 L203 214 L218 194 L214 186 L203 200 L192 186Z" fill="{shirt}" stroke="{O}" stroke-width="2.4"/>'
                 + (f'<path d="M199 206 L207 206 L211 232 L204 320 L197 232Z" fill="{tie}" stroke="{O}" stroke-width="2"/>' if tie and kind == "shirt" else "")
                 + (f'<path d="M198 214 L203 240 L208 214" fill="{sk}" stroke="{O}" stroke-width="2"/>' if kind == "shirt_open" else "")
                 + f'<path d="M203 222 L205 466" stroke="#b8c4d0" stroke-width="2"/>' + "".join(f'<circle cx="205" cy="{250 + k * 50}" r="3" fill="#a0a8b0"/>' for k in range(4))
                 + f'<path d="M168 300 q20 10 40 2 M222 330 q14 6 26 -2" fill="none" stroke="#b8c4d0" stroke-width="2.4"/>')
    elif kind == "polo":
        lapel = (f'<path d="M188 194 L203 210 L218 194 L222 204 L203 222 L184 204Z" fill="{jks}" stroke="{O}" stroke-width="2.4"/>'
                 f'<path d="M203 212 L203 252" stroke="{O}" stroke-width="2"/><circle cx="203" cy="232" r="3" fill="#e8e2d4"/>')
    else:  # sweater
        lapel = (f'<path d="M184 194 Q203 222 222 194" fill="none" stroke="{jks}" stroke-width="7"/><path d="M190 196 L203 212 L216 196Z" fill="{shirt}"/>'
                 + "".join(f'<path d="M{176 + k * 10} 440 V470" stroke="{jks}" stroke-width="2"/>' for k in range(6)))
    torso_path = ("M168 200 C188 188 222 188 244 202 C256 230 258 280 252 330 C250 380 246 430 244 474 C226 484 186 486 170 476 "
                  "C166 430 162 380 160 330 C156 280 158 230 168 200Z")
    hips = (f'<path d="M168 466 C186 476 226 476 246 466 L250 528 C232 540 182 540 160 528Z" fill="{tr}" stroke="{O}" stroke-width="3"/>'
            f'<path d="M168 466 C186 476 226 476 246 466 L246 478 C226 488 186 488 168 478Z" fill="#2a2420"/>'
            f'<rect x="200" y="468" width="16" height="12" rx="2" fill="#b8a070"/>')
    torso = (f'<g id="{p}-torso"><path d="{torso_path}" fill="{top}" stroke="{O}" stroke-width="3.2"/>'
             f'<path d="M168 200 C160 240 158 300 162 360 C164 410 166 450 170 476 C178 478 184 478 190 478 C182 420 180 330 186 230Z" fill="{top_s}" opacity=".8"/>'
             f'<path d="M238 214 C248 260 250 320 244 400" fill="none" stroke="#ffffff" stroke-width="4" opacity=".18" stroke-linecap="round"/>{lapel}</g>')
    body = (arm("back", ub, fb, hb) + leg("back", tb, sb) + leg("front", tf, sf)
            + f'<g id="{p}-upper" transform="rotate({tor} {J["waist"][0]} {J["waist"][1]})">{hips}{torso}'
            + f'<g id="{p}-neck" transform="rotate({hd} {nx} {ny})">{_face(p, sk, sks, skh, hc, style, expr, glasses, beard, female)}</g>'
            + arm("front", uf, ff, hf) + "</g>")
    shadow_svg = '<ellipse cx="210" cy="994" rx="120" ry="12" fill="#000" opacity=".25"/>' if shadow else ""
    g = f'<g class="rig3" id="{p}">{shadow_svg}{body}</g>'
    if inner:
        return g
    return f'<svg viewBox="{VIEWBOX}" xmlns="http://www.w3.org/2000/svg" overflow="visible">{g}</svg>'


def portrait_svg(p: str, costume: str = "founder", skin: int = 0, hair: int = 0, style: str = "short", expr: str = "worried",
                 glasses: bool = False, beard: bool = False, hand: str | None = "phone", rim: str = "#7cc8ff") -> str:
    """Close-up: head, shoulders and one hand, drawn at portrait scale (viewBox 0 0 400 420).
    rim = coloured rim light (screen glow) on the face's far side."""
    jk, jks, shirt, tie, tr, trs, shoe, kind = COSTUMES[costume]
    sk, sks, skh = SKINS[skin % len(SKINS)]
    hc = HAIR[hair % len(HAIR)]
    top, top_s = (jk, jks) if jk else (shirt, "#b8c4d0")
    neck = f'<path d="M180 210 L182 262 L226 262 L228 210Z" fill="{sk}" stroke="{O}" stroke-width="3"/><path d="M182 222 L227 236 L226 262 L182 258Z" fill="{sks}" opacity=".6"/>'
    shoulders = (neck
                 + f'<path d="M24 420 C30 360 60 316 118 296 C146 286 168 268 182 252 L226 252 C240 268 262 286 290 296 C348 316 378 360 384 420Z" fill="{top}" stroke="{O}" stroke-width="3.4"/>'
                 + f'<path d="M24 420 C30 360 60 316 118 296 C146 286 168 268 182 252 L190 256 C170 290 140 330 120 420Z" fill="{top_s}" opacity=".9"/>'
                 + f'<path d="M150 300 C160 330 166 370 168 420 M262 300 C254 330 250 370 248 420" fill="none" stroke="{top_s}" stroke-width="3" opacity=".8"/>'
                 + f'<path d="M180 250 L204 290 L228 250 L236 262 L204 312 L172 262Z" fill="{shirt}" stroke="{O}" stroke-width="2.8"/>'
                 + (f'<path d="M193 262 L204 292 L215 262Z" fill="{sk}" stroke="{O}" stroke-width="2.2"/>' if kind == "shirt_open" else "")
                 + f'<path d="M204 312 L204 420" stroke="#b8c4d0" stroke-width="2.4"/><circle cx="204" cy="350" r="3.4" fill="#a0a8b0"/><circle cx="204" cy="395" r="3.4" fill="#a0a8b0"/>'
                 + f'<path d="M318 312 C350 340 368 380 372 420" fill="none" stroke="{rim}" stroke-width="5" opacity=".55"/>')
    head = _face(p, sk, sks, skh, hc, style, expr, glasses, beard, False).replace(f'id="{p}-head"', f'id="{p}-head" transform="translate(0 70)"')
    rim_face = f'<path d="M248 132 C258 160 256 196 242 222" transform="translate(0 0)" fill="none" stroke="{rim}" stroke-width="6" opacity=".6" stroke-linecap="round"/>'
    hand_svg = ""
    if hand == "phone":
        hand_svg = f'<g transform="translate(140 236) rotate(176)">{_hand(0, 0, sk, sks, "phone", 1.0)}</g>'
    elif hand == "forehead":
        hand_svg = f'<g transform="translate(262 110) rotate(160)">{_hand(0, 0, sk, sks, "open", 1.05)}</g>'
    return (f'<svg viewBox="0 0 400 420" xmlns="http://www.w3.org/2000/svg" overflow="visible"><g class="rig3" id="{p}">'
            f'{shoulders}{head}{rim_face}{hand_svg}</g></svg>')


# ── close-up head (expressive, modelled) ────────────────────────────────────────────────────────
CLOSEUP_VIEWBOX = "0 0 800 900"
_CU_BROWS = {  # (near brow, far brow) — three-quarter facing right; inner ends are on the right
    "neutral": ("M398 300 Q446 284 498 290", "M538 290 Q562 286 586 296"),
    "worried": ("M398 312 Q448 300 500 280", "M536 278 Q560 288 584 304"),
    "angry":   ("M398 290 Q446 292 500 306", "M536 306 Q560 296 584 288"),
    "raised":  ("M398 290 Q446 268 498 276", "M538 276 Q562 270 586 282"),
}
_CU_MOUTH = {
    "neutral": "M478 496 Q520 500 560 492", "worried": "M476 502 Q518 484 560 496", "grim": "M478 496 L560 494",
    "smile": "M474 486 Q518 516 562 484", "talk": "M478 492 Q520 528 560 490 Q520 504 478 492Z",
}


def closeup_svg(p: str, costume: str = "founder", skin: int = 0, hair: int = 2, style: str = "parted", expr: str = "worried",
                hand: str | None = "phone", key: str = "#ff7a66", key_side: str = "right", stubble: bool = True, tired: bool = True) -> str:
    """Expressive close-up head and shoulders, modelled for screen sizes of 600-1100 px tall (viewBox 0 0 800 900).
    Three-quarter view facing screen-right. key = colour of the key light (e.g. a CRT), falling on the face's
    `key_side`; the opposite side takes a cool cel shadow. hand: 'phone' (held to the ear), 'chin', or None.
    Parts carry ids for animation: {p}-head, {p}-brows, {p}-mouth, {p}-lids, {p}-hand."""
    jk, jks, shirt, tie, tr, trs, shoe, kind = COSTUMES[costume]
    sk, sks, skh = SKINS[skin % len(SKINS)]
    hc = HAIR[hair % len(HAIR)]
    top, top_s = (jk, jks) if jk else (shirt, "#aab4c4")
    bn, bf = _CU_BROWS.get(expr, _CU_BROWS["neutral"])
    mouth = _CU_MOUTH.get(expr, _CU_MOUTH["neutral"])
    gid = f"{p}-cu"
    defs = (f'<defs><linearGradient id="{gid}-key" x1="{1 if key_side == "right" else 0}" y1="0" x2="{0 if key_side == "right" else 1}" y2="0">'
            f'<stop offset="0" stop-color="{key}" stop-opacity=".55"/><stop offset=".45" stop-color="{key}" stop-opacity=".12"/><stop offset="1" stop-color="{key}" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="{gid}-cheek" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#e0786a" stop-opacity=".35"/><stop offset="1" stop-color="#e0786a" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="{gid}-face"><path d="{_CU_FACE}"/></clipPath>'
            f'<pattern id="{gid}-stb" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r="1" fill="{O}" opacity=".2"/><circle cx="6.5" cy="7.5" r=".9" fill="{O}" opacity=".16"/><circle cx="7" cy="1.5" r=".8" fill="{O}" opacity=".12"/></pattern></defs>')
    # body: shoulders + open collar shirt (or jacket)
    body = (f'<path d="M0 900 C10 800 70 730 190 700 C260 684 318 660 344 618 L470 618 C500 660 560 684 630 702 C730 728 792 800 800 900Z" fill="{top}" stroke="{O}" stroke-width="5"/>'
            f'<path d="M0 900 C10 800 70 730 190 700 C260 684 318 660 344 618 L360 626 C330 690 280 760 250 900Z" fill="{top_s}" opacity=".9"/>'
            f'<path d="M300 690 C296 760 300 830 310 900 M600 700 C590 760 586 830 590 900" fill="none" stroke="{top_s}" stroke-width="4" opacity=".9"/>')
    neck = (f'<path d="M352 520 C356 580 352 620 340 648 L478 648 C468 610 468 580 476 548Z" fill="{sk}" stroke="{O}" stroke-width="5"/>'
            f'<path d="M352 520 C356 580 352 620 340 648 L420 648 C400 610 392 570 400 540Z" fill="{sks}" opacity=".7"/>'
            f'<path d="M380 566 C410 590 450 584 476 562 L476 548 C450 574 410 578 382 554Z" fill="{sks}" opacity=".8"/>')
    collar = (f'<path d="M330 640 L404 742 L470 640 L506 662 L420 790 L404 796 L384 786 L300 668Z" fill="{shirt}" stroke="{O}" stroke-width="4.5" stroke-linejoin="round"/>'
              f'<path d="M352 650 L404 742 L452 650Z" fill="{sk}" stroke="{O}" stroke-width="3.5"/><path d="M380 660 L404 730 L428 660Z" fill="{sks}" opacity=".5"/>'
              f'<path d="M404 796 L404 900" stroke="#9aa4b4" stroke-width="3"/><circle cx="404" cy="830" r="5" fill="#b8c0cc"/><circle cx="404" cy="880" r="5" fill="#b8c0cc"/>')
    ear = (f'<path d="M286 352 C252 330 236 372 246 410 C254 446 276 462 298 452" fill="{sk}" stroke="{O}" stroke-width="4.5"/>'
           f'<path d="M282 372 C264 366 260 392 268 414 C274 430 284 434 292 430" fill="none" stroke="{sks}" stroke-width="5"/>')
    head = f'<path d="{_CU_FACE}" fill="{sk}" stroke="{O}" stroke-width="5.5" stroke-linejoin="round"/>'
    # modelling: cool cel shadow on the side away from the key, eye sockets, under-nose, under-lip, jaw shadow
    away = ('M300 150 C250 230 248 330 270 420 C286 480 320 520 372 560 C350 500 330 420 336 330 C340 240 360 180 400 130Z' if key_side == "right"
            else 'M590 200 C612 280 606 380 580 470 C566 520 540 556 500 572 C530 500 548 420 548 330 C548 260 540 220 520 160Z')
    model = (f'<g clip-path="url(#{gid}-face)">'
             f'<path d="{away}" fill="{sks}" opacity=".85"/>'
             f'<path d="M420 336 C440 316 480 318 506 334 C490 326 446 326 420 344Z" fill="{sks}" opacity=".6"/>'           # near socket
             f'<path d="M546 334 C556 326 572 326 584 334 L584 352 C572 344 558 342 546 350Z" fill="{sks}" opacity=".5"/>'    # far socket
             f'<path d="M560 440 C576 452 596 452 610 444 C600 462 576 466 560 456Z" fill="{sks}" opacity=".8"/>'            # under nose
             f'<path d="M494 512 C514 522 540 520 556 510 C544 528 512 532 494 520Z" fill="{sks}" opacity=".6"/>'            # under lip
             f'<path d="M300 470 C360 560 450 590 540 560 L540 600 L300 600Z" fill="{sks}" opacity=".55"/>'                  # jaw underside
             + (f'<path d="M330 430 C380 520 470 560 560 520 C590 500 600 470 600 450 L600 600 L320 600Z" fill="url(#{gid}-stb)"/>' if stubble else "")
             + f'<rect width="800" height="900" fill="url(#{gid}-key)"/>'
             f'<ellipse cx="470" cy="430" rx="54" ry="34" fill="url(#{gid}-cheek)"/>'
             f'<path d="M560 210 C586 250 596 300 590 330" fill="none" stroke="{skh}" stroke-width="10" opacity=".5" stroke-linecap="round"/>'  # forehead plane highlight
             f'<path d="M598 380 C604 410 602 440 594 460" fill="none" stroke="{skh}" stroke-width="7" opacity=".45" stroke-linecap="round"/>'
             f'</g>')
    rim = (f'<path d="M574 240 C590 270 594 300 588 312 M590 372 C598 400 594 440 584 470 C576 510 560 540 540 562" fill="none" stroke="{key}" stroke-width="9" opacity=".75" stroke-linecap="round"/>'
           if key_side == "right" else
           f'<path d="M262 300 C246 360 256 440 290 500" fill="none" stroke="{key}" stroke-width="9" opacity=".7" stroke-linecap="round"/>')

    def eye(cx, cy, w, h, iris_dx, far=False):
        iw = h * .82
        return (f'<path d="M{cx - w} {cy + 2} Q{cx - w * .2} {cy - h * 1.15:.1f} {cx + w} {cy - 2} Q{cx + w * .1:.1f} {cy + h * .85:.1f} {cx - w} {cy + 2}Z" fill="#f6f0ea" stroke="{O}" stroke-width="2.4"/>'
                f'<clipPath id="{gid}-e{cx}"><path d="M{cx - w} {cy + 2} Q{cx - w * .2} {cy - h * 1.15:.1f} {cx + w} {cy - 2} Q{cx + w * .1:.1f} {cy + h * .85:.1f} {cx - w} {cy + 2}Z"/></clipPath>'
                f'<g clip-path="url(#{gid}-e{cx})"><circle cx="{cx + iris_dx}" cy="{cy}" r="{iw:.1f}" fill="#6a4426"/><circle cx="{cx + iris_dx}" cy="{cy}" r="{iw * .72:.1f}" fill="#4a2c16"/>'
                f'<circle cx="{cx + iris_dx}" cy="{cy}" r="{iw * .42:.1f}" fill="#0c0806"/>'
                f'<path d="M{cx - w} {cy - h * 1.2:.1f} H{cx + w} V{cy - h * .45:.1f} H{cx - w}Z" fill="{sks}" opacity="{.55 if tired else 0}"/></g>'   # heavy upper lid
                f'<circle cx="{cx + iris_dx + iw * .35:.1f}" cy="{cy - iw * .4:.1f}" r="{iw * .2:.1f}" fill="#fff"/>'
                f'<path d="M{cx - w - 3} {cy + 2} Q{cx - w * .2} {cy - h * 1.2 - 3:.1f} {cx + w + 2} {cy - 3}" fill="none" stroke="{O}" stroke-width="{5 if not far else 4}" stroke-linecap="round"/>'  # lash line
                f'<path d="M{cx - w + 2} {cy - h - 9:.1f} Q{cx - w * .1:.1f} {cy - h * 1.2 - 14:.1f} {cx + w} {cy - h - 7:.1f}" fill="none" stroke="{sks}" stroke-width="3"/>'                   # lid crease
                + (f'<path d="M{cx - w + 4} {cy + h * .9:.1f} Q{cx} {cy + h * 1.6:.1f} {cx + w - 2} {cy + h * .8:.1f}" fill="none" stroke="{sks}" stroke-width="3.5" opacity=".9"/>'
                   f'<path d="M{cx - w + 8} {cy + h * 1.45:.1f} Q{cx} {cy + h * 2.1:.1f} {cx + w - 6} {cy + h * 1.3:.1f}" fill="none" stroke="{sks}" stroke-width="2.5" opacity=".6"/>' if tired else ""))
    eyes = f'<g id="{p}-lids">{eye(456, 352, 34, 15, 9)}{eye(566, 350, 16, 13, 4, True)}</g>'
    brow_w = 12
    brows = (f'<path id="{p}-brows" d="{bn} M{bf[1:]}" fill="none" stroke="{hc}" stroke-width="{brow_w}" stroke-linecap="round"/>'
             f'<path d="{bn}" fill="none" stroke="{O}" stroke-width="2" opacity=".35" transform="translate(0 -6)"/>')
    worry_lines = ('<path d="M430 236 Q470 226 510 232 M440 258 Q478 250 514 256" fill="none" stroke="#000" stroke-width="2.6" opacity=".18"/>'
                   '<path d="M512 300 Q518 316 514 330" fill="none" stroke="#000" stroke-width="2.6" opacity=".22"/>' if expr in ("worried", "angry") else "")
    nose = (f'<path d="M586 392 C600 406 612 414 618 422 C630 432 628 448 616 454 C604 460 590 458 580 452 C584 432 588 412 586 392Z" fill="{sk}"/>'
            f'<path d="M538 372 C548 396 566 410 602 420 C622 428 628 442 616 452 C604 460 590 458 580 452" fill="none" stroke="{O}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M572 454 C562 458 552 452 555 442" fill="none" stroke="{O}" stroke-width="3.8" stroke-linecap="round"/>'
            f'<path d="M538 350 C548 380 560 400 586 414" fill="none" stroke="{skh}" stroke-width="6" opacity=".5" stroke-linecap="round"/>'
            f'<path d="M520 460 C506 476 498 490 500 500" fill="none" stroke="{sks}" stroke-width="4" opacity=".8" stroke-linecap="round"/>')   # nasolabial fold
    mouth_svg = (f'<path id="{p}-mouth" d="{mouth}" fill="{"#5a2422" if expr == "talk" else "none"}" stroke="#5a2a26" stroke-width="5.5" stroke-linecap="round"/>'
                 f'<path d="M492 514 Q520 522 548 512" fill="none" stroke="#b86a5e" stroke-width="4" opacity=".6"/>')
    hair_back = (f'<path d="M250 420 C210 330 220 200 300 130 C370 70 480 60 560 110 C610 140 630 200 612 252 C600 222 580 200 556 190 '
                 f'C500 210 440 200 390 220 C350 236 320 280 312 340 C308 380 300 410 286 430Z" fill="{hc}" stroke="{O}" stroke-width="5.5" stroke-linejoin="round"/>')
    hair_front = (f'<path d="M282 372 C236 250 270 118 428 100 C520 84 604 126 616 222 C592 198 558 188 522 192 C472 196 424 212 394 234 C362 258 340 296 330 344 C318 352 300 366 282 372Z" fill="{hc}" stroke="{O}" stroke-width="5" stroke-linejoin="round"/>'
                  f'<path d="M340 190 C400 136 490 116 570 140 M352 240 C410 190 490 176 572 176 M310 260 C320 200 360 150 420 126" fill="none" stroke="#ffffff" stroke-width="5" opacity=".15" stroke-linecap="round"/>'
                  f'<path d="M462 112 C478 140 500 160 540 168" fill="none" stroke="{O}" stroke-width="3" opacity=".55"/>'
                  f'<path d="M304 330 C300 360 304 390 312 410" fill="none" stroke="{hc}" stroke-width="16" stroke-linecap="round"/>')   # sideburn
    hand_svg = ""
    if hand == "phone":
        hand_svg = (f'<g id="{p}-hand">'
                    f'<path d="M150 900 C170 780 200 640 236 540 L330 556 C300 660 280 780 270 900Z" fill="{top}" stroke="{O}" stroke-width="5"/>'    # sleeve/forearm
                    f'<path d="M150 900 C170 780 200 640 236 540 L262 544 C240 660 224 780 214 900Z" fill="{top_s}" opacity=".85"/>'
                    f'<path d="M236 540 C232 520 236 504 244 496 L318 508 C326 520 330 540 330 556Z" fill="{sk}" stroke="{O}" stroke-width="4.5"/>'   # wrist
                    f'<g transform="rotate(-12 280 400)"><rect x="244" y="300" width="74" height="160" rx="14" fill="#1e1e24" stroke="{O}" stroke-width="5"/>'
                    f'<rect x="252" y="312" width="16" height="136" rx="5" fill="#3a3a46"/></g>'
                    f'<path d="M232 510 C210 470 214 420 236 392 C252 372 280 370 300 384 C318 398 326 440 320 480 C316 500 300 512 280 514Z" fill="{sk}" stroke="{O}" stroke-width="4.5" stroke-linejoin="round"/>'  # palm
                    f'<path d="M232 510 C210 470 214 420 236 392 C244 420 248 460 262 500Z" fill="{sks}" opacity=".75"/>'
                    + "".join(f'<path d="M{296 + i * 4} {384 + i * 26} C{318 + i * 2} {376 + i * 26} {334} {386 + i * 26} {330 - i * 2} {404 + i * 26} C{326} {414 + i * 26} {312} {412 + i * 26} {300} {406 + i * 26}" '
                              f'fill="{sk}" stroke="{O}" stroke-width="3.6" stroke-linejoin="round"/>' for i in range(4))     # fingers curled over the phone edge
                    + f'<path d="M236 400 C228 372 236 340 256 330 C268 326 276 336 272 352 C266 372 258 392 250 404Z" fill="{sk}" stroke="{O}" stroke-width="4" stroke-linejoin="round"/>'  # thumb
                    f'<path d="M244 338 C252 334 260 336 264 344" fill="none" stroke="{sks}" stroke-width="3"/></g>')
    elif hand == "chin":
        hand_svg = (f'<g id="{p}-hand"><path d="M380 900 C400 800 430 700 470 610 L560 630 C530 720 510 810 500 900Z" fill="{top}" stroke="{O}" stroke-width="5"/>'
                    f'<path d="M470 610 C470 580 490 556 520 552 C552 548 572 566 574 590 C576 612 566 630 552 636 L490 632Z" fill="{sk}" stroke="{O}" stroke-width="4.5"/>'
                    + "".join(f'<path d="M{500 + i * 18} 560 C{498 + i * 18} 540 {512 + i * 18} 532 {520 + i * 18} 544" fill="{sk}" stroke="{O}" stroke-width="3.4"/>' for i in range(3)) + '</g>')
    return (f'<svg viewBox="{CLOSEUP_VIEWBOX}" xmlns="http://www.w3.org/2000/svg" overflow="visible">{defs}<g class="rig3 closeup" id="{p}">'
            f'{body}{neck}{collar}<g id="{p}-head">{hair_back}{ear}{head}{model}{rim}{worry_lines}{eyes}{brows}{nose}{mouth_svg}{hair_front}</g>{hand_svg}</g></svg>')


# face silhouette for the close-up (three-quarter right): forehead, brow ridge, eye dip, cheekbone, mouth, chin, jaw, ear line
_CU_FACE = ("M300 170 C350 120 450 110 530 140 C574 160 590 210 590 262 C592 290 590 306 596 316 C590 330 584 342 588 360 "
            "C596 390 600 420 596 446 C590 472 580 492 572 512 C566 534 556 556 534 572 C508 590 470 590 440 580 "
            "C400 566 360 536 330 500 C300 466 284 426 282 380 C280 320 278 230 300 170Z")


# ── props in hands + forward kinematics (for placing objects where a hand is) ───────────────────
PROPS3 = {
    # drawn in the hand's local frame: wrist at (246, 538), fingers point down (+y)
    "stamp": ('<g class="prop"><rect x="236" y="560" width="20" height="44" rx="6" fill="#5a3a22" stroke="#1b1410" stroke-width="3"/>'
              '<ellipse cx="246" cy="560" rx="14" ry="9" fill="#7a4a2a" stroke="#1b1410" stroke-width="3"/>'
              '<rect x="216" y="600" width="60" height="18" rx="3" fill="#b8322a" stroke="#1b1410" stroke-width="3"/></g>'),
    "pen": '<g class="prop"><path d="M240 560 L252 640" stroke="#1b1410" stroke-width="7" stroke-linecap="round"/></g>',
    "envelope": ('<g class="prop"><rect x="214" y="570" width="64" height="42" rx="4" fill="#f2e6c8" stroke="#1b1410" stroke-width="3"/>'
                 '<path d="M214 570 L246 594 L278 570" fill="none" stroke="#1b1410" stroke-width="2.5"/></g>'),
}


def hold(markup: str, p: str, prop: str, side: str = "front") -> str:
    """Put a prop (PROPS3 key or raw SVG in hand-local space) into a figure's hand so it moves with the arm."""
    tag = f'<g id="{p}-hand-{side}">'
    return markup.replace(tag, tag + PROPS3.get(prop, prop), 1)


def hand_point(angles: dict, side: str = "front", mirrored: bool = False, reach: float = 40) -> tuple[float, float]:
    """Forward kinematics: the hand centre (viewBox coords) for a joint-angle dict (pose_angles format)."""
    def rot(v, deg):
        a = math.radians(deg)
        return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))
    sx, sy = J["sh_f"] if side == "front" else J["sh_b"]
    ua, fa = angles[f"uarm-{side}"], angles[f"farm-{side}"]
    e = rot((0, L["uarm"]), ua)
    w = rot((0, L["farm"] - 2 + reach), ua + fa)
    x, y = sx + e[0] + w[0], sy + e[1] + w[1]
    if side == "front":     # the front arm lives inside the upper body, which turns about the waist
        wx, wy = J["waist"]
        dx, dy = rot((x - wx, y - wy), angles.get("upper", 0))
        x, y = wx + dx, wy + dy
    return (400 - x if mirrored else x, y)


def reach(pose: str, target: tuple[float, float], side: str = "front", bend: int = 1) -> dict:
    """pose_angles(pose) with one arm solved by IK so its hand centre lands on `target` (viewBox coords, unmirrored)."""
    a = dict(pose_angles(pose))
    sh = J["sh_f"] if side == "front" else J["sh_b"]
    tx, ty = target
    if side == "front" and a.get("upper"):      # undo the upper-body turn so IK works in the arm's frame
        wx, wy = J["waist"]; r = math.radians(-a["upper"])
        dx, dy = tx - wx, ty - wy
        tx, ty = wx + dx * math.cos(r) - dy * math.sin(r), wy + dx * math.sin(r) + dy * math.cos(r)
    u, f = ik(sh, (tx, ty - 40 * 0), L["uarm"], L["farm"] - 2 + 40, bend)
    wrap = lambda v: ((v + 180) % 360) - 180
    a[f"uarm-{side}"], a[f"farm-{side}"] = round(wrap(u), 2), round(wrap(f), 2)
    return a
