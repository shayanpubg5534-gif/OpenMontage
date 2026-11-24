"""Style frame 2 — detailed medium shot (c03_04 "spending heavily on advertising, employees and infrastructure", ~3:37).

Scene plan: medium / interior, eye level, slight two-point. Focal point: the whiteboard (right third) where the
manager has drawn this month's cash — three tall spending bars (ads, staff, servers) beside one short revenue bar —
while the team works at the CRT desks (left/middle). Diegetic financial graphic: marker drawing on the board, not
an overlay. Secondary: the brass cash riser pipe in the corner, an ad campaign poster, the hiring banner.
Technique: illustrated vector 3D interior (oak floor + plaster CC0 textures), ceiling-panel and lamp lighting with
dusk window light, rig v3 cast, depth of field on the foreground desk. lightfx: beams, glow, grade.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from kit.lightfx import beams, grade  # noqa: E402
from kit.diegetic import whiteboard_gap, gauge, press_clip  # noqa: E402
from styleframes.common import page, people_sprites  # noqa: E402

O = "#1b1410"
# illustrative proportions for the narration "spending heavily on advertising, employees and infrastructure" (no figures shown)
BOARD = whiteboard_gap("THIS MONTH", [("ADS", 1.0, "#e07a5f"), ("STAFF", .81, "#f2c66d"), ("SERVERS", .67, "#7fd8ff")], ("REVENUE", .55), uid="wb")
POSTER = f"""<rect width="600" height="800" fill="#2b4f9e"/><circle cx="300" cy="300" r="190" fill="#3a66c0"/>
<g transform="translate(300 300) rotate(-18)"><path d="M0 -150 C70 -90 72 70 0 150 C-72 70 -70 -90 0 -150Z" fill="#f4ead5" stroke="{O}" stroke-width="7"/><circle cy="-30" r="36" fill="#7fc8ee" stroke="{O}" stroke-width="6"/>
<path d="M-28 150 Q0 250 28 150Z" fill="#ffb03a"/></g>
<text x="300" y="610" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="78" fill="#fff">BigCart.com</text>
<text x="300" y="690" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="#ffd56a">SUPER BOWL SPOT</text>
<text x="300" y="740" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#cfe0ff">ON AIR JAN 30</text>"""
WINDOW = """<defs><linearGradient id="wsk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3a6e"/><stop offset=".6" stop-color="#d47a6a"/><stop offset="1" stop-color="#f6b878"/></linearGradient></defs>
<rect width="800" height="600" fill="url(#wsk)"/>""" + "".join(
    f'<rect x="{x}" y="{600 - h}" width="{w}" height="{h}" fill="#4a3a52"/>' + "".join(
        f'<rect x="{x + 8 + c * 18}" y="{610 - h + r * 26}" width="9" height="14" fill="#ffd892" opacity="{.4 + ((x + r + c) % 4) * .15:.2f}"/>' for r in range(h // 30) for c in range(max(1, (w - 12) // 18)) if (x + r * 3 + c) % 3)
    for x, w, h in [(0, 110, 260), (120, 80, 360), (210, 140, 220), (360, 90, 420), (460, 130, 300), (600, 90, 380), (700, 100, 250)]) + \
    '<rect width="800" height="600" fill="none" stroke="#3a3a42" stroke-width="22"/><path d="M400 0 V600 M0 300 H800" stroke="#3a3a42" stroke-width="12"/>'
SCREEN = """<rect width="400" height="300" fill="#0a2a3a"/><rect x="0" y="0" width="400" height="34" fill="#1f6fbf"/>
<text x="14" y="24" font-family="Inter" font-weight="800" font-size="20" fill="#fff">BigCart Admin</text>
<g fill="#7fd8ff">""" + "".join(f'<rect x="20" y="{54 + i * 34}" width="{180 + (i * 53) % 160}" height="16" rx="3" opacity=".75"/>' for i in range(6)) + "</g>"

SCREEN_RED = """<rect width="400" height="300" fill="#1a0e10"/><text x="16" y="40" font-family="Inter" font-weight="800" font-size="28" fill="#ff8a7a">CASH BALANCE</text>
<path d="M20 90 L90 100 L160 130 L230 170 L300 220 L380 270" stroke="#ff5a4a" stroke-width="10" fill="none" stroke-linejoin="round"/>"""

SCENE = r"""
const sc = S3.scene(), T = (n) => TEX + n + '.jpg';
const floor = { color: '#b8875a', tex: T('wood_floor'), texScale: 1.6, sub: 3, receiver: true, outline: false, tint: '#ffe6cc' };
const wall = { color: '#ece0c8', tex: T('plaster'), texScale: 2.5, sub: 2, texMix: .35, tint: '#fff4e2', outline: false };
const W0 = -4.6, W1 = 4.4, ZB = -9.5, ZF = 4, H = 3.1;
sc.ground(W0, ZB, W1, ZF, 0, 1.6, floor);
sc.quad([W0, 0, ZB], [W1, 0, ZB], [W1, H, ZB], [W0, H, ZB], wall, { uv: [[0, 1.2], [3.6, 1.2], [3.6, 0], [0, 0]], bias: -3 });
sc.quad([W0, 0, ZF], [W0, 0, ZB], [W0, H, ZB], [W0, H, ZF], wall, { uv: [[0, 1.2], [5.4, 1.2], [5.4, 0], [0, 0]], bias: -3 });
sc.quad([W1, 0, ZB], [W1, 0, ZF], [W1, H, ZF], [W1, H, ZB], wall, { uv: [[0, 1.2], [5.4, 1.2], [5.4, 0], [0, 0]], bias: -3 });
sc.quad([W0, H, ZF], [W0, H, ZB], [W1, H, ZB], [W1, H, ZF], { color: '#f2ece0', emissive: .55, outline: false }, { bias: -3, allowBack: true });
sc.box([W0, 0, ZB], [W1, .1, ZB + .03], { color: '#6a4a30', outline: false }, { shadow: false });
sc.box([W1 - .03, 0, ZB], [W1, .1, ZF], { color: '#6a4a30', outline: false }, { shadow: false });
// tall windows on the left wall onto the dusk city
[-1.2, -5.0].forEach((z) => { sc.quad([W0 + .02, .7, z + 1.5], [W0 + .02, .7, z - 1.5], [W0 + .02, 2.8, z - 1.5], [W0 + .02, 2.8, z + 1.5], { color: '#f6b878', emissive: .9, outline: '#3a3a42' }, { bias: .05 });
  sc.art([W0 + .04, .7, z + 1.5], [W0 + .04, .7, z - 1.5], [W0 + .04, 2.8, z + 1.5], 800, 600, ART2.window, { bias: .1 });
  sc.box([W0, .62, z - 1.6], [W0 + .18, .7, z + 1.6], { color: '#d8cbb0', outline: '#5a4a3a' }, { shadow: false }); });
// ceiling light panels
for (let z = 1; z > -9; z -= 3.2) for (let x of [-2.4, 1.6]) sc.quad([x - .8, H - .02, z - .45], [x + .8, H - .02, z - .45], [x + .8, H - .02, z + .45], [x - .8, H - .02, z + .45], { color: '#fff6dc', emissive: 1.2, outline: '#c8c0b0', doubleSided: true }, { allowBack: true });
// back wall: hiring banner, campaign poster, brass cash riser + gauge, boxes of promo merchandise
sc.quad([-4.4, 2.45, ZB + .03], [-1.6, 2.45, ZB + .03], [-1.6, 2.85, ZB + .03], [-4.4, 2.85, ZB + .03], { color: '#d9503f', emissive: .15 }, { bias: .1 });
sc.art([-4.33, 2.48, ZB + .05], [-1.67, 2.48, ZB + .05], [-4.33, 2.82, ZB + .05], 760, 100, ART2.banner, { bias: .2 });
sc.art([.4, .9, ZB + .05], [1.75, .9, ZB + .05], [.4, 2.7, ZB + .05], 600, 800, ART2.poster, { bias: .2 });
sc.cyl([3.9, 0, ZB + .4], .14, 0, H, { color: '#c7953f', gloss: .5, outline: false }, { seg: 18 });
sc.art([3.56, 1.3, ZB + .62], [3.96, 1.3, ZB + .62], [3.56, 1.7, ZB + .62], 200, 200, ART2.gauge, { bias: .3 });
[[2.6, ZB + .6, 0, .5], [3.1, ZB + .7, 0, .42], [2.8, ZB + .6, .5, .34]].forEach(([x, z, y, h]) => sc.box([x - .27, y, z - .27], [x + .27, y + h, z + .27], { color: '#c9a06a' }, {}));
sc.cyl([-3.9, 0, ZB + .6], .22, 0, 1.0, { color: '#d8e4ee' }, { seg: 12 }); sc.cyl([-3.9, 0, ZB + .6], .17, 1.0, 1.35, { color: '#7fb8e0', alpha: .85 }, { seg: 12 });
// work desks in the background: CRTs facing the camera, staff typing behind them
const desk = (x, z) => { sc.box([x - .8, .72, z - .42], [x + .8, .76, z + .42], { color: '#8a6440' }, {});
  [[-.75, -.37], [.75, -.37], [-.75, .37], [.75, .37]].forEach(([a, b]) => sc.box([x + a - .025, 0, z + b - .025], [x + a + .025, .72, z + b + .025], { color: '#3a3a40' }, { shadow: false }));
  sc.box([x - .78, .32, z + .36], [x + .78, .72, z + .39], { color: '#7a5636' }, { shadow: false }); };
const crt = (x, z, w) => { sc.box([x - .24, .76, z - .34], [x + .24, 1.16, z + .06], { color: '#d8d0bc', gloss: .15 }, {});
  sc.art([x - .19, .82, z + .065], [x + .19, .82, z + .065], [x - .19, 1.1, z + .065], 400, 300, w ? ART2.screenRed : ART2.screen, { bias: .1 });
  sc.box([x - .26, .76, z + .12], [x + .26, .78, z + .3], { color: '#e4dccc' }, { shadow: false }); };
[[-2.6, -4.6], [-.6, -4.6], [-2.6, -6.6], [-.6, -6.6]].forEach(([x, z], i) => { desk(x, z); crt(x - .3, z, i === 1); crt(x + .45, z, false); });
// easel whiteboard angled toward the lens (the diegetic burn chart)
const bc = [1.35, 1.55, -.9], ya = .5, u = [Math.cos(ya), 0, Math.sin(ya)], bw = 2.0, bh = 1.2;
const P = (s, t, d) => [bc[0] + u[0] * s - Math.sin(ya) * (d || 0), bc[1] + t, bc[2] + u[2] * s + Math.cos(ya) * (d || 0)];
sc.quad(P(-bw / 2 - .05, -bh / 2 - .05, -.03), P(bw / 2 + .05, -bh / 2 - .05, -.03), P(bw / 2 + .05, bh / 2 + .05, -.03), P(-bw / 2 - .05, bh / 2 + .05, -.03), { color: '#a8aeb6', outline: '#2a2a30', doubleSided: true }, { allowBack: true });
sc.art(P(-bw / 2, -bh / 2, 0), P(bw / 2, -bh / 2, 0), P(-bw / 2, bh / 2, 0), 1000, 560, ART2.board, { bias: .3, id: 'wb-art' });
sc.quad(P(-bw / 2, -bh / 2 - .02, .01), P(bw / 2, -bh / 2 - .02, .01), P(bw / 2, -bh / 2 - .08, .12), P(-bw / 2, -bh / 2 - .08, .12), { color: '#8a9098', outline: '#2a2a30', doubleSided: true }, { allowBack: true, bias: .35 });
const leg = (a, b, w, m) => { const d = norm3(sub3(b, a)), side = [d[2] ? -d[2] : 1, 0, d[0] || 0]; const sl = Math.hypot(side[0], side[2]) || 1, s = [side[0] / sl * w, 0, side[2] / sl * w];
  sc.quad([a[0] - s[0], a[1], a[2] - s[2]], [a[0] + s[0], a[1], a[2] + s[2]], [b[0] + s[0], b[1], b[2] + s[2]], [b[0] - s[0], b[1], b[2] - s[2]], m, { allowBack: true, bias: -.2 }); };
const sub3 = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], norm3 = (a) => { const l = Math.hypot(...a) || 1; return a.map(v => v / l); };
const steel = { color: '#3a3a42', doubleSided: true };
leg(P(-.75, -bh / 2, -.05), [bc[0] - .9, 0, bc[2] - .2], .025, steel); leg(P(.75, -bh / 2, -.05), [bc[0] + .8, 0, bc[2] + .2], .025, steel);
leg(P(0, bh / 2, -.05), [bc[0] + .35, 0, bc[2] - .75], .025, steel);
// right wall: framed press clipping (the funding round) and a clock
sc.quad([W1 - .02, 1.1, -5.6], [W1 - .02, 1.1, -6.8], [W1 - .02, 2.2, -6.8], [W1 - .02, 2.2, -5.6], { color: '#3a2a20' }, { bias: .1 });
sc.art([W1 - .04, 1.16, -5.66], [W1 - .04, 1.16, -6.74], [W1 - .04, 2.14, -5.66], 500, 450, ART2.clip, { bias: .2 });
sc.art([W1 - .04, 2.3, -3.7], [W1 - .04, 2.3, -4.2], [W1 - .04, 2.8, -3.7], 200, 200, ART2.clock, { bias: .2 });
// coffee table in front of the team: mugs, printouts
sc.box([-1.3, .44, -.2], [.1, .48, .5], { color: '#6a4a30' }, {}); [[-1.25, -.15], [.05, -.15], [-1.25, .45], [.05, .45]].forEach(([x, z]) => sc.box([x - .025, 0, z - .025], [x + .025, .44, z + .025], { color: '#2a2a30' }, { shadow: false }));
sc.quad([-1.1, .481, .3], [-.75, .481, .22], [-.7, .481, .48], [-1.05, .481, .5], { color: '#fbf8f0', outline: '#8a8070' }, {}); sc.cyl([-.5, .48, 0], .05, .48, .6, { color: '#d9503f' }, { seg: 10 });
sc.quad([-.3, .481, .1], [0, .481, .02], [.04, .481, .4], [-.26, .481, .46], { color: '#fbf8f0', outline: '#8a8070' }, {});
// set dressing: low bookshelf with binders under the banner, printer cabinet, coat rack, desk lamps, paper stacks, bin
sc.box([-4.4, 0, ZB + .02], [-2.0, 1.25, ZB + .4], { color: '#7a5636' }, {});
for (let i = 0; i < 18; i++) { const x = -4.3 + i * .125, h = .3 + ((i * 7) % 5) * .02, y0 = (i % 2 ? .12 : .7);
  sc.box([x, y0, ZB + .42], [x + .1, y0 + h, ZB + .43], { color: ['#2e5ab0', '#d9503f', '#3a6a3a', '#f2c66d', '#4a4a52'][i % 5], outline: false }, { shadow: false });
  sc.box([x, (y0 > .5 ? .12 : .7), ZB + .42], [x + .1, (y0 > .5 ? .12 : .7) + .28, ZB + .43], { color: ['#c9a06a', '#2a2a30', '#8a5a3a'][i % 3], outline: false }, { shadow: false }); }
sc.box([1.9, 0, ZB + .3], [2.9, .8, ZB + .9], { color: '#c8c4bc' }, {}); sc.box([2.0, .8, ZB + .35], [2.8, 1.1, ZB + .85], { color: '#e8e4dc', gloss: .2 }, {});
sc.box([2.1, 1.1, ZB + .4], [2.7, 1.13, ZB + .8], { color: '#3a3a42' }, { shadow: false });
sc.cyl([4.0, 0, -6.4], .03, 0, 1.75, { color: '#3a2a20' }, { seg: 6 }); sc.box([3.78, 1.25, -6.62], [4.2, 1.7, -6.42], { color: '#8a3a2a' }, { shadow: false });
sc.box([3.85, 1.0, -6.46], [4.15, 1.6, -6.3], { color: '#3a4a6a' }, { shadow: false });
sc.ground(-3.7, -7.4, .5, -3.7, .006, 1.2, { color: '#6a6a7a', tex: T('carpet'), texScale: 1.2, sub: 2, texMix: .55, receiver: true, outline: false });
[[-3.25, -4.4], [-1.05, -6.4]].forEach(([x, z]) => { sc.cyl([x, .76, z], .07, .76, .79, { color: '#2a2a2a' }, { seg: 8 }); sc.cyl([x, .79, z], .015, .79, 1.1, { color: '#2a2a2a' }, { seg: 5, shadow: false });
  sc.cyl([x + .06, 1.05, z], .11, 1.05, 1.17, { color: '#3a5a3a', emissive: .2 }, { seg: 10 }); });
[[-2.2, -4.5], [.1, -4.45], [-2.0, -6.5]].forEach(([x, z], i) => { for (let k = 0; k < 3 + i; k++) sc.box([x - .15 + k * .01, .76 + k * .012, z - .12], [x + .15 + k * .01, .772 + k * .012, z + .12], { color: '#fbf8f0', outline: '#9a9080' }, { shadow: false }); });
sc.cyl([.55, 0, -4.1], .14, 0, .34, { color: '#4a4a52' }, { seg: 10 });
// plants
[[-4.1, -2.9], [4.0, -3.6], [-4.1, -8.6], [3.6, -8.9]].forEach(([x, z]) => { sc.cyl([x, 0, z], .2, 0, .45, { color: '#8a5a3a' }, { seg: 10 }); sc.sprite([x, .45, z], 1.2, ART2.plant, .9, { viewBox: '0 0 90 100' }); });
""" + "\n{people}"


def build(out: Path):
    import json
    from kit.rig3 import figure_svg, VIEWBOX, ASPECT
    art2 = {
        "board": BOARD, "poster": POSTER, "window": WINDOW, "screen": SCREEN, "screenRed": SCREEN_RED,
        "banner": '<rect width="760" height="100" fill="#d9503f"/><text x="380" y="70" text-anchor="middle" font-family="Inter" font-weight="800" font-size="56" fill="#fff">WE\'RE HIRING!</text>',
        "gauge": gauge("CASH", .22),
        "clip": press_clip("The Daily Ledger", "BigCart raises", "$40 million"),
        "clock": '<circle cx="100" cy="100" r="92" fill="#fbf8f0" stroke="#1b1410" stroke-width="10"/><path d="M100 100 L100 40 M100 100 L150 118" stroke="#1b1410" stroke-width="9" stroke-linecap="round"/>',
        "plant": '<g><ellipse cx="45" cy="40" rx="30" ry="26" fill="#3a6a3a" stroke="#1b1410" stroke-width="2"/><ellipse cx="26" cy="58" rx="20" ry="18" fill="#2e5a30" stroke="#1b1410" stroke-width="2"/>'
                 '<ellipse cx="64" cy="60" rx="22" ry="18" fill="#4a7a40" stroke="#1b1410" stroke-width="2"/><path d="M45 100 L45 60" stroke="#3a2a1a" stroke-width="4"/></g>',
    }
    people = []
    cast = [("e1", "casual", [-.75, 0, -1.25], "fold", 3, 3, "curly", False, "worried", False),
            ("e2", "casual2", [-1.55, 0, -1.9], "worry", 4, 6, "buzz", False, "worried", False),
            ("e3", "trader", [-2.6, 0, -5.15], "type", 2, 0, "short", False, "neutral", False),
            ("e5", "suit_w", [-.6, 0, -5.15], "type", 5, 1, "bun", True, "neutral", False),
            ("mgr", "founder", [2.75, 0, -.35], "point", 0, 2, "parted", False, "talk", True),
            ("e6", "suit", [2.45, 0, -7.6], "phone", 1, 5, "short", False, "neutral", False),
            ("w1", "casual2", [-1.6, 0, -7.75], "carry", 2, 1, "short", False, "neutral", False)]
    for pid, cos, foot, pose, sk, hr, st, gl, ex, flip in cast:
        mk = figure_svg(pid, cos, skin=sk, hair=hr, style=st, pose=pose, expr=ex, glasses=gl, inner=True)
        if pid == "w1":   # carton of BigCart promotional merchandise (ad spending) held in both hands
            mk += ('<g id="w1-box"><path d="M232 318 L352 318 L352 430 L232 430Z" fill="#c9a06a" stroke="#1b1410" stroke-width="4"/>'
                   '<path d="M232 318 L292 300 L352 318" fill="#b08a56" stroke="#1b1410" stroke-width="3"/><rect x="250" y="356" width="84" height="30" fill="#2e5ab0"/>'
                   '<text x="292" y="378" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="20" fill="#fff">BigCart</text></g>')
        if flip:
            mk = f'<g transform="translate(400 0) scale(-1 1)">{mk}</g>'
        people.append(f"sc.sprite({foot}, 1.76, {json.dumps(mk)}, {ASPECT}, {{ viewBox: '{VIEWBOX}', id: '{pid}' }});")
    scene = SCENE.replace("{people}", "\n".join(people))
    cam = ("const GLOWS = [" + ",".join(f"[[{x},3.05,{z}],{r},'#fff2cc']" for x, z, r in ((-2.4, 1, 150), (1.6, 1, 150), (-2.4, -2.2, 110), (1.6, -2.2, 110), (-2.4, -5.4, 80), (1.6, -5.4, 80)))
           + ",[[-4.5,1.8,-1.2],300,'#ffb878'],[[-4.5,1.8,-5],200,'#ffb878']];\n"
           "const cam = S3.camera({ pos: [-.05, 1.34, 2.45], look: [.85, 1.22, -3], fov: 52, shift: [0, -50] });")
    light = ("const L = { sun: { dir: [-1, .3, .2], color: '#ffb070', intensity: .42 }, sky: '#f4e2c8', ground: '#7a5a40', ambient: .82, "
             "points: [" + ",".join(f"{{pos:[{x},2.9,{z}],color:'#fff0d0',intensity:.5,range:5}}" for z in (1, -2.2, -5.4) for x in (-2.4, 1.6)) + "], "
             "fog: { color: '#f2d8b8', near: 7, far: 30, max: .3 }, shadowOpacity: .4, shadowColor: '#3a2418' };")
    over, root = grade(vignette=.5, grain=.05, contrast=1.05, saturate=1.05)
    back = '<div style="position:absolute;inset:0;background:#2a2020"></div>'
    front = (beams([(120, 260, 420, 1080, 700), (420, 330, 760, 1080, 460)], color="#ffc890", opacity=.18, blur=24) + over)
    fg = ""
    page(out, "Style frame 2 — medium", back, f"const ART2 = {json.dumps(art2)};\n" + scene, cam, light, front, root, fg=fg)


if __name__ == "__main__":
    build(Path(sys.argv[1]))
