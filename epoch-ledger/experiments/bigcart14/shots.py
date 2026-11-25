"""BigCart 14 s — the four shots of BRIEF.md as framework-neutral parts (html layers, js on absolute timeline seconds,
overlay html, plate name). build_aprime.py assembles them for OpenMontage/HyperFrames; build_openfilm.py wraps each as
an OpenFilm page whose frame(t) seeks the same timeline. Experimental — not part of the approved kit.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MT = ROOT / "epoch-ledger/episodes/ai-bubble-vs-dot-com/motiontest"


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, MT / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V3 = _load("ov3", "office_v3.py")
V2 = V3.V2
from kit import finmech as F, money as M, rig3  # noqa: E402

W, LED, INK = V3.W, V3.LED, "#1b1410"
D = 14.0
CUT = [0, 6.45, 8.65, 11.1, D]
C3 = V2.C3
PILE_TOP = (520, 690)


def office_shot(sid: str, px: str, t0: float, t1: float, mode: str):
    """mode 'burn' (shot 1) or 'refill' (shot 4): the same office, the same people, the same desk and cash."""
    wa, we, wi = W("advertising", "c03_04"), W("employees", "c03_04"), W("infrastructure", "c03_04")
    wr = W("revenue", "c03_04")
    wc, wcap = W("continuing", "c03_05"), W("capital", "c03_05")
    ws3 = [(x, z, px + pid, cos, sk, hr, st) for x, z, pid, cos, sk, hr, st in V2.WS3]
    live = ["const sc = S3.scene();"]
    for x, z, pid, cos, sk, hr, st in ws3:
        live.append(f"sc.box([{x + .2}, .72, {z - .62}], [{x + .92}, .76, {z + .62}], {{ color: '#8a6440' }}, {{}});"
                    f"[[{x + .24}, {z - .58}], [{x + .88}, {z - .58}], [{x + .24}, {z + .58}], [{x + .88}, {z + .58}]].forEach(([a, b]) => sc.box([a - .025, 0, b - .025], [a + .025, .72, b + .025], {{ color: '#3a3a40' }}, {{ shadow: false }}));"
                    f"sc.box([{x + .5}, .76, {z - .24}], [{x + .9}, 1.16, {z + .24}], {{ color: '#d8d0bc', gloss: .15 }}, {{}});"
                    f"sc.box([{x + .26}, .76, {z - .2}], [{x + .4}, .78, {z + .2}], {{ color: '#e4dccc' }}, {{ shadow: false }});"
                    f"sc.box([{x - .24}, .44, {z - .24}], [{x + .2}, .5, {z + .24}], {{ color: '#2a2a32' }}, {{}}); sc.box([{x - .3}, .5, {z - .22}], [{x - .25}, 1.02, {z + .22}], {{ color: '#2a2a32' }}, {{}});")
        live.append(f"sc.sprite([{x}, -.41, {z}], 1.76, {json.dumps(V2.figure(pid, cos, sk, hr, st, pose='type', shadow=False, glasses=pid.endswith('k2')))}, .4, {{ viewBox: '0 0 400 1000', id: '{pid}' }});")
    rack = (f'<g id="{px}rk"><rect x="300" y="380" width="250" height="600" rx="8" fill="#1e2228" stroke="#1b1410" stroke-width="5"/>'
            + "".join(f'<rect x="318" y="{400 + r * 44}" width="214" height="34" rx="3" fill="#2c3138"/>'
                      f'<g class="led" opacity="{.2 if mode == "burn" else 1}"><circle cx="500" cy="{417 + r * 44}" r="6" fill="#5aff7a"/><circle cx="478" cy="{417 + r * 44}" r="6" fill="#7fd8ff"/></g>' for r in range(13))
            + '<circle cx="330" cy="992" r="14" fill="#1b1410"/><circle cx="520" cy="992" r="14" fill="#1b1410"/></g>')
    tech = V2.figure(px + "tk", "casual2", 2, 0, "buzz", angles=rig3.reach("stand", (318, 520)), extra=rack, mirrored=True)
    live.append(f"sc.sprite([1.95, 0, -6.3], 1.76, {json.dumps(tech)}, .4, {{ viewBox: '0 0 400 1000', id: '{px}tk' }});")
    tvx, tvy, tvw = 380, 70, 470
    sx, sy, sw, sh = F.tv_screen(tvx, tvy, tvw)
    tv = F.tv_set(px + "tv", tvx, tvy, tvw, ad=M.commercial(px + "ad", sx, sy, sw, sh), stand=False)
    envs = []
    for i, (x, z, pid, *_r) in enumerate(ws3):
        e = C3.project([x + .33, .78, z + .32]); s = min(1.45, 3.6 / e[2])
        envs.append((F.envelope(f"{px}pay{i}", e[0], e[1] - 14 * s, s), (e[0], e[1] - 20 * s), pid))
    rack_end = C3.project([1.62, .9, -6.3])
    fsc = .82
    founder = V2.svg_sprite((-30, 236, 400 * fsc, 1000 * fsc, fsc), V2.figure(px + "fd", "founder", 0, 2, "parted", angles=rig3.pose_angles("stand2")), px + "fd-s")
    desk = (f'<path d="M-20 790 L1010 790 L1100 1100 L-20 1100Z" fill="#5a3a24" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M-20 790 L1010 790 L1016 812 L-20 812Z" fill="#7a5236"/>')
    extra = ""
    if mode == "burn":
        n0, cap = LED.units(LED.start), LED.units(LED.start) + 1
        pay = ('<g id="' + px + 'cust"><rect x="-70" y="-44" width="140" height="88" rx="6" fill="#f2e6c8" stroke="#1b1410" stroke-width="4"/>'
               '<path d="M-70 -44 L0 8 L70 -44" fill="none" stroke="#1b1410" stroke-width="4"/>'
               '<text x="0" y="30" text-anchor="middle" font-family="Inter" font-weight="800" font-size="15" fill="#2a6a2a">CUSTOMER</text>'
               '<text x="0" y="-52" text-anchor="middle" font-family="Inter" font-weight="800" font-size="18" fill="#f2e6c8">orders paid</text></g>')
        extra = f'<g id="{px}custwrap" transform="translate(2060 600)">{pay}</g>'
    else:
        n0, cap = LED.units(V3.CASH_AT_FUNDING), LED.units(V3.CASH_AFTER_FUNDING)
        page = ('<rect x="0" y="0" width="300" height="190" fill="#fbfaf4" stroke="#1b1410" stroke-width="3"/>'
                '<text x="150" y="34" text-anchor="middle" font-family="Inter" font-weight="800" font-size="20" fill="#1f3a5a">WIRE RECEIVED</text>'
                '<text x="150" y="62" text-anchor="middle" font-family="Inter" font-weight="700" font-size="14" fill="#5a6470">First National Bank</text>'
                '<text x="150" y="112" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="34" fill="#2a6a2a">$20,000,000</text>'
                '<text x="150" y="146" text-anchor="middle" font-family="Inter" font-weight="700" font-size="14" fill="#1b1410">from Summit Ventures</text>'
                '<text x="150" y="168" text-anchor="middle" font-family="Inter" font-weight="700" font-size="14" fill="#1b1410">to BigCart.com</text>')
        extra = (f'<g id="{px}fax"><rect x="770" y="700" width="230" height="100" rx="12" fill="#d8d4c8" stroke="{INK}" stroke-width="4"/>'
                 f'<rect x="790" y="690" width="190" height="16" rx="4" fill="#3a3a42"/><rect x="930" y="725" width="50" height="16" rx="3" fill="#2a2a30"/>'
                 f'<circle cx="800" cy="735" r="6" fill="#5aff7a"/></g>'
                 f'<g id="{px}faxclip"><clipPath id="{px}fc"><rect x="700" y="420" width="400" height="280"/></clipPath>'
                 f'<g clip-path="url(#{px}fc)"><g id="{px}faxpage" transform="translate(735 700)">{page}</g></g></g>')
    pile = M.cash_pile(px + "cash", 300, 760, n0, cols=4, w=118, capacity=cap)
    fx = V2.svg_layer(sid + "-fx", tv + "".join(e for e, _, _ in envs) + founder + desk + pile + extra + f'<g id="{px}bills"></g>', M.bill_defs(px + "b"))
    layers = f'<svg id="{sid}-live" class="full" viewBox="0 0 1920 1080"></svg>' + fx
    tvc = (sx + sw / 2, sy + sh / 2)
    bills = lambda to, t, **o: f"FM.bills('{px}bills', '{px}b', [{PILE_TOP[0]}, {PILE_TOP[1]}], [{to[0]:.0f}, {to[1]:.0f}], {t:.2f}, {json.dumps(o)});"
    js = [f"{{ const cam = {C3.js()}; {V2.OFFICE_LIGHT}", *live,
          f"document.getElementById('{sid}-live').innerHTML = S3.render(sc, cam, L, {{ ow: 2.0, shadowBlur: 5, uid: 'l{sid}' }});",
          f"gsap.set([{', '.join(repr(f'#{px}pay{i} .env') for i in range(4))}], {{ opacity: 0 }});",
          *[f"R3.type('{pid}', {t0}, {t1}, {21 + i});" for i, (_x, _z, pid, *_r) in enumerate(ws3)],
          f"R3.blinks('{px}fd', {t0}, {t1}, 31);"]   # (R3.breathe on -upper fought R3.rot('upper'): non-deterministic — found by openfilm look)
    pile_c = f"{PILE_TOP[0] - 70}px {PILE_TOP[1] + 20}px"
    if mode == "burn":
        a_ads, a_pay, a_srv = LED.start - LED.spending["ADVERTISING"], LED.start - LED.spending["ADVERTISING"] - LED.spending["PAYROLL"], LED.start - LED.total_spending
        a_rev = a_srv + LED.income["REVENUE"]
        js += [
            # reveal: open close on the cash, pull back to show what it feeds ("spending heavily")
            f"gsap.set('#{sid}-cam', {{ scale: 1.55, transformOrigin: '{pile_c}' }});   // the opening frame must already be framed (a frame-0 flash otherwise)",
            f"tl.fromTo('#{sid}-cam', {{ scale: 1.55 }}, {{ scale: 1.0, transformOrigin: '{pile_c}', duration: 2.1, ease: 'power2.inOut', immediateRender: false }}, {t0});",
            bills(tvc, wa - .2, n=9, dur=.8, arc=200), f"FM.pileTo('{px}cash', {wa - .15:.2f}, {LED.units(a_ads)});",
            f"FM.powerOn('{px}tv', {wa + .4:.2f});",
            f"tl.fromTo('#{px}ad-parcel', {{ x: 0 }}, {{ x: {sw * .17:.0f}, y: {-sh * .03:.0f}, duration: .7, ease: 'power2.inOut', immediateRender: false }}, {wa + .75:.2f});",
            f"tl.fromTo('#{px}ad-card', {{ opacity: 0 }}, {{ opacity: 1, duration: .25, immediateRender: false }}, {wa + 1.6:.2f});",
            *[bills(to, we - .25 + i * .14, n=3, dur=.55, arc=140, size=.8) + f"FM.pop('#{px}pay{i} .env', {we + .3 + i * .14:.2f});"
              f"R3.rot('{pid}', 'neck', {we + .4 + i * .14:.2f}, 16, .3); R3.look('{pid}', {we + .35 + i * .14:.2f}, 2, 2); R3.rot('{pid}', 'neck', {we + 1.05 + i * .14:.2f}, 6, .4); R3.look('{pid}', {we + 1.05 + i * .14:.2f}, 0, 0, .3);"
              for i, (_e, to, pid) in enumerate(envs)],
            f"FM.pileTo('{px}cash', {we - .2:.2f}, {LED.units(a_pay)});",
            f"{{ const A0 = R3.walk(cam, '{px}tk', '{px}tk', [3.0, 0, -6.3], [1.95, 0, -6.3], 1.76, .4, {wi - 1.1:.2f}, {wi + .1:.2f}, .5); tl.set('#{px}tk', {{ attr: A0 }}, {t0}); }}",
            bills(rack_end, wi - .05, n=5, dur=.7, arc=170, size=.85), f"FM.pileTo('{px}cash', {wi:.2f}, {LED.units(a_srv)});",
            f"tl.fromTo('#{px}rk .led', {{ opacity: .2 }}, {{ opacity: 1, duration: .05, stagger: .03, immediateRender: false }}, {wi + .45:.2f});",
            # the meagre inflow: one customer payment travels in and adds a single bundle, as the camera moves in on the pile
            f"tl.to('#{sid}-cam', {{ scale: 1.22, transformOrigin: '{pile_c}', duration: 1.9, ease: 'sine.inOut' }}, {wr - 1.5:.2f});",
            f"tl.fromTo('#{px}custwrap', {{ attr: {{ transform: 'translate(2060 600)' }} }}, {{ attr: {{ transform: 'translate({PILE_TOP[0] + 60} {PILE_TOP[1] - 40})' }}, duration: 1.0, ease: 'power2.out', immediateRender: false }}, {wr - .7:.2f});",
            f"tl.to('#{px}custwrap', {{ opacity: 0, duration: .2 }}, {wr + .35:.2f}); FM.pileTo('{px}cash', {wr + .3:.2f}, {LED.units(a_rev)});",
            f"FM.count('#{px}c-v', {LED.start}, [[{wa:.2f}, {a_ads}], [{we:.2f}, {a_pay}], [{wi + .1:.2f}, {a_srv}], [{wr + .35:.2f}, {a_rev}, .4]]);",
            # the founder directs each spend, then watches the single payment arrive and sags
            f"R3.look('{px}fd', {wa - .4:.2f}, 3, -2); R3.keys('{px}fd', 'neck', [[{wa - .35:.2f}, -8, .35], [{we - .35:.2f}, 2, .35], [{wi - .35:.2f}, -2, .35], [{wr - .7:.2f}, 2, .4], [{wr + .3:.2f}, 12, .5]]);",
            f"R3.keys('{px}fd', 'uarm-front', [[{wa - .4:.2f}, -100, .4, 'power2.out'], [{wa + .55:.2f}, -30, .5], [{we - .35:.2f}, -70, .35, 'power2.out'], [{we + .55:.2f}, -20, .5], [{wi - .35:.2f}, -84, .35, 'power2.out'], [{wi + .45:.2f}, -14, .5]]);",
            f"R3.keys('{px}fd', 'farm-front', [[{wa - .4:.2f}, -30, .4], [{wa + .55:.2f}, -40, .5], [{we - .35:.2f}, -20, .35], [{wi - .35:.2f}, -24, .35], [{wi + .45:.2f}, -30, .5]]);",
            f"R3.look('{px}fd', {we - .35:.2f}, 3, 1); R3.look('{px}fd', {wi - .35:.2f}, 3, -1); R3.look('{px}fd', {wr - .7:.2f}, 3, 0); R3.look('{px}fd', {wr + .3:.2f}, 2, 3);",
            f"R3.keys('{px}fd', 'upper', [[{wr + .3:.2f}, 4, .7, 'sine.inOut']]);",
        ]
        over = V3.counter(px + "c", 300, 520, LED.start) + V2.TAG.format("BigCart.com and Summit Ventures are fictional companies")
    else:
        spent = V3.CASH_AFTER_FUNDING - LED.spending["ADVERTISING"]
        js += [
            "gsap.set('#" + px + "rk .led', { opacity: 1 });",
            # two months later, close on the desk: the wire prints on "continuing", the pile refills, then the pull-back on "capital"
            f"tl.set('#{sid}-cam', {{ scale: 1.5, transformOrigin: '{PILE_TOP[0] + 120}px {PILE_TOP[1]}px' }}, {t0});",
            f"tl.fromTo('#{px}faxpage', {{ attr: {{ transform: 'translate(735 700)' }} }}, {{ attr: {{ transform: 'translate(735 480)' }}, duration: .8, ease: 'none', immediateRender: false }}, {wc - .05:.2f});",
            f"FM.pileTo('{px}cash', {wc + .8:.2f}, {LED.units(V3.CASH_AFTER_FUNDING)}, {{ gap: .03 }});",
            f"tl.to('#{sid}-cam', {{ scale: 1.0, duration: 1.1, ease: 'power2.inOut' }}, {wcap - .15:.2f});",
            # and straight back out: the commercial, payroll, servers
            bills(tvc, wcap + .45, n=8, dur=.75, arc=200), f"FM.pileTo('{px}cash', {wcap + .5:.2f}, {LED.units(spent)});",
            *[bills(to, wcap + .7 + i * .1, n=2, dur=.55, arc=140, size=.8) for i, (_e, to, pid) in enumerate(envs)],
            bills(rack_end, wcap + .8, n=4, dur=.65, arc=170, size=.85),
            f"FM.count('#{px}c-v', {V3.CASH_AT_FUNDING}, [[{wc + .8:.2f}, {V3.CASH_AFTER_FUNDING}, .8], [{wcap + .55:.2f}, {spent}, .5]]);",
            f"gsap.set([{', '.join(repr(f'#{px}pay{i} .env') for i in range(4))}], {{ opacity: 1 }});",
            f"R3.look('{px}fd', {wc - .1:.2f}, 3, 2); R3.keys('{px}fd', 'neck', [[{t0:.2f}, 10, 0], [{wc:.2f}, 6, .3], [{wcap + .4:.2f}, -6, .4]]);",
            f"R3.keys('{px}fd', 'upper', [[{t0:.2f}, 3, 0], [{wc + .9:.2f}, -1, .6]]); R3.look('{px}fd', {wcap + .4:.2f}, 3, -2);",
            f"tl.fromTo('#{px}later', {{ opacity: 0 }}, {{ opacity: 1, duration: .3, immediateRender: false }}, {t0 + .05:.2f}); tl.to('#{px}later', {{ opacity: 0, duration: .3 }}, {wc + .3:.2f});",
            f"tl.fromTo('#{px}st', {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: .35, immediateRender: false }}, {wc + .4:.2f});",
        ]
        over = (V3.counter(px + "c", 300, 520, V3.CASH_AT_FUNDING)
                + f'<div id="{px}later" class="step" style="opacity:0"><span class="sn">⏱</span>Two months later</div>'
                + V3.step(px + "st", 2, "Money received"))
    js.append("}")
    return layers, "\n".join(js), over


def ledger_shot(sid: str, t0: float, t1: float):
    """Insert: the founder's ledger — his hand writes this month's arithmetic; the shortfall and the runway are underlined."""
    ws, wt = W("sustain", "c03_04"), W("themselves", "c03_04")
    # one hand, one line at a time; the shortfall lands on "themselves"
    rows = [("This month", "", "#1f2a44", t0 + .02, True),
            ("Spending — ads, staff, servers", LED.fmt(-LED.total_spending), "#b0402a", t0 + .14, False),
            ("Revenue — customer orders", LED.fmt(LED.total_income, signed=True), "#2a6a2a", t0 + .56, False),
            ("Shortfall", LED.fmt(-LED.monthly_burn) + " a month", "#b0402a", wt - .05, True),
            ("Cash left", f"{LED.fmt(LED.balance)}  ≈ {int(LED.runway_months)} months", "#1f2a44", wt + .38, True)]
    lines, js = [], []
    y = 300
    for i, (lab, val, col, t, bold) in enumerate(rows):
        fs = 46 if bold else 40
        w = 1200
        lines.append(f'<clipPath id="lg-c{i}"><rect id="lg-r{i}" x="420" y="{y - 56}" width="0" height="80"/></clipPath>'
                     f'<g clip-path="url(#lg-c{i})"><text x="440" y="{y}" font-family="Fraunces" font-weight="{800 if bold else 600}" font-size="{fs}" fill="{col}">{lab}</text>'
                     f'<text x="1500" y="{y}" text-anchor="end" font-family="Fraunces" font-weight="800" font-size="{fs + 4}" fill="{col}">{val}</text></g>')
        js.append(f"tl.fromTo('#lg-r{i}', {{ attr: {{ width: 0 }} }}, {{ attr: {{ width: {w} }}, duration: {(.4 if i else .12)}, ease: 'power1.inOut', immediateRender: false }}, {t:.2f});"
                  f"tl.fromTo('#lg-hand', {{ attr: {{ transform: 'translate(440 {y + 6})' }} }}, {{ attr: {{ transform: 'translate(1490 {y + 6})' }}, duration: {(.4 if i else .12)}, ease: 'power1.inOut', immediateRender: false }}, {t:.2f});")
        if i == 2:
            lines.append(f'<path d="M440 {y + 36} H1500" stroke="#1b1410" stroke-width="4"/>')
        y += 120 if i else 110
    under = f'<path id="lg-u" d="M760 {y - 120 + 22} C960 {y - 120 + 34} 1200 {y - 120 + 30} 1500 {y - 120 + 20}" stroke="#d9503f" stroke-width="9" fill="none" stroke-linecap="butt"/>'
    js.append(f"{{ const u = document.getElementById('lg-u'), n = u.getTotalLength(); gsap.set(u, {{ strokeDasharray: n + ' ' + n, strokeDashoffset: n }}); tl.to(u, {{ strokeDashoffset: 0, duration: .4, ease: 'power1.inOut' }}, {wt + .85:.2f}); }}")
    js.append(f"tl.to('#lg-hand', {{ attr: {{ transform: 'translate(1700 1000)' }}, duration: .45, ease: 'power2.in' }}, {wt + .82:.2f});")
    js.append(f"tl.fromTo('#{sid}-cam', {{ scale: 1.0 }}, {{ scale: 1.05, transformOrigin: '60% 45%', duration: {t1 - t0:.2f}, ease: 'sine.inOut' }}, {t0});")
    hand = ('<g id="lg-hand" transform="translate(440 290)">'          # pen tip at the origin; hand and sleeve trail down-right, clear of the writing
            '<path d="M330 600 L430 560 L150 120 L70 150Z" fill="#f4f0e8" stroke="#1b1410" stroke-width="4"/>'
            '<path d="M86 156 L150 128 L160 150 L96 178Z" fill="#e8e2d4" stroke="#1b1410" stroke-width="3"/>'
            '<path d="M30 70 C20 100 40 140 80 150 C120 160 150 130 140 96 C130 66 100 50 70 52 C50 54 36 60 30 70Z" fill="#f1c9a5" stroke="#1b1410" stroke-width="4"/>'
            '<path d="M44 84 C40 74 30 60 22 54" fill="none" stroke="#1b1410" stroke-width="3"/>'
            '<path d="M0 0 L46 92" stroke="#1f3a7a" stroke-width="11" stroke-linecap="round"/><path d="M0 0 L8 16" stroke="#c8c4bc" stroke-width="6"/></g>')
    book = ('<pattern id="lg-wood" patternUnits="userSpaceOnUse" width="900" height="900"><image href="tex/wood_floor.jpg" width="900" height="900"/></pattern>')
    body = (f'<rect width="1920" height="1080" fill="url(#lg-wood)"/><rect width="1920" height="1080" fill="#2a160a" opacity=".5"/>'
            '<g transform="rotate(-2 960 540)"><rect x="300" y="110" width="1320" height="820" rx="16" fill="#3a2a1a"/>'
            '<rect x="330" y="130" width="630" height="780" fill="#f6f0e0"/><rect x="960" y="130" width="630" height="780" fill="#f3ecda"/>'
            + "".join(f'<path d="M350 {200 + k * 60} H1570" stroke="#c8d4e4" stroke-width="2"/>' for k in range(12))
            + '<path d="M420 130 V910" stroke="#e8a0a0" stroke-width="2"/><path d="M960 130 V910" stroke="#c8bba0" stroke-width="6"/>'
            + "".join(lines) + under
            + '<text x="1540" y="890" text-anchor="end" font-family="Inter" font-weight="700" font-size="22" fill="#8a8070">illustrative figures</text></g>'
            + hand)
    return V2.svg_layer(sid + "-fx", body, book), "\n".join(js), ""


def boardroom_shot(sid: str, t0: float, t1: float):
    layers, js, over = V3.beat_c1(t0, t1)
    return layers.replace("c1-live", f"{sid}-live"), js.replace("c1-live", f"{sid}-live").replace("#c1-cam", f"#{sid}-cam"), over


def shots():
    """(sid, plate, dim, builder) in order."""
    return [("s1", "office_floor", 0, lambda: office_shot("s1", "a", CUT[0], CUT[1], "burn")),
            ("s2", None, 0, lambda: ledger_shot("s2", CUT[1], CUT[2])),
            ("s3", "boardroom_c8", 0, lambda: boardroom_shot("s3", CUT[2], CUT[3])),
            ("s4", "office_floor", 0, lambda: office_shot("s4", "r", CUT[3], CUT[4], "refill"))]
