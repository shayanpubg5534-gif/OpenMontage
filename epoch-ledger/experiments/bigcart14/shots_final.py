"""BigCart 14 s — final acceptance preview (Phase 4): the revised cinematic storytelling (A′), V3's explanatory
cash-flow chart, Rig v4 for the founder and the investor, depth-layered environments with motivated camera moves,
gold spoken-word captions. Figures come from the one Ledger (office_v3.LED) and stay large and on screen long
enough to read. Workers and the technician keep rig v3 (they convert after the founder and investor are approved).

  0.00– 4.60  office    the founder directs the spending: advertising (TV), employees (desks), infrastructure (servers)
  4.60– 8.65  chart     V3 money in / money out for one month, the shortfall, and the cash runway
  8.65–11.10  boardroom he makes his case; the investor signs; handshake ("Their survival depended on investors")
 11.10–14.00  office    two months later: the wire lands, he reads it, the pile refills — and goes straight back out
"""
from __future__ import annotations

import json

import shots as S
from kit import depth, finmech as F, money as M, rig4

V2, V3 = S.V2, S.V3
W, LED, INK, C3, C8 = V3.W, V3.LED, S.INK, S.C3, V3.C8
D = 14.0
CUT = [0, 4.6, 8.65, 11.1, D]
FSC = .82                                   # founder sprite scale in the office (px per local unit)
FX0, FY0, FW = 40 - 300 * FSC, 236, 1000      # a little further into frame than A′ (his face was at the edge)    # founder sprite origin (screen) and width (local units)
DESK_Y = 790
PILE_TOP = S.PILE_TOP


def to_f(pt):
    """Screen point → the office founder's local coordinates."""
    return [round((pt[0] - FX0) / FSC, 1), round((pt[1] - FY0) / FSC, 1), 0]


# near foregrounds (blurred plates): a desk corner with a plant at the office's right edge; a chair back in the boardroom
FG_OFFICE = r"""
const sc = S3.scene();
sc.box([0.15, .70, -2.35], [1.3, .76, -1.45], { color: '#6a4630', gloss: .2 }, { layer: 'fg' });
sc.box([0.42, .76, -2.0], [0.62, .9, -1.8], { color: '#e8e0d0' }, { layer: 'fg' });
sc.art([0.05, .76, -2.2], [0.55, .76, -2.2], [0.05, 1.56, -2.2], 400, 640, FOLIAGE, { layer: 'fg' });
"""
FG_BOARD = r"""
const sc = S3.scene();
sc.box([-1.15, .45, -1.75], [-0.62, .52, -1.3], { color: '#2a1a14' }, { layer: 'fg' });
sc.box([-1.12, .52, -1.36], [-0.65, 1.12, -1.28], { color: '#3a2418', gloss: .3 }, { layer: 'fg' });
"""


def env(ws, name, scene, cam, light):
    return depth.layered(ws / "plates", name, scene, cam, light,
                         prelude_js=f"const ART = {json.dumps(V2.common.ART)};const FOLIAGE = {json.dumps(depth.foliage(seed=11))};",
                         split=(2.4, 6.5), blur={"fg": 7.0}, layers=("fg",),
                         assets=tuple(sorted((V2.EL / "kit/assets/textures").glob("*.jpg"))))


def layered_office(sid, plate_png, fg_rel, live, fx, extra_front=""):
    """bg plate (8 m) · live desks and workers (4.5 m) · founder, desk, cash and props (2.2 m) · blurred fg (1.2 m)."""
    lay = lambda k, z, inner: f'<div class="layer" id="{sid}-L{k}" data-depth="{z}">{inner}</div>'
    haze = '<div class="layer" style="background:linear-gradient(180deg,rgba(0,0,0,0) 25%,#f2d8b8 62%,rgba(0,0,0,0) 100%);opacity:.12;mix-blend-mode:screen"></div>'
    return (lay("bg", 8, f'<img class="plate" src="{plate_png}"/>') + haze + lay("mg", 4.5, live) + lay("near", 2.2, fx)
            + lay("fg", 1.2, f'<img class="plate" src="{fg_rel}"/>{extra_front}'))


def office(sid, px, t0, t1, mode, plate_png, fg_rel):
    """The same office, the same people, desk and cash in shots 1 and 4. The founder is rig v4."""
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
    tech = V2.figure(px + "tk", "casual2", 2, 0, "buzz", angles=S.rig3.reach("stand", (318, 520)), extra=rack, mirrored=True)
    live.append(f"sc.sprite([1.95, 0, -6.3], 1.76, {json.dumps(tech)}, .4, {{ viewBox: '0 0 400 1000', id: '{px}tk' }});")
    tvx, tvy, tvw = 380, 70, 470
    sx, sy, sw, sh = F.tv_screen(tvx, tvy, tvw)
    tv = F.tv_set(px + "tv", tvx, tvy, tvw, ad=M.commercial(px + "ad", sx, sy, sw, sh), stand=False)
    envs = []
    for i, (x, z, pid, *_r) in enumerate(ws3):
        e = C3.project([x + .33, .78, z + .32]); s = min(1.45, 3.6 / e[2])
        envs.append((F.envelope(f"{px}pay{i}", e[0], e[1] - 14 * s, s), (e[0], e[1] - 20 * s), pid))
    rack_end = C3.project([1.62, .9, -6.3])
    tvc = (sx + sw / 2, sy + sh / 2)
    fid = px + "f4"
    # the wire page (shot 4) lives inside the founder's sprite so it can travel with his hand; large enough to read
    page = ('<rect x="-150" y="-95" width="300" height="190" fill="#fbfaf4" stroke="#1b1410" stroke-width="3"/>'
            '<text x="0" y="-61" text-anchor="middle" font-family="Inter" font-weight="800" font-size="20" fill="#1f3a5a">WIRE RECEIVED</text>'
            '<text x="0" y="-33" text-anchor="middle" font-family="Inter" font-weight="700" font-size="14" fill="#5a6470">First National Bank</text>'
            '<text x="0" y="17" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="36" fill="#2a6a2a">$20,000,000</text>'
            '<text x="0" y="51" text-anchor="middle" font-family="Inter" font-weight="700" font-size="14" fill="#1b1410">from Summit Ventures</text>'
            '<text x="0" y="73" text-anchor="middle" font-family="Inter" font-weight="700" font-size="14" fill="#1b1410">to BigCart.com</text>')
    fax_out = to_f((885, 640))
    # held by its lower-left edge, so the sheet sits up and to his left of the hand (readable, clear of the counter)
    held = f'<g id="{px}wire" opacity="0"><g transform="translate(420 -110) scale(1.9)">{page}</g></g>' if mode == "refill" else ""
    founder = (f'<svg x="{FX0:.1f}" y="{FY0}" width="{FW * FSC:.1f}" height="{1000 * FSC:.1f}" viewBox="0 0 {FW} 1000" overflow="visible">'
               f'<g id="{fid}"></g>{held}</svg>')
    desk = (f'<path d="M-20 {DESK_Y} L1010 {DESK_Y} L1100 1100 L-20 1100Z" fill="#5a3a24" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M-20 {DESK_Y} L1010 {DESK_Y} L1016 812 L-20 812Z" fill="#7a5236"/>')
    extra = ""
    if mode == "refill":
        extra = (f'<g id="{px}fax"><rect x="770" y="700" width="230" height="100" rx="12" fill="#d8d4c8" stroke="{INK}" stroke-width="4"/>'
                 f'<rect x="790" y="690" width="190" height="16" rx="4" fill="#3a3a42"/><rect x="930" y="725" width="50" height="16" rx="3" fill="#2a2a30"/>'
                 f'<circle cx="800" cy="735" r="6" fill="#5aff7a"/></g>'
                 f'<g id="{px}faxclip"><clipPath id="{px}fc"><rect x="700" y="420" width="400" height="280"/></clipPath>'
                 f'<g clip-path="url(#{px}fc)"><g id="{px}faxpage" transform="translate(885 795)">{page}</g></g></g>')
        n0, cap = LED.units(V3.CASH_AT_FUNDING), LED.units(V3.CASH_AFTER_FUNDING)
    else:
        n0, cap = LED.units(LED.start), LED.units(LED.start) + 1
    pile = M.cash_pile(px + "cash", 300, 760, n0, cols=4, w=118, capacity=cap)
    fx = V2.svg_layer(sid + "-fx", tv + "".join(e for e, _, _ in envs) + desk + pile + extra + founder + f'<g id="{px}bills"></g>', M.bill_defs(px + "b"))
    layers = layered_office(sid, plate_png, fg_rel, f'<svg id="{sid}-live" class="full" viewBox="0 0 1920 1080"></svg>', fx)
    bills = lambda to, t, **o: f"FM.bills('{px}bills', '{px}b', [{PILE_TOP[0]}, {PILE_TOP[1]}], [{to[0]:.0f}, {to[1]:.0f}], {t:.2f}, {json.dumps(o)});"
    occ = {"y": round((DESK_Y + 4 - FY0) / FSC, 1)}
    create = rig4.create_js(fid, "founder", x=480, yaw=28, ground=1000, blink_seed=31 if mode == "burn" else 41, t0=t0, t1=t1).replace("});", f', "occlude": {json.dumps(occ)}}});')
    focus = f"[{PILE_TOP[0] - 70}, {PILE_TOP[1] + 20}]"
    js = [f"{{ const cam = {C3.js()}; {V2.OFFICE_LIGHT}", *live,
          f"document.getElementById('{sid}-live').innerHTML = S3.render(sc, cam, L, {{ ow: 2.0, shadowBlur: 5, uid: 'l{sid}' }});",
          f"gsap.set([{', '.join(repr(f'#{px}pay{i} .env') for i in range(4))}], {{ opacity: {0 if mode == 'burn' else 1} }});",
          *[f"R3.type('{pid}', {t0}, {t1}, {21 + i});" for i, (_x, _z, pid, *_r) in enumerate(ws3)],
          create,
          # resting: forearms on the desk edge
          f"R4.arm('{fid}', 'L', {t0}, [-40, 250, 120], 0); R4.arm('{fid}', 'R', {t0}, [30, 250, 120], 0);"]
    if mode == "burn":
        wa, we, wi = W("advertising", "c03_04"), W("employees", "c03_04"), W("infrastructure", "c03_04")
        a_ads = LED.start - LED.spending["ADVERTISING"]
        a_pay = a_ads - LED.spending["PAYROLL"]
        a_srv = LED.start - LED.total_spending
        rk = (rack_end[0], rack_end[1] - 40)
        js += [
            # opening frame: close on the cash; pull back to reveal what it feeds (a motivated reveal)
            f"DL.set('{sid}', {t0}, {{ dolly: .9, truck: -.12, focal: 1158, focus: {focus} }});",
            f"DL.move('{sid}', {t0 + .1:.2f}, 2.0, {{ dolly: 0, truck: 0, focal: 1158, focus: {focus}, ease: 'power2.inOut' }});",
            f"DL.move('{sid}', {wi - .3:.2f}, {t1 - wi + .3:.2f}, {{ dolly: .12, truck: .06, focal: 1158, focus: [1300, 520] }});",
            # advertising: he points at the TV; the ad switches on as the money arrives
            f"R4.look('{fid}', {wa - .55:.2f}, {json.dumps(to_f(tvc))});",
            f"R4.reach('{fid}', 'L', {wa - .45:.2f}, {json.dumps(to_f(tvc))}, .42, {{ shape: 3, lean: 6, look: false }});",
            bills(tvc, wa - .2, n=9, dur=.8, arc=200), f"FM.pileTo('{px}cash', {wa - .15:.2f}, {LED.units(a_ads)});",
            f"FM.powerOn('{px}tv', {wa + .4:.2f});",
            f"tl.fromTo('#{px}ad-parcel', {{ x: 0 }}, {{ x: {sw * .17:.0f}, y: {-sh * .03:.0f}, duration: .7, ease: 'power2.inOut', immediateRender: false }}, {wa + .75:.2f});",
            f"tl.fromTo('#{px}ad-card', {{ opacity: 0 }}, {{ opacity: 1, duration: .25, immediateRender: false }}, {wa + 1.6:.2f});",
            # employees: an open hand toward the desks; each gets paid
            f"R4.look('{fid}', {we - .5:.2f}, {json.dumps(to_f(envs[1][1]))});",
            f"R4.reach('{fid}', 'L', {we - .4:.2f}, {json.dumps(to_f(envs[1][1]))}, .45, {{ shape: 2, lean: 5, look: false }});",
            *[bills(to, we - .25 + i * .14, n=3, dur=.55, arc=140, size=.8) + f"FM.pop('#{px}pay{i} .env', {we + .3 + i * .14:.2f});"
              f"R3.rot('{pid}', 'neck', {we + .4 + i * .14:.2f}, 16, .3); R3.look('{pid}', {we + .35 + i * .14:.2f}, 2, 2); R3.rot('{pid}', 'neck', {we + 1.05 + i * .14:.2f}, 6, .4); R3.look('{pid}', {we + 1.05 + i * .14:.2f}, 0, 0, .3);"
              for i, (_e, to, pid) in enumerate(envs)],
            f"FM.pileTo('{px}cash', {we - .2:.2f}, {LED.units(a_pay)});",
            # infrastructure: he points across the room to the servers; the technician wheels the rack in and it powers up
            f"R4.look('{fid}', {wi - .55:.2f}, {json.dumps(to_f(rk))});",
            f"R4.reach('{fid}', 'L', {wi - .45:.2f}, {json.dumps(to_f(rk))}, .42, {{ shape: 3, lean: 5, look: false }});",
            f"{{ const A0 = R3.walk(cam, '{px}tk', '{px}tk', [3.0, 0, -6.3], [1.95, 0, -6.3], 1.76, .4, {wi - 1.1:.2f}, {wi + .1:.2f}, .5); tl.set('#{px}tk', {{ attr: A0 }}, {t0}); }}",
            bills(rack_end, wi - .05, n=5, dur=.7, arc=170, size=.85), f"FM.pileTo('{px}cash', {wi:.2f}, {LED.units(a_srv)});",
            f"tl.fromTo('#{px}rk .led', {{ opacity: .2 }}, {{ opacity: 1, duration: .05, stagger: .03, immediateRender: false }}, {wi + .45:.2f});",
            # the pile is visibly smaller; he lowers his hand and looks down at it — worried (not talking)
            f"R4.release('{fid}', 'L', {wi + .55:.2f}, .5, [-40, 250, 120]);",
            f"R4.look('{fid}', {wi + .6:.2f}, {json.dumps(to_f(PILE_TOP))});",
            f"R4.express('{fid}', {wi + .65:.2f}, {{ brow: [-.6, -.6], smile: -.3 }}, .4);",
            f"FM.count('#{px}c-v', {LED.start}, [[{wa:.2f}, {a_ads}], [{we:.2f}, {a_pay}], [{wi + .1:.2f}, {a_srv}]]);",
        ]
        over = V3.counter(px + "c", 300, 500, LED.start) + V2.TAG.format("BigCart.com and Summit Ventures are fictional companies")
    else:
        wc, wcap = W("continuing", "c03_05"), W("capital", "c03_05")
        spent = V3.CASH_AFTER_FUNDING - LED.spending["ADVERTISING"]
        grab = [fax_out[0] - 10, fax_out[1] - 20, 40]
        read = [690, 300, 160]      # page centre ≈ screen (704, 392): clear of the step labels and the cash counter
        js += [
            "gsap.set('#" + px + "rk .led', { opacity: 1 });",
            f"DL.set('{sid}', {t0}, {{ dolly: .32, truck: -.04, focal: 1158, focus: [640, 600] }});",
            # the wire prints on "continuing"; he takes it and reads it (palm on the page, grip, lift)
            f"tl.fromTo('#{px}faxpage', {{ attr: {{ transform: 'translate(885 795)' }} }}, {{ attr: {{ transform: 'translate(885 600)' }}, duration: .7, ease: 'none', immediateRender: false }}, {wc - .05:.2f});",
            f"R4.look('{fid}', {wc - .2:.2f}, {json.dumps(fax_out)});",
            f"R4.reach('{fid}', 'L', {wc + .55:.2f}, {json.dumps(grab)}, .4, {{ shape: 1, lean: 8, look: false }});",
            f"tl.set('#{px}faxpage', {{ opacity: 0 }}, {wc + .95:.2f}); tl.set('#{px}wire', {{ opacity: 1 }}, {wc + .95:.2f});",
            f"R4.hold('{fid}', 'L', '{px}wire', {wc + .95:.2f}, {t1 + 1:.2f}, 'upright');",
            f"R4.key('{fid}', 'handWL', {wc + 1.0:.2f}, {json.dumps(read)}, .5);",
            f"R4.look('{fid}', {wc + 1.1:.2f}, [{read[0] + 420}, {read[1] - 110}]);",
            f"R4.express('{fid}', {wc + 1.4:.2f}, {{ brow: [.6, .6], smile: .75 }}, .4); R4.key('{fid}', 'lean', {wc + 1.4:.2f}, -2, .6);",
            f"FM.pileTo('{px}cash', {wc + .8:.2f}, {LED.units(V3.CASH_AFTER_FUNDING)}, {{ gap: .03 }});",
            f"DL.move('{sid}', {wcap - .2:.2f}, 1.1, {{ dolly: 0, truck: 0, focal: 1158, focus: [640, 600], ease: 'power2.inOut' }});",
            # and straight back out: the commercial, payroll, servers
            bills(tvc, wcap + .45, n=8, dur=.75, arc=200), f"FM.pileTo('{px}cash', {wcap + .5:.2f}, {LED.units(spent)});",
            *[bills(to, wcap + .7 + i * .1, n=2, dur=.55, arc=140, size=.8) for i, (_e, to, pid) in enumerate(envs)],
            bills(rack_end, wcap + .8, n=4, dur=.65, arc=170, size=.85),
            f"R4.express('{fid}', {wcap + .7:.2f}, {{ smile: .12, brow: [.1, -.2] }}, .5); R4.look('{fid}', {wcap + .6:.2f}, {json.dumps(to_f(tvc))});",
            f"FM.count('#{px}c-v', {V3.CASH_AT_FUNDING}, [[{wc + .8:.2f}, {V3.CASH_AFTER_FUNDING}, .8], [{wcap + .55:.2f}, {spent}, .5]]);",
            f"tl.fromTo('#{px}later', {{ opacity: 0 }}, {{ opacity: 1, duration: .3, immediateRender: false }}, {t0 + .05:.2f}); tl.to('#{px}later', {{ opacity: 0, duration: .3 }}, {wc + .3:.2f});",
            f"tl.fromTo('#{px}st', {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: .35, immediateRender: false }}, {wc + .4:.2f});",
        ]
        over = (V3.counter(px + "c", 300, 500, V3.CASH_AT_FUNDING)
                + f'<div id="{px}later" class="step" style="opacity:0"><span class="sn">⏱</span>Two months later</div>'
                + V3.step(px + "st", 2, "Money received"))
    js.append("}")
    return layers, "\n".join(js), over


def chart(sid, t0, t1):
    layers, js, over = V3.beat_b(t0, t1)
    return layers.replace("b-fx", f"{sid}-fx"), js.replace("#b-fx", f"#{sid}-fx").replace("#b-cam", f"#{sid}-cam"), over


def boardroom(sid, t0, t1, plate_png, fg_rel):
    """He makes his case; she signs on "investors"; handshake. Rig v4 for both; the table edge occludes their legs."""
    IV, FD = [-0.1, 0, -3.3], [0.62, 0, -3.3]
    H_M, PX_M = 1.88, 1000 / 1.88

    class Sp:
        def __init__(self, pid, foot, w=1400):
            f, h = C8.project(foot), C8.project([foot[0], foot[1] + H_M, foot[2]])
            self.pid, self.foot, self.W, self.s = pid, foot, w, (f[1] - h[1]) / 1000
            self.x, self.y = f[0] - w * .5 * self.s, h[1]

        def local(self, p):
            q = C8.project(p)
            return [round((q[0] - self.x) / self.s, 1), round((q[1] - self.y) / self.s, 1), round((p[2] - self.foot[2]) * PX_M, 1)]

        def svg(self, extra=""):
            return (f'<svg x="{self.x:.1f}" y="{self.y:.1f}" width="{self.W * self.s:.1f}" height="{1000 * self.s:.1f}" '
                    f'viewBox="0 0 {self.W} 1000" overflow="visible"><g id="{self.pid}"></g>{extra}</svg>')
    iv, fd = Sp("ivb", IV), Sp("fdb4", FD)
    occ = {"y": iv.local([IV[0], .79, IV[2]])[1]}
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
    lay = lambda k, z, inner: f'<div class="layer" id="{sid}-L{k}" data-depth="{z}">{inner}</div>'
    layers = (lay("bg", 4.5, f'<img class="plate" src="{plate_png}"/><svg id="{sid}-doc" class="full" viewBox="0 0 1920 1080"></svg>')
              + lay("mg", 2.4, f'<svg id="{sid}-chars" class="full" viewBox="0 0 1920 1080" overflow="visible">{iv.svg(pen)}{fd.svg()}</svg>')
              + lay("fg", 1.0, f'<img class="plate" src="{fg_rel}"/>'))
    ws_, wd, wi = W("survival", "c03_05"), W("depended", "c03_05"), W("investors", "c03_05")
    ci = rig4.create_js("ivb", "investor", x=700, yaw=60, ground=1000, blink_seed=82, t0=t0, t1=t1).replace("});", f', "occlude": {json.dumps(occ)}}});')
    cf = rig4.create_js("fdb4", "founder", x=700, yaw=-60, ground=1000, blink_seed=83, t0=t0, t1=t1).replace("});", f', "occlude": {json.dumps(occ)}}});')
    js = ("{ const cam = " + C8.js() + "; " + V2.BOARD_LIGHT + "\n" + live + "\n"
          f"document.getElementById('{sid}-doc').innerHTML = S3.render(sc, cam, L, {{ ow: 2.0, shadowBlur: 5, uid: 'lb' }}); }}\n"
          + ci + cf
          + f"DL.set('{sid}', {t0}, {{ dolly: .06, focal: 1240, focus: [960, 560] }}); DL.move('{sid}', {t0 + .05:.2f}, {t1 - t0 - .1:.2f}, {{ dolly: .22, truck: .04, focal: 1240, focus: [960, 560] }});"
          # he makes his case during "Their survival" (he is speaking to her in the scene); she reads, then looks up
          + f"R4.key('ivb', 'headPitch', {t0}, 14); R4.key('ivb', 'gaze', {t0}, [.3, .6]);"
          + f"R4.say('fdb4', {t0 + .05:.2f}, {wd - .05:.2f}, 5); R4.express('fdb4', {t0:.2f}, {{brow: [.5, .5]}}, .2);"
          + f"R4.arm('fdb4', 'R', {t0 + .05:.2f}, [-10, 150, 150], .35); R4.key('fdb4', 'handShapeR', {t0 + .1:.2f}, 2, .25); R4.arm('fdb4', 'R', {wd - .05:.2f}, [-18, 236, 22], .4); R4.key('fdb4', 'handShapeR', {wd:.2f}, 0, .25);"
          + f"R4.look('ivb', {ws_ - .05:.2f}, [1100, 120], .3); R4.express('ivb', {ws_ + .1:.2f}, {{brow: [.3, .1], smile: .2}});"
          # pen to paper on "depended"; she signs
          + f"R4.reach('ivb', 'R', {ws_ + .08:.2f}, {json.dumps(pen_l)}, .44, {{shape: 1}});"
          + f"R4.hold('ivb', 'R', 'pen4', {wd - .04:.2f}, {wd + .76:.2f}, 200);"
          + "".join(f"R4.key('ivb', 'handWR', {wd + .06 + k * .15:.2f}, {json.dumps([sig[k][0], sig[k][1] - 4 - (k % 2) * 6, sig[k][2]])}, .14);" for k in range(4))
          + f"{{ const s = document.getElementById('ts-sig'); if (s) {{ const n = s.getTotalLength(); gsap.set(s, {{ strokeDasharray: n + ' ' + n, strokeDashoffset: n }}); tl.to(s, {{ strokeDashoffset: 0, duration: .55, ease: 'none' }}, {wd + .08:.2f}); }} }}"
          + f"R4.key('ivb', 'handWR', {wd + .62:.2f}, {json.dumps(pen_l)}, .14); R4.release('ivb', 'R', {wd + .76:.2f}, .3, [18, 236, 22]); R4.key('ivb', 'lean', {wd + .76:.2f}, 4, .35);"
          # the hands meet on "investors": grip and pumps before the cut; relief
          + f"R4.reach('ivb', 'R', {wi - .34:.2f}, {json.dumps(hi)}, .36, {{shape: 1, look: false}}); R4.reach('fdb4', 'R', {wi - .4:.2f}, {json.dumps(hf)}, .4, {{shape: 1, look: false}});"
          + "".join(f"R4.key('{p}', 'handWR', {wi + .1 + k * .12:.2f}, {json.dumps([q[0], q[1] + (12 if k % 2 == 0 else -6), q[2]])}, .12, 'sine');" for p, q in (("ivb", hi), ("fdb4", hf)) for k in range(4))
          + f"R4.express('fdb4', {wi - .1:.2f}, {{smile: .7, brow: [.3, .3]}}); R4.express('ivb', {wi:.2f}, {{smile: .45}});"
          + f"R4.look('fdb4', {wi - .4:.2f}, {json.dumps([hf[0] - 300, hf[1] - 420])}); R4.look('ivb', {wi - .4:.2f}, {json.dumps([hi[0] + 300, hi[1] - 420])});"
          + f"tl.fromTo('#st1', {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: .35, immediateRender: false }}, {wi:.2f});")
    over = V3.step("st1", 1, "Agreement signed") + V2.TAG.format("Summit Ventures and BigCart.com are fictional companies")
    return layers, js, over
