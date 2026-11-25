"""Epoch Ledger financial mechanisms — illustrated, diegetic "money machine" parts for narration-driven explanations.

A company's cash is a glass tank of gold coins; spending, revenue and investment are glass pipes carrying coins
to and from it; valves, gauges and lamps show control and state. Parts are drawn in 1920x1080 screen space (place
them in a shot's live SVG layer, over a cached plate) and every moving part has an id for kit/finmotion.js.
Original implementation; deterministic.

  coin_defs(uid)                         gradients for coins (call once per SVG)
  tank_svg(uid, x, y, w, h, level, label)        glass cash tank: fill ({uid}-fill), needle ({uid}-needle), lamp ({uid}-lamp)
  glass_pipe(uid, pts, width, label)     glass tube with brass collars along a polyline; coin path {uid}-path, coin layer {uid}-coins
  valve_wheel(uid, cx, cy, r)            hand wheel ({uid}) that turns
  gauge_dial(uid, cx, cy, r, frac, label)        big dial: needle {uid}-needle, red lamp {uid}-lamp
  brass_plate(x, y, text, size, anchor)  engraved label plate
  envelope(uid, x, y, s)                 pay envelope ({uid}) with coin
  tv_set(uid, x, y, w)                   period TV with an animatable ad: {uid}-off, {uid}-line, {uid}-ad, {uid}-rocket, {uid}-logo, {uid}-tag
"""
from __future__ import annotations

import math

INK = "#1b1410"
BRASS, BRASS_D, BRASS_L = "#c7953f", "#7a5420", "#f2d58a"
GLASS = "rgba(206,232,242,.22)"


def coin_defs(uid: str) -> str:
    return (f'<radialGradient id="{uid}-coin" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#fff2b8"/><stop offset=".5" stop-color="#f2c24a"/>'
            f'<stop offset="1" stop-color="#a8741e"/></radialGradient>'
            f'<linearGradient id="{uid}-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd76a"/><stop offset="1" stop-color="#b8801e"/></linearGradient>'
            f'<linearGradient id="{uid}-brass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BRASS_L}"/><stop offset=".45" stop-color="{BRASS}"/><stop offset="1" stop-color="{BRASS_D}"/></linearGradient>')


def brass_plate(x: float, y: float, text: str, size: int = 30, anchor: str = "middle", color: str = "#2a1a0a", uid: str = "") -> str:
    w = len(text) * size * .66 + size * 1.2
    x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    gid = f' id="{uid}"' if uid else ""
    return (f'<g{gid}><rect x="{x0:.0f}" y="{y - size * .95:.0f}" width="{w:.0f}" height="{size * 1.45:.0f}" rx="{size * .2:.0f}" fill="#d9ad55" stroke="{BRASS_D}" stroke-width="3"/>'
            f'<rect x="{x0 + 4:.0f}" y="{y - size * .95 + 4:.0f}" width="{w - 8:.0f}" height="{size * .35:.0f}" rx="3" fill="#fff" opacity=".25"/>'
            f'<circle cx="{x0 + size * .35:.0f}" cy="{y - size * .22:.0f}" r="3.5" fill="{BRASS_D}"/><circle cx="{x0 + w - size * .35:.0f}" cy="{y - size * .22:.0f}" r="3.5" fill="{BRASS_D}"/>'
            f'<text x="{x0 + w / 2:.0f}" y="{y:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{size}" letter-spacing="2" fill="{color}">{text}</text></g>')


def tank_svg(uid: str, x: float, y: float, w: float, h: float, level: float = .8, label: str = "BIGCART CASH", gauge: bool = True,
             outlet: str = "right", seed: int = 3) -> str:
    """Glass cylinder tank of gold coins standing on a brass plinth. Top-left of the glass at (x, y)."""
    e = w * .13                       # ellipse half-height (perspective of the round top/bottom)
    gx0, gx1, gy0, gy1 = x, x + w, y + e, y + h - e
    inner_h = gy1 - gy0
    lvl_y = gy0 + (1 - level) * inner_h
    glass = f"M{gx0} {gy0} A{w / 2} {e} 0 0 1 {gx1} {gy0} L{gx1} {gy1} A{w / 2} {e} 0 0 1 {gx0} {gy1}Z"
    # coin texture rows inside the fill (drawn for the full height; the fill group slides down to lower the level)
    rows = []
    k = seed
    for r in range(int(inner_h // 22) + 3):
        yy = gy0 + r * 22
        for c in range(int(w // 46) + 1):
            k = (k * 1103515245 + 12345) & 0x7fffffff
            cx = gx0 + 18 + c * 46 + (r % 2) * 23 + (k % 9) - 4
            rows.append(f'<ellipse cx="{cx:.0f}" cy="{yy + 8:.0f}" rx="19" ry="6.5" fill="url(#{uid}-coin)" stroke="#8a5a14" stroke-width="1.6"/>')
    fill = (f'<g id="{uid}-fill" data-inner="{inner_h:.1f}"><rect x="{gx0}" y="{gy0}" width="{w}" height="{inner_h + 2 * e}" fill="url(#{uid}-gold)"/>{"".join(rows)}'
            f'<ellipse cx="{x + w / 2}" cy="{gy0}" rx="{w / 2 - 2}" ry="{e - 2}" fill="#ffe08a" stroke="#b8801e" stroke-width="2"/>'
            + "".join(f'<ellipse cx="{x + w * f:.0f}" cy="{gy0 + d:.0f}" rx="18" ry="6" fill="url(#{uid}-coin)" stroke="#8a5a14" stroke-width="1.5"/>' for f, d in ((.3, -4), (.52, 3), (.7, -2), (.42, 6)))
            + '</g>')
    # level marks + LOW band
    marks = "".join(f'<path d="M{gx1 - 26} {gy0 + inner_h * f:.0f} H{gx1 - 8}" stroke="#ffffff" stroke-width="3" opacity=".55"/>' for f in (.2, .4, .6, .8))
    low_y = gy0 + inner_h * .82
    low = (f'<rect x="{gx0 + 6}" y="{low_y:.0f}" width="{w - 12}" height="{inner_h * .18 - 4:.0f}" fill="#d9503f" opacity=".16"/>'
           f'<text x="{gx1 - 14}" y="{low_y + 26:.0f}" text-anchor="end" font-family="Inter" font-weight="800" font-size="22" fill="#ff8a7a" opacity=".85">LOW</text>')
    hl = (f'<path d="M{gx0 + w * .12} {gy0 + 14} V{gy1 - 8}" stroke="#ffffff" stroke-width="{w * .06:.0f}" opacity=".22" stroke-linecap="round"/>'
          f'<path d="M{gx0 + w * .24} {gy0 + 30} V{gy1 - 30}" stroke="#ffffff" stroke-width="5" opacity=".28" stroke-linecap="round"/>'
          f'<path d="M{gx1 - w * .1} {gy0 + 20} V{gy1 - 12}" stroke="#ffffff" stroke-width="3" opacity=".18"/>')
    band = lambda yy: (f'<path d="M{gx0 - 6} {yy} A{w / 2 + 6} {e + 2} 0 0 0 {gx1 + 6} {yy} L{gx1 + 6} {yy + 22} A{w / 2 + 6} {e + 2} 0 0 1 {gx0 - 6} {yy + 22}Z" '
                       f'fill="url(#{uid}-brass)" stroke="{INK}" stroke-width="3"/>')
    lid = (f'<ellipse cx="{x + w / 2}" cy="{gy0}" rx="{w / 2 + 6}" ry="{e + 3}" fill="#3a2a1a" stroke="{INK}" stroke-width="3"/>'
           f'<ellipse cx="{x + w / 2}" cy="{gy0}" rx="{w * .14}" ry="{e * .35}" fill="#120c08"/>')    # open inlet at the top
    plinth = (f'<path d="M{gx0 - 30} {gy1 + 10} H{gx1 + 30} L{gx1 + 44} {gy1 + 110} H{gx0 - 44}Z" fill="#4a3424" stroke="{INK}" stroke-width="4"/>'
              f'<path d="M{gx0 - 30} {gy1 + 10} H{gx1 + 30} L{gx1 + 34} {gy1 + 28} H{gx0 - 34}Z" fill="#6a4a30"/>')
    shadow = f'<ellipse cx="{x + w / 2}" cy="{gy1 + 112}" rx="{w * .78}" ry="{e * 1.1}" fill="#000" opacity=".35"/>'
    dial = ""
    if gauge:
        cx, cy, r = x + w / 2, gy1 + 62, min(46, w * .16)
        a = math.pi * (1 - level)
        dial = (f'<circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="#3a2a1a" stroke="{INK}" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="#f6f0dc"/>'
                f'<path d="M{cx - r * .8:.1f} {cy + 4} A{r * .8:.1f} {r * .8:.1f} 0 0 1 {cx - r * .57:.1f} {cy - r * .57:.1f}" stroke="#d9503f" stroke-width="7" fill="none"/>'
                f'<g id="{uid}-needle"><path d="M{cx} {cy} L{cx + r * .78 * math.cos(math.pi * .5):.1f} {cy - r * .78}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/></g>'
                f'<circle cx="{cx}" cy="{cy}" r="6" fill="{INK}"/>'
                f'<circle id="{uid}-lamp" cx="{cx + r + 34}" cy="{cy - 8}" r="11" fill="#5a1a14" stroke="{INK}" stroke-width="3"/>')
    out_x, out_y = (gx1, gy1 - 34) if outlet == "right" else (gx0, gy1 - 34)
    outlet_svg = (f'<rect x="{out_x - (0 if outlet == "right" else 40)}" y="{out_y - 26}" width="40" height="52" fill="url(#{uid}-brass)" stroke="{INK}" stroke-width="3"/>')
    plate = brass_plate(x + w / 2, gy0 + inner_h * .52, label, 26) if label else ""
    return (f'<g id="{uid}" data-outlet="{out_x + (40 if outlet == "right" else -40):.0f},{out_y:.0f}" data-inlet="{x + w / 2:.0f},{gy0:.0f}" data-low="{low_y:.0f}">'
            f'<defs>{coin_defs(uid)}<clipPath id="{uid}-clip"><path d="{glass}"/></clipPath></defs>{shadow}{plinth}'
            f'<path d="{glass}" fill="#1a2a30" opacity=".55"/>'
            f'<g clip-path="url(#{uid}-clip)"><g id="{uid}-fillwrap" transform="translate(0 {lvl_y - gy0:.1f})">{fill}</g>{low}{marks}</g>'
            f'<path d="{glass}" fill="{GLASS}" stroke="{INK}" stroke-width="4"/>{hl}{band(gy0 + inner_h * .3)}{band(gy1 - 26)}{lid}{outlet_svg}{plate}{dial}</g>')


def _poly_d(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def glass_pipe(uid: str, pts: list[tuple[float, float]], width: float = 44, label: str | None = None, label_pos: float = .5,
               label_size: int = 26, collar_every: float = 150, tint: str = GLASS) -> str:
    """Glass tube along a polyline (right-angle runs read best), brass collars, a highlight, optional brass label plate.
    Coins travel along {uid}-path (invisible centreline); add them in {uid}-coins (drawn inside the glass)."""
    d = _poly_d(pts)
    collars = []
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    s = collar_every * .5
    acc = 0
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        while s <= acc + L:
            u = (s - acc) / L
            px, py = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            collars.append(f'<rect x="{-11}" y="{-width / 2 - 6:.0f}" width="22" height="{width + 12:.0f}" rx="4" fill="url(#{uid}-brass)" stroke="{INK}" stroke-width="3" '
                           f'transform="translate({px:.1f} {py:.1f}) rotate({ang:.1f})"/>')
            s += collar_every
        acc += L
    joints = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{width / 2 + 7:.0f}" fill="url(#{uid}-brass)" stroke="{INK}" stroke-width="3"/>' for x, y in pts[1:-1])
    lab = ""
    if label:
        # place the plate on the longest segment near label_pos
        segs = sorted(zip(pts, pts[1:]), key=lambda ab: -math.dist(*ab))
        a, b = segs[0]
        px, py = a[0] + (b[0] - a[0]) * label_pos, a[1] + (b[1] - a[1]) * label_pos
        horiz = abs(b[0] - a[0]) >= abs(b[1] - a[1])
        lab = brass_plate(px, py - width / 2 - 18 if horiz else py, label, label_size) if horiz else \
            f'<g transform="translate({px + width / 2 + 16:.0f} {py:.0f})">{brass_plate(0, 0, label, label_size, "start")}</g>'
    return (f'<g id="{uid}" data-length="{total:.0f}"><defs>{coin_defs(uid)}</defs>'
            f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{width + 8}" stroke-linejoin="round" stroke-linecap="butt"/>'
            f'<path d="{d}" fill="none" stroke="#18242a" stroke-width="{width}" stroke-linejoin="round" opacity=".55"/>'
            f'<path id="{uid}-path" d="{d}" fill="none" stroke="none"/>'
            f'<g id="{uid}-coins"></g>'
            f'<path d="{d}" fill="none" stroke="{tint}" stroke-width="{width}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="{max(3, width * .12):.0f}" stroke-linejoin="round" opacity=".35" transform="translate(0 {-width * .24:.1f})"/>'
            f'{joints}{"".join(collars)}{lab}</g>')


def valve_wheel(uid: str, cx: float, cy: float, r: float = 46, color: str = "#b8322a") -> str:
    spokes = "".join(f'<path d="M{cx} {cy} L{cx + r * math.cos(k * math.pi / 3):.1f} {cy + r * math.sin(k * math.pi / 3):.1f}" stroke="{color}" stroke-width="{r * .14:.1f}" stroke-linecap="round"/>' for k in range(6))
    return (f'<g id="{uid}"><circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="{r * .3:.1f}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{r * .2:.1f}"/>{spokes}'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .22:.1f}" fill="#7a1e18" stroke="{INK}" stroke-width="3"/>'
            f'<circle cx="{cx - r * .3:.1f}" cy="{cy - r * .95:.1f}" r="{r * .08:.1f}" fill="#fff" opacity=".6"/></g>')


def gauge_dial(uid: str, cx: float, cy: float, r: float = 220, frac: float = .7, label: str = "CASH") -> str:
    """Large analogue dial for close-ups: frac 0 (empty, left) .. 1 (full, right); red zone low; needle rotates about (cx, cy)."""
    ticks = "".join(f'<path d="M{cx + (r - 18) * math.cos(math.pi * (1 - k / 10)):.1f} {cy - (r - 18) * math.sin(math.pi * (1 - k / 10)):.1f} '
                    f'L{cx + (r - (44 if k % 5 == 0 else 32)) * math.cos(math.pi * (1 - k / 10)):.1f} {cy - (r - (44 if k % 5 == 0 else 32)) * math.sin(math.pi * (1 - k / 10)):.1f}" '
                    f'stroke="{INK}" stroke-width="{6 if k % 5 == 0 else 3}"/>' for k in range(11))
    red = f'<path d="M{cx - (r - 30)} {cy} A{r - 30} {r - 30} 0 0 1 {cx + (r - 30) * math.cos(math.pi * .78):.1f} {cy - (r - 30) * math.sin(math.pi * .78):.1f}" stroke="#d9503f" stroke-width="26" fill="none"/>'
    ang = -90 + 180 * frac     # needle drawn pointing up (frac .5); rotate by (frac-.5)*180
    return (f'<g id="{uid}"><circle cx="{cx}" cy="{cy}" r="{r + 26}" fill="url(#{uid}-brass)" stroke="{INK}" stroke-width="5"/>'
            f'<defs>{coin_defs(uid)}</defs><circle cx="{cx}" cy="{cy}" r="{r}" fill="#f6f0dc" stroke="{INK}" stroke-width="4"/>{red}{ticks}'
            f'<text x="{cx - r * .62:.0f}" y="{cy + 52:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{r * .15:.0f}" fill="#b8322a">EMPTY</text>'
            f'<text x="{cx + r * .62:.0f}" y="{cy + 52:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{r * .15:.0f}" fill="#2a1a0a">FULL</text>'
            f'<text x="{cx}" y="{cy + r * .5:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{r * .19:.0f}" letter-spacing="4" fill="#2a1a0a">{label}</text>'
            f'<g id="{uid}-needle" transform="rotate({ang:.1f} {cx} {cy})"><path d="M{cx - 9} {cy + 20} L{cx} {cy - r + 34} L{cx + 9} {cy + 20}Z" fill="#b8322a" stroke="{INK}" stroke-width="3"/></g>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .1:.0f}" fill="{INK}"/>'
            f'<path d="M{cx - r * .7:.0f} {cy - r * .55:.0f} A{r} {r} 0 0 1 {cx + r * .2:.0f} {cy - r * .86:.0f}" stroke="#fff" stroke-width="10" fill="none" opacity=".35"/>'
            f'<g transform="translate({cx + r * .75:.0f} {cy - r * .95:.0f})"><circle r="{r * .13:.0f}" fill="#3a1a14" stroke="{INK}" stroke-width="4"/>'
            f'<circle id="{uid}-lamp" r="{r * .1:.0f}" fill="#ff3a2a" opacity="0"/></g></g>')


def envelope(uid: str, x: float, y: float, s: float = 1.0) -> str:
    return (f'<g id="{uid}" transform="translate({x:.0f} {y:.0f}) scale({s})"><g class="env">'
            f'<rect x="-46" y="-30" width="92" height="60" rx="5" fill="#f2e6c8" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M-46 -30 L0 6 L46 -30" fill="none" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="-26" y="8" width="52" height="16" rx="3" fill="#2a6a2a"/><text x="0" y="21" text-anchor="middle" font-family="Inter" font-weight="800" font-size="14" fill="#fff">PAY</text></g></g>')


def tv_set(uid: str, x: float, y: float, w: float = 760) -> str:
    """Period CRT television on a short stand, three-quarter-ish, with an animatable BigCart ad on its screen."""
    h = w * .78
    sx, sy, sw, sh = x + w * .09, y + h * .1, w * .66, h * .7
    ad = (f'<g id="{uid}-ad" opacity="0"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#2b4f9e"/>'
          f'<circle cx="{sx + sw * .5}" cy="{sy + sh * .46}" r="{sh * .34}" fill="#3a66c0"/>'
          + "".join(f'<circle cx="{sx + sw * ((k * 37) % 100) / 100:.0f}" cy="{sy + sh * ((k * 53) % 100) / 100:.0f}" r="2.5" fill="#fff" opacity=".7"/>' for k in range(18))
          + f'<g id="{uid}-fly"><g id="{uid}-rocket" transform="translate({sx + sw * .2:.0f} {sy + sh * .95:.0f}) rotate(35)"><g transform="scale({sw / 900:.3f})">'
          f'<path d="M0 -150 C70 -90 72 70 0 150 C-72 70 -70 -90 0 -150Z" fill="#f4ead5" stroke="{INK}" stroke-width="9"/><circle cy="-30" r="36" fill="#7fc8ee" stroke="{INK}" stroke-width="8"/>'
          f'<path d="M-50 90 L-110 170 L-30 140Z M50 90 L110 170 L30 140Z" fill="#d9503f" stroke="{INK}" stroke-width="8"/>'
          f'<path id="{uid}-flame" d="M-30 150 Q0 330 30 150Z" fill="#ffb03a"/><path d="M-15 150 Q0 250 15 150Z" fill="#fff0a0"/></g></g></g>'
          f'<g id="{uid}-logo" opacity="0"><text x="{sx + sw * .5}" y="{sy + sh * .3}" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="{sw * .13:.0f}" fill="#fff">BigCart.com</text></g>'
          f'<g id="{uid}-tag" opacity="0"><text x="{sx + sw * .5}" y="{sy + sh * .86}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{sw * .065:.0f}" fill="#ffd56a">Everything. Delivered.</text></g></g>')
    return (f'<g id="{uid}"><defs><clipPath id="{uid}-scr"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="{sw * .06:.0f}"/></clipPath>'
            f'<pattern id="{uid}-scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000"/></pattern></defs>'
            f'<ellipse cx="{x + w / 2}" cy="{y + h + 40}" rx="{w * .5}" ry="22" fill="#000" opacity=".35"/>'
            f'<path d="M{x + w * .3} {y + h} L{x + w * .24} {y + h + 40} H{x + w * .76} L{x + w * .7} {y + h}Z" fill="#3a2a1a" stroke="{INK}" stroke-width="4"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w * .05:.0f}" fill="#6a4a30" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="{x + 8}" y="{y + 8}" width="{w - 16}" height="{h * .2}" rx="{w * .04:.0f}" fill="#fff" opacity=".08"/>'
            f'<rect x="{sx - 14}" y="{sy - 14}" width="{sw + 28}" height="{sh + 28}" rx="{sw * .08:.0f}" fill="#1a1410" stroke="{INK}" stroke-width="4"/>'
            f'<g clip-path="url(#{uid}-scr)"><rect id="{uid}-off" x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#141c1c"/>{ad}'
            f'<rect id="{uid}-line" x="{sx}" y="{sy + sh / 2 - 3}" width="{sw}" height="6" fill="#eaf6ff" opacity="0"/>'
            f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#{uid}-scan)" opacity=".25"/>'
            f'<path d="M{sx} {sy} h{sw * .5} l{-sw * .2} {sh} h{-sw * .3}Z" fill="#fff" opacity=".06"/></g>'
            f'<rect x="{x + w * .8}" y="{y + h * .12}" width="{w * .14}" height="{h * .7}" rx="8" fill="#4a3424" stroke="{INK}" stroke-width="3"/>'
            + "".join(f'<circle cx="{x + w * .87}" cy="{y + h * (.24 + k * .16):.0f}" r="{w * .035:.0f}" fill="#2a1a10" stroke="#c7953f" stroke-width="3"/>' for k in range(3))
            + "".join(f'<path d="M{x + w * .83} {y + h * (.7 + k * .03):.0f} H{x + w * .91}" stroke="#2a1a10" stroke-width="3"/>' for k in range(4))
            + '</g>')
