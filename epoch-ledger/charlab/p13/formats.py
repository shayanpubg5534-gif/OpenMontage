"""P13: two reusable formats added to the P12 library (charlab/p12/visuals.py, unchanged), each a kit.assemble.Scene.

  pool_map      a town seen from above: many houses, each loan drawn to its local lender (origination), lenders sell
                into ONE pool (a trust); the through-line's house and its thread are gold. Any "many become one"
                mechanism (pooling, consolidation, clearing).
  frame_overlay a rendered still or video shot (2.5D or 3D) with an ink kicker and callouts placed on the picture (a
                label with a rule to the thing it names), for explaining what is on screen without a card over it.

Same design rules as P12: key text ≥ 34–40 px at 1080p, labels ≤ 7 words, warm paper and ink, gold only for the thing
that matters now.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "p12"))
from visuals import CSS, E, GOLD, GREEN, INK, MUTED, RED, Scene  # noqa: E402,F401

NAVY = "#2f3b52"


def _house(x, y, s, fill, roof, cls="", extra=""):
    return (f'<g class="{cls}" {extra}><rect x="{x - s / 2:.0f}" y="{y - s * .3:.0f}" width="{s:.0f}" height="{s * .7:.0f}" fill="{fill}" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{x - s * .62:.0f} {y - s * .28:.0f} L{x:.0f} {y - s * .78:.0f} L{x + s * .62:.0f} {y - s * .28:.0f} Z" fill="{roof}" stroke="{INK}" stroke-width="2"/></g>')


def pool_map(sid, t0, dur, *, kicker, pool_label, lender_label, family_label, t_lines=None, t_pool=None, seed=4):
    """houses in four neighbourhoods → their lender → one pool on the right. t_lines: origination and sale lines
    draw on; t_pool: the pool fills (loan dots arrive)."""
    rnd = random.Random(seed)
    blocks = [(160, 230), (160, 640), (720, 230), (720, 640)]        # four neighbourhoods (top-left corners)
    lenders = [(560, 470), (1060, 470)]                              # two local lenders between them
    pool = (1610, 540)
    roads = "".join(f'<rect x="{x}" y="0" width="34" height="1080" fill="#e4d6bb"/>' for x in (120, 680, 1240)) + \
            "".join(f'<rect x="0" y="{y}" width="1300" height="34" fill="#e4d6bb"/>' for y in (190, 455, 600, 905))
    houses, lines, fam = [], [], None
    for bi, (bx, by) in enumerate(blocks):
        L = lenders[0] if bi in (0, 1) else lenders[1]
        for r in range(4):
            for q in range(7):
                x, y = bx + 30 + q * 62 + rnd.uniform(-4, 4), by + 40 + r * 62 + rnd.uniform(-3, 3)
                if bi == 1 and r == 3 and q == 5:
                    fam = (x, y); continue
                houses.append(_house(x, y, 34, ["#efe6d3", "#e4d8bf", "#d9ccb2"][(r + q) % 3], ["#7a5a46", "#6a5448", "#85664e"][(r * 3 + q) % 3]))
                if rnd.random() < .55:
                    lines.append(f'<path class="{sid}o" d="M{x:.0f} {y:.0f} L{L[0]} {L[1]}" stroke="{MUTED}" stroke-width="1.6" opacity=".55" fill="none"/>')
    lend = "".join(f'<g><rect x="{x - 62}" y="{y - 44}" width="124" height="88" rx="6" fill="{NAVY}" stroke="{INK}" stroke-width="3"/>'
                   + "".join(f'<rect x="{x - 46 + i * 26}" y="{y - 26}" width="12" height="52" fill="#d9cfbd"/>' for i in range(4))
                   + f'<text x="{x}" y="{y + 84}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="32" fill="{INK}">{E(lender_label)}</text></g>' for x, y in lenders)
    # each lender's sale to the pool: the first dips under the second lender, so no line passes through another building
    bend = [(260, 300), (200, -40)]
    sales = "".join(f'<path class="{sid}s" d="M{x} {y + 44} C{x + bx} {y + by}, {pool[0] - 300} {pool[1] + 20 * i}, {pool[0] - 150} {pool[1] + 20 * i}" stroke="{NAVY}" stroke-width="10" stroke-linecap="round" fill="none"/>'
                    for i, ((x, y), (bx, by)) in enumerate(zip(lenders, bend)))
    fx, fy = fam; l0 = lenders[0]
    thread = (f'<path class="{sid}g" d="M{fx:.0f} {fy:.0f} L{l0[0]} {l0[1] + 44} C{l0[0] + 260} {l0[1] + 300}, {pool[0] - 300} {pool[1] + 8}, {pool[0] - 150} {pool[1] + 8}" '
              f'stroke="{GOLD}" stroke-width="7" stroke-linecap="round" fill="none"/>')
    famg = (_house(fx, fy, 50, "#f1c45c", "#b9862c") + f'<circle cx="{fx:.0f}" cy="{fy - 12:.0f}" r="44" fill="none" stroke="{GOLD}" stroke-width="5"/>'
            f'<text x="{fx + 52:.0f}" y="{fy - 52:.0f}" font-family="Inter" font-weight="700" font-size="34" fill="{INK}" stroke="#f5ecd9" stroke-width="8" paint-order="stroke">{E(family_label)}</text>')
    dots = "".join(f'<rect class="{sid}d" x="{pool[0] - 120 + (i % 10) * 24:.0f}" y="{pool[1] - 150 + (i // 10) * 24:.0f}" width="18" height="14" rx="2" fill="#d2ae6c" stroke="{INK}" stroke-width="1.5"/>' for i in range(130))
    poolg = (f'<rect x="{pool[0] - 150}" y="{pool[1] - 180}" width="300" height="360" rx="18" fill="#efe3c9" stroke="{NAVY}" stroke-width="8"/>{dots}'
             f'<rect x="{pool[0] - 4}" y="{pool[1] + 10}" width="22" height="16" rx="2" fill="#f1c45c" stroke="{INK}" stroke-width="2"/>'
             f'<text x="{pool[0]}" y="{pool[1] + 240}" text-anchor="middle" font-family="Fraunces,Georgia" font-weight="800" font-size="48" fill="{INK}">{E(pool_label[0])}</text>'
             f'<text x="{pool[0]}" y="{pool[1] + 290}" text-anchor="middle" font-family="Inter" font-weight="600" font-size="32" fill="{MUTED}">{E(pool_label[1])}</text>')
    svg = f'<svg width="1920" height="1080" style="position:absolute;inset:0">{roads}{"".join(lines)}{sales}{"".join(houses)}{thread}{famg}{lend}{poolg}</svg>'
    ttl = f'<div class="vk" style="position:absolute;left:70px;top:60px;background:rgba(247,241,228,.94);padding:14px 22px;border-radius:8px;font-size:28px;color:{INK}">{E(kicker)}</div>'
    js = [f"tl.fromTo('#{sid}x',{{scale:1.05}},{{scale:1,transformOrigin:'{fx:.0f}px {fy:.0f}px',duration:{dur:.2f},ease:'sine.out',immediateRender:false}},{t0:.2f});"]
    if t_lines is not None: js.append(f"mDrawOn('.{sid}o',{t_lines:.2f},{{dur:.6,stagger:.004}});mDrawOn('.{sid}g',{t_lines:.2f},{{dur:1.2}});mDrawOn('.{sid}s',{t_lines + .6:.2f},{{dur:.8,stagger:.1}});")
    if t_pool is not None: js.append(f"tl.fromTo('.{sid}d',{{opacity:0}},{{opacity:1,duration:.02,stagger:.008,immediateRender:false}},{t_pool:.2f});")
    return Scene(sid, t0, dur, f'<div class="vpaper"></div><div class="vgrain"></div><div class="vx" id="{sid}x">{svg}</div>{ttl}', js="".join(js))


def frame_overlay(sid, t0, dur, *, src, kicker=None, callouts=(), push=(1.0, 1.0), legend=None):
    """src: an image or video path inside the workspace. callouts: [(text, (tx, ty), (ax, ay), t_in, color)] a label
    at t with a rule to the point a. legend: [(swatch, text)] at the left. push: (scale at start, scale at end)."""
    tag = (f'<video id="{sid}v" src="{src}" muted playsinline style="position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover"></video>'
           if src.endswith(".mp4") else f'<img id="{sid}v" src="{src}" style="position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover">')
    rules, labels, js = [], [], [f"tl.fromTo('#{sid}v',{{scale:{push[0]}}},{{scale:{push[1]},duration:{dur:.2f},ease:'sine.inOut',immediateRender:false}},{t0:.2f});"]
    for i, (text, (tx, ty), (ax, ay), t_in, col) in enumerate(callouts):
        rules.append(f'<path class="{sid}c{i}" d="M{tx:.0f} {ty:.0f} L{ax:.0f} {ay:.0f}" stroke="{col}" stroke-width="4" fill="none"/><circle class="{sid}c{i}" cx="{ax:.0f}" cy="{ay:.0f}" r="8" fill="{col}"/>')
        labels.append(f'<div class="{sid}c{i}" style="position:absolute;left:{tx - 10:.0f}px;top:{ty - 30:.0f}px;transform:translate(-100%,0);background:rgba(247,241,228,.95);'
                      f'border-left:6px solid {col};padding:8px 18px;border-radius:6px;font:700 36px Inter,sans-serif;color:{INK};white-space:nowrap">{E(text)}</div>')
        js.append(f"tl.fromTo('.{sid}c{i}',{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{t_in:.2f});")
    leg = ""
    if legend:
        leg = (f'<div style="position:absolute;left:70px;top:170px;background:rgba(247,241,228,.95);padding:22px 28px;border-radius:10px;border:2px solid #cdbb98">'
               + "".join(f'<div style="display:flex;align-items:center;gap:18px;margin:10px 0"><div style="width:44px;height:30px;background:{sw};border:2px solid {INK}"></div>'
                         f'<div style="font:700 34px Inter,sans-serif;color:{INK}">{E(tx)}</div></div>' for sw, tx in legend) + "</div>")
    kk = f'<div class="vk" style="position:absolute;left:70px;top:60px;background:rgba(247,241,228,.94);padding:14px 22px;border-radius:8px;font-size:28px;color:{INK}">{E(kicker)}</div>' if kicker else ""
    html_ = f'{tag}<svg width="1920" height="1080" style="position:absolute;inset:0">{"".join(rules)}</svg>{"".join(labels)}{leg}{kk}'
    return Scene(sid, t0, dur, html_, js="".join(js))


# ── P13 pilot formats: progressive reveals (one idea at a time, labels few and large) ─────────────────────────────

def _town(sid, seed=4):
    """the shared town layout (four neighbourhoods, two lenders, the family's house): the same streets in every
    reprise, so the viewer recognises the place"""
    rnd = random.Random(seed)
    blocks = [(160, 230), (160, 640), (720, 230), (720, 640)]
    lenders = [(560, 470), (1060, 470)]
    houses, fam = [], None
    for bi, (bx, by) in enumerate(blocks):
        for r in range(4):
            for q in range(7):
                x, y = bx + 30 + q * 62 + rnd.uniform(-4, 4), by + 40 + r * 62 + rnd.uniform(-3, 3)
                if bi == 1 and r == 3 and q == 5: fam = (x, y); continue
                houses.append((x, y, bi, (r, q), rnd.random()))
    roads = "".join(f'<rect x="{x}" y="-400" width="34" height="1900" fill="#e4d6bb"/>' for x in (120, 680, 1240)) + \
            "".join(f'<rect x="-400" y="{y}" width="2200" height="34" fill="#e4d6bb"/>' for y in (190, 455, 600, 905))
    return blocks, lenders, houses, fam, roads


def _house_svg(x, y, s, k, cls="", fill=None, roof=None):
    return _house(x, y, s, fill or ["#efe6d3", "#e4d8bf", "#d9ccb2"][k % 3], roof or ["#7a5a46", "#6a5448", "#85664e"][k % 3], cls)


def _cam_js(sel, keys, t0):
    """2D camera over a 1920×1080 map: keys [(t, scale, cx, cy)] — (cx, cy) is brought to the frame centre"""
    js = []
    for (ta, za, xa, ya), (tb, zb, xb, yb) in zip(keys, keys[1:]):
        js.append(f"tl.fromTo('{sel}',{{x:{960 - xa * za:.1f},y:{540 - ya * za:.1f},scale:{za}}},{{x:{960 - xb * zb:.1f},y:{540 - yb * zb:.1f},scale:{zb},"
                  f"duration:{max(.01, tb - ta):.3f},ease:'sine.inOut',immediateRender:false}},{ta:.3f});")
    z, x, y = keys[0][1:]
    js.insert(0, f"gsap.set('{sel}',{{svgOrigin:'0 0',x:{960 - x * z:.1f},y:{540 - y * z:.1f},scale:{z}}});")
    return "".join(js)


def pool_journey(sid, t0, dur, *, t_keep, t_sells, t_bundled, t_thousands, t_out):
    """S4: from their house (the street seen from above) to their lender, sold on to the pool; then the whole town's
    loans follow and the pool fills; at t_out the camera closes on the pool (the match cut to the 3D plinth)."""
    blocks, lenders, houses, (fx, fy), roads = _town(sid)
    pool = (1610, 540); l0, l1 = lenders
    hs = "".join(_house_svg(x, y, 34, i) for i, (x, y, *_r) in enumerate(houses))
    orig = []
    for i, (x, y, bi, _rq, rv) in enumerate(houses):
        if rv < .6:
            L = l0 if bi in (0, 1) else l1
            orig.append(f'<path class="{sid}o" d="M{x:.0f} {y:.0f} L{L[0]} {L[1]}" stroke="{MUTED}" stroke-width="1.8" opacity=".6" fill="none"/>')
    sale_other = f'<path class="{sid}s1" d="M{l1[0]} {l1[1] + 44} C{l1[0] + 200} {l1[1] - 40}, {pool[0] - 300} {pool[1] + 20}, {pool[0] - 150} {pool[1] + 20}" stroke="{NAVY}" stroke-width="10" stroke-linecap="round" fill="none"/>'
    to_lender = f'<path class="{sid}g1" d="M{fx:.0f} {fy:.0f} L{l0[0]} {l0[1] + 44}" stroke="{GOLD}" stroke-width="8" stroke-linecap="round" fill="none"/>'
    to_pool = f'<path class="{sid}g2" d="M{l0[0]} {l0[1] + 44} C{l0[0] + 260} {l0[1] + 300}, {pool[0] - 300} {pool[1] + 8}, {pool[0] - 150} {pool[1] + 8}" stroke="{GOLD}" stroke-width="8" stroke-linecap="round" fill="none"/>'
    lend = "".join(f'<g id="{sid}L{i}"><rect x="{x - 62}" y="{y - 44}" width="124" height="88" rx="6" fill="{NAVY}" stroke="{INK}" stroke-width="3"/>'
                   + "".join(f'<rect x="{x - 46 + k * 26}" y="{y - 26}" width="12" height="52" fill="#d9cfbd"/>' for k in range(4)) + "</g>" for i, (x, y) in enumerate(lenders))
    famg = (_house_svg(fx, fy, 52, 0, fill="#f1c45c", roof="#b9862c") + f'<circle id="{sid}fr" cx="{fx:.0f}" cy="{fy - 12:.0f}" r="46" fill="none" stroke="{GOLD}" stroke-width="5"/>')
    tiles = "".join(f'<rect class="{sid}d" x="{pool[0] - 120 + (i % 10) * 24:.0f}" y="{pool[1] - 150 + (i // 10) * 24:.0f}" width="18" height="14" rx="2" fill="#d2ae6c" stroke="{INK}" stroke-width="1.5" opacity="0"/>' for i in range(130))
    poolg = (f'<g id="{sid}P" opacity="0"><rect x="{pool[0] - 150}" y="{pool[1] - 180}" width="300" height="360" rx="18" fill="#efe3c9" stroke="{NAVY}" stroke-width="8"/>{tiles}'
             f'<rect id="{sid}ft" x="{pool[0] - 4}" y="{pool[1] + 10}" width="22" height="16" rx="2" fill="#f1c45c" stroke="{INK}" stroke-width="2" opacity="0"/></g>')
    lab = lambda i, x, y, txt, size=40, anchor="middle", fill=INK, w=800: (f'<text id="{sid}t{i}" x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-family="Inter" font-weight="{w}" '
                                                                           f'font-size="{size}" fill="{fill}" stroke="#f5ecd9" stroke-width="10" paint-order="stroke" opacity="0">{E(txt)}</text>')
    labels = (lab(0, fx + 40, fy - 70, "their loan", 30, "start") + lab(1, l0[0], l0[1] - 64, "their lender", 30) +
              lab(2, pool[0], pool[1] + 240, "THE POOL", 52) + lab(3, pool[0], pool[1] + 290, "thousands of loans", 34, w=600))
    svg = (f'<svg width="1920" height="1080" style="position:absolute;inset:0;overflow:visible"><g id="{sid}c">{roads}{"".join(orig)}{sale_other}{hs}'
           f'{to_lender}{to_pool}{famg}{lend}{poolg}{labels}</g></svg>')
    cam = _cam_js(f"#{sid}c", [(t0, 2.6, fx + 60, fy - 40), (t_keep - .1, 2.4, fx + 60, fy - 40), (t_keep + .6, 1.7, (fx + l0[0]) / 2, (fy + l0[1]) / 2),
                               (t_sells, 1.7, (fx + l0[0]) / 2, (fy + l0[1]) / 2), (t_sells + 1.15, 1.0, 960, 560), (t_out, 1.0, 960, 560), (t0 + dur, 2.2, pool[0], pool[1])], t0)
    fade = lambda sel, t, d=.3, to=1: f"tl.fromTo('{sel}',{{opacity:0}},{{opacity:{to},duration:{d},immediateRender:false}},{t:.2f});"
    js = [cam, f"gsap.set('#{sid}t0',{{opacity:1}});", f"mDrawOn('.{sid}g1',{t_keep:.2f},{{dur:.55}});", fade(f"#{sid}t1", t_keep + .25),
          f"tl.fromTo('#{sid}L0',{{scale:1}},{{scale:1.12,transformOrigin:'50% 50%',duration:.25,yoyo:true,repeat:1,immediateRender:false}},{t_keep + .55:.2f});",
          f"tl.to('#{sid}t0',{{opacity:0,duration:.3}},{t_sells:.2f});tl.to('#{sid}t1',{{opacity:0,duration:.3}},{t_bundled:.2f});",
          f"mDrawOn('.{sid}g2',{t_sells:.2f},{{dur:.9}});", fade(f"#{sid}P", t_sells + .5), fade(f"#{sid}ft", t_sells + .9), fade(f"#{sid}t2", t_sells + .6),
          f"mDrawOn('.{sid}o',{t_bundled:.2f},{{dur:.5,stagger:.006}});mDrawOn('.{sid}s1',{t_bundled + .3:.2f},{{dur:.7}});",
          f"tl.fromTo('.{sid}d',{{opacity:0}},{{opacity:1,duration:.02,stagger:.006,immediateRender:false}},{t_thousands:.2f});", fade(f"#{sid}t3", t_thousands + .1),
          f"tl.to(['#{sid}t2','#{sid}t3'],{{opacity:0,duration:.25}},{t_out:.2f});"]
    return Scene(sid, t0, dur, f'<div class="vpaper"></div><div class="vgrain"></div><div class="vx">{svg}</div>', js="".join(js))


def price_town(sid, t0, dur, *, series, turn, t_sale, t_line, t_fall, t_push, title, note):
    """S8: their town again; FOR SALE signs go up; the house-price line draws over the rooftops and turns down (red).
    series: [(year, value)] (indicative, labelled); turn: the peak year."""
    blocks, lenders, houses, (fx, fy), roads = _town(sid)
    rnd = random.Random(11)
    town = "".join(_house_svg(x, y, 34, i) for i, (x, y, *_r) in enumerate(houses)) + _house_svg(fx, fy, 52, 0, fill="#f1c45c", roof="#b9862c")
    sale = [houses[i] for i in sorted(rnd.sample(range(len(houses)), 11))]
    signs = "".join(f'<g class="{sid}fs" opacity="0"><rect x="{x + 34:.0f}" y="{y - 30:.0f}" width="5" height="34" fill="{INK}"/>'
                    f'<rect x="{x + 6:.0f}" y="{y - 74:.0f}" width="62" height="46" fill="{RED}" stroke="{INK}" stroke-width="3"/>'
                    f'<text x="{x + 37:.0f}" y="{y - 56:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="15" fill="#fff">FOR</text>'
                    f'<text x="{x + 37:.0f}" y="{y - 38:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="15" fill="#fff">SALE</text></g>' for x, y, *_ in sale)
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
             f'<text x="110" y="122" font-family="Inter" font-weight="800" font-size="40" fill="{INK}">{E(title)}</text>'
             f'<text x="1810" y="122" text-anchor="end" font-family="Inter" font-weight="600" font-size="24" fill="{MUTED}">{E(note)}</text>')
    svg = (f'<svg width="1920" height="1080" style="position:absolute;inset:0;overflow:visible"><g id="{sid}c"><g transform="translate(0,90)">{roads}{town}{signs}</g>'
           f'<g id="{sid}ch" opacity="0">{chart}</g></g></svg>')
    fy2 = fy + 90
    js = [_cam_js(f"#{sid}c", [(t0, 1.0, 960, 560), (t_push + .15, 1.0, 960, 560), (t0 + dur, 2.8, fx, fy2 - 20)], t0),
          f"tl.fromTo('.{sid}fs',{{opacity:0,y:8}},{{opacity:1,y:0,duration:.18,stagger:.03,immediateRender:false}},{t_sale:.2f});",
          f"tl.fromTo('#{sid}ch',{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{t_line - .2:.2f});",
          f"mDrawOn('.{sid}up',{t_line:.2f},{{dur:.4}});mDrawOn('.{sid}dn',{t_fall - .04:.2f},{{dur:.15}});",
          f"tl.to('#{sid}ch',{{opacity:0,duration:.3}},{t_push + .15:.2f});"]
    return Scene(sid, t0, dur, f'<div class="vpaper"></div><div class="vgrain"></div><div class="vx">{svg}</div>', js="".join(js))


def steps(sid, t0, dur, *, head, head_color, lines, box=(70, 60), arrow="↓"):
    """a legend that builds one line at a time with the narration: head (e.g. 'Payments: paid from the top'), then
    lines [(t, swatch, text)] — never more than four lines, each ≤ 7 words, ≥ 36 px"""
    x, y = box
    rows = "".join(f'<div id="{sid}r{i}" style="display:flex;align-items:center;gap:16px;margin-top:12px;opacity:0"><div style="width:40px;height:28px;background:{sw};border:2px solid {INK}"></div>'
                   f'<div style="font:700 36px Inter,sans-serif;color:{INK}">{E(tx)}</div></div>' for i, (_t, sw, tx) in enumerate(lines))
    h_ = (f'<div id="{sid}b" style="position:absolute;left:{x}px;top:{y}px;background:rgba(247,241,228,.95);padding:20px 28px 22px;border-radius:10px;border-left:8px solid {head_color};opacity:0">'
          f'<div style="font:800 38px Inter,sans-serif;color:{head_color}">{E(head)} <span style="font-size:42px">{arrow}</span></div>{rows}</div>')
    js = [f"tl.fromTo('#{sid}b',{{opacity:0,x:-16}},{{opacity:1,x:0,duration:.3,immediateRender:false}},{t0:.2f});"]
    js += [f"tl.fromTo('#{sid}r{i}',{{opacity:0,x:-10}},{{opacity:1,x:0,duration:.25,immediateRender:false}},{t:.2f});" for i, (t, *_r) in enumerate(lines)]
    return Scene(sid, t0, dur, h_, js="".join(js))


def super_(sid, t0, dur, *, text, t_in, sub=None):
    """a period super in the corner (the year): Fraunces numerals, quiet"""
    s = f'<div style="font:600 24px Inter;letter-spacing:3px;text-transform:uppercase;color:#f3e9d6;opacity:.85">{E(sub)}</div>' if sub else ""
    h_ = (f'<div id="{sid}" style="position:absolute;left:64px;top:52px;padding:12px 24px;background:rgba(18,14,10,.55);border-radius:8px;opacity:0">'
          f'<div style="font:800 64px Fraunces,Georgia,serif;color:#f6eedf;line-height:1">{E(text)}</div>{s}</div>')
    return Scene(sid, t0, dur, h_, js=f"tl.fromTo('#{sid}',{{opacity:0,y:-8}},{{opacity:1,y:0,duration:.35,immediateRender:false}},{t_in:.2f});"
                                       f"tl.to('#{sid}',{{opacity:0,duration:.4}},{t0 + dur - .4:.2f});")


def follow(sid, t0, dur, *, cam2d, svg, js=""):
    """an overlay in a 2.5D plate's own pixels that follows the compositor's 2D camera exactly (cam2d keys in film
    seconds, smoothstep as compose.mjs), so a mark drawn on the set stays on it while the camera pushes"""
    keys = json.dumps(cam2d)
    h_ = f'<div id="{sid}w" style="position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0"><svg width="1920" height="1080">{svg}</svg></div>'
    j = (f"(function(){{const K={keys},w=document.getElementById('{sid}w'),st={{t:{t0}}},ss=x=>(x=Math.min(1,Math.max(0,x)),x*x*(3-2*x));"
         f"const put=()=>{{const t=st.t;let a=K[0],b=K[K.length-1];for(let i=1;i<K.length;i++)if(t<K[i][0]){{a=K[i-1];b=K[i];break;}}"
         f"const u=b[0]>a[0]?ss((t-a[0])/(b[0]-a[0])):1,z=a[1]+(b[1]-a[1])*u,x=a[2]+(b[2]-a[2])*u,y=a[3]+(b[3]-a[3])*u;"
         f"w.style.transform='translate('+(960-x*z)+'px,'+(540-y*z)+'px) scale('+z+')';}};"
         f"tl.fromTo(st,{{t:{t0}}},{{t:{t0 + dur},duration:{dur},ease:'none',onUpdate:put,immediateRender:false}},{t0});put();}})();")
    return Scene(sid, t0, dur, h_, js=j + js)


def xfade(sid, t, d, *, out_sel=None, in_sel=None):
    """a dissolve between two clips that overlap for d seconds: fades the outgoing one (or the incoming in)"""
    j = ""
    if out_sel: j += f"tl.fromTo({out_sel!r},{{opacity:1}},{{opacity:0,duration:{d},ease:'sine.inOut',immediateRender:false}},{t:.3f});"
    if in_sel: j += f"tl.fromTo({in_sel!r},{{opacity:0}},{{opacity:1,duration:{d},ease:'sine.inOut',immediateRender:false}},{t:.3f});"
    return Scene(sid, t, d, "", js=j)
