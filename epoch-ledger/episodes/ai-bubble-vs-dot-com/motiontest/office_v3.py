"""Office sequence v3 (14 s) — meaning-first redesign of c03_04 + c03_05 as three connected beats.

  python epoch-ledger/episodes/ai-bubble-vs-dot-com/motiontest/office_v3.py [WS]     (default projects/<slug>/office_v3)

Beats (plan: office_v3_plan.json), four compositions, every figure from one Ledger (kit/finstate.py):
  A  0.00– 4.60  SPENDING — one office shot. BigCart's cash sits on the founder's desk as banknote bundles. As each
                 cost is named, bills fly to it: the TV commercial airs, pay lands on the staff's desks, a new server
                 rack is wheeled in. The pile and the counter fall $13M → $9M.
  B  4.60– 8.65  NOT ENOUGH REVENUE — explanatory charts: money out (by category) vs money in, the monthly shortfall,
                 then the cash line heading for zero in about three months.
  C1 8.65–11.10  THE AGREEMENT — Summit Ventures' boardroom: the investor signs the term sheet; handshake.
  C2 11.10–14.00 THE MONEY ARRIVES — the wire is received, the cash pile refills, and the same cash chart jumps,
                 then heads down again toward "next round needed": survival depends on *continuing* capital.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ov2", HERE / "office_v2.py")
V2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V2)

from kit import explain as X, finmech as F, money as M, rig3  # noqa: E402
from kit.assemble import Scene, assemble  # noqa: E402
from kit.camera3d import Camera  # noqa: E402
from kit.finstate import Ledger  # noqa: E402
from kit.plates import plate  # noqa: E402

W, D, ROOT, INK = V2.W, 14.0, V2.ROOT, "#1b1410"
CUT = [0, 4.6, 8.65, 11.1, D]

# One source of truth for every number on screen (illustrative figures for a fictional company)
LED = Ledger(start=13).spend({"ADVERTISING": 2, "PAYROLL": 1, "SERVERS": 1}).earn({"REVENUE": 1})
FUNDING = {2: 20}                                  # received at the end of month 2
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
CASH_AT_FUNDING = LED.balance_after(2)             # 4
CASH_AFTER_FUNDING = CASH_AT_FUNDING + FUNDING[2]  # 24


def counter(cid, x, y, value, label="BIGCART CASH", note="illustrative"):
    return (f'<div id="{cid}" class="counter" style="left:{x}px;top:{y}px"><div class="cl">{label}</div>'
            f'<div class="cv"><span id="{cid}-v">{LED.fmt(value)}</span></div><div class="cn">{note}</div></div>')


def step(sid, n, text):
    return f'<div id="{sid}" class="step"><span class="sn">{n}</span>{text}</div>'


# ── A: spending ──────────────────────────────────────────────────────────────────────────────────
C3 = V2.C3


def beat_a(t0, t1):
    wa, we, wi = W("advertising", "c03_04"), W("employees", "c03_04"), W("infrastructure", "c03_04")
    # live: the workstations + a technician wheeling a new server rack in (faces left, pushes the rack)
    live = ["const sc = S3.scene();"]
    for x, z, pid, cos, sk, hr, st in V2.WS3:
        live.append(f"sc.box([{x + .2}, .72, {z - .62}], [{x + .92}, .76, {z + .62}], {{ color: '#8a6440' }}, {{}});"
                    f"[[{x + .24}, {z - .58}], [{x + .88}, {z - .58}], [{x + .24}, {z + .58}], [{x + .88}, {z + .58}]].forEach(([a, b]) => sc.box([a - .025, 0, b - .025], [a + .025, .72, b + .025], {{ color: '#3a3a40' }}, {{ shadow: false }}));"
                    f"sc.box([{x + .5}, .76, {z - .24}], [{x + .9}, 1.16, {z + .24}], {{ color: '#d8d0bc', gloss: .15 }}, {{}});"
                    f"sc.box([{x + .26}, .76, {z - .2}], [{x + .4}, .78, {z + .2}], {{ color: '#e4dccc' }}, {{ shadow: false }});"
                    f"sc.box([{x - .24}, .44, {z - .24}], [{x + .2}, .5, {z + .24}], {{ color: '#2a2a32' }}, {{}}); sc.box([{x - .3}, .5, {z - .22}], [{x - .25}, 1.02, {z + .22}], {{ color: '#2a2a32' }}, {{}});")
        live.append(f"sc.sprite([{x}, -.41, {z}], 1.76, {json.dumps(V2.figure(pid, cos, sk, hr, st, pose='type', shadow=False, glasses=pid == 'k2'))}, .4, {{ viewBox: '0 0 400 1000', id: '{pid}' }});")
    rack = ('<g id="rk3"><rect x="300" y="380" width="250" height="600" rx="8" fill="#1e2228" stroke="#1b1410" stroke-width="5"/>'
            + "".join(f'<rect x="318" y="{400 + r * 44}" width="214" height="34" rx="3" fill="#2c3138"/>'
                      f'<g class="led" opacity=".2"><circle cx="{500}" cy="{417 + r * 44}" r="6" fill="#5aff7a"/><circle cx="{478}" cy="{417 + r * 44}" r="6" fill="#7fd8ff"/></g>' for r in range(13))
            + '<circle cx="330" cy="992" r="14" fill="#1b1410"/><circle cx="520" cy="992" r="14" fill="#1b1410"/></g>')
    tech = V2.figure("tk", "casual2", 2, 0, "buzz", angles=rig3.reach("stand", (318, 520)), extra=rack, mirrored=True)
    live.append(f"sc.sprite([1.95, 0, -6.3], 1.76, {json.dumps(tech)}, .4, {{ viewBox: '0 0 400 1000', id: 'tk' }});")
    # 2D: wall TV with a real commercial, founder at his desk with the company's cash
    tvx, tvy, tvw = 380, 70, 470
    sx, sy, sw, sh = F.tv_screen(tvx, tvy, tvw)
    tv = F.tv_set("tv", tvx, tvy, tvw, ad=M.commercial("ad", sx, sy, sw, sh), stand=False)
    envs = []
    for i, (x, z, pid, *_r) in enumerate(V2.WS3):
        e = C3.project([x + .33, .78, z + .32]); s = min(1.45, 3.6 / e[2])
        envs.append((F.envelope(f"pay{i}", e[0], e[1] - 14 * s, s), (e[0], e[1] - 20 * s), pid))
    rack_end = C3.project([1.62, .9, -6.3])
    fsc = .82
    a_fd = rig3.pose_angles("stand2")
    founder = V2.svg_sprite((-30, 236, 400 * fsc, 1000 * fsc, fsc), V2.figure("fda", "founder", 0, 2, "parted", angles=a_fd), "fda-s")
    desk = (f'<path d="M-20 790 L1010 790 L1100 1100 L-20 1100Z" fill="#5a3a24" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M-20 790 L1010 790 L1016 812 L-20 812Z" fill="#7a5236"/>')
    pile = M.cash_pile("cash", 300, 760, LED.units(LED.start), cols=4, w=118)
    fx = V2.svg_layer("a-fx", tv + "".join(e for e, _, _ in envs) + founder + desk + pile + '<g id="a-bills"></g>', M.bill_defs("a"))
    layers = '<svg id="a-live" class="full" viewBox="0 0 1920 1080"></svg>' + fx
    over = counter("ca", 300, 520, LED.start)
    pile_top = (520, 690)
    after_ads, after_pay, after_srv = (LED.start - LED.spending["ADVERTISING"], LED.start - LED.spending["ADVERTISING"] - LED.spending["PAYROLL"], LED.start - LED.total_spending)
    tvc = (sx + sw / 2, sy + sh / 2)
    js = [f"{{ const cam = {C3.js()}; {V2.OFFICE_LIGHT}", *live,
          "document.getElementById('a-live').innerHTML = S3.render(sc, cam, L, { ow: 2.0, shadowBlur: 5, uid: 'la' });",
          "gsap.set(['#pay0 .env', '#pay1 .env', '#pay2 .env', '#pay3 .env'], { opacity: 0 });",
          # advertising: bills to the TV, the commercial airs
          f"FM.bills('a-bills', 'a', [{pile_top[0]}, {pile_top[1]}], [{tvc[0]:.0f}, {tvc[1]:.0f}], {wa - .15:.2f}, {{ n: 9, dur: .8, arc: 200 }});",
          f"FM.pileTo('cash', {wa - .1:.2f}, {LED.units(after_ads)}); FM.count('#ca-v', {LED.start}, [[{wa:.2f}, {after_ads}], [{we:.2f}, {after_pay}], [{wi + .1:.2f}, {after_srv}]]);",
          f"FM.powerOn('tv', {wa + .45:.2f});",
          f"tl.fromTo('#ad-parcel', {{ x: 0 }}, {{ x: {sw * .17:.0f}, y: {-sh * .03:.0f}, duration: .7, ease: 'power2.inOut', immediateRender: false }}, {wa + .8:.2f});",
          f"tl.fromTo('#ad-card', {{ opacity: 0 }}, {{ opacity: 1, duration: .25, immediateRender: false }}, {wa + 1.7:.2f});",
          # payroll: bills to each desk, pay envelopes land, staff glance at them
          *[f"FM.bills('a-bills', 'a', [{pile_top[0]}, {pile_top[1]}], [{to[0]:.0f}, {to[1]:.0f}], {we - .2 + i * .14:.2f}, {{ n: 3, dur: .55, arc: 140, size: .8 }}); FM.pop('#pay{i} .env', {we + .35 + i * .14:.2f});"
            f"R3.rot('{pid}', 'neck', {we + .45 + i * .14:.2f}, 16, .3); R3.look('{pid}', {we + .4 + i * .14:.2f}, 2, 2); R3.rot('{pid}', 'neck', {we + 1.1 + i * .14:.2f}, 6, .4); R3.look('{pid}', {we + 1.1 + i * .14:.2f}, 0, 0, .3);"
            for i, (_e, to, pid) in enumerate(envs)],
          f"FM.pileTo('cash', {we - .15:.2f}, {LED.units(after_pay)});",
          *[f"R3.type('{pid}', {t0}, {t1}, {21 + i});" for i, (_x, _z, pid, *_r) in enumerate(V2.WS3)],
          # infrastructure: the rack is wheeled in (it arrives on the word), bills follow it, it powers up
          f"{{ const A0 = R3.walk(cam, 'tk', 'tk', [3.0, 0, -6.3], [1.95, 0, -6.3], 1.76, .4, {wi - 1.1:.2f}, {wi + .1:.2f}, .5); tl.set('#tk', {{ attr: A0 }}, {t0}); }}",
          f"FM.bills('a-bills', 'a', [{pile_top[0]}, {pile_top[1]}], [{rack_end[0]:.0f}, {rack_end[1]:.0f}], {wi - .05:.2f}, {{ n: 5, dur: .7, arc: 170, size: .85 }});",
          f"FM.pileTo('cash', {wi:.2f}, {LED.units(after_srv)});",
          f"tl.fromTo('#rk3 .led', {{ opacity: .2 }}, {{ opacity: 1, duration: .05, stagger: .03, immediateRender: false }}, {wi + .45:.2f});",
          # the founder signs off each spend: gestures toward each destination, eyes leading the head
          f"R3.look('fda', {wa - .35:.2f}, 3, -2); R3.keys('fda', 'neck', [[{wa - .3:.2f}, -8, .35], [{we - .3:.2f}, 2, .35], [{wi - .3:.2f}, -2, .35]]);",
          f"R3.keys('fda', 'uarm-front', [[{wa - .35:.2f}, -100, .4, 'power2.out'], [{wa + .6:.2f}, -30, .5], [{we - .3:.2f}, -70, .35, 'power2.out'], [{we + .6:.2f}, -20, .5], [{wi - .3:.2f}, -84, .35, 'power2.out'], [{wi + .5:.2f}, -14, .5]]);",
          f"R3.keys('fda', 'farm-front', [[{wa - .35:.2f}, -30, .4], [{wa + .6:.2f}, -40, .5], [{we - .3:.2f}, -20, .35], [{wi - .3:.2f}, -24, .35], [{wi + .5:.2f}, -30, .5]]);",
          f"R3.look('fda', {we - .3:.2f}, 3, 1); R3.look('fda', {wi - .3:.2f}, 3, -1); R3.blinks('fda', {t0}, {t1}, 31); R3.breathe('#fda-upper', {t0}, {t1}, 2, 3.4);",
          f"tl.fromTo('#a-cam', {{ scale: 1 }}, {{ scale: 1.035, transformOrigin: '55% 45%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0}); }}"]
    return layers, "\n".join(js), over


# ── B / C2: the explanation (cash-flow bars, cash runway) ───────────────────────────────────────
ICONS = {}
RUNWAY = dict(x=1000, y=150, w=850, h=640)


def runway(uid):
    return X.runway_chart(uid, RUNWAY["x"], RUNWAY["y"], RUNWAY["w"], RUNWAY["h"], LED, months=10, injections=FUNDING, labels=MONTHS, ymax=27, ticks=(5, 10, 15, 20, 25), title="BigCart's cash")


def beat_b(t0, t1):
    bars = X.cashflow_bars("cf", 70, 150, 860, 640, LED, title="One month at BigCart")
    fx = V2.svg_layer("b-fx", bars + runway("rw"))
    wr, ws, we_ = W("revenue", "c03_04"), W("sustain", "c03_04"), W("enough", "c03_04")
    js = f"""
gsap.set(['#rw-jump', '#rw-line2', '#rw-next'], {{ opacity: 0 }});
tl.fromTo(['#b-fx'], {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: .45, ease: 'power2.out', immediateRender: false }}, {t0});
gsap.set(['#cf-seg0', '#cf-seg1', '#cf-seg2', '#cf-in'], {{ scaleY: 0, transformOrigin: '50% 100%' }});
gsap.set(['#cf-segl0', '#cf-segl1', '#cf-segl2', '#cf-outl', '#cf-inl', '#cf-gap', '#cf-gapl', '#rw-runway'], {{ opacity: 0 }});
[0, 1, 2].forEach(i => {{ tl.to('#cf-seg' + i, {{ scaleY: 1, duration: .45, ease: 'power2.out' }}, {t0 + .35} + i * .3); tl.to('#cf-segl' + i, {{ opacity: 1, duration: .25 }}, {t0 + .5} + i * .3); }});
tl.to('#cf-outl', {{ opacity: 1, duration: .3 }}, {t0 + 1.25:.2f});
tl.to('#cf-in', {{ scaleY: 1, duration: .5, ease: 'power2.out' }}, {wr:.2f}); tl.to('#cf-inl', {{ opacity: 1, duration: .3 }}, {wr + .1:.2f});
tl.to('#cf-gap', {{ opacity: 1, duration: .3 }}, {wr + .55:.2f}); FM.pop('#cf-gapl', {wr + .7:.2f}, {{ origin: '0% 50%' }});
{{ const l = document.getElementById('rw-line'), n = l.getTotalLength(); gsap.set(l, {{ strokeDasharray: n + ' ' + n, strokeDashoffset: n }});
  tl.to(l, {{ strokeDashoffset: 0, duration: .9, ease: 'power1.inOut' }}, {ws - .1:.2f}); }}
{{ const l = document.getElementById('rw-proj'), n = l.getTotalLength(); gsap.set(l, {{ strokeDasharray: '12 10', strokeDashoffset: 0 }});
  tl.fromTo('#rw-runway', {{ opacity: 0 }}, {{ opacity: 1, duration: .35, immediateRender: false }}, {ws + .8:.2f}); }}
tl.fromTo('#b-cam', {{ scale: 1 }}, {{ scale: 1.02, transformOrigin: '50% 50%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0});
"""
    return fx, js, ""


def beat_c2(t0, t1):
    slip = M.wire_slip("wire", 110, 150, "$20,000,000", "Summit Ventures", "BigCart.com", w=700)
    pile = M.cash_pile("cash2", 140, 770, LED.units(CASH_AT_FUNDING), cols=4, w=96, capacity=LED.units(CASH_AFTER_FUNDING))
    fx = V2.svg_layer("c2-fx", runway("rw2") + slip + pile + '<g id="c2-bills"></g>', M.bill_defs("c2"))
    over = counter("cc", 640, 600, CASH_AT_FUNDING) + step("st2", 2, "Money received")
    wc, wp, wcap = W("continuing", "c03_05"), W("provide", "c03_05"), W("capital", "c03_05")
    js = f"""
gsap.set(['#rw2-jump', '#rw2-line2', '#rw2-next'], {{ opacity: 0 }});
tl.fromTo('#wire', {{ x: -820 }}, {{ x: 0, duration: .55, ease: 'power3.out', immediateRender: false }}, {t0 + .05:.2f}); gsap.set('#wire', {{ x: -820 }});
FM.stampIn('#wire-stamp', {wc + .55:.2f});
FM.bills('c2-bills', 'c2', [600, 420], [330, 700], {wc + .8:.2f}, {{ n: 12, dur: .6, arc: 60, gap: .05 }});
FM.pileTo('cash2', {wc + .9:.2f}, {LED.units(CASH_AFTER_FUNDING)}, {{ gap: .035 }});
FM.count('#cc-v', {CASH_AT_FUNDING}, [[{wc + .9:.2f}, {CASH_AFTER_FUNDING}, .9]]);
tl.fromTo('#st2', {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: .35, immediateRender: false }}, {t0 + .1:.2f});
tl.to('#rw2-runway', {{ opacity: .3, duration: .3 }}, {wcap - .1:.2f});
tl.fromTo('#rw2-jump', {{ opacity: 0, scaleY: 0, transformOrigin: '50% 100%' }}, {{ opacity: 1, scaleY: 1, duration: .4, ease: 'power2.out', immediateRender: false }}, {wcap - .3:.2f});
{{ const l = document.getElementById('rw2-line2'), n = l.getTotalLength(); gsap.set(l, {{ strokeDasharray: n + ' ' + n, strokeDashoffset: n, opacity: 1 }});
  tl.to(l, {{ strokeDashoffset: 0, duration: .7, ease: 'power1.inOut' }}, {wcap + .1:.2f}); }}
tl.fromTo('#rw2-next', {{ opacity: 0 }}, {{ opacity: 1, duration: .3, immediateRender: false }}, {wcap + .8:.2f});
tl.fromTo('#c2-cam', {{ scale: 1 }}, {{ scale: 1.02, transformOrigin: '50% 50%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0});
"""
    return fx, js, over


# ── C1: the agreement (boardroom two-shot) ──────────────────────────────────────────────────────
C8 = Camera(pos=[0.25, 1.68, -1.1], look=[0.25, 1.0, -4], fov=46)
IV, FD, BG = [-0.22, 0, -3.3], [0.72, 0, -3.3], [-1.55, 0, -3.8]
DOC = [0.25, .79, -3.0]


def beat_c1(t0, t1):
    b_iv, b_fd = V2.sprite_box(C8, IV), V2.sprite_box(C8, FD)
    sig = C8.project([DOC[0] + .14, .8, DOC[2] + .1])
    a_sign = rig3.reach("stand2", V2.to_view(b_iv, (sig[0], sig[1] - 10)))
    a_read = rig3.reach("stand2", V2.to_view(b_iv, (sig[0] - 60, sig[1] - 40)))
    mid = C8.project([0.25, 1.05, -3.2])
    a_shake_iv = rig3.reach("stand2", V2.to_view(b_iv, (mid[0], mid[1])))
    a_shake_fd = rig3.reach("stand2", V2.to_view(b_fd, (mid[0], mid[1]), mirrored=True))
    doc = M.term_sheet("ts")
    live = ("const sc = S3.scene();" + V2.BOARD_TABLE
            + f"sc.art([{DOC[0] - .3}, .792, {DOC[2] + .24}], [{DOC[0] + .3}, .792, {DOC[2] + .24}], [{DOC[0] - .3}, .792, {DOC[2] - .24}], 700, 560, {json.dumps(doc)}, {{ bias: .4 }});"
            + f"sc.sprite({IV}, 1.76, {json.dumps(V2.figure('iv', 'suit', 1, 5, 'short', angles=a_read, prop='pen'))}, .4, {{ viewBox: '0 0 400 1000', id: 'iv' }});"
            + f"sc.sprite({FD}, 1.76, {json.dumps(V2.figure('fdb', 'founder', 0, 2, 'parted', pose='talk', mirrored=True, expr='talk'))}, .4, {{ viewBox: '0 0 400 1000', id: 'fdb' }});"
            + f"sc.sprite({BG}, 1.76, {json.dumps(V2.figure('bgi', 'suit_w', 5, 1, 'bun', pose='hips', glasses=True))}, .4, {{ viewBox: '0 0 400 1000', id: 'bgi' }});")
    layers = '<svg id="c1-live" class="full" viewBox="0 0 1920 1080"></svg>'
    ws, wd, wi = W("survival", "c03_05"), W("depended", "c03_05"), W("investors", "c03_05")
    talk = rig3.pose_angles("talk")
    js = (f"{{ const cam = {C8.js()}; {V2.BOARD_LIGHT}\n{live}\n"
          "document.getElementById('c1-live').innerHTML = S3.render(sc, cam, L, { ow: 2.0, shadowBlur: 5, uid: 'lc1' });\n"
          # the founder makes the case; the investor reads, then signs on "investors"; handshake
          f"R3.talk('fdb', {t0 + .05:.2f}, {wd + .3:.2f}, 81); R3.keys('fdb', 'uarm-front', [[{ws - .1:.2f}, {talk['uarm-front'] - 14}, .3], [{wd - .1:.2f}, {talk['uarm-front']}, .35]]);"
          f"R3.keys('fdb', 'farm-front', [[{ws - .1:.2f}, {talk['farm-front'] - 18}, .3], [{wd - .1:.2f}, {talk['farm-front']}, .35]]); R3.look('fdb', {t0:.2f}, 2, 0, 0);"
          f"R3.keys('iv', 'neck', [[{t0:.2f}, 14, 0], [{ws:.2f}, 6, .35], [{wd + .2:.2f}, 15, .35], [{wi + .25:.2f}, 2, .35]]); R3.look('iv', {t0:.2f}, 1, 3, 0); R3.look('iv', {ws:.2f}, 2, 0); R3.look('iv', {wd + .2:.2f}, 1, 3);"
          f"R3.pose('iv', {json.dumps(a_sign)}, {wd + .15:.2f}, .45);"
          f"R3.write('iv', {wd + .6:.2f}, {wi + .1:.2f}, {a_sign['farm-front']}, 9);"
          f"{{ const s = document.getElementById('ts-sig'), n = s.getTotalLength(); gsap.set(s, {{ strokeDasharray: n + ' ' + n, strokeDashoffset: n }}); tl.to(s, {{ strokeDashoffset: 0, duration: {wi + .1 - (wd + .6):.2f}, ease: 'none' }}, {wd + .6:.2f}); }}"
          f"R3.pose('iv', {json.dumps(a_shake_iv)}, {wi + .2:.2f}, .4); R3.pose('fdb', {json.dumps(a_shake_fd)}, {wi + .2:.2f}, .4);"
          f"R3.look('iv', {wi + .2:.2f}, 3, -1); R3.look('fdb', {wi + .2:.2f}, 3, -1);"
          f"[['iv', {a_shake_iv['farm-front']}], ['fdb', {a_shake_fd['farm-front']}]].forEach(([p, f]) => R3.keys(p, 'farm-front', [[{wi + .62:.2f}, f - 7, .1], [{wi + .72:.2f}, f + 5, .1], [{wi + .82:.2f}, f - 4, .1], [{wi + .92:.2f}, f, .1]]));"
          f"R3.blinks('iv', {t0}, {t1}, 82); R3.blinks('fdb', {t0}, {t1}, 83); R3.blinks('bgi', {t0}, {t1}, 84); R3.idle('bgi', {t0}, {t1}, 85, 6);"
          f"tl.fromTo('#st1', {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: .35, immediateRender: false }}, {wi + .05:.2f});"
          f"tl.fromTo('#c1-cam', {{ scale: 1 }}, {{ scale: 1.045, transformOrigin: '50% 60%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0}); }}")
    return layers, js, step("st1", 1, "Agreement signed") + V2.TAG.format("Summit Ventures and BigCart.com are fictional companies")


NAME_SVG = ('<rect width="1200" height="40" fill="none"/><text x="600" y="32" text-anchor="middle" font-family="Fraunces" font-weight="800" '
            'font-size="34" letter-spacing="14" fill="#e9dcbc">SUMMIT VENTURES</text>')


# ── build ────────────────────────────────────────────────────────────────────────────────────────
def build(ws: Path):
    V2.prepare(ws)
    P = V2.plates(ws)
    art5 = {"window": V2.SF2.art2_dict()["window"], "plant": V2.SF2.art2_dict()["plant"], "name": NAME_SVG}
    c8_html = V2.plate_html(ws / "plates" / "boardroom_c8.html", f"const ART5 = {json.dumps(art5)};" + V2.BOARD_SCENE + V2.BOARD_TABLE,
                            "const GLOWS = [[[-1.6,2.5,-2.7],160,'#ffd8a0'],[[1.6,2.5,-2.7],160,'#ffd8a0']];" + f"const cam = {C8.js()};", V2.BOARD_LIGHT,
                            root="contrast(1.05) saturate(1.05)")
    c8 = plate(ws / "plates", "boardroom_c8", c8_html, assets=tuple(sorted((V2.EL / "kit/assets/textures").glob("*.jpg"))) + (V2.EL / "kit/scene3d.js",))
    P["boardroom_c8"] = "plates/" + c8.name
    beats = [("a", beat_a, "office_floor", 0), ("b", beat_b, "office_tank", .58), ("c1", beat_c1, "boardroom_c8", 0), ("c2", beat_c2, "office_tank", .58)]
    scenes = []
    for i, (sid, fn, pl, dim) in enumerate(beats):
        t0, t1 = CUT[i], CUT[i + 1]
        layers, js, over = fn(t0, t1)
        scenes.append(Scene(sid, t0, round(t1 - t0, 3), V2.shot(sid, P[pl], layers, over, dim=dim), js="{\n" + js + "\n}"))
    poses = {k: rig3.pose_angles(k) for k in rig3.POSES}
    css = (".shot{position:absolute;inset:0;overflow:hidden;background:#100c0c}.layer{position:absolute;inset:0}.full{position:absolute;inset:0;width:1920px;height:1080px}"
           ".plate{position:absolute;left:0;top:0;width:1920px;height:1080px}"
           ".tag{position:absolute;right:64px;top:56px;padding:10px 20px;border-radius:8px;background:rgba(12,14,24,.62);color:#f3e9d6;font:700 28px Inter}"
           ".counter{position:absolute;padding:14px 26px;border-radius:14px;background:rgba(14,12,10,.72);color:#f3e9d6;font-family:Inter;box-shadow:0 8px 30px rgba(0,0,0,.35)}"
           ".counter .cl{font:700 24px Inter;letter-spacing:3px;color:#c8bba0}.counter .cv{font:800 72px Fraunces;color:#9fe39a;line-height:1.05}.counter .cn{font:700 18px Inter;color:#8a8070}"
           ".step{position:absolute;left:64px;top:52px;padding:10px 22px 10px 12px;border-radius:30px;background:rgba(12,14,24,.72);color:#f3e9d6;font:700 32px Inter;opacity:0}"
           ".step .sn{display:inline-block;width:44px;height:44px;margin-right:14px;border-radius:22px;background:#f2c66d;color:#1b1410;text-align:center;line-height:44px;font:800 28px Inter}"
           "@font-face{font-family:Inter;src:url(fonts/inter-latin-700-normal.woff2) format('woff2');font-weight:800}")
    html = assemble(title="Epoch Ledger — office sequence v3", duration=D, scenes=scenes, caption_pages=V2.caption_pages(), extra_css=css,
                    head_scripts=["vendor/scene3d.js", "vendor/rig3.js", "vendor/finmotion.js"], vignette=False,
                    shared_js=f"const TEX = 'tex/';\nconst ART = {json.dumps(V2.common.ART)};\nR3.P = {json.dumps(poses)};")
    (ws / "index.html").write_text(html)
    V2.narration(ws)
    print("wrote", ws / "index.html", f"({D}s, {len(scenes)} compositions)")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "projects/ai-bubble-vs-dot-com/office_v3")
