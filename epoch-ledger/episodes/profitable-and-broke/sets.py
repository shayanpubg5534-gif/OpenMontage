"""Profitable and Broke — sets (new for this episode): Maya's bakery and the bank's lending office.

Built with kit/scene3d.js and rendered once as depth-layered cached plates (kit/depth.py). All art is original SVG.
"""
from __future__ import annotations

import json
import math
import random

from kit.camera3d import Camera

INK = "#1b1410"


# ── art ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def loaf(x, y, w, h, c="#c98a4a", score=True):
    s = f'<ellipse cx="{x}" cy="{y}" rx="{w / 2}" ry="{h / 2}" fill="{c}" stroke="{INK}" stroke-width="3"/>'
    s += f'<ellipse cx="{x - w * .12}" cy="{y - h * .18}" rx="{w * .26}" ry="{h * .14}" fill="#e8b878" opacity=".55"/>'
    if score:
        s += "".join(f'<path d="M{x - w * .3 + k * w * .2} {y - h * .25} q{w * .06} {h * .2} {w * .1} {h * .45}" stroke="#8a5428" stroke-width="2.5" fill="none"/>' for k in range(3))
    return s


def bread_shelves(seed=3):
    """1000x700 wall unit of three shelves of loaves, baguettes and rolls."""
    r = random.Random(seed)
    out = ['<rect width="1000" height="700" fill="#7a5236" stroke="#1b1410" stroke-width="6"/>']
    for k, y in enumerate((210, 440, 670)):
        out.append(f'<rect x="0" y="{y}" width="1000" height="26" fill="#5a3a24" stroke="{INK}" stroke-width="3"/>')
        x = 40
        while x < 960:
            kind = r.choice(["loaf", "loaf", "bag", "roll"])
            if kind == "bag":
                for j in range(3):
                    out.append(f'<rect x="{x + j * 18}" y="{y - 150}" width="22" height="150" rx="11" fill="#d49a58" stroke="{INK}" stroke-width="2.5" transform="rotate({-6 + j * 4} {x + j * 18} {y})"/>')
                x += 90
            elif kind == "roll":
                for j in range(4):
                    out.append(loaf(x + 28 + (j % 2) * 44, y - 26 - (j // 2) * 40, 46, 38, "#d9a25e", False))
                x += 110
            else:
                w = r.uniform(110, 140)
                out.append(loaf(x + w / 2, y - 44, w, 70, r.choice(["#c98a4a", "#b8763c", "#d49a58"])))
                x += w + 14
    return "".join(out)


def chalkboard():
    return ('<rect width="900" height="560" rx="16" fill="#2a2e2c" stroke="#5a3a24" stroke-width="22"/>'
            '<text x="450" y="120" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="74" fill="#f4ead4">Maya\'s Bakery</text>'
            '<path d="M200 150 H700" stroke="#e2c27a" stroke-width="4"/>'
            + "".join(f'<text x="120" y="{230 + i * 78}" font-family="Inter" font-weight="700" font-size="44" fill="#f4ead4">{a}</text>'
                      f'<text x="780" y="{230 + i * 78}" text-anchor="end" font-family="Inter" font-weight="700" font-size="44" fill="#e2c27a">{b}</text>'
                      for i, (a, b) in enumerate((("Sourdough", "$6"), ("Rye loaf", "$5"), ("Baguette", "$3"), ("Cinnamon roll", "$4")))))


def street_window():
    """700x900 view through the shop window: morning street, the bakery's sign painted on the glass (mirrored)."""
    houses = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{900 - y}" fill="{c}" stroke="{INK}" stroke-width="3"/>'
                     + "".join(f'<rect x="{x + 18 + i * 44}" y="{y + 30 + j * 70}" width="26" height="40" fill="#f6e2a8" stroke="{INK}" stroke-width="2"/>'
                               for i in range(int((w - 30) // 44)) for j in range(int((900 - y - 60) // 70)))
                     for x, y, w, c in ((-20, 300, 260, "#c96a4a"), (240, 220, 220, "#d8b070"), (460, 330, 260, "#7a8aa8")))
    return (f'<rect width="700" height="900" fill="#bfe0f0"/><circle cx="560" cy="160" r="70" fill="#fff2c0"/>{houses}'
            '<rect y="780" width="700" height="120" fill="#8a8a8a"/>'
            '<rect width="700" height="900" fill="#ffffff" opacity=".12"/>'
            '<g transform="translate(350 120) scale(-1 1)"><text x="0" y="0" text-anchor="middle" font-family="Fraunces" font-weight="800" '
            'font-size="64" fill="#f4ead4" stroke="#2f6f73" stroke-width="3">BAKERY</text></g>')


def pastry_case():
    cakes = "".join(loaf(80 + i * 130, 150, 100, 60, c, False) for i, c in enumerate(("#e8b0a0", "#d49a58", "#f0d0a0", "#c98a4a", "#e8c070")))
    return (f'<rect width="760" height="240" fill="#dff0f4" opacity=".55" stroke="{INK}" stroke-width="5"/>'
            f'<rect y="180" width="760" height="60" fill="#e8dcc4" stroke="{INK}" stroke-width="3"/>{cakes}'
            '<path d="M20 20 L180 20" stroke="#fff" stroke-width="8" opacity=".7"/>')


def crate(label="FRESHMART"):
    return (f'<rect width="400" height="220" rx="10" fill="#e9a23b" stroke="{INK}" stroke-width="6"/>'
            + "".join(f'<rect x="{30 + i * 90}" y="40" width="60" height="120" rx="8" fill="#c8862e" stroke="{INK}" stroke-width="3"/>' for i in range(4))
            + f'<text x="200" y="205" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#1b1410">{label}</text>'
            + "".join(loaf(70 + i * 90, 30, 80, 46) for i in range(4)))


def bank_window():
    towers = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{700 - y}" fill="#5a6a88" stroke="#2a3048" stroke-width="3"/>'
                     + "".join(f'<rect x="{x + 12 + i * 30}" y="{y + 20 + j * 40}" width="16" height="22" fill="#c8d8f0" opacity=".8"/>'
                               for i in range(int((w - 20) // 30)) for j in range(int((700 - y - 40) // 40)))
                     for x, y, w in ((0, 200, 180), (200, 120, 160), (380, 260, 200), (600, 160, 160)))
    return f'<rect width="760" height="700" fill="#a8c4e0"/>{towers}<rect width="760" height="700" fill="#ffffff" opacity=".18"/>'


def bank_sign():
    return ('<rect width="900" height="160" rx="10" fill="#1f3550"/><text x="450" y="70" text-anchor="middle" font-family="Fraunces" font-weight="800" '
            'font-size="58" fill="#f2f2ee">Harbor Community Bank</text><text x="450" y="125" text-anchor="middle" font-family="Inter" font-weight="700" '
            'font-size="34" fill="#9fc0e0" letter-spacing="6">BUSINESS LENDING</text>')


def monitor_logo():
    return ('<rect width="400" height="250" rx="8" fill="#1f3550"/><circle cx="200" cy="105" r="50" fill="none" stroke="#9fc0e0" stroke-width="10"/>'
            '<text x="200" y="205" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#f2f2ee">HARBOR</text>')


ART = {"shelves": bread_shelves(), "chalk": chalkboard(), "street": street_window(), "case": pastry_case(), "crate": crate(),
       "bankwin": bank_window(), "banksign": bank_sign(), "monitor": monitor_logo()}


# ── the bakery ─────────────────────────────────────────────────────────────────────────────────────────────────────
BAKERY = r"""
const sc = S3.scene();
// checkered floor
for (let i = -6; i < 6; i++) for (let j = -7; j < 3; j++) sc.quad([i * .6, 0, (j + 1) * .6], [(i + 1) * .6, 0, (j + 1) * .6], [(i + 1) * .6, 0, j * .6], [i * .6, 0, j * .6],
  { color: (i + j) % 2 ? '#e8dcc4' : '#9a5a3a', receiver: true, outline: false }, {});
const wall = { color: '#f0e2c6', outline: false };
sc.quad([-3.6, 0, -4.2], [3.6, 0, -4.2], [3.6, 3.2, -4.2], [-3.6, 3.2, -4.2], wall, { bias: -3 });
sc.quad([-3.6, 0, 1.8], [-3.6, 0, -4.2], [-3.6, 3.2, -4.2], [-3.6, 3.2, 1.8], { color: '#e8d6b4', outline: false }, { bias: -3 });
sc.quad([3.6, 0, -4.2], [3.6, 0, 1.8], [3.6, 3.2, 1.8], [3.6, 3.2, -4.2], { color: '#e8d6b4', outline: false }, { bias: -3 });
sc.quad([-3.6, 3.2, 1.8], [-3.6, 3.2, -4.2], [3.6, 3.2, -4.2], [3.6, 3.2, 1.8], { color: '#f6ead2', outline: false }, { bias: -3, allowBack: true });
sc.quad([-3.6, 0, -4.18], [3.6, 0, -4.18], [3.6, .9, -4.18], [-3.6, .9, -4.18], { color: '#2f6f73', outline: false }, { bias: -2.5 });     // wainscot
// bread shelves (left), oven (centre-right), chalkboard (above oven)
sc.box([-3.2, 0, -4.15], [-0.6, 2.2, -3.75], { color: '#5a3a24' }, {});
sc.art([-3.15, .05, -3.74], [-0.65, .05, -3.74], [-3.15, 2.15, -3.74], 1000, 700, ART.shelves, { bias: .05 });
sc.box([0.3, 0, -4.15], [2.1, 1.6, -3.4], { color: '#5a5a60', gloss: .4 }, {});
sc.box([0.5, .55, -3.39], [1.9, 1.25, -3.37], { color: '#ff9a40', emissive: 1.4, outline: '#1b1410' }, { shadow: false });
sc.box([0.4, 1.6, -4.1], [2.0, 2.9, -3.6], { color: '#6a6a70' }, { shadow: false });
sc.art([0.35, 1.85, -3.58], [2.05, 1.85, -3.58], [0.35, 2.85, -3.58], 900, 560, ART.chalk, { bias: .05 });
// shop window + door on the right wall
sc.art([3.58, .9, -3.6], [3.58, .9, -1.2], [3.58, 2.7, -3.6], 700, 900, ART.street, { bias: .02 });
sc.box([3.5, .85, -3.65], [3.6, .9, -1.15], { color: '#5a3a24' }, { shadow: false });
// the counter: top, front panel, pastry case
sc.box([-1.9, .96, -3.0], [1.9, 1.02, -2.25], { color: '#7a4a2a', gloss: .3 }, {});
sc.box([-1.85, 0, -2.4], [1.85, .96, -2.27], { color: '#2f6f73' }, {});
sc.box([-1.85, .05, -2.28], [1.85, .2, -2.26], { color: '#244f52' }, { shadow: false });
sc.art([-1.7, 1.02, -2.32], [-0.2, 1.02, -2.32], [-1.7, 1.5, -2.32], 760, 240, ART.case, { bias: .3 });
sc.box([0.9, 1.02, -2.8], [1.3, 1.32, -2.5], { color: '#c8c8c0', gloss: .3 }, {});                      // the till
// pendant lamps
[-1.4, 0, 1.4].forEach(x => { sc.cyl([x, 2.3, -2.6], .012, 2.3, 3.2, { color: '#2a2a2a' }, { seg: 4, shadow: false });
  sc.cyl([x, 2.18, -2.6], .2, 2.18, 2.34, { color: '#e2c27a', gloss: .5, emissive: .5 }, { seg: 12, shadow: false }); });
// near foreground: a bread basket on a stool (blurred in the fg plate)
sc.box([-1.3, 0, -1.25], [-0.8, .62, -0.85], { color: '#5a3a24' }, { layer: 'fg' });
sc.box([-1.37, .62, -1.3], [-0.73, .82, -0.8], { color: '#b8803e' }, { layer: 'fg' });
sc.art([-1.35, .78, -1.0], [-0.75, .78, -1.0], [-1.35, 1.08, -1.0], 400, 200, BASKET, { layer: 'fg' });
"""
BAKERY_LIGHT = ("const L = { sun: { dir: [1, .45, .35], color: '#ffe0b0', intensity: .55 }, sky: '#fff4e0', ground: '#8a6a50', ambient: .86, "
                "points: [{pos:[-1.4,2.1,-2.6],color:'#ffd8a0',intensity:.5,range:3.5},{pos:[1.4,2.1,-2.6],color:'#ffd8a0',intensity:.5,range:3.5},"
                "{pos:[1.2,1.0,-3.2],color:'#ff9a40',intensity:.6,range:2.5}], fog: { color: '#f6e6cc', near: 6, far: 20, max: .2 }, "
                "shadowOpacity: .35, shadowColor: '#4a2a18' };")
BAKERY_GLOWS = "const GLOWS = [[[-1.4,2.15,-2.6],120,'#ffe2a8'],[[0,2.15,-2.6],120,'#ffe2a8'],[[1.4,2.15,-2.6],120,'#ffe2a8'],[[1.2,.9,-3.36],220,'#ff9a40']];"


def basket():
    return "".join(loaf(60 + i * 95, 110 - (i % 2) * 30, 110, 64, c) for i, c in enumerate(("#c98a4a", "#d49a58", "#b8763c", "#d49a58")))


CAM_SHOP = Camera(pos=[0.3, 1.5, 0.2], look=[0.0, 1.28, -3.2], fov=40)          # customer side, close enough that Maya leads the frame
CAM_SHOP_DAWN = Camera(pos=[1.8, 1.45, 1.4], look=[-0.4, 1.15, -3.2], fov=46)  # wider, from by the window

# ── the bank ───────────────────────────────────────────────────────────────────────────────────────────────────────
BANK = r"""
const sc = S3.scene();
sc.ground(-4, -5, 4, 3, 0, 1.4, { color: '#5a6478', receiver: true, outline: false });
const wall = { color: '#dfe4ea', outline: false };
sc.quad([-4, 0, -4.5], [4, 0, -4.5], [4, 3, -4.5], [-4, 3, -4.5], wall, { bias: -3 });
sc.quad([-4, 0, 3], [-4, 0, -4.5], [-4, 3, -4.5], [-4, 3, 3], { color: '#cfd6de', outline: false }, { bias: -3 });
sc.quad([4, 0, -4.5], [4, 0, 3], [4, 3, 3], [4, 3, -4.5], { color: '#cfd6de', outline: false }, { bias: -3 });
sc.quad([-4, 3, 3], [-4, 3, -4.5], [4, 3, -4.5], [4, 3, 3], { color: '#eef0f2', outline: false }, { bias: -3, allowBack: true });
sc.art([-2.6, 1.0, -4.48], [0.4, 1.0, -4.48], [-2.6, 2.7, -4.48], 760, 700, ART.bankwin, { bias: .02 });
sc.box([-2.7, .95, -4.5], [0.5, 1.0, -4.3], { color: '#8a9098' }, { shadow: false });
sc.art([0.9, 2.2, -4.48], [3.4, 2.2, -4.48], [0.9, 2.64, -4.48], 900, 160, ART.banksign, { bias: .02 });
sc.box([1.2, 0, -4.45], [3.2, 1.9, -4.0], { color: '#7a5a3a' }, {});                                   // filing cabinet / shelf
[0.35, .95, 1.55].forEach(y => sc.box([1.25, y, -4.02], [3.15, y + .04, -3.98], { color: '#5a3a24' }, { shadow: false }));
// the desk between lender (left) and borrower (right), monitor turned to the lender
sc.box([-1.1, .72, -2.6], [1.1, .78, -1.6], { color: '#6a4a30', gloss: .3 }, {});
sc.box([-1.05, 0, -2.55], [-0.95, .72, -1.65], { color: '#4a3220' }, {}); sc.box([0.95, 0, -2.55], [1.05, .72, -1.65], { color: '#4a3220' }, {});
sc.box([-1.05, .2, -2.56], [1.05, .72, -2.5], { color: '#4a3220' }, {});
sc.box([-0.75, .78, -2.4], [-0.71, 1.18, -2.0], { color: '#1b1b20' }, {});
sc.art([-0.705, .82, -2.38], [-0.705, .82, -2.02], [-0.705, 1.16, -2.38], 400, 250, ART.monitor, { bias: .05 });
sc.box([0.3, .78, -2.3], [0.62, .8, -2.05], { color: '#f6f2e6' }, { shadow: false });
sc.cyl([-0.4, .78, -1.85], .04, .78, .9, { color: '#2f6f73' }, { seg: 10, shadow: false });
// chairs (behind each sitter)
sc.box([-1.7, .45, -2.35], [-1.2, .5, -1.85], { color: '#2a2e36' }, {}); sc.box([-1.75, .5, -2.35], [-1.69, 1.15, -1.85], { color: '#2a2e36' }, {});
sc.box([1.2, .45, -2.35], [1.7, .5, -1.85], { color: '#2a2e36' }, {}); sc.box([1.69, .5, -2.35], [1.75, 1.1, -1.85], { color: '#2a2e36' }, {});
sc.box([-1.5, 0, -2.15], [-1.4, .45, -2.05], { color: '#1a1a1e' }, { shadow: false }); sc.box([1.4, 0, -2.15], [1.5, .45, -2.05], { color: '#1a1a1e' }, { shadow: false });
// near foreground: a plant at the left edge (blurred)
sc.art([-2.6, 0, -.2], [-1.9, 0, -.2], [-2.6, 1.15, -.2], 400, 640, FOLIAGE, { layer: 'fg' });
"""
BANK_LIGHT = ("const L = { sun: { dir: [-.4, .5, 1], color: '#e0ecff', intensity: .5 }, sky: '#f0f4fa', ground: '#4a5060', ambient: .85, "
              "points: [{pos:[0,2.8,-2],color:'#f4f6ff',intensity:.45,range:5}], shadowOpacity: .3, shadowColor: '#1a2030' };")
CAM_BANK = Camera(pos=[0.0, 1.38, 0.7], look=[0.0, 1.0, -2.1], fov=42)


def prelude(foliage: str) -> str:
    return f"const ART = {json.dumps(ART)};\nconst BASKET = {json.dumps(basket())};\nconst FOLIAGE = {json.dumps(foliage)};"
