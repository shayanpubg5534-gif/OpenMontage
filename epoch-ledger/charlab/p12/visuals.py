"""P12: reusable visual-explanation formats for narrated passages (any finance or economic-history subject).

Each function returns a kit.assemble.Scene timed by the caller from the narration-to-visual map (p11/visual_map.py), so
the format is chosen per clause by what the narration says, not by a template. Formats:

  env_card       environmental typography: a printed object in the scene (calendar, sign, tray label), in perspective
  document       a paper document in close-up (fields, a budget bar that fills, a signature written by a pen)
  world_map      a geographic map with routes from an origin, buyers, steady flows that can stop (dry up), a value panel
  line_chart     a full-screen animated chart that draws to a turning point, then continues in a second colour
  newspaper      a front page in close-up, headline emphasised, with a timeline strip that moves to the date
  before_after   two bars, before and after (used inside other formats)

Design rules (mobile readable): key text ≥ 40 px at 1080p, labels ≤ 7 words, one idea per element, warm paper and ink
palette shared with the series' captions (gold), no decorative motion.
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kit.assemble import Scene  # noqa: E402
from kit import motion as KM  # noqa: E402

INK, GOLD, RED, GREEN, MUTED, PAPER = "#2b2118", "#c9963a", "#b5473a", "#3d7a52", "#6b5a48", "#f7f1e4"
CSS = f"""
.vx{{position:absolute;inset:0;overflow:hidden}}
.vpaper{{position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 40%,#f7f0e3 0%,#efe3cd 70%,#e3d3b6 100%)}}
.vgrain{{position:absolute;inset:0;opacity:.35;background-image:repeating-linear-gradient(0deg,rgba(90,60,30,.035) 0 2px,transparent 2px 5px),repeating-linear-gradient(90deg,rgba(90,60,30,.03) 0 3px,transparent 3px 7px)}}
.vk{{font:700 26px Inter,sans-serif;letter-spacing:3px;text-transform:uppercase;color:#8a7a64}}
.vh{{font:700 56px Fraunces,Georgia,serif;color:{INK};line-height:1.08}}
.vl{{font:600 40px Inter,sans-serif;color:{INK}}}
.vdoc{{position:absolute;background:{PAPER};box-shadow:0 14px 34px rgba(20,10,4,.45);border-radius:3px;box-sizing:border-box}}
.vdoc .f{{font:600 22px Inter,sans-serif;letter-spacing:2px;color:#7a6a58;text-transform:uppercase}}
.vdoc .v{{font:600 36px Inter,sans-serif;color:{INK};margin:4px 0 22px}}
"""
E = lambda s: html.escape(str(s))


def env_card(sid, t0, dur, *, top, big, box, transform, t_in, color=RED):
    """a printed object in the scene (e.g. a wall calendar showing the year), flipping into place on its word"""
    x, y, w, h = box
    h_ = (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;perspective:900px">'
          f'<div id="{sid}c" style="position:absolute;inset:0;transform:{transform};transform-origin:50% 0;background:{PAPER};border-radius:4px;'
          f'box-shadow:0 10px 24px rgba(15,8,3,.45);overflow:hidden">'
          f'<div style="background:{color};color:#f7efe2;font:800 {int(h * .13)}px Inter;letter-spacing:3px;text-align:center;padding:{int(h * .04)}px 0">{E(top)}</div>'
          f'<div id="{sid}y" style="font:800 {int(min(h * .42, w * .29))}px Fraunces,Georgia,serif;color:{INK};text-align:center;line-height:{int(h * .62)}px;opacity:0">{E(big)}</div>'
          f'<div style="position:absolute;left:12%;right:12%;bottom:10%;height:{int(h * .12)}px;background:repeating-linear-gradient(90deg,#cdbfa6 0 10%,transparent 10% 14.3%)"></div></div></div>')
    js = (f"tl.fromTo('#{sid}c',{{rotationX:-75,opacity:0}},{{rotationX:0,opacity:1,duration:.4,ease:'power2.out',immediateRender:false}},{t_in - .2:.2f});"
          f"tl.fromTo('#{sid}y',{{opacity:0,y:10}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{t_in:.2f});")
    return Scene(sid, t0, dur, h_, js=js)


def document(sid, t0, dur, *, title, fields, box, transform, sign_t=None, bar=None, push=None, video=None):
    """a document in close-up. bar = {label, t_fill, frac, t_left, left_label}: a budget bar printed on it that fills on
    its word (the payment against the income) and marks what is left. sign_t: a pen writes the signature (only the pen
    is seen; the hand is out of frame, as in a real insert)"""
    x, y, w, h = box
    rows = "".join(f'<div class="f">{E(k)}</div><div class="v">{E(v)}</div>' for k, v in fields)
    barh = ""
    if bar:
        barh = (f'<div class="f" style="margin-top:6px">{E(bar["label"])}</div>'
                f'<div style="position:relative;height:46px;margin:10px 0 6px;background:#e2d7c2;border:2px solid {INK};border-radius:4px">'
                f'<div id="{sid}b" style="position:absolute;left:0;top:0;bottom:0;width:{bar["frac"] * 100:.0f}%;background:#5b6b7d;transform:scaleX(0);transform-origin:0 50%"></div>'
                f'<div id="{sid}l" style="position:absolute;left:{bar["frac"] * 100:.0f}%;right:0;top:-6px;bottom:-6px;border:4px solid {RED};border-radius:4px;opacity:0"></div></div>'
                f'<div style="display:flex;justify-content:space-between;font:600 22px Inter;color:{MUTED}"><span>{E(bar.get("left_text", "payment"))}</span>'
                f'<span id="{sid}lt" style="color:{RED};font-weight:800;opacity:0">{E(bar["left_label"])}</span></div>')
    sig = ""
    if sign_t is not None:
        sig = (f'<div class="f" style="margin-top:34px">Signature</div><div style="position:relative;height:90px;border-bottom:3px solid {INK}">'
               f'<svg width="{w - 120}" height="90" style="position:absolute;left:0;top:0"><path id="{sid}s" d="M10 70 C40 10 70 10 60 60 C55 85 95 30 110 40 C125 50 120 70 140 55 '
               f'C165 35 175 20 185 60 C190 80 215 30 240 45 C260 55 270 62 300 40" fill="none" stroke="#1f3a6b" stroke-width="5" stroke-linecap="round"/></svg></div>')
    doc = (f'<div id="{sid}w" style="position:absolute;inset:0;perspective:1600px"><div id="{sid}d" class="vdoc" '
           f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:{transform};transform-origin:50% 60%;padding:48px 60px">'
           f'<div class="vh" style="font-size:44px">{E(title)}</div><div style="height:3px;background:{INK};margin:14px 0 26px"></div>'
           f'{rows}{barh}{sig}</div></div>')
    pen = ""
    js = []
    if sign_t is not None:   # the pen: its tip follows the signature stroke; its body runs out of frame (the hand is off-screen)
        pen = (f'<svg id="{sid}p" width="1920" height="1080" style="position:absolute;inset:0;opacity:0;pointer-events:none"><g id="{sid}pg">'
               f'<path d="M0 0 L16 -12 L820 560 L800 580 Z" fill="#2b2b33"/><path d="M0 0 L16 -12 L44 8 L28 26 Z" fill="#c9a25a"/>'
               f'<path d="M300 200 L330 222 L312 244 L282 222 Z" fill="#8a7a64"/></g></svg>')   # long enough to leave the frame: held, not floating
        js.append(f"(function(){{const p=document.getElementById('{sid}s'),pg=document.getElementById('{sid}pg'),n=p.getTotalLength(),st={{u:0}};"
                  f"gsap.set(p,{{strokeDasharray:n,strokeDashoffset:n}});"
                  f"const put=()=>{{const q=p.getPointAtLength(st.u*n),m=p.getScreenCTM(),r=document.getElementById('{sid}p').getScreenCTM().inverse().multiply(m);"
                  f"const x=r.a*q.x+r.c*q.y+r.e,y=r.b*q.x+r.d*q.y+r.f;pg.setAttribute('transform','translate('+x+' '+y+')');p.style.strokeDashoffset=n*(1-st.u);}};"
                  f"tl.fromTo('#{sid}p',{{opacity:0}},{{opacity:1,duration:.12,immediateRender:false}},{sign_t - .12:.2f});"
                  f"tl.fromTo(st,{{u:0}},{{u:1,duration:.9,ease:'none',onUpdate:put,immediateRender:false}},{sign_t:.2f});"
                  f"tl.to('#{sid}p',{{opacity:0,duration:.25}},{sign_t + 1.05:.2f});}})();")
    if bar:
        js.append(f"tl.fromTo('#{sid}b',{{scaleX:0}},{{scaleX:1,duration:.55,ease:'power2.out',immediateRender:false}},{bar['t_fill']:.2f});"
                  f"tl.fromTo(['#{sid}l','#{sid}lt'],{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{bar['t_left']:.2f});")
    if push:
        tgt = [f"#{sid}w"] + ([f"#{video}"] if video else [])
        js.append(f"tl.fromTo({tgt!r},{{scale:1}},{{scale:{push},transformOrigin:'50% 60%',duration:{dur:.2f},ease:'sine.inOut',immediateRender:false}},{t0:.2f});")
    return Scene(sid, t0, dur, doc + pen, js="".join(js))


def arc(a, b, lift=.22):
    """a clean projected arc between two screen points (reads better than a great circle on a flat map)"""
    (x1, y1), (x2, y2) = a, b; mx, my = (x1 + x2) / 2, (y1 + y2) / 2; L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5
    return f"M{x1:.0f} {y1:.0f} Q{mx:.0f} {my - L * lift:.0f} {x2:.0f} {y2:.0f}"


def world_map(sid, t0, dur, *, origin, buyers, title, t_routes=None, t_buy=None, t_flow=None, t_dry=None, panel=None,
              center=(25, 28), scale=7.6, highlight=None):
    """origin (name, lon, lat); buyers [(name, lon, lat)]. Routes draw on t_routes, buyers light on t_buy, payments
    flow along the routes from t_flow (or from the cut, for a reprise), and stop on t_dry (routes go grey). panel:
    before/after value bars {label, t_before, t_after} on the right."""
    P = KM.projection("equirect", center=center, scale=scale)
    land = KM.world_map_svg(f"{sid}m", P, highlight=highlight or {}, land="#d6c4a0", stroke="#efe3c9")
    ox, oy = P(origin[1], origin[2])
    routes, pins = [], []
    for i, (name, lon, lat, *lab) in enumerate(buyers):           # lab: optional (dx, dy, anchor) for the name
        x, y = P(lon, lat); d = arc((ox, oy), (x, y))
        dx, dy, anc = (lab[0] if lab else (18, -14, "start"))
        routes.append(f'<path id="{sid}r{i}" class="{sid}r" d="{d}" fill="none" stroke="{GOLD}" stroke-width="4" stroke-linecap="round"/>')
        pins.append(f'<g id="{sid}p{i}" class="{sid}p" opacity="0"><circle cx="{x:.0f}" cy="{y:.0f}" r="12" fill="{INK}"/><circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="{GOLD}"/>'
                    f'<text x="{x + dx:.0f}" y="{y + dy:.0f}" text-anchor="{anc}" font-family="Inter" font-weight="700" font-size="30" fill="{INK}">{E(name)}</text></g>')
    org = (f'<g id="{sid}o"><rect x="{ox - 46:.0f}" y="{oy - 30:.0f}" width="92" height="60" rx="6" fill="{INK}"/>'
           f'<text x="{ox:.0f}" y="{oy + 10:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="24" fill="{GOLD}">MBS</text>'
           f'<text x="{ox:.0f}" y="{oy + 64:.0f}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="{INK}">{E(origin[0])}</text></g>')
    pan = ""
    if panel:
        px, py = panel.get("at", (1290, 200))
        pan = (f'<div id="{sid}v" style="position:absolute;left:{px}px;top:{py}px;width:520px;padding:30px 34px;background:rgba(247,241,228,.96);border:2px solid #cdbb98;border-radius:10px;opacity:0">'
               f'<div class="vk">{E(panel["label"])}</div><div style="display:flex;gap:60px;align-items:flex-end;height:260px;margin-top:16px">'
               f'<div style="text-align:center"><div style="width:150px;height:230px;background:#5b6b7d;border-radius:4px"></div><div class="vl" style="font-size:32px;margin-top:10px">before</div></div>'
               f'<div style="text-align:center"><div style="height:230px;display:flex;align-items:flex-end"><div id="{sid}va" style="width:150px;height:230px;background:{RED};border-radius:4px;transform-origin:50% 100%"></div></div>'
               f'<div class="vl" style="font-size:32px;margin-top:10px;color:{RED}">after</div></div></div></div>')
    svg = f'<svg width="1920" height="1080" style="position:absolute;inset:0">{land}{"".join(routes)}{org}{"".join(pins)}</svg>'
    ttl = f'<div class="vk" style="position:absolute;left:70px;top:60px;background:rgba(247,241,228,.92);padding:14px 22px;border-radius:8px;font-size:28px;color:{INK}">{E(title)}</div>'
    html_ = f'<div class="vpaper"></div><div class="vgrain"></div><div class="vx" id="{sid}x">{svg}</div>{ttl}{pan}'
    js = [f"tl.fromTo('#{sid}x',{{scale:1.04}},{{scale:1,transformOrigin:'{ox:.0f}px {oy:.0f}px',duration:{dur:.2f},ease:'sine.out',immediateRender:false}},{t0:.2f});"]
    if t_routes is not None: js.append(f"mDrawOn('.{sid}r',{t_routes:.2f},{{dur:.7,stagger:.07}});")
    if t_buy is not None: js.append(f"tl.fromTo('.{sid}p',{{opacity:0,scale:.6,transformOrigin:'50% 50%'}},{{opacity:1,scale:1,duration:.3,stagger:.06,immediateRender:false}},{t_buy:.2f});")
    else: js.append(f"gsap.set('.{sid}p',{{opacity:1}});")
    t_f = t0 if t_flow is None else t_flow
    end = t0 + dur if t_dry is None else t_dry
    for i in range(len(buyers)):   # payment dots travel origin → buyer, steadily, until the flow stops
        js.append(f"(function(){{const p=document.getElementById('{sid}r{i}'),n=p.getTotalLength(),s=p.ownerSVGElement;for(let k=0;k<3;k++){{"
                  f"const c=document.createElementNS('http://www.w3.org/2000/svg','circle');c.setAttribute('r',9);c.setAttribute('fill','{GREEN}');c.setAttribute('opacity',0);s.appendChild(c);"
                  f"const st={{u:0}},put=()=>{{const q=p.getPointAtLength(((st.u+k/3)%1)*n);c.setAttribute('cx',q.x);c.setAttribute('cy',q.y);}};"
                  f"tl.fromTo(st,{{u:0}},{{u:{(end - t_f) / 1.6:.3f},duration:{max(.1, end - t_f):.2f},ease:'none',onUpdate:put,immediateRender:false}},{t_f:.2f});"
                  f"tl.fromTo(c,{{opacity:0}},{{opacity:1,duration:.2,immediateRender:false}},{t_f:.2f});tl.to(c,{{opacity:0,duration:.25}},{end:.2f});}}}})();")
    if t_dry is not None: js.append(f"tl.to('.{sid}r',{{stroke:'#a39a8c',strokeDasharray:'8 10',duration:.4}},{t_dry:.2f});")
    if panel:
        js.append(f"tl.fromTo('#{sid}v',{{opacity:0,x:24}},{{opacity:1,x:0,duration:.3,immediateRender:false}},{panel['t_before']:.2f});"
                  f"tl.fromTo('#{sid}va',{{scaleY:1}},{{scaleY:.18,duration:.6,ease:'power3.in',immediateRender:false}},{panel['t_after']:.2f});")
    return Scene(sid, t0, dur, html_, js="".join(js))


def line_chart(sid, t0, dur, *, series, turn, t_fall, title, note, source, ylabel=""):
    """series [(year, value)], drawn to `turn` (its year) from the cut, then on t_fall continues in red"""
    xs = [p[0] for p in series]; ys = [p[1] for p in series]
    X = lambda v: 200 + (v - xs[0]) / (xs[-1] - xs[0]) * 1480
    Y = lambda v: 860 - (v - min(ys) * .9) / (max(ys) * 1.05 - min(ys) * .9) * 560
    up = [p for p in series if p[0] <= turn]; dn = [p for p in series if p[0] >= turn]
    path = lambda pts: "M" + " L".join(f"{X(a):.0f} {Y(b):.0f}" for a, b in pts)
    ticks = "".join(f'<text x="{X(v):.0f}" y="912" text-anchor="middle" font-family="Inter" font-weight="600" font-size="30" fill="{MUTED}">{v}</text>' for v in xs if v % 2 == 0)
    pk = dict(up)[turn]
    svg = (f'<svg width="1920" height="1080" style="position:absolute;inset:0"><line x1="200" y1="862" x2="1680" y2="862" stroke="{INK}" stroke-width="3"/>{ticks}'
           f'<path id="{sid}u" d="{path(up)}" fill="none" stroke="{INK}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round"/>'
           f'<path id="{sid}d" d="{path(dn)}" fill="none" stroke="{RED}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round"/>'
           f'<g id="{sid}pk" opacity="0"><circle cx="{X(turn):.0f}" cy="{Y(pk):.0f}" r="13" fill="{GOLD}"/>'
           f'<text x="{X(turn):.0f}" y="{Y(pk) - 34:.0f}" text-anchor="middle" font-family="Fraunces" font-weight="700" font-size="44" fill="{INK}">Peak {turn}</text></g>'
           f'<text id="{sid}n" x="{X(xs[-1]) - 10:.0f}" y="{Y(series[-1][1]) - 40:.0f}" text-anchor="end" font-family="Fraunces" font-weight="700" font-size="46" fill="{RED}" opacity="0">{E(note)}</text></svg>')
    html_ = (f'<div class="vpaper"></div><div class="vgrain"></div>'
             f'<div class="vk" style="position:absolute;left:200px;top:96px;font-size:30px;color:{INK}">{E(title)}</div>'
             f'<div style="position:absolute;left:200px;top:140px;font:600 24px Inter;color:{MUTED}">{E(ylabel)}</div>{svg}'
             f'<div style="position:absolute;right:240px;top:104px;width:620px;text-align:right;font:500 20px Inter;color:{MUTED}">{E(source)}</div>')
    js = (f"mDrawOn('#{sid}u',{t0 + .05:.2f},{{dur:{max(.4, t_fall - t0 - .35):.2f},ease:'power1.inOut'}});"
          f"tl.fromTo('#{sid}pk',{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{t_fall - .3:.2f});"
          f"mDrawOn('#{sid}d',{t_fall:.2f},{{dur:.8,ease:'power2.in'}});"
          f"tl.fromTo('#{sid}n',{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{t_fall + .6:.2f});")
    return Scene(sid, t0, dur, html_, js=js)


def newspaper(sid, t0, dur, *, masthead, date, headline, deck, emph, t_head, t_emph, timeline=None, box, transform, push=1.08, video=None):
    """a front page on the desk; the camera pushes into the headline on t_head and the key word is underlined on t_emph.
    timeline = {start, end, marks:[(label, frac)], to_frac, to_label, t_move}: a slim strip at the top"""
    x, y, w, h = box
    words = headline.split()
    head = " ".join(f'<span id="{sid}e" style="position:relative">{E(wd)}<span id="{sid}u" style="position:absolute;left:0;right:0;bottom:-6px;height:8px;background:{RED};transform:scaleX(0);transform-origin:0 50%"></span></span>'
                    if wd.strip(".,").upper() == emph.upper() else E(wd) for wd in words)
    page = (f'<div id="{sid}w" style="position:absolute;inset:0;perspective:1600px"><div id="{sid}pg" class="vdoc" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
            f'transform:{transform};transform-origin:50% 40%;padding:36px 48px;background:#f1ebdc">'
            f'<div style="text-align:center;font:900 64px \'Fraunces\',Georgia,serif;letter-spacing:2px;color:{INK}">{E(masthead)}</div>'
            f'<div style="display:flex;justify-content:space-between;border-top:3px solid {INK};border-bottom:1px solid {INK};padding:6px 2px;margin:10px 0 24px;font:600 20px Inter;color:#4b3f33"><span>{E(date)}</span><span>Illustrative reconstruction</span></div>'
            f'<div id="{sid}h" style="font:900 74px \'Fraunces\',Georgia,serif;line-height:1.02;color:{INK};text-transform:uppercase">{head}</div>'
            f'<div style="font:500 30px Georgia,serif;color:#3b3127;margin-top:22px;line-height:1.3">{E(deck)}</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px;margin-top:26px">' +
            "".join(f'<div style="height:150px;background:repeating-linear-gradient(0deg,#b9ad98 0 3px,transparent 3px 13px)"></div>' for _ in range(3)) +
            '</div></div></div>')
    tlh, tjs = "", ""
    if timeline:
        T = timeline; L = lambda f: 240 + f * 1440
        marks = "".join(f'<div style="position:absolute;left:{L(f) - 4:.0f}px;top:0;width:8px;height:28px;background:{INK}"></div>'
                        f'<div style="position:absolute;left:{L(f) - 80:.0f}px;top:36px;width:160px;text-align:center;font:700 30px Inter;color:{INK}">{E(lab)}</div>' for lab, f in T["marks"])
        tlh = (f'<div style="position:absolute;left:0;right:0;top:0;height:132px;background:rgba(247,241,228,.94);box-shadow:0 6px 18px rgba(20,10,4,.25)">'
               f'<div style="position:absolute;left:240px;width:1440px;top:46px;height:6px;background:{INK}"></div><div style="position:absolute;top:34px;left:0;right:0">{marks}</div>'
               f'<div id="{sid}tm" style="position:absolute;top:30px;left:{L(0) - 18:.0f}px;width:36px;height:36px;border-radius:18px;background:{RED};box-shadow:0 0 0 6px rgba(181,71,58,.25)"></div>'
               f'<div id="{sid}tl" style="position:absolute;top:84px;left:{L(T["to_frac"]) - 160:.0f}px;width:320px;text-align:center;font:800 34px Inter;color:{RED};opacity:0">{E(T["to_label"])}</div></div>')
        tjs = (f"tl.fromTo('#{sid}tm',{{x:0}},{{x:{T['to_frac'] * 1440:.0f},duration:.7,ease:'power2.inOut',immediateRender:false}},{T['t_move']:.2f});"
               f"tl.fromTo('#{sid}tl',{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{T['t_move'] + .5:.2f});")
    tgt = [f"#{sid}w"] + ([f"#{video}"] if video else [])
    js = (f"tl.fromTo({tgt!r},{{scale:1}},{{scale:{push},transformOrigin:'50% 48%',duration:{t0 + dur - t_head:.2f},ease:'sine.inOut',immediateRender:false}},{t_head:.2f});"
          f"tl.fromTo('#{sid}h',{{opacity:.35}},{{opacity:1,duration:.3,immediateRender:false}},{t_head:.2f});"
          f"tl.fromTo('#{sid}u',{{scaleX:0}},{{scaleX:1,duration:.35,ease:'power2.out',immediateRender:false}},{t_emph:.2f});" + tjs)
    return Scene(sid, t0, dur, page + tlh, js=js)


def stamp(sid, t0, dur, *, text, box, rotate, t_in, sub=""):
    """a printed stamp/label on an object in the scene (SOLD on a tray, OVERDUE on a notice): a state, not a motion"""
    x, y, w, h = box
    h_ = (f'<div id="{sid}s" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rotate}deg);border:6px solid {RED};'
          f'border-radius:8px;color:{RED};font:900 {int(h * .5)}px Inter;letter-spacing:6px;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;'
          f'background:rgba(247,241,228,.15);mix-blend-mode:multiply">{E(text)}<span style="font:700 {int(h * .16)}px Inter;letter-spacing:2px">{E(sub)}</span></div>')
    js = f"tl.fromTo('#{sid}s',{{opacity:0,scale:1.35}},{{opacity:.92,scale:1,duration:.18,ease:'power3.in',immediateRender:false}},{t_in:.2f});"
    return Scene(sid, t0, dur, h_, js=js)


def label(sid, t0, dur, *, kicker, text, box, t_in, align="left"):
    """a short label tied to something on screen (the bundle: one security). Text ≥ 48 px."""
    x, y, w = box
    h_ = (f'<div id="{sid}l" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;padding:22px 30px;background:rgba(247,241,228,.95);border:2px solid #cdbb98;'
          f'border-radius:10px;box-shadow:0 16px 40px rgba(20,10,4,.35);text-align:{align};opacity:0"><div class="vk">{E(kicker)}</div><div class="vh" style="font-size:52px;margin-top:6px">{E(text)}</div></div>')
    js = f"tl.fromTo('#{sid}l',{{opacity:0,y:16}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{t_in:.2f});"
    return Scene(sid, t0, dur, h_, js=js)
