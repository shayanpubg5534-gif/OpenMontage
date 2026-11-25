"""Profitable and Broke — a 41 s Epoch Ledger demonstration episode, built from scratch.

  python epoch-ledger/episodes/profitable-and-broke/build.py [WS]      (default projects/profitable-and-broke/hyperframes)
  python epoch-ledger/scripts/render.py render WS --isolate --audio WS/mix.wav -o WS/profitable_and_broke.mp4

Story: Maya's bakery wins a profitable supermarket order, but she must pay for flour and wages now and is paid in
60 days, so she runs out of cash before the profit arrives; a short bank loan bridges the gap.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EL = HERE.parents[1]
ROOT = EL.parent
sys.path.insert(0, str(EL))
sys.path.insert(0, str(HERE))
import cast as CA  # noqa: E402
import diagrams as DG  # noqa: E402
import sets as SE  # noqa: E402
from kit import depth  # noqa: E402
from kit.assemble import Scene, assemble  # noqa: E402

ART = HERE / "artifacts"
WORDS = json.loads((ART / "words.json").read_text())
PAGES = json.loads((ART / "caption_phrases.json").read_text())
D = round(json.loads((ART / "narration_timing.json").read_text())["total"], 2)


def W(word, after=0.0):
    """Start time of the first spoken word matching `word` at or after `after` seconds."""
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(".,:;!?").lower() == word.lower():
            return round(w["start"], 3)
    raise KeyError(word)


T = {"order": W("order"), "12,000": W("12,000"), "month": W("month."[:-1]) if False else W("month"),
     "40,000": W("$40,000"), "Flour": W("Flower"), "wages": W("wages"), "30,000": W("30,000"), "10,000": W("10,000"), "profit": W("profit"),
     "flour2": W("flower", 16), "wages2": W("wages", 16), "due": W("due"), "pays": W("pays", 19), "days": W("days"),
     "bank12": W("12,000", 21), "pays_bills": W("pays", 24), "18,000": W("18,000"), "lends": W("lends"), "difference": W("difference"),
     "loan": W("loan"), "repaid": W("repaid"), "supermarket3": W("supermarket", 32.5), "pays3": W("pays", 33),
     "profitable": W("profitable"), "losses": W("losses"), "they": W("they", 37), "cash": W("cash"), "first": W("first")}
CUT = [0, 7.0, 15.85, 21.55, 24.45, 28.45, 30.75, 35.0, D]
H_M = 1.88                                # metres spanned by a sprite's 1000 units
PX_M = 1000 / H_M
INK = "#1b1410"


class Sprite:
    """A rig-v4 sprite in screen space at a projected foot point (perspective scale fixed at the feet)."""

    def __init__(self, pid, cam, foot, width=1600, anchor=.5):
        f, h = cam.project(foot), cam.project([foot[0], foot[1] + H_M, foot[2]])
        self.pid, self.cam, self.foot, self.W = pid, cam, foot, width
        self.s = (f[1] - h[1]) / 1000
        self.x, self.y = f[0] - width * anchor * self.s, h[1]

    def local(self, p):
        q = self.cam.project(p)
        return [round((q[0] - self.x) / self.s, 1), round((q[1] - self.y) / self.s, 1), round((p[2] - self.foot[2]) * PX_M, 1)]

    def lx(self, X):           # world x at the feet → local x
        return self.local([X, 0, self.foot[2]])[0]

    def screen(self, p):
        q = self.cam.project(p)
        return [round(q[0], 1), round(q[1], 1)]

    def svg(self, extra=""):
        return (f'<svg x="{self.x:.1f}" y="{self.y:.1f}" width="{self.W * self.s:.1f}" height="{1000 * self.s:.1f}" '
                f'viewBox="0 0 {self.W} 1000" overflow="visible"><g id="{self.pid}"></g>{extra}</svg>')

    def js_reg(self):
        return f"BR.spr['{self.pid}'] = [{self.x:.2f}, {self.y:.2f}, {self.s:.5f}];"


# a prop that passes between hands (and sprites) in screen space; a pure function of time like the rig itself
BRIDGE_JS = r"""
// segments: [a, b, charId, side, dx, dy, rot, sx, sy0, sy1, tr]   a prop in a hand (dx/dy 'auto': grip it where it is)
//           [a, b, 'path', x0, y0, x1, y1, rot, sx, sy0, sy1]     a free move (x0 null: from wherever it is)
const BR = { spr: {},
  add(el, t0, t1, segs, before, after) {
    const e = document.getElementById(el); if (!e) return;
    const lerp = (a, b, p) => a + (b - a) * p, ease = p => p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
    const wrist = (id, side, t) => { const c = R4.chars[id], J = R4._solve(c, t), w = J['wrist' + side], S = BR.spr[id]; return [S[0] + w[0] * S[2], S[1] + w[1] * S[2]]; };
    const pos = (i, t) => { const sg = segs[i];
      if (sg[2] === 'path') { const p = ease(Math.min(1, Math.max(0, (t - sg[0]) / (sg[1] - sg[0]))));
        const st = sg[3] === null ? (sg._s = sg._s || pos(i - 1, sg[0] - 1e-4)) : [sg[3], sg[4], sg[7], sg[8], sg[9]];
        return [lerp(st[0], sg[5], p), lerp(st[1], sg[6], p), sg[7] || 0, sg[8] || 1, lerp(sg[9] ?? 1, sg[10] ?? 1, p)]; }
      const w = wrist(sg[2], sg[3], t);
      if (sg[4] === 'auto') { if (!sg._o) { const m = /translate\(([-\d.]+) ([-\d.]+)\)/.exec(before || ''), pv = i > 0 ? pos(i - 1, sg[0] - 1e-4) : (m ? [+m[1], +m[2]] : wrist(sg[2], sg[3], sg[0])), w0 = wrist(sg[2], sg[3], sg[0]); sg._o = [pv[0] - w0[0], pv[1] - w0[1]]; } }
      const o = sg[4] === 'auto' ? sg._o : [sg[4], sg[5]], tr = sg[10] || 0, sy = tr ? lerp(sg[8] ?? 1, sg[9] ?? 1, Math.min(1, (t - sg[0]) / tr)) : (sg[8] ?? 1);
      return [w[0] + o[0], w[1] + o[1], sg[6] || 0, sg[7] || 1, sy]; };
    const place = t => { const i = segs.findIndex(s => t >= s[0] && t < s[1]);
      if (i < 0) { e.setAttribute('transform', t < segs[0][0] ? before : after); return; }
      const q = pos(i, t); e.setAttribute('transform', `translate(${q[0].toFixed(1)} ${q[1].toFixed(1)}) rotate(${q[2]}) scale(${q[3]} ${q[4].toFixed(3)})`); };
    tl.fromTo(e, { '--br': 0 }, { '--br': t1 - t0, duration: t1 - t0, ease: 'none', immediateRender: false, onUpdate() { place(this.startTime() + this.time()); } }, t0);
    place(t0);
  } };
"""


def layer(sid, k, z, inner):
    return f'<div class="layer" id="{sid}-L{k}" data-depth="{z}">{inner}</div>'


def card(cid, x, y, label, value, color, w=520):
    return (f'<div id="{cid}" class="callout" style="left:{x}px;top:{y}px;width:{w}px;opacity:0">'
            f'<div class="cl">{label}</div><div class="cv" style="color:{color}">{value}</div></div>')


SHEET = ('<g><rect x="-60" y="-80" width="120" height="160" rx="6" fill="#fffdf6" stroke="#1b1410" stroke-width="4"/>'
         '<rect x="-60" y="-80" width="120" height="30" rx="6" fill="#c0442e"/>'
         + "".join(f'<rect x="-44" y="{-36 + i * 22}" width="{88 - (i % 2) * 24}" height="8" fill="#9a8a74"/>' for i in range(5)) + '</g>')
TABLET = ('<g><rect x="-120" y="-80" width="240" height="160" rx="16" fill="#1b1d22" stroke="#0d0a08" stroke-width="4"/>'
          '<rect x="-108" y="-68" width="216" height="136" rx="6" fill="#f7f1e4"/><rect x="-108" y="-68" width="216" height="24" fill="#1f3550"/>'
          '<path d="M-90 10 H-60 V40 H90" fill="none" stroke="#c0442e" stroke-width="6"/></g>')
FOLDER = ('<g><rect x="-110" y="-75" width="220" height="150" rx="8" fill="#2d6fb3" stroke="#1b1410" stroke-width="4"/>'
          '<rect x="-80" y="-40" width="160" height="70" rx="4" fill="#f7f1e4"/><text x="0" y="5" text-anchor="middle" font-family="Inter" '
          'font-weight="800" font-size="30" fill="#1b1410">LOAN</text></g>')
CRATE = f'<g transform="translate(-200 -110)">{SE.crate()}</g>'


# ── S1 · the order ─────────────────────────────────────────────────────────────────────────────────────────────────
def s1_order(P, t0, t1):
    cam = SE.CAM_SHOP
    my = Sprite("maya1", cam, [-0.15, 0, -3.25], 1600)
    dn = Sprite("dan1", cam, [0.0, 0, -1.95], 3200)
    occ = {"y": my.local([0, 1.02, -3.0])[1]}
    counter_l = [my.local([-.45, 1.03, -2.8]), my.local([.25, 1.03, -2.8])]
    hand_pt = [0.38, 1.2, -2.6]
    to, o, m = T["order"], T["12,000"], T["month"]
    js = [my.js_reg(), dn.js_reg(),
          CA.create_js("maya1", "maya", my.lx(-0.15), 12, blink_seed=11, t0=t0, t1=t1, occlude=occ),
          CA.create_js("dan1", "daniel", dn.lx(2.6), -90, blink_seed=12, t0=t0, t1=t1),
          # Maya is setting out loaves, hands on the counter, eyes down
          f"R4.reach('maya1', 'R', {t0 - 1}, {json.dumps(counter_l[0])}, .3, {{ shape: 0, lean: 8, look: false }});",
          f"R4.reach('maya1', 'L', {t0 - 1}, {json.dumps(counter_l[1])}, .3, {{ shape: 0, look: false }});",
          f"R4.key('maya1', 'headPitch', {t0}, 14); R4.key('maya1', 'gaze', {t0}, [0, .7]);",
          # the door: Daniel walks in, she looks up
          f"R4.walk('dan1', {t0 + .25:.2f}, {to - .35:.2f}, {dn.lx(0.85)});",
          f"R4.look('maya1', {t0 + .9:.2f}, {json.dumps(my.local([1.6, 1.6, -1.75])[:2])}, .4); R4.express('maya1', {t0 + 1.1:.2f}, {{ smile: .45, brow: [.3, .3] }});",
          f"R4.release('maya1', 'L', {t0 + 1.0:.2f}, .5, [-24, 236, 30]); R4.release('maya1', 'R', {t0 + 1.0:.2f}, .5, [24, 236, 30]);",
          f"R4.key('maya1', 'lean', {t0 + 1.0:.2f}, 4, .5);",
          f"R4.turn('dan1', {to - .3:.2f}, -128, .5);",
          f"R4.arm('dan1', 'R', {t0:.2f}, [20, 210, 90], 0);",
          # he holds out the order on "order"; she takes it
          f"R4.reach('dan1', 'R', {to - .05:.2f}, {json.dumps(dn.local(hand_pt))}, .45, {{ shape: 1, look: false, lean: 6 }});",
          f"R4.look('maya1', {to - .1:.2f}, {json.dumps(my.local(hand_pt)[:2])}, .3);",
          f"R4.reach('maya1', 'L', {to + .3:.2f}, {json.dumps(my.local(hand_pt))}, .4, {{ shape: 1, look: false }});",
          f"R4.release('dan1', 'R', {to + .9:.2f}, .5, [20, 236, 30]);",
          # she draws it in and reads it; on "month" her face lights up; he nods
          f"R4.key('maya1', 'handWL', {to + .85:.2f}, {json.dumps(my.local([-0.05, 1.25, -2.85]))}, .5);",
          f"R4.key('maya1', 'headPitch', {to + .9:.2f}, 12, .4); R4.key('maya1', 'gaze', {to + .9:.2f}, [.2, .6], .3);",
          f"R4.express('maya1', {o - .2:.2f}, {{ brow: [.7, .7], smile: .2 }}, .3);",
          f"R4.key('maya1', 'headPitch', {m - .3:.2f}, -2, .4); R4.look('maya1', {m - .3:.2f}, {json.dumps(my.local([0.9, 1.7, -1.75])[:2])}, .35);",
          f"R4.express('maya1', {m - .2:.2f}, {{ smile: .9, brow: [.5, .5] }}, .35); R4.nod('dan1', {m - .1:.2f}, 2, 7);",
          f"BR.add('sheet1', {t0}, {t1}, [[{t0}, {to + .62:.2f}, 'dan1', 'R', 0, 10, -10, 1], [{to + .62:.2f}, {t1 + 1}, 'maya1', 'L', 'auto', 0, 0, 1]], '', '');",
          # the order itself, readable, on "12,000"
          f"gsap.set('#order1w', {{ opacity: 0 }}); tl.fromTo('#order1w', {{ opacity: 0, scale: .4, x: -260, y: 160 }}, {{ opacity: 1, scale: 1, x: 0, y: 0, transformOrigin: '1240px 200px', duration: .5, ease: 'power3.out', immediateRender: false }}, {o - .25:.2f});",
          # camera: a slow push toward Maya as the story becomes hers
          f"DL.set('s1', {t0}, {{ dolly: 0, truck: .1, focal: 1407, focus: [860, 560] }}); DL.move('s1', {t0 + .1:.2f}, {t1 - t0 - .1:.2f}, {{ dolly: .55, truck: -.05, focal: 1407, focus: [820, 520], ease: 'sine.inOut' }});"]
    props = f'<svg class="full" viewBox="0 0 1920 1080" overflow="visible"><g id="sheet1">{SHEET}</g></svg>'
    # characters who touch share one layer (one transform), so hands and props stay in contact during camera moves
    layers = (layer("s1", "bg", 4.0, f'<img class="plate" src="{P["shop"]["bg"]}"/>')
              + layer("s1", "chars", 3.0, f'<svg class="full" viewBox="0 0 1920 1080" overflow="visible">{my.svg()}{dn.svg()}</svg>{props}')
              + layer("s1", "fg", 1.1, f'<img class="plate" src="{P["shop"]["fg"]}"/>'))
    over = (f'<svg class="full" viewBox="0 0 1920 1080" style="position:absolute;inset:0"><g id="order1w" opacity="0">{DG.order_card("order1", 1240, 200)}</g></svg>'
            '<div class="tag">Maya, her bakery and FreshMart are fictional</div>')
    return layers + over, "\n".join(js)


# ── S2 · profit on paper ───────────────────────────────────────────────────────────────────────────────────────────
def s2_profit(t0, t1):
    svg, js = DG.profit_board(T)
    card_ = f'<g id="order2w">{DG.order_card("order2", 1240, 200)}</g>'
    js += (f"tl.fromTo('#order2w', {{ scale: 1, x: 0, y: 0 }}, {{ scale: .42, x: 360, y: -150, transformOrigin: '1240px 200px', duration: .7, ease: 'power2.inOut', immediateRender: false }}, {t0 + .35:.2f});"
           f"DL.set('s2', {t0}, {{ dolly: 0, focal: 1400, focus: [960, 540] }}); DL.move('s2', {t0 + .1:.2f}, {t1 - t0 - .1:.2f}, {{ dolly: .12, focal: 1400, focus: [760, 640] }});")
    return layer("s2", "board", 3.0, f'<svg class="full" viewBox="0 0 1920 1080">{svg}{card_}</svg>'), js


def s3_timeline(t0, t1):
    svg, js = DG.timeline_board(T)
    js += f"DL.set('s3', {t0}, {{ dolly: 0, focal: 1400, focus: [960, 540] }}); DL.move('s3', {t0 + .1:.2f}, {t1 - t0 - .1:.2f}, {{ dolly: .1, focal: 1400, focus: [960, 600] }});"
    return layer("s3", "board", 3.0, f'<svg class="full" viewBox="0 0 1920 1080">{svg}</svg>'), js


# ── S4a · Maya checks the account ──────────────────────────────────────────────────────────────────────────────────
def s4_tablet(P, t0, t1):
    cam = SE.CAM_SHOP
    my = Sprite("maya4", cam, [-0.15, 0, -3.25], 1600)
    occ = {"y": my.local([0, 1.02, -3.0])[1]}
    read = my.local([0.12, 1.12, -2.8])
    js = [my.js_reg(), CA.create_js("maya4", "maya", my.lx(-0.15), 8, blink_seed=21, t0=t0, t1=t1, occlude=occ),
          f"R4.reach('maya4', 'L', {t0 - 1}, {json.dumps(read)}, .3, {{ shape: 1, look: false }});",
          f"R4.key('maya4', 'headPitch', {t0}, 18); R4.key('maya4', 'gaze', {t0}, [.3, .9]); R4.express('maya4', {t0}, {{ smile: .1, brow: [.1, .1] }}, 0);",
          f"R4.reach('maya4', 'R', {T['bank12'] + .9:.2f}, {json.dumps([read[0] + 60, read[1] - 10, read[2] + 40])}, .35, {{ shape: 3, look: false }});",
          f"R4.express('maya4', {T['bank12'] + .2:.2f}, {{ brow: [-.3, -.3], smile: -.1 }}, .4);",
          f"BR.add('tab4', {t0}, {t1}, [[{t0 - 2}, {t1 + 1}, 'maya4', 'L', 60, -10, -8, .7]], '', '');",
          f"tl.fromTo('#bal4', {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: .35, ease: 'power2.out', immediateRender: false }}, {T['bank12'] - .1:.2f});",
          # push in toward the tablet: we are about to look at what she sees
          f"DL.set('s4', {t0}, {{ dolly: .55, truck: -.05, focal: 1407, focus: [820, 520] }}); DL.move('s4', {t0 + .1:.2f}, {t1 - t0 - .1:.2f}, {{ dolly: 1.3, truck: -.02, focal: 1407, focus: [840, 600], ease: 'power2.in' }});"]
    props = f'<svg class="full" viewBox="0 0 1920 1080" overflow="visible"><g id="tab4">{TABLET}</g></svg>'
    layers = (layer("s4", "bg", 4.0, f'<img class="plate" src="{P["shop"]["bg"]}"/>')
              + layer("s4", "maya", 3.4, f'<svg class="full" viewBox="0 0 1920 1080" overflow="visible">{my.svg()}</svg>{props}')
              + layer("s4", "fg", 1.1, f'<img class="plate" src="{P["shop"]["fg"]}"/>'))
    over = card("bal4", 1240, 300, "IN THE BANK", "$12,000", "#2f8a4a")
    return layers + over, "\n".join(js)


def s4b_gap(t0, t1):
    svg, js = DG.cash_chart("c4", "gap", {"start": t0, "pays": T["pays_bills"], "18,000": T["18,000"]})
    js += f"DL.set('s4b', {t0}, {{ dolly: .25, focal: 1400, focus: [960, 540] }}); DL.move('s4b', {t0 + .05:.2f}, {t1 - t0 - .05:.2f}, {{ dolly: 0, focal: 1400, focus: [960, 540], ease: 'power2.out' }});"
    return layer("s4b", "board", 3.0, f'<svg class="full" viewBox="0 0 1920 1080">{svg}</svg>'), js


# ── S5a · the bank ─────────────────────────────────────────────────────────────────────────────────────────────────
def s5_bank(P, t0, t1):
    cam = SE.CAM_BANK
    sp = Sprite("bank5", cam, [0.0, 0, -2.1], 4200)
    ok_x, my_x = sp.lx(-1.38), sp.lx(1.38)
    seat_ok, seat_my = sp.local([-1.45, .5, -2.1]), sp.local([1.45, .5, -2.1])
    f_start, f_push, f_end = [-0.78, .8, -2.1], [-0.5, .8, -2.1], [0.5, .8, -2.1]
    ln, dif = T["lends"], T["difference"]
    push0, push1, slide1, grip = ln - .1, ln + .45, ln + .95, dif + .12
    js = [f"BR.spr['okafor5'] = BR.spr['maya5'] = [{sp.x:.2f}, {sp.y:.2f}, {sp.s:.5f}];",
          CA.create_js("okafor5", "okafor", ok_x, 84, blink_seed=31, t0=t0, t1=t1),
          CA.create_js("maya5", "maya", my_x, -82, blink_seed=32, t0=t0, t1=t1),
          f"R4.sit('okafor5', {t0 - 1.5}, {json.dumps(seat_ok)}, .5, {{ lean: 6 }}); R4.sit('maya5', {t0 - 1.5}, {json.dumps(seat_my)}, .5, {{ lean: 8 }});",
          # his hand rests on the folder; on "lends" he slides it across the desk to her
          f"R4.reach('okafor5', 'R', {t0 - .4}, {json.dumps(sp.local([f_start[0], .86, -2.1]))}, .3, {{ shape: 2, look: false, lean: 14 }});",
          f"R4.look('okafor5', {t0 + .05:.2f}, {json.dumps(sp.local([1.5, 1.2, -2.1])[:2])}, .2); R4.look('maya5', {t0 + .05:.2f}, {json.dumps(sp.local([-1.5, 1.2, -2.1])[:2])}, .2);",
          f"R4.express('maya5', {t0:.2f}, {{ brow: [.4, -.2], smile: 0 }}, 0); R4.express('okafor5', {t0:.2f}, {{ smile: .35, brow: [.2, .2] }}, 0);",
          f"R4.key('okafor5', 'handWR', {push0:.2f}, {json.dumps(sp.local([f_push[0], .86, -2.1]))}, {push1 - push0:.2f});",
          f"R4.key('okafor5', 'lean', {push0:.2f}, 24, {push1 - push0:.2f});",
          f"R4.release('okafor5', 'R', {push1 + .1:.2f}, .5, [20, 236, 60]); R4.key('okafor5', 'lean', {push1 + .15:.2f}, 6, .5);",
          f"R4.look('maya5', {push1 - .2:.2f}, {json.dumps(sp.local(f_end)[:2])}, .3); R4.look('okafor5', {push1:.2f}, {json.dumps(sp.local(f_end)[:2])}, .3);",
          # she picks it up on "difference" and draws it to her; relief; he nods
          f"R4.reach('maya5', 'L', {grip - .35:.2f}, {json.dumps(sp.local([f_end[0], .86, -2.1]))}, .35, {{ shape: 1, look: false }});",
          f"R4.key('maya5', 'handWL', {grip + .15:.2f}, {json.dumps(sp.local([0.95, 1.05, -2.1]))}, .45); R4.key('maya5', 'lean', {grip + .15:.2f}, 6, .45);",
          f"R4.express('maya5', {grip + .2:.2f}, {{ brow: [.4, .4], smile: .75 }}, .4); R4.look('maya5', {grip + .45:.2f}, {json.dumps(sp.local([-1.5, 1.2, -2.1])[:2])}, .3);",
          f"R4.nod('okafor5', {grip + .3:.2f}, 1, 6); R4.look('okafor5', {grip + .3:.2f}, {json.dumps(sp.local([1.5, 1.2, -2.1])[:2])}, .3);",
          f"BR.add('folder5', {t0}, {t1}, [[{t0 - .1}, {push1:.2f}, 'okafor5', 'R', 'auto', 0, 0, .8, .32], "
          f"[{push1:.2f}, {slide1:.2f}, 'path', null, 0, {sp.screen(f_end)[0]}, {sp.screen(f_end)[1]}, 0, .8, .32, .32], "
          f"[{slide1:.2f}, {grip:.2f}, 'path', null, 0, {sp.screen(f_end)[0]}, {sp.screen(f_end)[1]}, 0, .8, .32, .32], "
          f"[{grip:.2f}, {t1 + 1}, 'maya5', 'L', 'auto', 0, 0, .8, .32, 1, .35]], 'translate({sp.screen(f_start)[0]} {sp.screen(f_start)[1]}) scale(.8 .32)', '');",
          f"tl.fromTo('#loan5', {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: .35, ease: 'power2.out', immediateRender: false }}, {ln + .2:.2f});",
          f"DL.set('s5', {t0}, {{ dolly: .1, truck: .04, focal: 1404, focus: [960, 600] }}); DL.move('s5', {t0 + .1:.2f}, {t1 - t0 - .1:.2f}, {{ dolly: .4, truck: 0, focal: 1404, focus: [980, 620] }});"]
    props = f'<svg class="full" viewBox="0 0 1920 1080" overflow="visible"><g id="folder5">{FOLDER}</g></svg>'
    layers = (layer("s5", "bg", 3.0, f'<img class="plate" src="{P["bank"]["bg"]}"/>')
              + layer("s5", "chars", 2.8, f'<svg class="full" viewBox="0 0 1920 1080" overflow="visible">{sp.svg().replace(chr(60) + "g id=" + chr(34) + "bank5" + chr(34) + "></g>", "<g id=" + chr(34) + "okafor5" + chr(34) + "></g><g id=" + chr(34) + "maya5" + chr(34) + "></g>")}</svg>{props}')
              + layer("s5", "fg", 0.9, f'<img class="plate" src="{P["bank"]["fg"]}"/>'))
    over = card("loan5", 1300, 140, "BRIDGE LOAN", "$18,000", "#2d6fb3") + '<div class="tag">Harbor Community Bank is fictional</div>'
    return layers + over, "\n".join(js)


def s5b_loan(t0, t1):
    svg, js = DG.cash_chart("c5", "loan", {"start": t0, "loan_fill": t0 + .15, "repaid": T["repaid"], "pays2": T["supermarket3"]})
    js += f"DL.set('s5b', {t0}, {{ dolly: 0, focal: 1400, focus: [960, 540] }}); DL.move('s5b', {t0 + .1:.2f}, {t1 - t0 - .1:.2f}, {{ dolly: .08, focal: 1400, focus: [1200, 500] }});"
    return layer("s5b", "board", 3.0, f'<svg class="full" viewBox="0 0 1920 1080">{svg}</svg>'), js


# ── S6 · the first delivery ────────────────────────────────────────────────────────────────────────────────────────
def s6_delivery(P, t0, t1):
    cam = SE.CAM_SHOP
    my = Sprite("maya6", cam, [-0.15, 0, -3.25], 1600)
    dn = Sprite("dan6", cam, [0.0, 0, -1.95], 3200)
    occ = {"y": my.local([0, 1.02, -3.0])[1]}
    crate_on = [0.55, 1.12, -2.75]
    over_counter = [0.42, 1.28, -2.5]
    js = [my.js_reg(), dn.js_reg(),
          CA.create_js("maya6", "maya", my.lx(-0.15), 20, blink_seed=41, t0=t0, t1=t1, occlude=occ),
          CA.create_js("dan6", "daniel", dn.lx(0.85), -128, blink_seed=42, t0=t0, t1=t1),
          f"R4.express('maya6', {t0}, {{ smile: .7, brow: [.3, .3] }}, 0); R4.express('dan6', {t0}, {{ smile: .4 }}, 0);",
          # she lifts the first crate of the order and hands it over the counter
          f"R4.reach('maya6', 'L', {t0 - .3}, {json.dumps(my.local(crate_on))}, .3, {{ shape: 1, look: false }});",
          f"R4.reach('maya6', 'R', {t0 - .3}, {json.dumps(my.local([0.2, 1.12, -2.75]))}, .3, {{ shape: 1, look: false }});",
          f"R4.key('maya6', 'handWL', {t0 + .5:.2f}, {json.dumps(my.local(over_counter))}, .8); R4.key('maya6', 'handWR', {t0 + .5:.2f}, {json.dumps(my.local([0.07, 1.28, -2.5]))}, .8);",
          f"R4.key('maya6', 'lean', {t0 + .5:.2f}, 18, .8);",
          f"R4.reach('dan6', 'R', {t0 + .8:.2f}, {json.dumps(dn.local([0.42, 1.25, -2.4]))}, .5, {{ shape: 1, look: false }}); R4.reach('dan6', 'L', {t0 + .8:.2f}, {json.dumps(dn.local([0.07, 1.25, -2.4]))}, .5, {{ shape: 1, look: false }});",
          f"R4.release('maya6', 'R', {t0 + 1.55:.2f}, .5, [24, 236, 30]); R4.release('maya6', 'L', {t0 + 1.55:.2f}, .5, [-24, 236, 30]); R4.key('maya6', 'lean', {t0 + 1.6:.2f}, 4, .5);",
          # he carries it out to the door; she watches the order leave
          f"R4.key('dan6', 'handWR', {t0 + 1.6:.2f}, {json.dumps(dn.local([0.55, 1.05, -1.95]))}, .5); R4.key('dan6', 'handWL', {t0 + 1.6:.2f}, {json.dumps(dn.local([0.25, 1.05, -1.95]))}, .5);",
          f"R4.walk('dan6', {t0 + 2.3:.2f}, {t0 + 5.0:.2f}, {dn.lx(3.4)}); R4.key('dan6', 'handBlendR', {t0 + 2.2:.2f}, 0, .3); R4.key('dan6', 'handBlendL', {t0 + 2.2:.2f}, 0, .3);",
          f"R4.arm('dan6', 'R', {t0 + 2.2:.2f}, [26, 150, 120], .3); R4.arm('dan6', 'L', {t0 + 2.2:.2f}, [-26, 150, 120], .3);",
          f"R4.look('maya6', {t0 + 2.5:.2f}, {json.dumps(my.local([2.5, 1.6, -1.75])[:2])}, .5);",
          f"R4.express('maya6', {T['they'] - .2:.2f}, {{ smile: .45, brow: [.1, .3] }}, .5); R4.look('maya6', {T['they']:.2f}, {json.dumps(my.local([0.0, 1.0, -2.6])[:2])}, .6);",
          f"BR.add('crate6', {t0}, {t1}, [[{t0 - .5}, {t0 + 1.3:.2f}, 'maya6', 'L', -122, 6, 0, .55], [{t0 + 1.3:.2f}, {t1 + 1}, 'dan6', 'R', 'auto', 0, 0, .55]], '', '');",
          # the lesson: the camera pulls back from the shop; the idea, in four words, on "cash"
          f"DL.set('s6', {t0}, {{ dolly: .45, truck: -.04, focal: 1407, focus: [860, 560] }});",
          f"DL.move('s6', {T['they'] - .4:.2f}, {t1 - T['they'] + .3:.2f}, {{ dolly: 0, truck: 0, focal: 1407, focus: [860, 560], ease: 'sine.inOut' }});",
          f"tl.fromTo('#title6', {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: .5, ease: 'power2.out', immediateRender: false }}, {T['cash'] - .15:.2f});"]
    props = f'<svg class="full" viewBox="0 0 1920 1080" overflow="visible"><g id="crate6">{CRATE}</g></svg>'
    # characters who touch share one layer (one transform), so hands and props stay in contact during camera moves
    layers = (layer("s6", "bg", 4.0, f'<img class="plate" src="{P["shop"]["bg"]}"/>')
              + layer("s6", "chars", 3.0, f'<svg class="full" viewBox="0 0 1920 1080" overflow="visible">{my.svg()}{dn.svg()}</svg>{props}')
              + layer("s6", "fg", 1.1, f'<img class="plate" src="{P["shop"]["fg"]}"/>'))
    over = '<div id="title6" class="title"><span>Profit</span> is not <span class="c">cash.</span></div>'
    return layers + over, "\n".join(js)


CSS = (".shot{position:absolute;inset:0;overflow:hidden;background:#100c0c}.layer{position:absolute;inset:0}"
       ".full{position:absolute;inset:0;width:1920px;height:1080px}.plate{position:absolute;left:0;top:0;width:1920px;height:1080px}"
       ".tag{position:absolute;left:56px;top:44px;padding:8px 18px;border-radius:8px;background:rgba(12,14,24,.6);color:#f3e9d6;font:700 26px Inter}"
       ".callout{position:absolute;padding:16px 28px;border-radius:16px;background:rgba(255,253,246,.96);border:4px solid #1b1410;box-shadow:0 10px 30px rgba(0,0,0,.3)}"
       ".callout .cl{font:800 28px Inter;letter-spacing:3px;color:#5a4a3a}.callout .cv{font:800 80px Fraunces;line-height:1.05}"
       ".title{position:absolute;left:50%;top:120px;transform:translateX(-50%);white-space:nowrap;padding:18px 56px 26px;border-radius:24px;"
       "background:rgba(20,16,12,.78);font:800 104px Fraunces;color:#fffdf6;opacity:0;box-shadow:0 12px 40px rgba(0,0,0,.4)}.title span{color:#f2c66d}.title .c{color:#7fd89a}"
       "@font-face{font-family:Inter;src:url(fonts/inter-latin-700-normal.woff2) format('woff2');font-weight:800}")


def plates(ws: Path) -> dict:
    pd = ws / "plates"
    (pd / "tex").mkdir(parents=True, exist_ok=True)
    for f in (EL / "kit/assets/textures").glob("*.jpg"):
        if not (pd / "tex" / f.name).exists():
            shutil.copy(f, pd / "tex" / f.name)
    if not (pd / "fonts").exists():
        shutil.copytree(ws / "fonts", pd / "fonts")
    pre = SE.prelude(depth.foliage(seed=21)) + SE.BAKERY_GLOWS
    out = {}
    for name, scene, cam, light in (("shop", SE.BAKERY, SE.CAM_SHOP, SE.BAKERY_LIGHT), ("bank", SE.BANK, SE.CAM_BANK, SE.BANK_LIGHT)):
        L = depth.layered(pd, name, scene, cam, light, prelude_js=pre, split=(1.2, 1.2), blur={"fg": 6}, layers=("bg", "fg"))
        out[name] = L.rel
    return out


def prepare(ws: Path):
    """A fresh workspace with its own render cache: vendor scripts from the kit, fonts, HyperFrames config."""
    ws.mkdir(parents=True, exist_ok=True)
    draft = ROOT / "projects/ai-bubble-vs-dot-com/draft"
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(draft / f, ws / f)
    for d in ("fonts", "vendor"):
        if not (ws / d).exists():
            shutil.copytree(draft / d, ws / d)
    for f in ("scene3d.js", "rig4.js", "depth.js"):
        shutil.copy(EL / "kit" / f, ws / "vendor" / f)


def sound(ws: Path):
    """Original synthesised sound design (no music): room tone, footsteps, paper, tablet taps, the folder slide."""
    import numpy as np
    import soundfile as sf
    sys.path.insert(0, str(EL / "episodes/ai-bubble-vs-dot-com"))
    import sfx as S  # noqa: E402
    SR = S.SR
    n = int(D * SR)
    fx = np.zeros(n, np.float32)
    r = np.random.default_rng(7)

    def put(t, snd):
        s = max(0, int(t * SR)); e = min(n, s + len(snd))
        if e > s:
            fx[s:e] += snd[:e - s]
    shop = [(CUT[0], CUT[1]), (CUT[3], CUT[4]), (CUT[7], CUT[8])]
    for a, b in shop:
        put(a, S.norm(S.bed(b - a, lo=180, hi=1600, mod=.15), -40))
    for a, b in ((CUT[1], CUT[3]), (CUT[4], CUT[5]), (CUT[6], CUT[7])):
        put(a, S.norm(S.bed(b - a, lo=200, hi=1200, mod=.1), -46))
    put(CUT[5], S.norm(S.bed(CUT[6] - CUT[5], lo=150, hi=900, mod=.2), -40))
    for t in np.arange(.35, T["order"] - .4, .52):
        put(t, S.norm(S.clunk(), -40 + r.uniform(-2, 1)))                     # Daniel's footsteps
    for t in np.arange(CUT[7] + 2.4, CUT[7] + 5.0, .5):
        put(t, S.norm(S.clunk(), -40 + r.uniform(-2, 1)))
    rust = lambda db: S.norm(S.highpass(S.noise(int(.18 * SR)), 2500) * np.exp(-np.arange(int(.18 * SR)) / (SR * .05)).astype(np.float32), db)
    put(T["order"] + .5, rust(-30)); put(T["order"] + .9, rust(-32))       # the order changes hands
    for k in range(3):
        put(T["Flour"] - .05 + k * .05, rust(-34)); put(T["wages"] - .05 + k * .05, rust(-34))
    put(T["10,000"], S.norm(S.chime(880)[: int(.4 * SR)], -30))
    put(T["days"] + .2, S.norm(S.chime(660)[: int(.3 * SR)], -32))
    put(T["bank12"] + .9, S.norm(S.tick(), -28)); put(T["pays_bills"], S.norm(S.tick(), -26))
    put(T["18,000"], S.norm(S.clunk(), -30))
    put(T["lends"] + .1, rust(-30)); put(T["difference"], rust(-31))
    put(T["pays3"], S.norm(S.chime(880)[: int(.4 * SR)], -30)); put(T["pays3"] + .9, S.norm(S.chime(1320)[: int(.4 * SR)], -32))
    put(CUT[7] + .4, S.norm(S.clunk(), -32)); put(CUT[7] + 1.4, S.norm(S.clunk(), -33))
    sf.write(ws / "sfx.wav", np.stack([fx, fx], 1), SR)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(ws / "narration.wav"), "-i", str(ws / "sfx.wav"), "-filter_complex",
                    "[0:a][1:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[o]", "-map", "[o]", "-ar", "48000", "-ac", "2", str(ws / "mix.wav")], check=True)


def build(ws: Path):
    prepare(ws)
    P = plates(ws)
    shots = [("s1", lambda a, b: s1_order(P, a, b)), ("s2", s2_profit), ("s3", s3_timeline), ("s4", lambda a, b: s4_tablet(P, a, b)),
             ("s4b", s4b_gap), ("s5", lambda a, b: s5_bank(P, a, b)), ("s5b", s5b_loan), ("s6", lambda a, b: s6_delivery(P, a, b))]
    scenes = []
    for i, (sid, fn) in enumerate(shots):
        t0, t1 = CUT[i], CUT[i + 1]
        html, js = fn(t0, t1)
        body = f'<div class="shot" id="{sid}" style="filter:contrast(1.04) saturate(1.06)">{html}</div>'
        scenes.append(Scene(sid, t0, round(t1 - t0, 3), body, js="{\n" + js + "\n}"))
    page = assemble(title="Profitable and Broke", duration=D, scenes=scenes, caption_pages=PAGES, extra_css=CSS, audio="mix.wav",
                    vignette=False, head_scripts=["vendor/scene3d.js", "vendor/rig4.js", "vendor/depth.js"], shared_js=BRIDGE_JS)
    page = page.replace('window.__timelines["main"] = tl;', 'R4.attach(tl);\nwindow.__timelines["main"] = tl;')
    (ws / "index.html").write_text(page)
    sound(ws)
    print("wrote", ws / "index.html", f"({D}s, {len(scenes)} shots)")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "projects/profitable-and-broke/hyperframes")
