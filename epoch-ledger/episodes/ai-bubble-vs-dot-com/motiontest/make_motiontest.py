"""Art-direction v2 motion test (~25 s): the three approved style frames in motion, with narration and captions.

  python epoch-ledger/episodes/ai-bubble-vs-dot-com/motiontest/make_motiontest.py [WS]   (default WS: projects/<slug>/motiontest)
  python epoch-ledger/scripts/render.py render WS -o WS/motiontest.mp4

Narration: the episode's own lines, unedited — c03_03, c03_04, c03_05 (contiguous) then c03_10 — sliced from the
episode narration so the test hears exactly what the film will. Shot plan: scene_plan.json (validated).
  s1 establishing  0.00– 5.30  c03_03 "But beneath the rising stock prices, many businesses were struggling."
  s2 medium        5.30–19.15  c03_04 + c03_05 (spending vs revenue; investor cash fills the gap)
  s3 close-up     19.15–24.70  c03_10 "Without fresh capital, they could no longer finance their operations."
The sets are the style-frame builders themselves (their page() call is captured), so stills and motion never drift.
"""
from __future__ import annotations

import importlib
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

from kit.assemble import Scene, assemble  # noqa: E402
from kit import rig3  # noqa: E402
import timeline as TL  # noqa: E402
from styleframes import common  # noqa: E402

D = 24.7
CUT1, CUT2 = 5.40, 19.15
# narration segments: (film_start, film_end, test_start)
SEGS = [(210.45, 228.95, 0.5), (248.95, 253.75, 19.3)]
LINES = ["c03_03", "c03_04", "c03_05", "c03_10"]


def ft(t: float) -> float:
    """film time → test time"""
    for a, b, s in SEGS:
        if a - .01 <= t <= b + .01:
            return round(t - a + s, 3)
    raise ValueError(f"film time {t} is outside the test's narration")


def W(word: str, line: str) -> float:
    return ft(TL.W(word, line))


def capture(mod_name: str) -> dict:
    mod = importlib.import_module(f"styleframes.{mod_name}")
    got = {}

    def page(out, title, back, scene_js, cam_js, light_js, front, root_filter="", fg="", extra_css="", after_svg=""):
        got.update(back=back, scene=scene_js, cam=cam_js, light=light_js, front=front, root=root_filter, fg=fg, css=extra_css, after=after_svg)
    mod.page = page
    if mod_name == "sf1_establishing":   # the founder walks into his company in the opening shot (same look as shots 2-3)
        orig = mod.people_sprites
        mod.people_sprites = lambda spec: orig([(("p1", "founder", [-4.3, .16, -1.2], "walk", 1.0) if s[0] == "p1" else s) for s in spec])
    mod.build(Path("/dev/null"))
    return got


def shot_html(sid: str, g: dict, fg_wrap=True) -> str:
    return (f'<div class="shot" id="{sid}-frame" style="filter:{g["root"] or "none"}">'
            f'<div class="layer" id="{sid}-back">{g["back"]}</div>'
            f'<div class="layer" id="{sid}-cam"><svg id="{sid}-set" class="full" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg"></svg>'
            f'<svg id="{sid}-glows" class="full" viewBox="0 0 1920 1080" style="mix-blend-mode:screen;opacity:.8"></svg>{g["after"]}</div>'
            f'{g["front"]}<div class="layer" id="{sid}-fg">{g["fg"]}</div></div>')


def shot_js(sid: str, g: dict, anim: str, geo: str = "") -> str:
    """Block-scoped: build the set with the style frame's own scene/camera/light (+ extra geometry), render it,
    draw id'd glows, animate."""
    return ("{\n" + g["scene"] + "\n" + geo + "\n" + g["cam"] + "\n" + g["light"] + "\n"
            f"document.getElementById('{sid}-set').innerHTML = S3.render(sc, cam, L, {{ ow: 2.0, shadowBlur: 5, uid: '{sid}' }});\n"
            f"if (typeof GLOWS !== 'undefined') document.getElementById('{sid}-glows').innerHTML = GLOWS.map(([p, r, c], i) => {{ const q = cam.project(p); if (!q) return '';\n"
            f"  const rr = r * Math.min(2.5, 14 / q[2]) + r * .3; return `<radialGradient id=\"{sid}gw${{i}}\"><stop offset=\"0\" stop-color=\"${{c}}\" stop-opacity=\".95\"/><stop offset=\".22\" stop-color=\"${{c}}\" stop-opacity=\".4\"/><stop offset=\"1\" stop-color=\"${{c}}\" stop-opacity=\"0\"/></radialGradient><circle id=\"{sid}-gw${{i}}\" cx=\"${{q[0]}}\" cy=\"${{q[1]}}\" r=\"${{rr}}\" fill=\"url(#{sid}gw${{i}})\"/>`; }}).join('');\n"
            + anim + "\n}")


# BigCart's furnace chimney at the back of the roof (the episode's cash-furnace metaphor, seen from outside)
GEO1 = ("sc.box([-7.7, 17.0, -22.6], [-6.5, 21.2, -21.4], { color: '#7a3a2a', tex: T('brick'), texScale: 1.2, sub: 2 }, { bias: .2 });"
        "sc.box([-7.85, 21.2, -22.75], [-6.35, 21.55, -21.25], { color: '#3a2a24' }, { shadow: false, bias: .2 });")


# ── shot 1: establishing — rising market, struggling company, capital flowing in ─────────────────
def anim1() -> str:
    w_rising, w_beneath, w_struggling, w_businesses = W("rising", "c03_03"), W("beneath", "c03_03"), W("struggling", "c03_03"), W("businesses", "c03_03")
    return f"""
const T1 = {CUT1};
// camera: one slow dolly toward BigCart's lobby (the subject named by "businesses"), sky barely moves, foreground passes faster
const fq = cam.project([-5.7, 2.6, -13.5]);
tl.fromTo('#s1-cam', {{ scale: 1 }}, {{ scale: 1.09, transformOrigin: fq[0] + 'px ' + fq[1] + 'px', duration: T1, ease: 'sine.inOut' }}, 0);
tl.fromTo('#s1-back', {{ scale: 1 }}, {{ scale: 1.025, transformOrigin: '50% 75%', duration: T1, ease: 'sine.inOut' }}, 0);
tl.fromTo('#s1-fg', {{ x: 0, scale: 1 }}, {{ x: -170, scale: 1.14, transformOrigin: '0% 100%', duration: T1, ease: 'sine.inOut' }}, 0);
// "rising stock prices": the market board's line climbs and its last point lights up
const ln = document.getElementById('tick-line'), n = ln.getTotalLength();
gsap.set(ln, {{ strokeDasharray: n, strokeDashoffset: n * .42 }}); gsap.set('#tick-dot', {{ opacity: 0 }});
tl.to(ln, {{ strokeDashoffset: 0, duration: 1.5, ease: 'power2.out' }}, {w_rising - .25});
tl.to('#tick-dot', {{ opacity: 1, duration: .2 }}, {w_rising + 1.15});
tl.fromTo('#s1-gw4', {{ opacity: .55 }}, {{ opacity: 1, duration: 1.2, ease: 'sine.out' }}, {w_rising});
// capital in: gold glints travel through the pipe from Summit Ventures into BigCart for the whole shot
const pipe = Array.from({{ length: 24 }}, (_, i) => cam.project([5.4 - i * 11 / 23, 6.2, -16])).filter(Boolean);
const gl = document.getElementById('s1-glows');
gl.insertAdjacentHTML('beforeend', [0, 1, 2, 3, 4].map(k => `<circle id="s1-cash${{k}}" r="9" fill="#ffe08a" opacity="0"/>`).join(''));
const at = (u) => {{ const f = u * (pipe.length - 1), i = Math.min(pipe.length - 2, Math.floor(f)), r = f - i; return [pipe[i][0] + (pipe[i + 1][0] - pipe[i][0]) * r, pipe[i][1] + (pipe[i + 1][1] - pipe[i][1]) * r]; }};
const P1 = {{ u: 0 }};
tl.fromTo(P1, {{ u: 0 }}, {{ u: 1, duration: T1, ease: 'none', onUpdate: () => {{ for (let k = 0; k < 5; k++) {{ const u = (P1.u * 2.2 + k / 5) % 1, q = at(u), e = document.getElementById('s1-cash' + k);
  e.setAttribute('cx', q[0].toFixed(1)); e.setAttribute('cy', q[1].toFixed(1)); e.setAttribute('opacity', (Math.sin(u * Math.PI) * .9).toFixed(2)); }} }} }}, 0);
// "struggling": inside the lobby, the cash tank drains even while money flows in
tl.to(['#tank-fill', '#tank-coins'], {{ scaleY: .32, transformOrigin: '50% 100%', duration: 1.6, ease: 'power2.inOut' }}, {w_struggling - .1});
tl.to('#tank-fill', {{ fill: '#c98a3a', duration: 1.2 }}, {w_struggling + .2});
tl.to('#s1-gw5', {{ opacity: .45, duration: 1.4 }}, {w_struggling});
// "struggling": the furnace chimney puffs harder — smoke and gold embers (money burning) while capital pours in
const src = cam.project([-7.1, 21.7, -22.0]);
document.getElementById('s1-cam').insertAdjacentHTML('beforeend', `<svg id="s1-fx" class="full" viewBox="0 0 1920 1080"><defs><filter id="s1-sm" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter></defs>
 <g filter="url(#s1-sm)">${{Array.from({{ length: 14 }}, (_, k) => `<circle id="s1-pf${{k}}" r="10" fill="${{k % 3 ? '#231a1e' : '#3a2e30'}}" opacity="0"/>`).join('')}}</g>
 ${{Array.from({{ length: 7 }}, (_, k) => `<circle id="s1-em${{k}}" r="4.2" fill="#ffd27a" opacity="0"/>`).join('')}}</svg>`);
const SM = {{ u: 0, I: .28 }};
const smoke = () => {{ for (let k = 0; k < 14; k++) {{ const ph = (SM.u * 1.6 + k / 14) % 1, e = document.getElementById('s1-pf' + k);
    e.setAttribute('cx', (src[0] + ph * 150 + Math.sin(k * 2.1 + ph * 5) * 14).toFixed(1)); e.setAttribute('cy', (src[1] - 6 - ph * 360).toFixed(1));
    e.setAttribute('r', (10 + ph * 88).toFixed(1)); e.setAttribute('opacity', (Math.min(1, SM.I * Math.min(1, ph * 8) * (1 - ph * .85) * 1.15)).toFixed(3)); }}
  for (let k = 0; k < 7; k++) {{ const ph = (SM.u * 2.6 + k / 7) % 1, e = document.getElementById('s1-em' + k);
    e.setAttribute('cx', (src[0] + ph * 90 + Math.sin(k * 3.3 + ph * 9) * 12).toFixed(1)); e.setAttribute('cy', (src[1] - ph * 230).toFixed(1));
    e.setAttribute('opacity', (Math.max(0, SM.I - .35) * 1.4 * (1 - ph) * (.6 + .4 * Math.sin(ph * 40 + k))).toFixed(3)); }} }};
tl.fromTo(SM, {{ u: 0 }}, {{ u: 1, duration: T1, ease: 'none', onUpdate: smoke }}, 0);
tl.fromTo(SM, {{ I: .28 }}, {{ I: 1, duration: 1.1, ease: 'power2.out', immediateRender: false }}, {w_struggling - .2});
// people: the founder walks to BigCart's door; commuters keep the street alive
R3.walk(cam, 'p1', 'p1', [-4.3, .16, -1.2], [-4.6, .16, -6.6], 1.76, {rig3.ASPECT}, 0, T1, .52);
R3.walk(cam, 'p3', 'p3', [4.6, .16, -1.6], [4.8, .16, 3.2], 1.76, {rig3.ASPECT}, 0, T1, .5);
R3.blinks('p2', 0, T1, 21, '50% 50%'); R3.talk('p2', .6, 2.4, 3); R3.talk('p2', 3.1, 4.6, 4); R3.idle('p2', 0, T1, 5, -6);
R3.pose('p4', 'talk', 1.2, .5); R3.pose('p4', 'stand', 3.3, .6); R3.talk('p4', 1.3, 3.0, 8); R3.idle('p4', 0, T1, 9);
R3.idle('p5', 0, T1, 13); R3.idle('p6', 0, T1, 17);
// ambient: street lamps breathe very slightly
[0, 1, 2, 3].forEach(i => tl.to('#s1-gw' + i, {{ opacity: .82, duration: 1.3 + i * .2, ease: 'sine.inOut', yoyo: true, repeat: 3 }}, .2 * i));
"""


# ── shot 2: medium — the spending/revenue gap, then investor cash fills it ───────────────────────
def anim2() -> str:
    t = {k: W(k, "c03_04") for k in ("spending", "advertising", "employees", "infrastructure", "without", "earning", "revenue", "sustain")}
    u = {k: W(k, "c03_05") for k in ("survival", "depended", "investors", "continuing", "provide", "capital")}
    T0, T1 = CUT1, CUT2
    return f"""
const T0 = {T0}, T1 = {T1};
// map a point of the whiteboard art (1000x560 authoring box) to screen space, for camera targets
const A = document.getElementById('wb-art').getAttribute('transform').match(/[-\\d.e]+/g).map(Number);
const artPt = (x, y) => [A[0] * x + A[2] * y + A[4], A[1] * x + A[3] * y + A[5]];
const cb = artPt(520, 300), cg = artPt(700, 260);
// camera: open a touch wide on the team, settle onto the board as the manager starts; push to the gap on "investors"
gsap.set('#s2-cam', {{ transformOrigin: cb[0] + 'px ' + cb[1] + 'px' }});
tl.fromTo('#s2-cam', {{ scale: 1, x: 70 }}, {{ scale: 1.05, x: 0, duration: {t['advertising'] + .4 - T0:.2f}, ease: 'sine.inOut' }}, T0);
tl.to('#s2-cam', {{ scale: 1.066, duration: {u['survival'] - .6 - (t['advertising'] + .4):.2f}, ease: 'none' }}, {t['advertising'] + .4});
tl.to('#s2-cam', {{ scale: 1.1, x: -60, y: 30, duration: 2.4, ease: 'sine.inOut' }}, {u['survival'] - .6});
tl.to('#s2-cam', {{ scale: 1.118, duration: {T1 - (u['survival'] + 1.8):.2f}, ease: 'none' }}, {u['survival'] + 1.8});
tl.fromTo('#s2-fg', {{ x: 0 }}, {{ x: 120, duration: T1 - T0, ease: 'sine.inOut' }}, T0);
// whiteboard build, each part on its word (marker strokes grow from the baseline; no overshoot on financial content)
const hide = ['#wb-seg0', '#wb-seg1', '#wb-seg2', '#wb-rev', '#wb-gap'];
gsap.set(hide, {{ scaleY: 0, transformOrigin: '50% 100%' }});
gsap.set(['#wb-segl0', '#wb-segl1', '#wb-segl2', '#wb-coll0', '#wb-coll1', '#wb-gapl'], {{ opacity: 0 }});
{{ const e = document.getElementById('wb-ring'), n = e.getTotalLength(); gsap.set(e, {{ strokeDasharray: n + ' ' + n, strokeDashoffset: n }}); }}
gsap.set('#wb-dash', {{ scaleX: 0, transformOrigin: '0% 50%' }});
const grow = (sel, lbl, at) => {{ tl.to(sel, {{ scaleY: 1, duration: .7, ease: 'power2.out' }}, at); if (lbl) tl.to(lbl, {{ opacity: 1, duration: .3 }}, at + .15); }};
tl.to('#wb-coll0', {{ opacity: 1, duration: .3 }}, {t['spending']});
grow('#wb-seg0', '#wb-segl0', {t['advertising']}); grow('#wb-seg1', '#wb-segl1', {t['employees']}); grow('#wb-seg2', '#wb-segl2', {t['infrastructure']});
tl.to('#wb-rev', {{ scaleY: 1, duration: .6, ease: 'power2.out' }}, {t['revenue']}); tl.to('#wb-coll1', {{ opacity: 1, duration: .3 }}, {t['revenue']});
tl.to('#wb-ring', {{ strokeDashoffset: 0, duration: .55, ease: 'power1.inOut' }}, {t['sustain'] - .1});
tl.to('#wb-dash', {{ scaleX: 1, duration: .6, ease: 'power1.inOut' }}, {u['depended']});
tl.to('#wb-gap', {{ scaleY: 1, duration: 1.0, ease: 'power2.out' }}, {u['investors']});
tl.to('#wb-gapl', {{ opacity: 1, duration: .35 }}, {u['investors'] + .5});
tl.to('#wb-gap', {{ opacity: .75, duration: .25, yoyo: true, repeat: 1 }}, {u['capital']});
// the manager (the founder) walks the team through it: talk → point at each part → turn to the team → point at the gap
const M = 'mgr', pt = (a, at, d) => R3.rot(M, 'uarm-front', at, a, d || .35, 'power2.inOut');
R3.pose(M, 'talk', T0, 0); R3.rot(M, 'neck', T0, 6, 0);
R3.pose(M, 'point', {t['spending'] - .35}, .45); R3.rot(M, 'neck', {t['spending'] - .3}, -8, .4);
pt(-100, {t['advertising'] - .2}); pt(-110, {t['employees'] - .2}); pt(-121, {t['infrastructure'] - .2}); pt(-92, {t['revenue'] - .25});
R3.rot(M, 'farm-front', {t['sustain']}, -26, .12); R3.rot(M, 'farm-front', {t['sustain'] + .14}, -14, .14);   // tap
R3.pose(M, 'talk', {u['survival'] - .4}, .5); R3.rot(M, 'neck', {u['survival'] - .3}, 8, .45);
R3.pose(M, 'point', {u['investors'] - .35}, .45); pt(-106, {u['investors'] - .3}); R3.rot(M, 'neck', {u['investors'] - .3}, -6, .4);
R3.pose(M, 'talk', {u['continuing'] - .15}, .5); R3.rot(M, 'neck', {u['continuing'] - .1}, 9, .45);
R3.rot(M, 'neck', {u['capital'] - .05}, 15, .18); R3.rot(M, 'neck', {u['capital'] + .18}, 8, .3);   // nod on "capital"
R3.rot(M, 'farm-front', {u['provide']}, -40, .3); R3.rot(M, 'farm-front', {u['capital'] + .1}, -22, .35);
R3.talk(M, {u['continuing']}, {u['capital'] + .6}, 34);
R3.rot('e2', 'neck', {t['sustain'] + .4}, 14, .22); R3.rot('e2', 'neck', {t['sustain'] + .62}, 4, .25); R3.rot('e2', 'neck', {t['sustain'] + .87}, 13, .25); R3.rot('e2', 'neck', {t['sustain'] + 1.12}, 8, .3);
R3.rot('e1', 'neck', {u['continuing']}, -4, .5); R3.rot('e1', 'upper', {u['capital']}, 2.5, .6);
R3.talk(M, T0 + .2, {t['spending'] - .2}, 31); R3.talk(M, {u['survival'] - .3}, {u['investors'] - .3}, 32);
R3.blinks(M, T0, T1, 33); R3.breathe('#mgr-upper', T0, T1, 1.6, 3.4);
// team reactions: e2 goes from listening to hand-on-forehead on "without earning enough"; e1 folds tighter and frowns
R3.pose('e2', 'stand', T0, 0); R3.rot('e2', 'neck', T0, 4, 0);
R3.pose('e2', 'worry', {t['without'] + .1}, .6, 'power2.out'); R3.blinks('e2', T0, T1, 41); R3.idle('e2', {t['without'] + .8}, T1, 42, 10);
R3.blinks('e1', T0, T1, 51); R3.idle('e1', T0, T1, 52, 2); R3.breathe('#e1-upper', T0, T1, 1.4, 3.1);
tl.to('#e1-brows', {{ y: -3, duration: .3 }}, {t['revenue'] + .2}); R3.rot('e1', 'neck', {u['investors']}, 8, .5);
// background work never stops: typing, a phone call, a carton of BigCart merchandise (ad spending) carried past
R3.type('e3', T0, T1, 61); R3.type('e5', T0, T1, 71); R3.blinks('e3', T0, T1, 62); R3.blinks('e5', T0, T1, 72);
R3.rot('e5', 'neck', {u['investors'] + .2}, -2, .5);   // glances up at the board
R3.talk('e6', T0 + .4, T0 + 3.2, 81); R3.talk('e6', T0 + 4.4, T0 + 7.9, 82); R3.idle('e6', T0, T1, 83, -6);
R3.walk(cam, 'w1', 'w1', [-3.9, 0, -7.75], [1.7, 0, -7.75], 1.76, {rig3.ASPECT}, {t['advertising'] - .6:.2f}, {t['advertising'] + 4.4:.2f}, .5);
tl.set('#w1', {{ attr: {{ x: -400 }} }}, T0);
"""


# ── shot 3: close-up — the money runs out ────────────────────────────────────────────────────────
def anim3() -> str:
    v = {k: W(k, "c03_10") for k in ("without", "fresh", "capital", "no", "longer", "finance", "operations")}
    T0, T1 = CUT2, D
    return f"""
const T0 = {T0}, T1 = {T1};
// locked-off frame with a barely perceptible push: stillness sells the dread
tl.fromTo('#s3-frame', {{ scale: 1 }}, {{ scale: 1.035, transformOrigin: '34% 42%', duration: T1 - T0, ease: 'sine.inOut' }}, T0);
// the founder listens; brows knit on "without fresh capital"; the call ends on "no longer finance"
R3.blinks('fdr', T0, {v['no']}, 91, '50% 50%');
R3.breathe('#founder', T0, T1, 3, 3.2);
tl.to('#fdr-brows', {{ y: -9, rotation: 0, duration: .45, ease: 'power2.out' }}, {v['without'] + .05});
tl.to('#fdr-head', {{ rotation: 2.2, svgOrigin: '420 600', duration: 1.4, ease: 'sine.inOut' }}, {v['fresh']});
tl.to('#fdr-lids', {{ scaleY: .55, transformOrigin: '50% 30%', duration: .5, ease: 'sine.inOut' }}, {v['longer']});      // heavy, defeated eyes
tl.to('#fdr-hand', {{ rotation: -24, y: 110, svgOrigin: '210 900', duration: 1.2, ease: 'power2.inOut' }}, {v['finance'] - .25});
tl.to('#fdr-head', {{ rotation: 5, y: 10, svgOrigin: '420 600', duration: 1.2, ease: 'sine.inOut' }}, {v['operations']});
tl.to('#fdr-mouth', {{ scaleY: 1.25, transformOrigin: '50% 50%', duration: .5 }}, {v['operations'] + .3});
// the screen: the cash line finishes its fall; the runway counts down to zero
const ln = document.getElementById('sf3crt-line'), n = ln.getTotalLength();
gsap.set(ln, {{ strokeDasharray: n, strokeDashoffset: n * .14 }}); gsap.set('#sf3crt-dot', {{ opacity: 0 }});
tl.to(ln, {{ strokeDashoffset: 0, duration: 1.6, ease: 'power1.inOut' }}, {v['no'] - .1});
tl.to('#sf3crt-dot', {{ opacity: 1, duration: .15 }}, {v['no'] + 1.45});
const fig = document.getElementById('sf3crt-fig'), RW = {{ m: 3 }};
const put = () => {{ const m = Math.max(0, Math.round(RW.m)); fig.textContent = m + (m === 1 ? ' MONTH' : ' MONTHS'); }};
tl.fromTo(RW, {{ m: 3 }}, {{ m: 0, duration: 1.4, ease: 'power1.in', onUpdate: put }}, {v['finance']});
tl.fromTo(fig, {{ opacity: 1 }}, {{ opacity: .35, duration: .14, yoyo: true, repeat: 5, ease: 'none' }}, {v['operations'] + .2});
// screen flicker drives the red key light on his face (seeded, low amplitude)
const r = R3.seed(7); for (let tt = T0; tt < T1 - .2; tt += .18 + r() * .3) tl.to('#crtglow', {{ opacity: .3 + r() * .12, duration: .08, ease: 'none' }}, tt);
// "operations": the last lights in the office behind him go out, one by one
[3, 0, 1, 2].forEach((i, k) => tl.to('#s3-gw' + i, {{ opacity: 0, duration: .35 }}, {v['operations'] - .1} + k * .22));
tl.to('#s3-set', {{ opacity: .55, duration: 1.2, ease: 'sine.inOut' }}, {v['operations']});
"""


def caption_pages() -> list[dict]:
    out = []
    for p in TL.PAGES:
        try:
            s, e = ft(p["start"]), ft(p["end"])
        except ValueError:
            continue
        out.append({"start": s, "end": e, "text": p["text"], "words": [{"word": w["word"], "start": ft(w["start"]), "end": ft(w["end"])} for w in p["words"]]})
    return out


def narration(ws: Path) -> None:
    src = ROOT / "projects/ai-bubble-vs-dot-com/draft/narration.wav"
    parts, filt = [], []
    for i, (a, b, s) in enumerate(SEGS):
        filt.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,adelay={int(s * 1000)}:all=1[s{i}]")
        parts.append(f"[s{i}]")
    filt.append(f"{''.join(parts)}amix=inputs={len(parts)}:normalize=0,apad=whole_dur={D}[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-filter_complex", ";".join(filt), "-map", "[out]", str(ws / "narration.wav")], check=True)


def prepare(ws: Path) -> None:
    draft = ROOT / "projects/ai-bubble-vs-dot-com/draft"
    ws.mkdir(parents=True, exist_ok=True)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(draft / f, ws / f)
    for d in ("fonts", "vendor"):
        if not (ws / d).exists():
            shutil.copytree(draft / d, ws / d)
    shutil.copy(EL / "kit/scene3d.js", ws / "vendor/scene3d.js")
    shutil.copy(EL / "kit/rig3.js", ws / "vendor/rig3.js")
    (ws / "tex").mkdir(exist_ok=True)
    for f in (EL / "kit/assets/textures").glob("*.jpg"):
        shutil.copy(f, ws / "tex" / f.name)


def build(ws: Path) -> None:
    prepare(ws)
    g1, g2, g3 = capture("sf1_establishing"), capture("sf2_medium"), capture("sf3_closeup")
    g3["css"] = g3["css"].replace("#set,#glows", "#s3-set,#s3-glows")
    poses = {k: rig3.pose_angles(k) for k in rig3.POSES}
    shared = f"const TEX = 'tex/';\nconst ART = {json.dumps(common.ART)};\nR3.P = {json.dumps(poses)};"
    tag = ('<div class="tag" data-read>BigCart.com and Summit Ventures are fictional companies</div>')
    scenes = [Scene("s1", 0, CUT1, shot_html("s1", g1) + tag, js=shot_js("s1", g1, anim1(), GEO1)),
              Scene("s2", CUT1, round(CUT2 - CUT1, 3), shot_html("s2", g2), js=shot_js("s2", g2, anim2())),
              Scene("s3", CUT2, round(D - CUT2, 3), shot_html("s3", g3), js=shot_js("s3", g3, anim3()))]
    css = (".shot{position:absolute;inset:0;overflow:hidden}.layer{position:absolute;inset:0}.full{position:absolute;inset:0;width:1920px;height:1080px}"
           ".tag{position:absolute;right:64px;top:56px;padding:10px 20px;border-radius:8px;background:rgba(12,14,24,.62);color:#f3e9d6;font:700 30px Inter;letter-spacing:.2px}"
           "@font-face{font-family:Inter;src:url(fonts/inter-latin-700-normal.woff2) format('woff2');font-weight:800}"
           + g3["css"])
    html = assemble(title="Epoch Ledger — art direction v2 motion test", duration=D, scenes=scenes, caption_pages=caption_pages(),
                    extra_css=css, head_scripts=["vendor/scene3d.js", "vendor/rig3.js"], shared_js=shared, vignette=False)
    (ws / "index.html").write_text(html)
    narration(ws)
    print("wrote", ws / "index.html", f"({D}s)")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "projects/ai-bubble-vs-dot-com/motiontest")
