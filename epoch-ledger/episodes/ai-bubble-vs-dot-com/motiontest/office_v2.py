"""Office sequence v2 (~14 s): narration-driven "follow the money" montage for c03_04 + c03_05.

  python epoch-ledger/episodes/ai-bubble-vs-dot-com/motiontest/office_v2.py [WS]     (default projects/<slug>/office_v2)
  python epoch-ledger/scripts/render.py render WS -o WS/office_v2.mp4

Every narration beat gets its own visible action (plan: office_v2_plan.json):
  S1 0.00 "They were spending heavily"     the founder spins the cash tank's outlet valve; coins burst into the spending pipe
  S2 1.50 "on advertising"                 match cut on the coins: they pour into a TV, which powers on and plays BigCart's ad
  S3 2.85 "employees"                      payroll pipe drops coins onto four desks as pay envelopes; staff typing; a new hire walks in
  S4 3.75 "infrastructure"                 server room: a technician slides a new server in, the rack lights up, coins feed it
  S5 4.75 "without earning enough revenue" pull out to the whole money machine: three outflows gush, revenue trickles, tank drains
  S6 6.85 "to sustain themselves"          push into the gauge: needle falls into red, warning lamp
  S7 8.65 "survival depended on investors" Summit Ventures boardroom: an investor stamps FUNDED, another opens the capital valve
  S8 11.25 "continuing to provide capital" the investor pipe pours into the tank; it refills while the outflows continue
Static sets are cached plates (kit/plates.py); characters, money and machines animate live on top.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent
EL = EP.parents[1]
ROOT = EL.parent
sys.path[:0] = [str(EL), str(EP)]

from kit import finmech as F, rig3  # noqa: E402
from kit.assemble import Scene, assemble  # noqa: E402
from kit.camera3d import Camera  # noqa: E402
from kit.lightfx import grade  # noqa: E402
from kit.motion import ktext  # noqa: E402
from kit.plates import plate  # noqa: E402
import timeline as TL  # noqa: E402
from styleframes import common, sf2_medium as SF2  # noqa: E402

OFF = 215.2                 # film time of preview t=0
D = 14.0
CUT = [0, 1.5, 2.85, 3.75, 4.75, 6.85, 8.65, 10.35, 10.95, 11.6, D]
INK = "#1b1410"


def W(word, line):
    return round(TL.W(word, line) - OFF, 3)


OFFICE_LIGHT = ("const L = { sun: { dir: [-1, .3, .2], color: '#ffb070', intensity: .42 }, sky: '#f4e2c8', ground: '#7a5a40', ambient: .82, points: ["
                + ",".join(f"{{pos:[{x},2.9,{z}],color:'#fff0d0',intensity:.5,range:5}}" for z in (1, -2.2, -5.4) for x in (-2.4, 1.6))
                + "], fog: { color: '#f2d8b8', near: 7, far: 30, max: .3 }, shadowOpacity: .4, shadowColor: '#3a2418' };")


def office_scene(drop_desks=False) -> str:
    sc = SF2.SCENE.replace("{people}", "")
    lines, out, skip = sc.split("\n"), [], False          # the easel whiteboard belongs to the old staging — drop it
    for l in lines:
        if l.startswith("// easel whiteboard"):
            skip = True
        elif l.startswith("// right wall"):
            skip = False
        if not skip:
            out.append(l)
    sc = "\n".join(out)
    if drop_desks:       # remove the original desk rows (and what stands on them) — the shot builds its own live workstations
        out, skip = [], False
        for l in sc.split("\n"):
            if l.startswith(("[[-2.6, -4.6]", "[[-3.25, -4.4]", "[[-2.2, -4.5]")):
                skip = True
                continue
            if skip and l.startswith("  "):
                continue
            skip = False
            out.append(l)
        sc = "\n".join(out)
    return f"const ART2 = {json.dumps(SF2.art2_dict())};\n" + sc


# ── plates (static sets, rendered once at 2x and cached) ─────────────────────────────────────────
def plate_html(out: Path, scene_js: str, cam_js: str, light_js: str, blur: float = 0, root: str = "", back: str = "", front: str = "") -> str:
    common.page(out, out.stem, back or '<div style="position:absolute;inset:0;background:#201818"></div>', scene_js, cam_js, light_js, front, root,
                extra_css=f"#set,#glows{{filter:blur({blur}px)}}" if blur else "")
    return out.read_text()


SERVER_SCENE = r"""
const sc = S3.scene(), T = (n) => TEX + n + '.jpg';
sc.ground(-3, -13, 3, 2, 0, 2, { color: '#8a8e96', tex: T('concrete'), texScale: 2.2, sub: 2, texMix: .55, receiver: true, outline: false });
const wall = { color: '#262a34', outline: false };
sc.quad([-3, 0, -13], [3, 0, -13], [3, 3, -13], [-3, 3, -13], wall, { bias: -3 });
sc.quad([-3, 0, 2], [-3, 0, -13], [-3, 3, -13], [-3, 3, 2], wall, { bias: -3 }); sc.quad([3, 0, -13], [3, 0, 2], [3, 3, 2], [3, 3, -13], wall, { bias: -3 });
sc.quad([-3, 3, 2], [-3, 3, -13], [3, 3, -13], [3, 3, 2], { color: '#1a1d24', outline: false }, { bias: -3, allowBack: true });
for (let z = -1.2; z > -12.5; z -= 1.8) sc.quad([-.25, 2.98, z - .7], [.25, 2.98, z - .7], [.25, 2.98, z + .7], [-.25, 2.98, z + .7], { color: '#dff2ff', emissive: 1.3, outline: '#5a6a7a', doubleSided: true }, { allowBack: true });
[[1.25, 2.15], [-2.15, -1.25]].forEach(([x0, x1]) => sc.box([x0 + .1, 2.4, -12.5], [x1 - .1, 2.46, -1.2], { color: '#5a5e66' }, { shadow: false }));
for (let i = 0; i < 16; i++) { const z0 = -1.4 - i * .66;
  if (i !== 2) { sc.box([1.2, 0, z0 - .62], [2.2, 2.1, z0], { color: '#1e2228' }, { bias: -.5 });
    sc.art([1.19, .05, z0 - .62], [1.19, .05, z0], [1.19, 2.05, z0 - .62], 300, 1000, ART4.rack, { bias: .1 }); }
  else sc.box([1.2, 0, z0 - .62], [2.2, 2.1, z0], { color: '#1e2228' }, { bias: -.5 });
  sc.box([-2.2, 0, z0 - .62], [-1.2, 2.1, z0], { color: '#1e2228' }, { bias: -.5 });
  sc.art([-1.19, .05, z0], [-1.19, .05, z0 - .62], [-1.19, 2.05, z0], 300, 1000, ART4.rack, { bias: .1 }); }
"""
SERVER_LIGHT = ("const L = { sun: { dir: [.1, 1, .3], color: '#9ab8ff', intensity: .35 }, sky: '#7a8aaa', ground: '#1a1e28', ambient: .75, "
                "points: [" + ",".join(f"{{pos:[0,2.8,{z}],color:'#dff0ff',intensity:.7,range:4}}" for z in (-1.2, -3, -4.8, -6.6)) + "], "
                "fog: { color: '#141a28', near: 4, far: 17, max: .6 }, shadowOpacity: .35, shadowColor: '#05070c' };")

BOARD_SCENE = r"""
const sc = S3.scene(), T = (n) => TEX + n + '.jpg';
sc.ground(-5, -6, 5, 4, 0, 1.6, { color: '#6a4a30', tex: T('wood_floor'), texScale: 1.6, sub: 3, receiver: true, outline: false, tint: '#e0c098' });
const panel = { color: '#4a3428', tex: T('wood_floor'), texScale: 2.4, sub: 2, texMix: .35, outline: false };
sc.quad([-5, 0, -6], [5, 0, -6], [5, 3.2, -6], [-5, 3.2, -6], panel, { uv: [[0, 1.3], [4, 1.3], [4, 0], [0, 0]], bias: -3 });
sc.quad([-5, 0, 4], [-5, 0, -6], [-5, 3.2, -6], [-5, 3.2, 4], panel, { bias: -3 }); sc.quad([5, 0, -6], [5, 0, 4], [5, 3.2, 4], [5, 3.2, -6], panel, { bias: -3 });
sc.quad([-5, 3.2, 4], [-5, 3.2, -6], [5, 3.2, -6], [5, 3.2, 4], { color: '#2a2220', emissive: .15, outline: false }, { bias: -3, allowBack: true });
[-3.0, 0, 3.0].forEach(x => { sc.quad([x - 1.35, 1.45, -5.97], [x + 1.35, 1.45, -5.97], [x + 1.35, 2.95, -5.97], [x - 1.35, 2.95, -5.97], { color: '#1a2040', emissive: .5, outline: '#1a1410' }, { bias: .05 });
  sc.art([x - 1.35, 1.45, -5.95], [x + 1.35, 1.45, -5.95], [x - 1.35, 2.95, -5.95], 800, 600, ART5.window, { bias: .1 }); });
sc.art([-2.6, 3.0, -5.95], [2.6, 3.0, -5.95], [-2.6, 3.17, -5.95], 1200, 40, ART5.name, { bias: .1 });
sc.box([-5, 0, -6], [5, .14, -5.96], { color: '#2a1a12' }, { shadow: false });
[-1.6, 1.6].forEach(x => { sc.cyl([x, 2.6, -2.7], .01, 2.6, 3.2, { color: '#2a2a2a' }, { seg: 4, shadow: false }); sc.cyl([x, 2.45, -2.7], .32, 2.45, 2.62, { color: '#c7953f', gloss: .5, emissive: .2 }, { seg: 14, shadow: false }); });
[[-4.3, -5.4], [4.3, -5.4]].forEach(([x, z]) => { sc.cyl([x, 0, z], .22, 0, .5, { color: '#3a2a20' }, { seg: 10 }); sc.sprite([x, .5, z], 1.3, ART5.plant, .9, { viewBox: '0 0 90 100' }); });
"""
BOARD_LIGHT = ("const L = { sun: { dir: [0, .4, 1], color: '#8a9ad8', intensity: .45 }, sky: '#a8a0c0', ground: '#3a2a20', ambient: .78, "
               "points: [{pos:[-1.6,2.3,-2.7],color:'#ffd8a0',intensity:.9,range:4.5},{pos:[1.6,2.3,-2.7],color:'#ffd8a0',intensity:.9,range:4.5}], "
               "fog: { color: '#2a2440', near: 6, far: 20, max: .35 }, shadowOpacity: .45, shadowColor: '#100808' };")
BOARD_TABLE = r"""
sc.box([-2.5, .72, -3.3], [2.5, .79, -2.1], { color: '#4a2a1a', gloss: .35 }, {});
[[-2.3, -3.15], [2.3, -3.15], [-2.3, -2.25], [2.3, -2.25]].forEach(([x, z]) => sc.box([x - .06, 0, z - .06], [x + .06, .72, z + .06], { color: '#2a1a10' }, { shadow: false }));
sc.box([-2.45, .3, -2.16], [2.45, .72, -2.12], { color: '#3a2214' }, { shadow: false });
"""


def rack_art(live=False) -> str:
    rows = []
    for r in range(20):
        y = 30 + r * 47
        if live and r in (8, 9):
            continue
        rows.append(f'<rect x="20" y="{y}" width="260" height="40" rx="3" fill="#2c3138" stroke="#0e1014" stroke-width="2"/>'
                    + "".join(f'<path d="M{40 + k * 14} {y + 8} V{y + 32}" stroke="#14171c" stroke-width="4"/>' for k in range(8))
                    + f'<g {"id=" + chr(34) + f"rk-led{r}" + chr(34) if live else ""} opacity="{0.25 if live else 1}">'
                    + "".join(f'<circle cx="{200 + k * 18}" cy="{y + 20}" r="5" fill="{["#5aff7a", "#7fd8ff", "#5aff7a", "#ffcf5a"][(r + k) % 4]}"/>' for k in range(4)) + "</g>")
    new = ""
    if live:   # the new server (2U) that the technician installs
        y = 30 + 8 * 47
        new = (f'<rect x="20" y="{y}" width="260" height="87" rx="4" fill="#0a0c10"/>'
               f'<g id="rk-new" opacity="0"><rect x="20" y="{y}" width="260" height="87" rx="4" fill="#c8ccd4" stroke="#0e1014" stroke-width="3"/>'
               f'<rect x="34" y="{y + 14}" width="120" height="58" rx="3" fill="#2e5ab0"/><text x="94" y="{y + 50}" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="22" fill="#fff">BigCart</text>'
               f'<g id="rk-newled" opacity="0">' + "".join(f'<circle cx="{190 + k * 20}" cy="{y + 43}" r="7" fill="#5aff7a"/>' for k in range(4)) + '</g></g>')
    return f'<rect width="300" height="1000" fill="#14171c"/>{"".join(rows)}{new}'


# ── shot compositions ────────────────────────────────────────────────────────────────────────────
def sprite_box(cam: Camera, foot, height=1.76):
    f, h = cam.project(foot), cam.project([foot[0], foot[1] + height, foot[2]])
    hp = f[1] - h[1]
    return f[0] - hp * .2, h[1], hp * .4, hp, hp / 1000      # x, y, w, h, scale (viewBox units → px)


def to_view(box, pt, mirrored=False):
    x, y, w, h, s = box
    vx, vy = (pt[0] - x) / s, (pt[1] - y) / s
    return (400 - vx if mirrored else vx, vy)


def figure(pid, costume, skin, hair, style, pose="stand", angles=None, mirrored=False, prop=None, extra="", shadow=True, expr="neutral", glasses=False):
    mk = rig3.figure_svg(pid, costume, skin=skin, hair=hair, style=style, pose=pose, expr=expr, glasses=glasses, inner=True, angles=angles, shadow=shadow)
    if prop:
        mk = rig3.hold(mk, pid, prop)
    mk += extra
    return f'<g transform="translate(400 0) scale(-1 1)">{mk}</g>' if mirrored else mk


def svg_sprite(box, markup, sid=""):
    x, y, w, h, _ = box
    return f'<svg {f"id={chr(34)}{sid}{chr(34)} " if sid else ""}x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" viewBox="0 0 400 1000" overflow="visible">{markup}</svg>'


def shot(sid, plate_png, layers, overlays="", root="contrast(1.05) saturate(1.05)", dim=0.0):
    over, _ = grade(vignette=.5, grain=.05, seed=hash(sid) % 97)
    return (f'<div class="shot" id="{sid}" style="filter:{root}"><div class="layer" id="{sid}-cam">'
            + (f'<img class="plate" src="{plate_png}"/>' if plate_png else "")
            + (f'<div class="layer" style="background:rgba(8,6,12,{dim})"></div>' if dim else "")
            + layers + f'</div>{overlays}{over}</div>')


def svg_layer(lid, inner, defs=""):
    return f'<svg id="{lid}" class="full" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" overflow="visible"><defs>{F.coin_defs(lid)}{defs}</defs>{inner}</svg>'


TAG = '<div class="tag">{}</div>'


def s1(t0, t1):
    """Medium-close: the founder opens the outlet valve; spending begins."""
    tx, ty, tw, th = 430, 80, 440, 660
    tank = F.tank_svg("tk1", tx, ty, tw, th, level=.82, label="BIGCART CASH")
    oy = ty + th - tw * .13 - 34
    pipe = F.glass_pipe("p1", [(tx + tw + 30, oy), (1990, oy)], 70, "SPENDING", label_pos=.62, label_size=30)
    vx, vy, vr = 1040, oy, 62
    valve = F.valve_wheel("v1", vx, vy, vr)
    # founder (same look as every shot), mirrored to face the tank; IK puts his hand on the wheel's rim
    sc = .64
    hand_screen = (vx + vr * .7, vy - vr * .7)
    a_grip = rig3.reach("stand", (330, 470))
    hx, hy = rig3.hand_point(a_grip, mirrored=True)
    X0, Y0 = hand_screen[0] - hx * sc, hand_screen[1] - hy * sc
    box = (X0, Y0, 400 * sc, 1000 * sc, sc)
    fdr = svg_sprite(box, figure("fd1", "founder", 0, 2, "parted", angles=a_grip, mirrored=True, expr="neutral"), "fd1s")
    cx, cy = tx + tw / 2, ty + th - tw * .13 + 62
    layers = svg_layer("s1-fx", tank + pipe + valve + fdr)
    js = f"""
FM.setLevel('tk1', .82); document.getElementById('tk1-needle').setAttribute('transform', 'rotate({-90 + 180 * .82:.1f} {cx} {cy})');
// anticipation: he settles his grip and leans back, then heaves the wheel round — the valve opens on "spending"
R3.keys('fd1', 'upper', [[.05, -3, .25], [.35, 4, .5, 'power3.inOut'], [1.0, 1, .4]]);
R3.keys('fd1', 'farm-front', [[.2, {a_grip['farm-front'] + 10}, .15], [.36, {a_grip['farm-front'] - 18}, .62, 'power3.inOut'], [1.0, {a_grip['farm-front'] - 12}, .3]]);
R3.keys('fd1', 'uarm-front', [[.36, {a_grip['uarm-front'] - 10}, .62, 'power3.inOut']]);
R3.keys('fd1', 'neck', [[.1, 10, .3], [.95, -4, .4]]);
FM.valve('v1', .22, 250, {{ dur: .75, anti: 16 }});
FM.coins('p1', .55, {CUT[1]}, {{ rate: 11, speed: 950, r: 23 }});
FM.level('tk1', .55, {CUT[1] - .55:.2f}, .74, 'none'); FM.needle('tk1-needle', {cx}, {cy}, .55, .9, .74);
R3.blink('fd1', 1.1);
tl.fromTo('#s1-cam', {{ scale: 1.03 }}, {{ scale: 1.0, transformOrigin: '50% 60%', duration: {CUT[1]}, ease: 'sine.out' }}, 0);
"""
    return layers, js, TAG.format("BigCart.com and Summit Ventures are fictional companies")


def s2(t0, t1):
    """Insert: coins pour into a TV, which powers on and plays the BigCart ad (advertising)."""
    tvx, tvy, tvw = 640, 150, 840
    tv = F.tv_set("tv", tvx, tvy, tvw)
    pipe = F.glass_pipe("p2", [(-70, 560), (tvx + 8, 560)], 70, "ADVERTISING", label_pos=.5, label_size=30)
    sx, sy, sw, sh = tvx + tvw * .09, tvy + tvw * .78 * .1, tvw * .66, tvw * .78 * .7
    glowd = '<radialGradient id="tvglow"><stop offset="0" stop-color="#7fb0ff" stop-opacity=".5"/><stop offset="1" stop-color="#7fb0ff" stop-opacity="0"/></radialGradient>'
    layers = svg_layer("s2-fx", f'<circle id="tv-glow" cx="{sx + sw / 2}" cy="{sy + sh / 2}" r="760" fill="url(#tvglow)" opacity="0"/>' + tv + pipe, glowd)
    w = W("advertising", "c03_04")
    js = f"""
FM.coins('p2', {t0}, {t1}, {{ rate: 11, speed: 950, r: 23 }});
FM.powerOn('tv', {w:.2f}); tl.fromTo('#tv-glow', {{ opacity: 0 }}, {{ opacity: 1, duration: .25, immediateRender: false }}, {w + .12:.2f});
tl.fromTo('#tv-fly', {{ x: 0, y: 0 }}, {{ x: {sw * .62:.0f}, y: {-sh * .72:.0f}, duration: 1.0, ease: 'power2.in', immediateRender: false }}, {w + .2:.2f});
tl.fromTo('#tv-flame', {{ scaleY: .7, transformOrigin: '50% 0%' }}, {{ scaleY: 1.25, duration: .07, yoyo: true, repeat: 15, ease: 'none', immediateRender: false }}, {w + .2:.2f});
FM.pop('#tv-logo', {w + .45:.2f}, {{ origin: '50% 50%' }}); tl.fromTo('#tv-tag', {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: .3, immediateRender: false }}, {w + .7:.2f});
tl.fromTo('#s2-cam', {{ scale: 1 }}, {{ scale: 1.045, transformOrigin: '60% 45%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0});
"""
    return layers, js, ""


C3 = Camera(pos=[-1.85, 1.5, -1.1], look=[-1.85, 1.0, -6], fov=50)
WS3 = [(-3.0, -3.5, "k1", "trader", 2, 0, "short"), (-0.7, -3.5, "k2", "suit_w", 5, 1, "bun"), (-3.0, -5.6, "k3", "casual", 3, 3, "curly"), (-0.7, -5.6, "k4", "casual2", 4, 6, "buzz")]


def s3(t0, t1):
    """Payroll: coins drop from the payroll pipe onto each desk as pay envelopes; staff at work; a new hire walks in."""
    live = ["const sc = S3.scene();"]
    for x, z, pid, cos, sk, hr, st in WS3:
        live.append(f"sc.box([{x + .2}, .72, {z - .62}], [{x + .92}, .76, {z + .62}], {{ color: '#8a6440' }}, {{}});"
                    f"[[{x + .24}, {z - .58}], [{x + .88}, {z - .58}], [{x + .24}, {z + .58}], [{x + .88}, {z + .58}]].forEach(([a, b]) => sc.box([a - .025, 0, b - .025], [a + .025, .72, b + .025], {{ color: '#3a3a40' }}, {{ shadow: false }}));"
                    f"sc.box([{x + .5}, .76, {z - .24}], [{x + .9}, 1.16, {z + .24}], {{ color: '#d8d0bc', gloss: .15 }}, {{}});"
                    f"sc.box([{x + .26}, .76, {z - .2}], [{x + .4}, .78, {z + .2}], {{ color: '#e4dccc' }}, {{ shadow: false }});"
                    f"sc.box([{x - .24}, .44, {z - .24}], [{x + .2}, .5, {z + .24}], {{ color: '#2a2a32' }}, {{}}); sc.box([{x - .3}, .5, {z - .22}], [{x - .25}, 1.02, {z + .22}], {{ color: '#2a2a32' }}, {{}});"
                    f"sc.cyl([{x - .02}, 0, {z}], .03, 0, .44, {{ color: '#555' }}, {{ seg: 6, shadow: false }});")
        mk = figure(pid, cos, sk, hr, st, pose="type", shadow=False, glasses=pid == "k2")
        live.append(f"sc.sprite([{x}, -.41, {z}], 1.76, {json.dumps(mk)}, .4, {{ viewBox: '0 0 400 1000', id: '{pid}' }});")
    box_prop = ('<g id="w3-box"><path d="M232 318 L352 318 L352 430 L232 430Z" fill="#c9a06a" stroke="#1b1410" stroke-width="4"/>'
                '<path d="M232 318 L292 300 L352 318" fill="#b08a56" stroke="#1b1410" stroke-width="3"/><rect x="250" y="356" width="84" height="30" fill="#2e5ab0"/></g>')
    mk = figure("w3", "suit", 1, 5, "short", pose="carry", extra=box_prop)
    live.append(f"sc.sprite([-4.4, 0, -4.55], 1.76, {json.dumps(mk)}, .4, {{ viewBox: '0 0 400 1000', id: 'w3' }});")
    # payroll pipe + drops + envelopes (screen space)
    pipe = F.glass_pipe("p3", [(-70, 96), (1990, 96)], 54, "PAYROLL", label_pos=.5, label_size=28)
    envs, drops = [], []
    we = W("employees", "c03_04")
    for i, (x, z, pid, *_r) in enumerate(WS3):
        e = C3.project([x + .33, .78, z + .32])
        s = min(1.45, 3.6 / e[2])
        envs.append(F.envelope(f"env{i}", e[0], e[1] - 14 * s, s))
        spout = f'<rect x="{e[0] - 20:.0f}" y="118" width="40" height="40" fill="url(#p3-brass)" stroke="{INK}" stroke-width="3"/>'
        envs.insert(0, spout)
        t = we + i * .13
        drops.append(f"FM.drop('s3-drops', [{e[0]:.0f}, 158], [{e[0]:.0f}, {e[1] - 18 * s:.0f}], {t:.2f}, {{ n: 4, dur: .38, r: {15 * s:.1f}, coinUid: 's3-fx' }});"
                     f"FM.pop('#env{i} .env', {t + .38:.2f});"
                     f"R3.rot('{pid}', 'neck', {t + .4:.2f}, 16, .3); R3.rot('{pid}', 'neck', {t + .9:.2f}, 6, .4);")
    fx = svg_layer("s3-fx", pipe + "".join(envs) + '<g id="s3-drops"></g>')
    layers = '<svg id="s3-live" class="full" viewBox="0 0 1920 1080"></svg>' + fx
    js = (f"{{ const cam = {C3.js(52, [-1.7, 1.05, -6])}; {OFFICE_LIGHT}\n" + "\n".join(live)
          + "\ndocument.getElementById('s3-live').innerHTML = S3.render(sc, cam, L, { ow: 2.0, shadowBlur: 5, uid: 'l3' });\n"
          + f"gsap.set(['#env0 .env', '#env1 .env', '#env2 .env', '#env3 .env'], {{ opacity: 0 }});\n"
          + "\n".join(drops)
          + f"\nFM.coins('p3', {t0}, {t1}, {{ rate: 12, speed: 1300, r: 17 }});"
          + "".join(f"\nR3.type('{pid}', {t0}, {t1}, {11 + i});" for i, (_x, _z, pid, *_r) in enumerate(WS3))
          + f"\nR3.walk(cam, 'w3', 'w3', [-4.4, 0, -4.55], [-2.3, 0, -4.55], 1.76, .4, {t0}, {t1}, .45);"
          + f"\ntl.fromTo('#s3-cam', {{ x: 30 }}, {{ x: -20, duration: {t1 - t0:.2f}, ease: 'none' }}, {t0}); }}")
    return layers, js, ""


C4 = Camera(pos=[-0.3, 1.5, -0.2], look=[0.75, 1.15, -6], fov=54)


def s4(t0, t1):
    """Infrastructure: a technician slides a new server into the rack; it lights up; coins feed the servers."""
    z0 = -1.4 - 2 * .66
    face = f"sc.art([1.19, .05, {z0 - .62}], [1.19, .05, {z0}], [1.19, 2.05, {z0 - .62}], 300, 1000, ART4.live, {{ bias: .15, id: 'rk' }});"
    server_prop = ('<g id="tc-box"><path d="M226 330 L372 312 L372 372 L226 392Z" fill="#c8ccd4" stroke="#1b1410" stroke-width="4"/>'
                   '<path d="M226 330 L262 318 L372 312" fill="#e0e4ea" stroke="#1b1410" stroke-width="3"/><rect x="290" y="330" width="50" height="22" fill="#2e5ab0"/></g>')
    mk = figure("tc", "casual2", 2, 0, "buzz", pose="carry", extra=server_prop)
    live = (f"const sc = S3.scene(); sc.box([1.2, 0, {z0 - .62}], [2.2, 2.1, {z0}], {{ color: '#1e2228' }}, {{ bias: -.5 }}); {face}"
            f"sc.sprite([.5, 0, {z0 - .25}], 1.76, {json.dumps(mk)}, .4, {{ viewBox: '0 0 400 1000', id: 'tc' }});")
    top = C4.project([1.7, 2.1, z0 - .31])
    pipe = F.glass_pipe("p4", [(-70, 150), (top[0], 150), (top[0], top[1] - 8)], 60, "SERVERS", label_pos=.42, label_size=30)
    fx = svg_layer("s4-fx", pipe)
    wi = W("infrastructure", "c03_04")
    layers = '<svg id="s4-live" class="full" viewBox="0 0 1920 1080"></svg>' + fx
    carry = rig3.pose_angles("carry")
    js = (f"{{ const cam = {C4.js(54, [0.75, 1.15, -6])}; {SERVER_LIGHT}\n{live}\n"
          f"document.getElementById('s4-live').innerHTML = S3.render(sc, cam, L, {{ ow: 2.0, shadowBlur: 5, uid: 'l4' }});\n"
          f"FM.coins('p4', {t0}, {t1}, {{ rate: 11, speed: 1100, r: 19 }});\n"
          # push: anticipation (pull the server back), shove it in, follow-through
          f"R3.keys('tc', 'upper', [[{wi - .12:.2f}, -3, .14], [{wi + .04:.2f}, 6, .22, 'power3.out'], [{wi + .4:.2f}, 2, .3]]);\n"
          f"R3.keys('tc', 'uarm-front', [[{wi - .12:.2f}, {carry['uarm-front'] + 10}, .14], [{wi + .04:.2f}, {carry['uarm-front'] - 34}, .22, 'power3.out']]);\n"
          f"R3.keys('tc', 'uarm-back', [[{wi - .12:.2f}, {carry['uarm-back'] + 10}, .14], [{wi + .04:.2f}, {carry['uarm-back'] - 30}, .22, 'power3.out']]);\n"
          f"tl.to('#tc-box', {{ x: 70, y: -6, duration: .22, ease: 'power3.out' }}, {wi + .04:.2f}); tl.to('#tc-box', {{ opacity: 0, duration: .06 }}, {wi + .24:.2f});\n"
          f"tl.fromTo('#rk-new', {{ opacity: 0 }}, {{ opacity: 1, duration: .06, immediateRender: false }}, {wi + .22:.2f});\n"
          f"tl.fromTo('#rk-newled', {{ opacity: 0 }}, {{ opacity: 1, duration: .05, immediateRender: false }}, {wi + .35:.2f});\n"
          + "".join(f"tl.fromTo('#rk-led{r}', {{ opacity: .25 }}, {{ opacity: 1, duration: .05, immediateRender: false }}, {wi + .3 + abs(r - 8.5) * .025:.3f});" for r in range(20) if r not in (8, 9))
          + f"\nR3.rot('tc', 'neck', {wi + .45:.2f}, 8, .3);\n"
          f"tl.fromTo('#s4-cam', {{ scale: 1.0 }}, {{ scale: 1.05, transformOrigin: '62% 45%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0}); }}")
    return layers, js, ""


def mechanism(sid, level, investor=False):
    """Wide money machine: revenue in (left), the cash tank, three spending outflows (right); optional investor pipe."""
    tx, ty, tw, th = 760, 250, 400, 540
    e = tw * .13
    oy = ty + th - e - 34
    parts = []
    src = (f'<g><rect x="60" y="470" width="270" height="180" rx="14" fill="#3a2a1e" stroke="{INK}" stroke-width="4"/>'
           f'<rect x="76" y="486" width="238" height="148" rx="8" fill="#f4ead5"/>'
           f'<path d="M120 520 H150 L172 590 H262 L280 540 H160" fill="none" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
           f'<circle cx="182" cy="610" r="10" fill="{INK}"/><circle cx="252" cy="610" r="10" fill="{INK}"/>'
           f'{F.brass_plate(195, 690, "CUSTOMERS", 26)}</g>')
    parts.append(src)
    parts.append(F.glass_pipe(f"{sid}r", [(330, 560), (tx - 6, 560)], 30, "REVENUE", label_pos=.5, label_size=22))
    parts.append(f'<rect x="{tx - 22}" y="540" width="26" height="40" fill="url(#{sid}r-brass)" stroke="{INK}" stroke-width="3"/>')
    ys = [(380, "ADVERTISING"), (545, "PAYROLL"), (oy, "SERVERS")]
    for k, (y, lab) in enumerate(ys):
        pts = [(tx + tw + 30, oy), (1330, oy)] + ([(1330, y)] if y != oy else []) + [(1990, y)]
        parts.append(F.glass_pipe(f"{sid}b{k}", pts, 46, lab, label_pos=.42, label_size=24))
    # destination icons on the right
    parts.append(f'<g transform="translate(1800 336) scale(.17)">{F.tv_set("ico-tv-" + sid, 0, 0, 760)}</g>')
    parts.append("".join(F.envelope(f"ico-env{sid}{k}", 1840 + k * 14, 520 - k * 10, .8) for k in range(3)))
    parts.append(f'<g transform="translate(1800 {oy - 60})"><rect width="90" height="120" rx="6" fill="#1e2228" stroke="{INK}" stroke-width="3"/>'
                 + "".join(f'<rect x="8" y="{8 + r * 18}" width="74" height="13" rx="2" fill="#2c3138"/><circle cx="70" cy="{14 + r * 18}" r="3" fill="#5aff7a"/>' for r in range(6)) + '</g>')
    if investor:
        parts.append(f'<g id="{sid}-inv">' + F.glass_pipe(f"{sid}i", [(-80, 150), (tx + tw / 2, 150), (tx + tw / 2, ty + e + 60)], 60, "INVESTOR CAPITAL", label_pos=.35, label_size=28) + '</g>')
    parts.append(F.tank_svg(f"{sid}t", tx, ty, tw, th, level=level, label="BIGCART CASH"))
    cx, cy = tx + tw / 2, ty + th - e + 62
    return svg_layer(f"{sid}-fx", "".join(parts)), (cx, cy), oy


def s5(t0, t1):
    layers, (cx, cy), oy = mechanism("m5", .64)
    wr = W("revenue", "c03_04")
    kin = (ktext("m5-out", "MONEY OUT", by="word", style="position:absolute;left:1350px;top:196px;font:800 84px Fraunces;color:#ff9a7a;text-shadow:0 4px 18px rgba(0,0,0,.6)")
           + ktext("m5-in", "money in", by="word", style="position:absolute;left:96px;top:392px;font:800 40px Fraunces;color:#9fe39a;text-shadow:0 4px 14px rgba(0,0,0,.6)"))
    js = f"""
tl.fromTo('#s5-cam', {{ scale: 1.22 }}, {{ scale: 1, transformOrigin: '50% 62%', duration: .8, ease: 'power2.out' }}, {t0});
document.getElementById('m5t-needle').setAttribute('transform', 'rotate({-90 + 180 * .64:.1f} {cx} {cy})');
[0, 1, 2].forEach(k => FM.coins('m5b' + k, {t0}, {t1}, {{ rate: 6, speed: 650, r: 16 }}));
FM.level('m5t', {t0 + .3:.2f}, {t1 - t0 - .5:.2f}, .4, 'none'); FM.needle('m5t-needle', {cx}, {cy}, {t0 + .3:.2f}, {t1 - t0 - .5:.2f}, .4, {{ ease: 'none', wobble: false }});
FM.coins('m5r', {wr:.2f}, {wr + .9:.2f}, {{ rate: 2.2, speed: 300, r: 11 }});
mReveal('#m5-out', {t0 + .35:.2f}, {{ by: 'word' }}); mReveal('#m5-in', {wr + .05:.2f}, {{ by: 'word' }});
tl.to('#s5-cam', {{ scale: 1.35, transformOrigin: '{cx}px {cy}px', duration: .32, ease: 'power2.in' }}, {t1 - .32:.2f});   // push into the gauge
"""
    return layers, js, kin


def s6(t0, t1):
    """Close-up: the cash gauge falls into the red; warning lamp."""
    tank = F.tank_svg("tk6", 1210, -980, 860, 1980, level=.3, label=None, gauge=False)
    dial = F.gauge_dial("g6", 720, 500, 300, frac=.34, label="BIGCART CASH")
    layers = svg_layer("s6-fx", tank + dial)
    ws = W("sustain", "c03_04")
    js = f"""
FM.needle('g6-needle', 720, 500, {ws:.2f}, .95, .07, {{ ease: 'power2.in' }});
FM.level('tk6', {t0 + .1:.2f}, {t1 - t0 - .2:.2f}, .1, 'sine.in');
tl.fromTo('#g6-lamp', {{ opacity: 0 }}, {{ opacity: 1, duration: .05, immediateRender: false }}, {ws + .6:.2f}); FM.lamp('g6-lamp', {ws + .6:.2f}, {t1}, .38);
tl.fromTo('#s6-red', {{ opacity: 0 }}, {{ opacity: .5, duration: .19, yoyo: true, repeat: 5, ease: 'none', immediateRender: false }}, {ws + .6:.2f});
tl.fromTo('#s6-cam', {{ scale: 1.0 }}, {{ scale: 1.06, transformOrigin: '38% 46%', duration: {t1 - t0:.2f}, ease: 'sine.in' }}, {t0});
"""
    red = '<div id="s6-red" class="layer" style="background:radial-gradient(ellipse 900px 700px at 70% 30%,rgba(255,40,30,.45),rgba(255,40,30,0) 70%);mix-blend-mode:screen;opacity:0"></div>'
    return layers, js, red


C7A = Camera(pos=[-0.35, 1.5, 0.1], look=[-0.15, 1.28, -4], fov=46)     # medium: the investors at the table
C7C = Camera(pos=[2.0, 1.45, -2.3], look=[3.3, 1.2, -6], fov=44)         # medium: the capital valve on the wall
DOC_C = [0.62, .79, -3.12]
INV1, INV2, INV3 = [0.1, 0, -3.6], [-1.25, 0, -3.6], [2.95, 0, -5.3]
VALVE3D = [3.55, 1.25, -5.85]
DOC_SVG = ('<rect width="700" height="560" fill="#f6f0e2" stroke="#1b1410" stroke-width="6"/>'
           '<text x="350" y="92" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="62" fill="#1b1410">TERM SHEET</text>'
           '<text x="350" y="160" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="#2e5ab0">BigCart.com</text>'
           + "".join(f'<rect x="70" y="{200 + k * 40}" width="{520 - (k * 61) % 160}" height="14" fill="#9a9080"/>' for k in range(6))
           + '<g class="stampmark" opacity="0"><rect x="300" y="350" width="330" height="130" rx="10" fill="none" stroke="#c8281c" stroke-width="14" transform="rotate(-10 465 415)"/>'
             '<text x="465" y="445" text-anchor="middle" font-family="Inter" font-weight="800" font-size="84" fill="#c8281c" transform="rotate(-10 465 415)">FUNDED</text></g>')


def board_live(cam: Camera, uid: str, a_iv1: dict, a_iv3: dict | None = None) -> str:
    doc = DOC_SVG.replace('class="stampmark"', f'id="{uid}-stamp"')
    return ("const sc = S3.scene();" + BOARD_TABLE
            + f"sc.art([{DOC_C[0] - .3}, .792, {DOC_C[2] + .24}], [{DOC_C[0] + .3}, .792, {DOC_C[2] + .24}], [{DOC_C[0] - .3}, .792, {DOC_C[2] - .24}], 700, 560, {json.dumps(doc)}, {{ bias: .4 }});"
            + "".join(f"sc.box([{x - .26}, .45, -4.0], [{x + .26}, .52, -3.5], {{ color: '#2a1a14' }}, {{}}); sc.box([{x - .26}, .52, -4.03], [{x + .26}, 1.25, -3.95], {{ color: '#2a1a14' }}, {{}});" for x in (-1.9, 1.5))
            + f"sc.sprite({INV1}, 1.76, {json.dumps(figure(uid + 'a', 'suit', 1, 5, 'short', angles=a_iv1, prop='stamp'))}, .4, {{ viewBox: '0 0 400 1000', id: '{uid}a' }});"
            + f"sc.sprite({INV2}, 1.76, {json.dumps(figure(uid + 'b', 'suit_w', 5, 1, 'bun', pose='talk', expr='talk', glasses=True))}, .4, {{ viewBox: '0 0 400 1000', id: '{uid}b' }});"
            + f"sc.sprite({INV3}, 1.76, {json.dumps(figure(uid + 'c', 'suit', 0, 0, 'parted', angles=a_iv3, pose='stand'))}, .4, {{ viewBox: '0 0 400 1000', id: '{uid}c' }});")


def wall_pipe(cam: Camera, uid: str):
    vp = cam.project(VALVE3D)
    pa, pb = cam.project([-4.9, 1.25, -5.9]) or (-80, vp[1]), cam.project([4.9, 1.25, -5.9]) or (2000, vp[1])
    pipe = F.glass_pipe(uid, [(min(pa[0], 0) - 60, vp[1]), (max(pb[0], 1920) + 60, vp[1])], 46, "INVESTOR CAPITAL  →  BIGCART", label_pos=.3, label_size=24)
    return pipe, vp


def s7a(t0, t1):
    """Boardroom medium: the investors weigh BigCart's request; one lifts the FUNDED stamp (anticipation for the insert)."""
    b1 = sprite_box(C7A, INV1)
    dp = C7A.project(DOC_C)
    tgt = to_view(b1, (dp[0], dp[1]))
    a_rest = rig3.reach("stand", (tgt[0] - 50, tgt[1] - 70))
    a_up = rig3.reach("stand", (tgt[0] - 10, tgt[1] - 260))
    pipe, vp = wall_pipe(C7A, "p7a")
    layers = svg_layer("s7a-pipe", pipe + F.valve_wheel("v7a", vp[0], vp[1], 40)) + '<svg id="s7a-live" class="full" viewBox="0 0 1920 1080"></svg>'
    ws, wd = W("survival", "c03_05"), W("depended", "c03_05")
    js = (f"{{ const cam = {C7A.js()}; {BOARD_LIGHT}\n{board_live(C7A, 'q', a_rest)}\n"
          f"document.getElementById('s7a-live').innerHTML = S3.render(sc, cam, L, {{ ow: 2.0, shadowBlur: 5, uid: 'l7a' }});\n"
          f"R3.talk('qb', {t0 + .1:.2f}, {wd + .5:.2f}, 71); R3.keys('qb', 'uarm-front', [[{t0 + .05:.2f}, -40, .3], [{ws:.2f}, -74, .35], [{wd:.2f}, -50, .4]]);\n"
          f"R3.keys('qb', 'neck', [[{t0:.2f}, -2, 0], [{ws + .1:.2f}, 8, .35], [{wd + .3:.2f}, 0, .4]]); R3.keys('qb', 'upper', [[{ws:.2f}, -3, .4]]);\n"
          f"R3.keys('qa', 'neck', [[{t0:.2f}, 16, 0], [{wd + .25:.2f}, 4, .35]]);\n"
          f"R3.keys('qa', 'uarm-front', [[{wd + .35:.2f}, {a_up['uarm-front'] + 8}, .18, 'power2.out'], [{wd + .53:.2f}, {a_up['uarm-front']}, .45, 'power2.inOut']]);\n"
          f"R3.keys('qa', 'farm-front', [[{wd + .53:.2f}, {a_up['farm-front']}, .45, 'power2.inOut']]);\n"
          f"R3.keys('qa', 'upper', [[{wd + .5:.2f}, -4, .4]]);\n"
          f"R3.blinks('qa', {t0}, {t1}, 72); R3.blinks('qb', {t0}, {t1}, 73); R3.blinks('qc', {t0}, {t1}, 74); R3.idle('qc', {t0}, {t1}, 75, 4);\n"
          f"tl.fromTo('#s7a-cam', {{ scale: 1.0 }}, {{ scale: 1.06, transformOrigin: '48% 52%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0}); }}")
    return layers, js, TAG.format("Summit Ventures and BigCart.com are fictional companies")


def s7b(t0, t1):
    """Insert close-up: the stamp slams FUNDED onto BigCart's term sheet on "investors"."""
    doc = DOC_SVG.replace('class="stampmark"', 'id="ins-stamp"')
    desk = ('<pattern id="ins-wood" patternUnits="userSpaceOnUse" width="900" height="900"><image href="tex/wood_floor.jpg" width="900" height="900"/></pattern>')
    hand = ('<g id="ins-hand"><path d="M1010 -400 L1170 -400 L1150 120 L1030 120Z" fill="#26303e" stroke="#1b1410" stroke-width="6"/>'
            '<rect x="1022" y="100" width="136" height="40" rx="8" fill="#eef2f6" stroke="#1b1410" stroke-width="5"/>'
            '<path d="M1030 140 C1010 190 1020 240 1060 250 L1130 250 C1170 240 1176 190 1152 140Z" fill="#c98f63" stroke="#1b1410" stroke-width="5"/>'
            '<rect x="1060" y="232" width="64" height="120" rx="14" fill="#5a3a22" stroke="#1b1410" stroke-width="5"/>'
            '<rect x="990" y="342" width="204" height="56" rx="8" fill="#b8322a" stroke="#1b1410" stroke-width="5"/></g>')
    body = (f'<rect width="1920" height="1080" fill="url(#ins-wood)"/><rect width="1920" height="1080" fill="#3a1e10" opacity=".55"/>'
            f'<g transform="translate(560 250) rotate(-4) scale(1.15)">{doc}</g>'
            '<ellipse id="ins-shadow" cx="1092" cy="640" rx="140" ry="40" fill="#000" opacity="0"/>'
            f'<g transform="translate(0 0)">{hand}</g>')
    layers = svg_layer("s7b-fx", body, desk)
    wi = W("investors", "c03_05")
    js = f"""
// anticipation: the stamp hovers, lifts a touch, then slams; squash on impact; the mark is left behind as it lifts
tl.fromTo('#ins-hand', {{ y: -120 }}, {{ y: -170, duration: {wi - .1 - t0:.2f}, ease: 'sine.inOut', immediateRender: false }}, {t0});
gsap.set('#ins-hand', {{ y: -120 }});
tl.to('#ins-hand', {{ y: 240, duration: .1, ease: 'power3.in' }}, {wi - .1:.2f});
tl.to('#ins-hand', {{ scaleY: .93, transformOrigin: '50% 100%', duration: .05, yoyo: true, repeat: 1 }}, {wi:.2f});
tl.fromTo('#ins-shadow', {{ opacity: 0 }}, {{ opacity: .45, duration: .1, immediateRender: false }}, {wi - .1:.2f});
tl.to('#ins-hand', {{ y: -260, duration: .32, ease: 'power2.out' }}, {wi + .16:.2f}); tl.to('#ins-shadow', {{ opacity: 0, duration: .2 }}, {wi + .16:.2f});
tl.fromTo('#ins-stamp', {{ opacity: 0 }}, {{ opacity: 1, duration: .02, immediateRender: false }}, {wi + .01:.2f});
tl.to('#s7b-cam', {{ x: 6, y: 6, duration: .04, yoyo: true, repeat: 3, ease: 'none' }}, {wi:.2f});
tl.fromTo('#s7b-cam', {{ scale: 1.04 }}, {{ scale: 1.0, transformOrigin: '50% 50%', duration: {t1 - t0:.2f}, ease: 'sine.out' }}, {t0});
"""
    return layers, js, ""


def s7c(t0, t1):
    """The capital valve opens: coins stream along the wall pipe toward BigCart."""
    b3 = sprite_box(C7C, INV3)
    pipe, vp = wall_pipe(C7C, "p7c")
    vt = to_view(b3, (vp[0], vp[1]))
    a_valve = rig3.reach("stand", (vt[0], vt[1]))
    b1 = sprite_box(C7C, INV1)
    layers = svg_layer("s7c-pipe", pipe + F.valve_wheel("v7c", vp[0], vp[1], 46)) + '<svg id="s7c-live" class="full" viewBox="0 0 1920 1080"></svg>'
    a_rest1 = rig3.pose_angles("stand")
    js = (f"{{ const cam = {C7C.js()}; {BOARD_LIGHT}\n{board_live(C7C, 'u', a_rest1, a_valve)}\n"
          f"document.getElementById('s7c-live').innerHTML = S3.render(sc, cam, L, {{ ow: 2.0, shadowBlur: 5, uid: 'l7c' }});\n"
          f"gsap.set('#u-stamp', {{ opacity: 1 }});\n"
          f"FM.valve('v7c', {t0 + .05:.2f}, 300, {{ dur: .5, anti: 18 }});\n"
          f"R3.keys('uc', 'farm-front', [[{t0 + .05:.2f}, {a_valve['farm-front'] + 10}, .14], [{t0 + .19:.2f}, {a_valve['farm-front'] - 22}, .5, 'power3.inOut']]);\n"
          f"R3.keys('uc', 'upper', [[{t0 + .05:.2f}, -2, .14], [{t0 + .19:.2f}, 3, .5, 'power3.inOut']]);\n"
          f"FM.coins('p7c', {t0 + .35:.2f}, {t1}, {{ rate: 12, speed: 1000, r: 17 }});\n"
          f"tl.fromTo('#s7c-cam', {{ scale: 1.0 }}, {{ scale: 1.04, transformOrigin: '60% 50%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0}); }}")
    return layers, js, ""


def s8(t0, t1):
    layers, (cx, cy), oy = mechanism("m8", .4, investor=True)
    wc = W("capital", "c03_05")
    kin = (ktext("m8-out", "MONEY OUT", by="word", style="position:absolute;left:1350px;top:196px;font:800 84px Fraunces;color:#ff9a7a;text-shadow:0 4px 18px rgba(0,0,0,.6)")
           + ktext("m8-cap", "INVESTOR CAPITAL IN", by="word", style="position:absolute;left:96px;top:300px;font:800 60px Fraunces;color:#ffd56a;text-shadow:0 4px 18px rgba(0,0,0,.6)"))
    js = f"""
document.getElementById('m8t-needle').setAttribute('transform', 'rotate({-90 + 180 * .14:.1f} {cx} {cy})'); FM.setLevel('m8t', .14);
gsap.set('#m8-out', {{ opacity: 1 }});
tl.fromTo('#m8-inv', {{ y: -260 }}, {{ y: 0, duration: .45, ease: 'power3.out', immediateRender: false }}, {t0});
gsap.set('#m8-inv', {{ y: -260 }});
FM.coins('m8i', {t0 + .4:.2f}, {wc:.2f}, {{ rate: 14, speed: 900, r: 20 }}); FM.coins('m8i', {wc:.2f}, {t1}, {{ rate: 22, speed: 1000, r: 20 }});
[0, 1, 2].forEach(k => FM.coins('m8b' + k, {t0}, {t1}, {{ rate: 6, speed: 650, r: 16 }}));
FM.coins('m8r', {t0 + .8:.2f}, {t1}, {{ rate: 1.2, speed: 300, r: 11 }});
FM.level('m8t', {t0 + .9:.2f}, {t1 - t0 - 1.1:.2f}, .66, 'sine.inOut'); FM.needle('m8t-needle', {cx}, {cy}, {t0 + .9:.2f}, {t1 - t0 - 1.1:.2f}, .66, {{ wobble: false }});
mReveal('#m8-cap', {t0 + .55:.2f}, {{ by: 'word' }}); tl.to('#m8-cap', {{ scale: 1.08, transformOrigin: '0% 50%', duration: .25, yoyo: true, repeat: 1 }}, {wc:.2f});
tl.fromTo('#s8-cam', {{ scale: 1.0 }}, {{ scale: 1.04, transformOrigin: '50% 45%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0});
"""
    return layers, js, kin


# ── build ────────────────────────────────────────────────────────────────────────────────────────
def prepare(ws: Path) -> None:
    draft = ROOT / "projects/ai-bubble-vs-dot-com/draft"
    ws.mkdir(parents=True, exist_ok=True)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(draft / f, ws / f)
    for d in ("fonts", "vendor"):
        if not (ws / d).exists():
            shutil.copytree(draft / d, ws / d)
    for f in ("scene3d.js", "rig3.js", "finmotion.js"):
        shutil.copy(EL / "kit" / f, ws / "vendor" / f)
    (ws / "tex").mkdir(exist_ok=True)
    for f in (EL / "kit/assets/textures").glob("*.jpg"):
        shutil.copy(f, ws / "tex" / f.name)


def plates(ws: Path) -> dict:
    pd = ws / "plates"
    cam = lambda pos, look, fov, glows="": f"{glows}const cam = S3.camera({{ pos: {pos}, look: {look}, fov: {fov} }});"
    office_glows = "const GLOWS = [" + ",".join(f"[[{x},3.05,{z}],{r},'#fff2cc']" for x, z, r in ((-2.4, 1, 150), (1.6, 1, 150), (-2.4, -2.2, 110), (1.6, -2.2, 110), (-2.4, -5.4, 80), (1.6, -5.4, 80))) + "];"
    art4 = f"const ART4 = {json.dumps({'rack': rack_art(), 'live': rack_art(True)})};"
    name_svg = ('<rect width="1200" height="40" fill="none"/><text x="600" y="32" text-anchor="middle" font-family="Fraunces" font-weight="800" '
                'font-size="34" letter-spacing="14" fill="#e9dcbc">SUMMIT VENTURES</text>')
    art5 = f"const ART5 = {json.dumps({'window': SF2.art2_dict()['window'], 'plant': SF2.art2_dict()['plant'], 'name': name_svg})};"
    specs = {
        "office_tank": (office_scene(), cam([0.4, 1.45, 0.8], [2.2, 1.3, -8], 55, office_glows), OFFICE_LIGHT, 7),
        "office_window": (office_scene(), cam([1.5, 1.5, 0.5], [-4.6, 1.7, -3.6], 50, office_glows), OFFICE_LIGHT, 9),
        "office_floor": (office_scene(drop_desks=True), office_glows + f"const cam = {C3.js()};", OFFICE_LIGHT, 0),
        "servers": (art4 + SERVER_SCENE, f"const cam = {C4.js()};", SERVER_LIGHT, 0),
        "boardroom_a": (art5 + BOARD_SCENE + BOARD_TABLE, "const GLOWS = [[[-1.6,2.5,-2.7],160,'#ffd8a0'],[[1.6,2.5,-2.7],160,'#ffd8a0']];" + f"const cam = {C7A.js()};", BOARD_LIGHT, 0),
        "boardroom_c": (art5 + BOARD_SCENE, "const GLOWS = [[[1.6,2.5,-2.7],160,'#ffd8a0']];" + f"const cam = {C7C.js()};", BOARD_LIGHT, 0),
    }
    out = {}
    for name, (scene_js, cam_js, light_js, blur) in specs.items():
        html = plate_html(pd / f"{name}.html", scene_js, cam_js, light_js, blur=blur, root="contrast(1.05) saturate(1.05)")
        png = plate(pd, name, html, assets=tuple(sorted((EL / "kit/assets/textures").glob("*.jpg"))) + (EL / "kit/scene3d.js",))
        out[name] = "plates/" + png.name
    return out


def caption_pages():
    out = []
    for p in TL.PAGES:
        if OFF - .01 <= p["start"] and p["end"] <= OFF + D + .5:
            out.append({"start": round(p["start"] - OFF, 3), "end": round(min(D, p["end"] - OFF), 3), "text": p["text"],
                        "words": [{"word": w["word"], "start": round(w["start"] - OFF, 3), "end": round(w["end"] - OFF, 3)} for w in p["words"]]})
    return out


def narration(ws: Path):
    src = ROOT / "projects/ai-bubble-vs-dot-com/draft/narration.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", f"atrim={OFF}:{OFF + D},asetpts=PTS-STARTPTS,apad=whole_dur={D}",
                    str(ws / "narration.wav")], check=True)


def build(ws: Path):
    prepare(ws)
    P = plates(ws)
    shots = [("s1", s1, "office_tank", .25), ("s2", s2, "office_window", .2), ("s3", s3, "office_floor", 0), ("s4", s4, "servers", 0),
             ("s5", s5, "office_tank", .45), ("s6", s6, "office_tank", .55), ("s7a", s7a, "boardroom_a", 0), ("s7b", s7b, None, 0), ("s7c", s7c, "boardroom_c", 0),
             ("s8", s8, "office_tank", .45)]
    scenes = []
    for i, (sid, fn, pl, dim) in enumerate(shots):
        t0, t1 = CUT[i], CUT[i + 1]
        layers, js, over = fn(t0, t1)
        scenes.append(Scene(sid, t0, round(t1 - t0, 3), shot(sid, P[pl] if pl else None, layers, over, dim=dim), js="{\n" + js + "\n}"))
    poses = {k: rig3.pose_angles(k) for k in rig3.POSES}
    css = (".shot{position:absolute;inset:0;overflow:hidden;background:#100c0c}.layer{position:absolute;inset:0}.full{position:absolute;inset:0;width:1920px;height:1080px}"
           ".plate{position:absolute;left:0;top:0;width:1920px;height:1080px}"
           ".tag{position:absolute;right:64px;top:56px;padding:10px 20px;border-radius:8px;background:rgba(12,14,24,.62);color:#f3e9d6;font:700 28px Inter}"
           "@font-face{font-family:Inter;src:url(fonts/inter-latin-700-normal.woff2) format('woff2');font-weight:800}")
    html = assemble(title="Epoch Ledger — office sequence v2", duration=D, scenes=scenes, caption_pages=caption_pages(), extra_css=css,
                    head_scripts=["vendor/scene3d.js", "vendor/rig3.js", "vendor/finmotion.js"], vignette=False,
                    shared_js=f"const TEX = 'tex/';\nconst ART = {json.dumps(common.ART)};\nconst ART4 = {json.dumps({'live': rack_art(True)})};\nR3.P = {json.dumps(poses)};")
    (ws / "index.html").write_text(html)
    narration(ws)
    print("wrote", ws / "index.html", f"({D}s, {len(scenes)} shots)")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "projects/ai-bubble-vs-dot-com/office_v2")
