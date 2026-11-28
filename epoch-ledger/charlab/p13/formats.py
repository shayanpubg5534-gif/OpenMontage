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
