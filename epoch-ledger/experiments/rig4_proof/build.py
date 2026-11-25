"""Rig v4 proof: the founder and the investor acting in two short shots (no narration; not part of the episode).

  A  office floor  — the founder walks in (planted feet), stops, turns, sees the cash gauge and reacts.
  B  boardroom     — the founder makes his case (his mouth moves only while he speaks); the investor looks up, nods,
                     picks up the pen, signs, puts the pen down; they shake hands.

  python epoch-ledger/experiments/rig4_proof/build.py [WS]   (default projects/ai-bubble-vs-dot-com/rig4_proof)
Plates are the approved cached PNGs from the BigCart A′ workspace (nothing re-rendered). Original implementation.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EL = HERE.parents[1]
ROOT = EL.parent
sys.path.insert(0, str(EL))
from kit import money as M, rig4  # noqa: E402
from kit.assemble import Scene, assemble  # noqa: E402

spec = importlib.util.spec_from_file_location("ov3", EL / "episodes/ai-bubble-vs-dot-com/motiontest/office_v3.py")
OV3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(OV3)
C8 = OV3.C8
SRC = ROOT / "projects/ai-bubble-vs-dot-com/compare/aprime"
H_M = 1.88                       # metres spanned by the 1000-unit sprite height (figure ≈ 936 units ≈ 1.76 m)
PX_M = 1000 / H_M
D = 12.4
CUT = 5.2


class Sprite:
    """A rig-v4 sprite placed in screen space at a projected foot point (perspective scale fixed at the feet)."""

    def __init__(self, pid, foot, width=1400, anchor=.5):
        f, h = C8.project(foot), C8.project([foot[0], foot[1] + H_M, foot[2]])
        self.pid, self.foot, self.W = pid, foot, width
        self.s = (f[1] - h[1]) / 1000
        self.x, self.y = f[0] - width * anchor * self.s, h[1]

    def local(self, world):
        """World point → sprite-local (x, y, z); z from depth relative to the feet (toward the camera is +)."""
        p = C8.project(world)
        return [round((p[0] - self.x) / self.s, 1), round((p[1] - self.y) / self.s, 1), round((world[2] - self.foot[2]) * PX_M, 1)]

    def svg(self, extra=""):
        return (f'<svg x="{self.x:.1f}" y="{self.y:.1f}" width="{self.W * self.s:.1f}" height="{1000 * self.s:.1f}" '
                f'viewBox="0 0 {self.W} 1000" overflow="visible"><g id="{self.pid}"></g>{extra}</svg>')


def shot_a(t0, t1):
    # screen-space floor sprite: feet on the floor near the camera, 660 px tall
    s, W = .66, 3200
    x0, y0 = -120, 1012 - 1000 * s
    L = lambda sx: round((sx - x0) / s, 1)
    svg = f'<svg x="{x0}" y="{y0:.1f}" width="{W * s:.1f}" height="{1000 * s:.1f}" viewBox="0 0 {W} 1000" overflow="visible"><g id="fa"></g></svg>'
    layers = f'<svg id="a-live" class="full" viewBox="0 0 1920 1080" overflow="visible">{svg}</svg>'
    gauge = [L(1800), (420 - y0) / s]
    js = (rig4.create_js("fa", "founder", x=L(2080), yaw=-90, ground=1000, blink_seed=11, t0=t0, t1=t1)
          + f"R4.walk('fa', {t0 + .2:.2f}, {t0 + 2.6:.2f}, {L(1120)});"
          + f"R4.turn('fa', {t0 + 2.75:.2f}, -20, .7);"
          # he notices the cash gauge: eyes first, then the head; the brows knit, shoulders sink a little
          + f"R4.look('fa', {t0 + 3.4:.2f}, {json.dumps(gauge)}, .4);"
          + f"R4.express('fa', {t0 + 3.75:.2f}, {{brow: [-.7, -.7], smile: -.35}}, .4);"
          + f"R4.key('fa', 'lean', {t0 + 3.9:.2f}, 10, .6); R4.key('fa', 'headPitch', {t0 + 4.3:.2f}, 6, .5);"
          + f"R4.arm('fa', 'L', {t0 + 4.1:.2f}, [-30, 200, 90], .6); R4.arm('fa', 'R', {t0 + 4.2:.2f}, [40, 210, 110], .6);")
    return layers, js


def shot_b(t0, t1):
    IV, FD = [-0.1, 0, -3.3], [0.62, 0, -3.3]      # a step closer than v3, so the handshake meets naturally
    iv = Sprite("ib", IV, 1400)
    fd = Sprite("fb", FD, 1400)
    table_y = iv.local([IV[0], .79, IV[2]])[1]
    # the term sheet lies turned toward the investor (its signature line on the edge nearest her)
    cx, cz, hw, hd = .2, -3.1, .22, .176
    pen_l = iv.local([.3, .80, -3.2])
    sig = [iv.local([cx - .04 - k * .04, .80, cz - hd + .063]) for k in range(4)]
    mid = [.26, 1.1, -3.16]
    hi, hf = iv.local(mid), fd.local(mid)
    pen = (f'<g id="pen4" transform="translate({pen_l[0]} {pen_l[1]}) rotate(-12)"><rect x="-6" y="-4" width="70" height="8" rx="4" fill="#14213d" '
           f'stroke="#0d0a08" stroke-width="2"/><rect x="58" y="-3" width="10" height="6" fill="#c9a24a"/></g>')
    doc = M.term_sheet("ts")
    live = ("const sc = S3.scene();"
            f"sc.art([{cx + hw}, .792, {cz - hd}], [{cx - hw}, .792, {cz - hd}], [{cx + hw}, .792, {cz + hd}], 700, 560, {json.dumps(doc)}, {{ bias: .4 }});")
    layers = (f'<svg id="b-doc" class="full" viewBox="0 0 1920 1080"></svg>'
              f'<svg id="b-live" class="full" viewBox="0 0 1920 1080" overflow="visible">{iv.svg(pen)}{fd.svg()}</svg>')
    occ = {"y": table_y}
    js = ("{ const cam = " + C8.js() + "; " + OV3.V2.BOARD_LIGHT + "\n" + live + "\n"
          "document.getElementById('b-doc').innerHTML = S3.render(sc, cam, L, { ow: 2.0, shadowBlur: 5, uid: 'lb' }); }\n"
          + rig4.create_js("ib", "investor", x=700, yaw=60, ground=1000, blink_seed=21, t0=t0, t1=t1).replace("});", f', "occlude": {json.dumps(occ)}}});')
          + rig4.create_js("fb", "founder", x=700, yaw=-60, ground=1000, blink_seed=22, t0=t0, t1=t1).replace("});", f', "occlude": {json.dumps(occ)}}});')
          # beat 1: he makes his case (only he speaks); she reads, then looks up at him
          + f"R4.key('ib', 'headPitch', {t0}, 14); R4.key('ib', 'gaze', {t0}, [.3, .6]);"
          + f"R4.say('fb', {t0 + .3:.2f}, {t0 + 1.7:.2f}, 5); R4.express('fb', {t0 + .3:.2f}, {{brow: [.5, .5]}});"
          + f"R4.arm('fb', 'R', {t0 + .5:.2f}, [-10, 150, 150], .45); R4.key('fb', 'handShape' + 'R', {t0 + .6:.2f}, 2, .3); R4.arm('fb', 'R', {t0 + 1.5:.2f}, [-18, 236, 22], .5); R4.key('fb', 'handShapeR', {t0 + 1.6:.2f}, 0, .3);"
          + f"R4.look('ib', {t0 + 1.0:.2f}, [1100, 120], .4); R4.express('ib', {t0 + 1.3:.2f}, {{brow: [.3, .1], smile: .3}}); R4.nod('ib', {t0 + 1.8:.2f}, 2, 7);"
          # beat 2: she picks up the pen and signs
          + f"R4.reach('ib', 'R', {t0 + 2.4:.2f}, {json.dumps(pen_l)}, .6, {{shape: 1}});"
          + f"R4.hold('ib', 'R', 'pen4', {t0 + 3.0:.2f}, {t0 + 5.0:.2f}, 200);"
          + "".join(f"R4.key('ib', 'handWR', {t0 + 3.2 + k * .35:.2f}, {json.dumps([sig[k][0], sig[k][1] - 4 - (k % 2) * 6, sig[k][2]])}, .3);" for k in range(4))
          + f"{{ const s = document.getElementById('ts-sig'); if (s) {{ const n = s.getTotalLength(); gsap.set(s, {{ strokeDasharray: n + ' ' + n, strokeDashoffset: n }}); tl.to(s, {{ strokeDashoffset: 0, duration: 1.3, ease: 'none' }}, {t0 + 3.25:.2f}); }} }}"
          + f"R4.key('ib', 'handWR', {t0 + 4.65:.2f}, {json.dumps(pen_l)}, .3); R4.release('ib', 'R', {t0 + 5.0:.2f}, .5, [18, 236, 22]); R4.key('ib', 'lean', {t0 + 5.0:.2f}, 4, .5);"
          f"tl.set('#pen4', {{ attr: {{ transform: 'translate({pen_l[0]} {pen_l[1]}) rotate(-12)' }} }}, {t0 + 5.0:.2f});"
          # beat 3: handshake — both hands meet at one point, grip, three pumps; he smiles
          + f"R4.reach('ib', 'R', {t0 + 5.55:.2f}, {json.dumps(hi)}, .55, {{shape: 1, look: false}}); R4.reach('fb', 'R', {t0 + 5.45:.2f}, {json.dumps(hf)}, .6, {{shape: 1, look: false}});"
          + "".join(f"R4.key('{p}', 'handW' + 'R', {t0 + 6.15 + k * .16:.2f}, {json.dumps([q[0], q[1] + (14 if k % 2 == 0 else -6), q[2]])}, .16, 'sine');" for p, q in (("ib", hi), ("fb", hf)) for k in range(4))
          + f"R4.express('fb', {t0 + 6.0:.2f}, {{smile: .7, brow: [.3, .3]}}); R4.express('ib', {t0 + 6.1:.2f}, {{smile: .5}}); R4.look('fb', {t0 + 5.4:.2f}, {json.dumps([hf[0] - 300, hf[1] - 420])});"
          + f"R4.look('ib', {t0 + 5.4:.2f}, {json.dumps([hi[0] + 300, hi[1] - 420])});")
    return layers, js


def build(ws: Path):
    ws.mkdir(parents=True, exist_ok=True)
    for d in ("fonts", "vendor"):
        if (ws / d).exists():
            shutil.rmtree(ws / d)
        shutil.copytree(SRC / d, ws / d)
    for f in ("rig4.js", "scene3d.js"):
        shutil.copy(EL / "kit" / f, ws / "vendor" / f)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(SRC / f, ws / f)
    (ws / "plates").mkdir(exist_ok=True)
    plates = {}
    for name in ("office_floor", "boardroom_c8"):
        src = next((SRC / "plates").glob(name + "-*.png"))
        shutil.copy(src, ws / "plates" / src.name)
        plates[name] = "plates/" + src.name
    la, ja = shot_a(0, CUT)
    lb, jb = shot_b(CUT, D)
    css = (".shot{position:absolute;inset:0;overflow:hidden;background:#100c0c}.layer{position:absolute;inset:0}"
           ".full{position:absolute;inset:0;width:1920px;height:1080px}.plate{position:absolute;left:0;top:0;width:1920px;height:1080px}"
           ".tag{position:absolute;right:64px;top:56px;padding:10px 20px;border-radius:8px;background:rgba(12,14,24,.62);color:#f3e9d6;font:700 28px Inter}")
    tag = '<div class="tag">Rig v4 proof · BigCart.com and Summit Ventures are fictional</div>'
    scenes = [Scene("a", 0, CUT, OV3.V2.shot("a", plates["office_floor"], la, tag), js="{\n" + ja + "\n}"),
              Scene("b", CUT, round(D - CUT, 3), OV3.V2.shot("b", plates["boardroom_c8"], lb, tag), js="{\n" + jb + "\n}")]
    html = assemble(title="Rig v4 proof", duration=D, scenes=scenes, extra_css=css, audio="", vignette=False,
                    head_scripts=["vendor/scene3d.js", "vendor/rig4.js"],
                    shared_js=f"const TEX = 'tex/';\nconst ART = {json.dumps(OV3.V2.common.ART)};")
    html = html.replace("window.__timelines[\"main\"] = tl;", "R4.attach(tl);\nwindow.__timelines[\"main\"] = tl;")
    (ws / "index.html").write_text(html)
    print("wrote", ws / "index.html")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "projects/ai-bubble-vs-dot-com/rig4_proof")
