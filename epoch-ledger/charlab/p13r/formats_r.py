"""P13R formats (STANDARD §3B pacing variants; the P12 and P13 libraries are unchanged and reused where they fit).

  budget_insert    the signature, then ONE large bar (payment against income) on the table from above; the paper
                   recedes on its word as the scene hands over to the town (the camera rising off the papers)
  pool_map_r       P13's journey map with one motivated camera move: it starts framing their house and their lender,
                   holds, and pulls back on "sells" to reveal the pool; then holds while the country's loans fill it
  world_map_staged the world map with each buyer arriving on its own word (one focal point at a time)
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "p13"), str(HERE.parent / "p12")]
import formats as F  # noqa: E402  (P13)
from visuals import CSS, E, GOLD, GREEN, INK, MUTED, RED, Scene, arc, KM  # noqa: E402,F401  (P12)

NAVY = F.NAVY


def budget_insert(sid, t0, dur, *, sign_t, t_bar, t_left, t_rise, video):
    """the paper on their table: the signature finishes (pen; the hand out of frame), then one bar"""
    x, y, w, h = 560, 120, 800, 760
    sig = (f'<svg width="{w - 120}" height="110" style="position:absolute;left:60px;top:150px"><path id="{sid}s" d="M10 80 C40 15 70 15 60 70 C55 95 95 35 110 45 C125 55 120 75 140 60 '
           f'C165 40 175 25 185 65 C190 85 215 35 240 50 C260 60 270 67 300 45" fill="none" stroke="#1f3a6b" stroke-width="6" stroke-linecap="round"/></svg>')
    bar = (f'<div style="position:absolute;left:60px;right:60px;top:380px">'
           f'<div style="font:800 46px Inter,sans-serif;color:{INK};margin-bottom:14px">Income</div>'
           f'<div style="position:relative;height:110px;border:5px solid {INK};border-radius:8px;background:#efe6d3">'
           f'<div id="{sid}b" style="position:absolute;left:0;top:0;bottom:0;width:90%;background:#5b6b7d;transform:scaleX(0);transform-origin:0 50%"></div>'
           f'<div id="{sid}bl" style="position:absolute;left:28px;top:26px;font:800 44px Inter,sans-serif;color:#f6eedf;opacity:0">Monthly payment</div>'
           f'<div id="{sid}l" style="position:absolute;left:90%;right:-10px;top:-14px;bottom:-14px;border:6px solid {RED};border-radius:6px;opacity:0"></div></div>'
           f'<div id="{sid}lt" style="text-align:right;font:900 46px Inter,sans-serif;color:{RED};margin-top:14px;opacity:0">little left</div></div>')
    paper = (f'<div id="{sid}w" style="position:absolute;inset:0;perspective:1600px"><div class="vdoc" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
             f'transform:rotateX(12deg) rotateZ(-3deg);transform-origin:50% 60%;padding:46px 60px">'
             f'<div class="vh" style="font-size:44px">MORTGAGE AGREEMENT</div><div style="height:3px;background:{INK};margin:12px 0 0"></div>'
             f'<div class="f" style="position:absolute;left:60px;top:126px">Signature</div>{sig}{bar}</div></div>')
    pen = (f'<svg id="{sid}p" width="1920" height="1080" style="position:absolute;inset:0;opacity:0;pointer-events:none"><g id="{sid}pg">'
           f'<path d="M0 0 L16 -12 L820 560 L800 580 Z" fill="#2b2b33"/><path d="M0 0 L16 -12 L44 8 L28 26 Z" fill="#c9a25a"/></g></svg>')
    js = [f"(function(){{const p=document.getElementById('{sid}s'),pg=document.getElementById('{sid}pg'),n=p.getTotalLength(),st={{u:.55}};"
          f"gsap.set(p,{{strokeDasharray:n,strokeDashoffset:n*.45}});"
          f"const put=()=>{{const q=p.getPointAtLength(st.u*n),m=p.getScreenCTM(),r=document.getElementById('{sid}p').getScreenCTM().inverse().multiply(m);"
          f"pg.setAttribute('transform','translate('+(r.a*q.x+r.c*q.y+r.e)+' '+(r.b*q.x+r.d*q.y+r.f)+')');p.style.strokeDashoffset=n*(1-st.u);}};"
          f"tl.fromTo('#{sid}p',{{opacity:1}},{{opacity:1,duration:.01,immediateRender:false}},{t0:.2f});"
          f"tl.fromTo(st,{{u:.55}},{{u:1,duration:.6,ease:'none',onUpdate:put,immediateRender:false}},{sign_t:.2f});"
          f"tl.to('#{sid}p',{{opacity:0,duration:.3}},{sign_t + .7:.2f});}})();",
          f"tl.fromTo('#{sid}b',{{scaleX:0}},{{scaleX:1,duration:.7,ease:'power2.out',immediateRender:false}},{t_bar:.2f});",
          f"tl.fromTo('#{sid}bl',{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{t_bar + .4:.2f});",
          f"tl.fromTo(['#{sid}l','#{sid}lt'],{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{t_left:.2f});",
          f"tl.fromTo(['#{sid}w','#{video}'],{{scale:1}},{{scale:.84,transformOrigin:'50% 50%',duration:{t0 + dur - t_rise:.2f},ease:'sine.inOut',immediateRender:false}},{t_rise:.2f});"]
    return Scene(sid, t0, dur, paper + pen, js="".join(js))


def pool_map_r(sid, t0, dur, *, t_keep, t_sells, t_bundled, t_thousands, t_out):
    """P13's journey map (same town, same thread), with one motivated camera move and labels that stay"""
    blocks, lenders, houses, (fx, fy), roads = F._town(sid)
    pool = (1610, 540); l0, l1 = lenders
    hs = "".join(F._house_svg(x, y, 34, i) for i, (x, y, *_r) in enumerate(houses))
    orig = [f'<path class="{sid}o" d="M{x:.0f} {y:.0f} L{(l0 if bi in (0, 1) else l1)[0]} {(l0 if bi in (0, 1) else l1)[1]}" stroke="{MUTED}" stroke-width="1.8" opacity=".6" fill="none"/>'
            for (x, y, bi, _rq, rv) in houses if rv < .6]
    sale_other = f'<path class="{sid}s1" d="M{l1[0]} {l1[1] + 44} C{l1[0] + 200} {l1[1] - 40}, {pool[0] - 300} {pool[1] + 20}, {pool[0] - 150} {pool[1] + 20}" stroke="{NAVY}" stroke-width="10" stroke-linecap="round" fill="none"/>'
    to_lender = f'<path class="{sid}g1" d="M{fx:.0f} {fy:.0f} L{l0[0]} {l0[1] + 44}" stroke="{GOLD}" stroke-width="8" stroke-linecap="round" fill="none"/>'
    to_pool = f'<path class="{sid}g2" d="M{l0[0]} {l0[1] + 44} C{l0[0] + 260} {l0[1] + 300}, {pool[0] - 300} {pool[1] + 8}, {pool[0] - 150} {pool[1] + 8}" stroke="{GOLD}" stroke-width="8" stroke-linecap="round" fill="none"/>'
    lend = "".join(f'<g><rect x="{x - 62}" y="{y - 44}" width="124" height="88" rx="6" fill="{NAVY}" stroke="{INK}" stroke-width="3"/>'
                   + "".join(f'<rect x="{x - 46 + k * 26}" y="{y - 26}" width="12" height="52" fill="#d9cfbd"/>' for k in range(4)) + "</g>" for x, y in lenders)
    famg = F._house_svg(fx, fy, 52, 0, fill="#f1c45c", roof="#b9862c") + f'<circle cx="{fx:.0f}" cy="{fy - 12:.0f}" r="46" fill="none" stroke="{GOLD}" stroke-width="5"/>'
    tiles = "".join(f'<rect class="{sid}d" x="{pool[0] - 120 + (i % 10) * 24:.0f}" y="{pool[1] - 150 + (i // 10) * 24:.0f}" width="18" height="14" rx="2" fill="#d2ae6c" stroke="{INK}" stroke-width="1.5" opacity="0"/>' for i in range(130))
    poolg = (f'<g id="{sid}P" opacity="0"><rect x="{pool[0] - 150}" y="{pool[1] - 180}" width="300" height="360" rx="18" fill="#efe3c9" stroke="{NAVY}" stroke-width="8"/>{tiles}'
             f'<rect x="{pool[0] - 4}" y="{pool[1] + 10}" width="22" height="16" rx="2" fill="#f1c45c" stroke="{INK}" stroke-width="2"/></g>')
    lab = lambda i, x, y, txt, size=40, anchor="middle", w=800: (f'<text id="{sid}t{i}" x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-family="Inter" font-weight="{w}" '
                                                                 f'font-size="{size}" fill="{INK}" stroke="#f5ecd9" stroke-width="10" paint-order="stroke" opacity="0">{E(txt)}</text>')
    labels = (lab(0, fx + 40, fy - 70, "their loan", 34, "start") + lab(1, l0[0], l0[1] - 64, "their lender", 34) +
              lab(2, pool[0], pool[1] + 240, "THE POOL", 54) + lab(3, pool[0], pool[1] + 292, "thousands of loans", 36, w=600))
    svg = (f'<svg width="1920" height="1080" style="position:absolute;inset:0;overflow:visible"><g id="{sid}c">{roads}{"".join(orig)}{sale_other}{hs}'
           f'{to_lender}{to_pool}{famg}{lend}{poolg}{labels}</g></svg>')
    mid = ((fx + l0[0]) / 2, (fy + l0[1]) / 2)
    cam = F._cam_js(f"#{sid}c", [(t0, 1.7, *mid), (t_sells + .15, 1.7, *mid), (t_sells + 1.65, 1.0, 960, 560), (t_out, 1.0, 960, 560), (t0 + dur, 2.2, *pool)], t0)
    fade = lambda sel, t, d=.35: f"tl.fromTo('{sel}',{{opacity:0}},{{opacity:1,duration:{d},immediateRender:false}},{t:.2f});"
    js = [cam, fade(f"#{sid}t0", t0 + .3), f"mDrawOn('.{sid}g1',{t_keep:.2f},{{dur:.6}});", fade(f"#{sid}t1", t_keep + .35),
          f"tl.to('#{sid}t0',{{opacity:0,duration:.3}},{t_sells:.2f});tl.to('#{sid}t1',{{opacity:0,duration:.3}},{t_bundled - .1:.2f});",
          f"mDrawOn('.{sid}g2',{t_sells:.2f},{{dur:1.2}});", fade(f"#{sid}P", t_sells + .5), fade(f"#{sid}t2", t_sells + .6),
          f"mDrawOn('.{sid}o',{t_bundled:.2f},{{dur:.6,stagger:.01}});mDrawOn('.{sid}s1',{t_bundled + .8:.2f},{{dur:.8}});",
          f"tl.fromTo('.{sid}d',{{opacity:0}},{{opacity:1,duration:.03,stagger:.012,immediateRender:false}},{t_thousands:.2f});", fade(f"#{sid}t3", t_thousands + .1),
          f"tl.to(['#{sid}t2','#{sid}t3'],{{opacity:0,duration:.3}},{t_out:.2f});"]
    return Scene(sid, t0, dur, f'<div class="vpaper"></div><div class="vgrain"></div><div class="vx">{svg}</div>', js="".join(js))


def world_map_staged(sid, t0, dur, *, origin, buyers, t_flow, title, tag, t_tag, center=(22, 30), scale=6.4, highlight=None):
    """buyers [(label, lon, lat, (dx, dy, anchor), t)]: each route draws and its buyer arrives on its own word"""
    P = KM.projection("equirect", center=center, scale=scale)
    land = KM.world_map_svg(f"{sid}m", P, highlight=highlight or {}, land="#d6c4a0", stroke="#efe3c9")
    ox, oy = P(origin[1], origin[2]); routes, pins, js = [], [], []
    for i, (name, lon, lat, (dx, dy, anc), t) in enumerate(buyers):
        x, y = P(lon, lat)
        routes.append(f'<path id="{sid}r{i}" class="{sid}r{i}" d="{arc((ox, oy), (x, y))}" fill="none" stroke="{GOLD}" stroke-width="5" stroke-linecap="round"/>')
        pins.append(f'<g id="{sid}p{i}" opacity="0"><circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="{INK}"/><circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="{GOLD}"/>'
                    f'<text x="{x + dx:.0f}" y="{y + dy:.0f}" text-anchor="{anc}" font-family="Inter" font-weight="800" font-size="36" fill="{INK}" stroke="#f5ecd9" stroke-width="8" paint-order="stroke">{E(name)}</text></g>')
        js.append(f"mDrawOn('.{sid}r{i}',{t - .1:.2f},{{dur:.5}});tl.fromTo('#{sid}p{i}',{{opacity:0,scale:.7,transformOrigin:'{x:.0f}px {y:.0f}px'}},{{opacity:1,scale:1,duration:.3,immediateRender:false}},{t + .3:.2f});")
        js.append(f"(function(){{const p=document.getElementById('{sid}r{i}'),n=p.getTotalLength(),s=p.ownerSVGElement;for(let k=0;k<3;k++){{"
                  f"const c=document.createElementNS('http://www.w3.org/2000/svg','circle');c.setAttribute('r',10);c.setAttribute('fill','{GREEN}');c.setAttribute('opacity',0);s.appendChild(c);"
                  f"const st={{u:0}},put=()=>{{const q=p.getPointAtLength(((st.u+k/3)%1)*n);c.setAttribute('cx',q.x);c.setAttribute('cy',q.y);}};"
                  f"tl.fromTo(st,{{u:0}},{{u:{(t0 + dur - t_flow) / 2.2:.3f},duration:{t0 + dur - t_flow:.2f},ease:'none',onUpdate:put,immediateRender:false}},{t_flow:.2f});"
                  f"tl.fromTo(c,{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{t_flow:.2f});}}}})();")
    org = (f'<g><rect x="{ox - 50:.0f}" y="{oy - 32:.0f}" width="100" height="64" rx="6" fill="{INK}"/>'
           f'<text x="{ox:.0f}" y="{oy + 11:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="26" fill="{GOLD}">MBS</text>'
           f'<text x="{ox:.0f}" y="{oy + 70:.0f}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="32" fill="{INK}">{E(origin[0])}</text></g>')
    svg = f'<svg width="1920" height="1080" style="position:absolute;inset:0">{land}{"".join(routes)}{org}{"".join(pins)}</svg>'
    ttl = f'<div class="vk" style="position:absolute;left:70px;top:60px;background:rgba(247,241,228,.94);padding:14px 22px;border-radius:8px;font-size:30px;color:{INK}">{E(title)}</div>'
    tg = f'<div id="{sid}tg" class="ptag" style="bottom:170px;opacity:0">{E(tag)}</div>'
    js.insert(0, f"tl.fromTo('#{sid}tg',{{opacity:0}},{{opacity:1,duration:.4,immediateRender:false}},{t_tag:.2f});")
    return Scene(sid, t0, dur, f'<div class="vpaper"></div><div class="vgrain"></div><div class="vx">{svg}</div>{ttl}{tg}', js="".join(js))


def price_town_r(sid, t0, dur, *, series, turn, t_line, t_fall, t_push, t_sign, title):
    """P13's price town (same streets) with one change for a first viewing: no scattered signs; the camera eases to
    their gold house and a large FOR SALE sign appears on it on its word (selling no longer repays the loan)"""
    blocks, lenders, houses, (fx, fy), roads = F._town(sid)
    town = "".join(F._house_svg(x, y, 34, i) for i, (x, y, *_r) in enumerate(houses)) + F._house_svg(fx, fy, 52, 0, fill="#f1c45c", roof="#b9862c")
    sign = (f'<g id="{sid}sg" opacity="0"><rect x="{fx + 34:.0f}" y="{fy - 40:.0f}" width="6" height="52" fill="{INK}"/>'
            f'<rect x="{fx + 6:.0f}" y="{fy - 104:.0f}" width="96" height="66" rx="3" fill="{RED}" stroke="{INK}" stroke-width="3"/>'
            f'<text x="{fx + 54:.0f}" y="{fy - 77:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="#fff">FOR</text>'
            f'<text x="{fx + 54:.0f}" y="{fy - 51:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="#fff">SALE</text></g>')
    y0, y1 = 120, 470; xs0, xs1 = 140, 1780
    v0, v1 = min(v for _, v in series) * .95, max(v for _, v in series) * 1.03
    P = lambda yr, v: (xs0 + (yr - series[0][0]) / (series[-1][0] - series[0][0]) * (xs1 - xs0), y1 - (v - v0) / (v1 - v0) * (y1 - y0))
    up = [P(yr, v) for yr, v in series if yr <= turn]; dn = [P(yr, v) for yr, v in series if yr >= turn]
    path = lambda pts: "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    ticks = "".join(f'<text x="{P(yr, v0)[0]:.0f}" y="{y1 + 46}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="30" fill="{MUTED}">{yr}</text>'
                    for yr, _ in series if yr in (series[0][0], turn, series[-1][0]))
    chart = (f'<rect x="80" y="70" width="1760" height="460" rx="14" fill="#f5eedf" stroke="#cdbb98" stroke-width="2"/>'
             f'<path class="{sid}up" d="{path(up)}" stroke="{INK}" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<path class="{sid}dn" d="{path(dn)}" stroke="{RED}" stroke-width="16" fill="none" stroke-linecap="round" stroke-linejoin="round"/>{ticks}'
             f'<text x="110" y="122" font-family="Inter" font-weight="800" font-size="40" fill="{INK}">{E(title)}</text>')
    svg = (f'<svg width="1920" height="1080" style="position:absolute;inset:0;overflow:visible"><g id="{sid}c"><g transform="translate(0,90)">{roads}{town}{sign}</g>'
           f'<g id="{sid}ch" opacity="0">{chart}</g></g></svg>')
    fy2 = fy + 90
    js = [F._cam_js(f"#{sid}c", [(t0, 1.0, 960, 560), (t_push, 1.0, 960, 560), (t0 + dur, 2.6, fx + 30, fy2 - 50)], t0),
          f"tl.fromTo('#{sid}ch',{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{t_line - .2:.2f});",
          f"mDrawOn('.{sid}up',{t_line:.2f},{{dur:.4}});mDrawOn('.{sid}dn',{t_fall - .04:.2f},{{dur:.15}});",
          f"tl.to('#{sid}ch',{{opacity:0,duration:.3}},{t_push + .15:.2f});",
          f"tl.fromTo('#{sid}sg',{{opacity:0,y:10}},{{opacity:1,y:0,duration:.25,immediateRender:false}},{t_sign:.2f});"]
    return Scene(sid, t0, dur, f'<div class="vpaper"></div><div class="vgrain"></div><div class="vx">{svg}</div>', js="".join(js))
