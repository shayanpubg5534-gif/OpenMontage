"""Style frame 3 — expressive close-up (c03_06 "...the money ran out", ~4:02).

Scene plan: close-up, late night, the founder alone at his desk. Focal point: his worried face, lit from the right by
the CRT, phone pressed to his ear (calling investors). Diegetic financial graphic: the CRT screen in the right
foreground shows the company's cash balance falling toward zero and the runway countdown — the data is on an object in
the scene, not a floating panel. Supporting story props: the term sheet on the desk, cold coffee, a calculator.
Background: the empty BigCart office (scene3d interior at night, real perspective) thrown out of focus, city lights
in the window, CRT bokeh. Technique: rig v3 portrait + scene3d background + 2.5D layers + lightfx (glow, grade).
Light: cool cyan/red key from the screen (screen-right), warm desk-lamp fill low on the left, deep blue ambient.
"""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from kit.lightfx import glow, grade  # noqa: E402
from kit.diegetic import crt_chart  # noqa: E402
from kit.rig3 import closeup_svg  # noqa: E402
from styleframes.common import page  # noqa: E402

O = "#1b1410"
WINDOW_NIGHT = """<defs><linearGradient id="wsn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070a1c"/><stop offset=".7" stop-color="#1a2046"/><stop offset="1" stop-color="#3a2a4a"/></linearGradient></defs>
<rect width="800" height="600" fill="url(#wsn)"/>""" + "".join(
    f'<rect x="{x}" y="{600 - h}" width="{w}" height="{h}" fill="#11142a"/>' + "".join(
        f'<rect x="{x + 8 + c * 18}" y="{610 - h + r * 26}" width="9" height="14" fill="#ffd27a" opacity="{.5 + ((x + r + c) % 3) * .2:.2f}"/>'
        for r in range(h // 30) for c in range(max(1, (w - 12) // 18)) if (x * 7 + r * 5 + c * 3) % 5 == 0)
    for x, w, h in [(0, 110, 260), (120, 80, 360), (210, 140, 220), (360, 90, 420), (460, 130, 300), (600, 90, 380), (700, 100, 250)]) + \
    '<rect width="800" height="600" fill="none" stroke="#1a1a22" stroke-width="22"/><path d="M400 0 V600 M0 300 H800" stroke="#1a1a22" stroke-width="12"/>'
SCREEN_DIM = '<rect width="400" height="300" fill="#0a2a3a"/>' + "".join(f'<rect x="20" y="{40 + i * 36}" width="{150 + (i * 61) % 180}" height="14" fill="#5fb8e0" opacity=".7"/>' for i in range(6))

SCENE = r"""
const sc = S3.scene();
const wall = { color: '#4a4a6a', outline: false }, floorM = { color: '#3a2a26', outline: false, receiver: true };
sc.ground(-6, -16, 6, 2, 0, 3, floorM);
sc.quad([-6, 0, -16], [6, 0, -16], [6, 3.1, -16], [-6, 3.1, -16], wall, { bias: -3 });
sc.quad([-6, 0, 2], [-6, 0, -16], [-6, 3.1, -16], [-6, 3.1, 2], wall, { bias: -3 });
sc.quad([6, 0, -16], [6, 0, 2], [6, 3.1, 2], [6, 3.1, -16], wall, { bias: -3 });
sc.quad([-6, 3.1, 2], [-6, 3.1, -16], [6, 3.1, -16], [6, 3.1, 2], { color: '#2a2a3a', emissive: .25, outline: false }, { bias: -3, allowBack: true });
// big window wall on the back with the night city
[-3.4, 0, 3.4].forEach((x) => { sc.art([x - 1.6, .7, -15.95], [x + 1.6, .7, -15.95], [x - 1.6, 2.8, -15.95], 800, 600, ART3.window, { bias: .1 }); });
// rows of empty desks with sleeping CRTs (a few still on)
for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) { const x = -3.6 + c * 3.2, z = -4 - r * 3.4;
  sc.box([x - .8, .72, z - .42], [x + .8, .76, z + .42], { color: '#4a3424', outline: false }, {});
  sc.box([x - .24, .76, z - .3], [x + .24, 1.14, z + .08], { color: '#8a8478', outline: false }, {});
  if ((r + c) % 2 === 0) sc.art([x - .19, .82, z + .085], [x + .19, .82, z + .085], [x - .19, 1.08, z + .085], 400, 300, ART3.screen, { bias: .1 }); }
// one desk lamp still on in the distance
sc.cyl([2.8, .76, -7.3], .05, .76, 1.2, { color: '#2a2a2a', outline: false }, { seg: 8 });
"""


def crt_svg() -> str:
    """Hand-drawn CRT in three-quarter view (screen turned toward the founder), with the falling cash chart."""
    # illustrative cash curve for "...the money ran out" (shape, not a sourced figure)
    chart = crt_chart("BigCart — CASH BALANCE", [100, 98, 93, 85, 74, 61, 46, 32, 18], "RUNWAY LEFT", "3 MONTHS", uid="sf3crt")
    return f"""<svg viewBox="0 0 900 900" width="900" height="900" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="scrglow" cx=".5" cy=".5" r=".6"><stop offset="0" stop-color="#fff" stop-opacity=".18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="caseg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#cfc6b2"/><stop offset="1" stop-color="#8a8272"/></linearGradient></defs>
<path d="M150 90 L700 40 L860 120 L860 720 L700 800 L150 760Z" fill="url(#caseg)" stroke="{O}" stroke-width="5" stroke-linejoin="round"/>
<path d="M700 40 L860 120 L860 720 L700 800Z" fill="#7a7262" stroke="{O}" stroke-width="5" stroke-linejoin="round"/>
<path d="M150 90 L700 40 L700 800 L150 760Z" fill="#d8d0bc" stroke="{O}" stroke-width="5" stroke-linejoin="round"/>
<g transform="matrix(.8 -.07 0 1.12 190 140)"><rect x="-10" y="-10" width="660" height="500" rx="26" fill="#2a2620"/>
<g clip-path="inset(0 round 18px)">{chart}</g><rect width="640" height="480" rx="18" fill="url(#scrglow)"/></g>
<path d="M150 760 L700 800 L700 830 L150 790Z" fill="#b8b0a0" stroke="{O}" stroke-width="4"/>
<circle cx="640" cy="770" r="9" fill="#5aff7a"/></svg>"""


def desk_svg() -> str:
    """Desk top running across the bottom of frame: term sheet, calculator, cold coffee."""
    lines = "".join(f'<rect x="{60}" y="{100 + k * 26}" width="{360 - (k * 53) % 140}" height="9" fill="#8a8478"/>' for k in range(7))
    return f"""<svg viewBox="0 0 1920 300" width="1920" height="300" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="dk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a3a26"/><stop offset="1" stop-color="#2a1a12"/></linearGradient>
<linearGradient id="dkl" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#ff6a5a" stop-opacity=".35"/><stop offset=".5" stop-color="#ff6a5a" stop-opacity="0"/></linearGradient></defs>
<path d="M0 40 L1920 20 L1920 300 L0 300Z" fill="url(#dk)" stroke="{O}" stroke-width="4"/><path d="M0 40 L1920 20 L1920 300 L0 300Z" fill="url(#dkl)"/>
<g transform="translate(980 60) rotate(-8)"><rect width="480" height="300" fill="#f2ecdc" stroke="{O}" stroke-width="3"/>
<text x="60" y="64" font-family="Fraunces" font-weight="800" font-size="40" fill="#1b1410">TERM SHEET</text>{lines}
<path d="M300 260 q30 -30 60 0 t60 0" stroke="#1f3a7a" stroke-width="4" fill="none"/></g>
<g transform="translate(560 70) rotate(6)"><rect width="150" height="200" rx="14" fill="#3a3a40" stroke="{O}" stroke-width="3"/><rect x="16" y="16" width="118" height="44" fill="#a8b89a"/>
<text x="126" y="50" text-anchor="end" font-family="Inter" font-weight="800" font-size="30" fill="#1b2a1a">-4.2M</text>
{''.join(f'<rect x="{18 + (k % 4) * 30}" y="{76 + (k // 4) * 30}" width="22" height="22" rx="4" fill="#6a6a72"/>' for k in range(16))}</g>
<g transform="translate(250 30)"><path d="M0 20 L10 160 Q60 180 110 160 L120 20Z" fill="#f2ece0" stroke="{O}" stroke-width="4"/>
<ellipse cx="60" cy="20" rx="60" ry="16" fill="#3a2414" stroke="{O}" stroke-width="4"/><path d="M118 50 q44 10 34 50 q-8 30 -38 30" fill="none" stroke="{O}" stroke-width="12"/>
<path d="M118 50 q44 10 34 50 q-8 30 -38 30" fill="none" stroke="#f2ece0" stroke-width="6"/></g></svg>"""


def build(out: Path):
    face = closeup_svg("fdr", "founder", skin=0, hair=2, style="parted", expr="worried", hand="phone", key="#ff7a66")
    art3 = {"window": WINDOW_NIGHT, "screen": SCREEN_DIM}
    cam = ("const cam = S3.camera({ pos: [.6, 1.2, 1.2], look: [-.4, 1.25, -10], fov: 44, shift: [0, -170] });\n"
           "const GLOWS = [[[-3.6,.95,-3.9],60,'#7fd8ff'],[[2.8,.95,-3.9],60,'#7fd8ff'],[[-.4,.95,-7.3],45,'#7fd8ff'],[[2.8,1.2,-7.3],90,'#ffc070'],"
           "[[-3.4,1.8,-15.9],240,'#3a4a9a'],[[0,1.8,-15.9],240,'#3a4a9a'],[[3.4,1.8,-15.9],240,'#3a4a9a']];")
    light = ("const L = { sun: { dir: [.2, .6, 1], color: '#8a9ad8', intensity: .35 }, sky: '#3a4270', ground: '#1a1420', ambient: .9, "
             "points: [{pos:[2.8,1.3,-7.3],color:'#ffc070',intensity:.9,range:4}], fog: { color: '#1c2448', near: 4, far: 26, max: .4 }, shadowOpacity: .3, shadowColor: '#05060c' };")
    over, root = grade(vignette=.7, grain=.06, contrast=1.08, saturate=1.06, seed=11)
    # bokeh discs from out-of-focus city lights / screens
    bokeh = glow([(260, 300, 70, "#ffd27a"), (420, 250, 50, "#ffd27a"), (1500, 260, 60, "#7fd8ff"), (1660, 330, 46, "#ffd27a"), (120, 520, 54, "#7fd8ff")], opacity=.55, id_="bokeh")
    # founder: portrait drawn big, centre-left; rim light from the screen on the right
    sized = face.replace("<svg ", '<svg width="1000" height="1125" ', 1)
    founder = f'<div id="founder" style="position:absolute;left:200px;top:20px;width:1000px;height:1125px">{sized}</div>'
    # key light from the CRT: red/cyan wash across the face (screen blend), cool shadow side on the left
    keylight = ('<div style="position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;'
                'background:radial-gradient(ellipse 620px 760px at 1240px 520px,rgba(255,110,90,.38),rgba(255,110,90,0) 70%)"></div>'
                '<div style="position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply;'
                'background:linear-gradient(90deg,rgba(40,48,110,.55) 0%,rgba(40,48,110,.25) 32%,rgba(255,255,255,0) 55%)"></div>')
    lamp = ('<div style="position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;'
            'background:radial-gradient(ellipse 520px 300px at 300px 1060px,rgba(255,180,90,.35),rgba(255,180,90,0) 75%)"></div>')
    crt = f'<div style="position:absolute;left:1150px;top:250px;width:900px;height:900px">{crt_svg()}</div>'
    desk = f'<div style="position:absolute;left:0;top:860px;width:1920px;height:300px">{desk_svg()}</div>'
    front = bokeh + founder + desk + crt + keylight + lamp + glow([(1560, 560, 520, "#ff6a5a")], opacity=.35, id_="crtglow") + over
    page(out, "Style frame 3 — close-up", '<div style="position:absolute;inset:0;background:#0c0e1c"></div>',
         f"const ART3 = {json.dumps(art3)};\n" + SCENE, cam, light, front, root,
         extra_css="#set,#glows{filter:blur(5px)}")


if __name__ == "__main__":
    build(Path(sys.argv[1]))
