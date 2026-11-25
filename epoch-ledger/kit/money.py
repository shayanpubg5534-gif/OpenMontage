"""Recognisable money and the paperwork around it — illustrated, screen-space SVG with animation ids.

  bill(uid, s)                      one banknote (green, portrait oval, denomination), for flying bills
  cash_pile(uid, x, y, n, cols)     physical cash on hand: n banknote bundles stacked in layers ({uid}-bd{k});
                                    FM.pileTo() removes / adds bundles so the pile always matches the Ledger
  wire_slip(uid, x, y, ...)         incoming wire confirmation (capital *received*) with a RECEIVED stamp
  term_sheet(uid, ...)              the funding *agreement* (signature line {uid}-sig to draw on)
  commercial(uid, sx, sy, sw, sh)   a period TV commercial: doorstep delivery → end card (logo, tagline, URL, offer)
Original implementation; deterministic.
"""
from __future__ import annotations

INK = "#1b1410"
GREEN, GREEN_D, GREEN_L = "#8dbb84", "#3e6a3a", "#c8e2bf"


def bill_defs(uid: str) -> str:
    return (f'<symbol id="{uid}-bill" viewBox="-60 -26 120 52" overflow="visible">'
            f'<rect x="-58" y="-24" width="116" height="48" rx="4" fill="{GREEN}" stroke="{GREEN_D}" stroke-width="3"/>'
            f'<rect x="-50" y="-17" width="100" height="34" rx="3" fill="none" stroke="{GREEN_D}" stroke-width="1.6" opacity=".7"/>'
            f'<ellipse cx="0" cy="0" rx="14" ry="15" fill="{GREEN_L}" stroke="{GREEN_D}" stroke-width="2"/>'
            f'<circle cx="0" cy="-3" r="5" fill="{GREEN_D}" opacity=".6"/><path d="M-8 9 Q0 2 8 9" fill="{GREEN_D}" opacity=".6"/>'
            f'<text x="-44" y="-6" font-family="Inter" font-weight="800" font-size="12" fill="{GREEN_D}">100</text>'
            f'<text x="44" y="16" text-anchor="end" font-family="Inter" font-weight="800" font-size="12" fill="{GREEN_D}">100</text>'
            f'<text x="34" y="-6" font-family="Fraunces" font-weight="800" font-size="16" fill="{GREEN_D}">$</text></symbol>')


def bundle_svg(x: float, y: float, w: float = 150, uid: str = "", hidden: bool = False) -> str:
    """One strapped bundle of notes, three-quarter view from slightly above. (x, y) = front-top-left corner."""
    h, dx, dy = w * .2, w * .16, w * .2
    top = f"M{x} {y} L{x + w} {y} L{x + w + dx} {y - dy} L{x + dx} {y - dy}Z"
    edges = "".join(f'<path d="M{x} {y + h * k / 6:.1f} H{x + w}" stroke="{"#eef4e8" if k % 2 else "#a8c8a0"}" stroke-width="2"/>' for k in range(1, 6))
    cx, cy = x + w / 2 + dx / 2, y - dy / 2
    gid = f' id="{uid}"' if uid else ""
    return (f'<g{gid}{" opacity=" + chr(34) + "0" + chr(34) if hidden else ""}>'
            f'<path d="M{x + w} {y} L{x + w + dx} {y - dy} L{x + w + dx} {y - dy + h} L{x + w} {y + h}Z" fill="#6f9a68" stroke="{INK}" stroke-width="2.4"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#b9d6b0" stroke="{INK}" stroke-width="2.4"/>{edges}'
            f'<path d="{top}" fill="{GREEN}" stroke="{INK}" stroke-width="2.4"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{w * .1:.1f}" ry="{dy * .32:.1f}" fill="{GREEN_L}" stroke="{GREEN_D}" stroke-width="1.6"/>'
            f'<path d="M{x + w * .52} {y} L{x + w * .52 + dx} {y - dy} L{x + w * .66 + dx} {y - dy} L{x + w * .66} {y}Z" fill="#efe2c2" stroke="{INK}" stroke-width="1.6"/>'
            f'<rect x="{x + w * .52}" y="{y}" width="{w * .14}" height="{h}" fill="#e6d6ae" stroke="{INK}" stroke-width="1.6"/></g>')


def cash_pile(uid: str, x: float, y: float, n: int, cols: int = 4, w: float = 150, capacity: int | None = None) -> str:
    """Bundles stacked in layers (cols x 2 per layer). Bundles >= n start hidden (room to grow up to `capacity`).
    Draw order is back-to-front, bottom-to-top; FM.pileTo removes from the top/front first."""
    cap = capacity or n
    h, dx, dy = w * .2, w * .16, w * .2
    per = cols * 2
    out = [f'<g id="{uid}" data-n="{n}" data-cap="{cap}">',
           f'<ellipse cx="{x + cols * w / 2 + dx}" cy="{y + h + 14}" rx="{cols * w * .62}" ry="{w * .22}" fill="#000" opacity=".3"/>']
    for k in range(cap):
        layer, i = divmod(k, per)
        row, col = divmod(i, cols)          # row 0 = back
        bx = x + col * (w + 4) + (1 - row) * dx
        by = y - layer * h - (1 - row) * dy
        out.append(bundle_svg(bx, by, w, f"{uid}-bd{k}", hidden=k >= n))
    return "".join(out) + "</g>"


def wire_slip(uid: str, x: float, y: float, amount: str, sender: str, receiver: str, bank: str = "First National Bank", w: float = 620) -> str:
    h = w * .62
    return (f'<g id="{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f4f6f2" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h * .2}" rx="10" fill="#1f3a5a"/><rect x="{x}" y="{y + h * .12}" width="{w}" height="{h * .08}" fill="#1f3a5a"/>'
            f'<text x="{x + 28}" y="{y + h * .14}" font-family="Inter" font-weight="800" font-size="{w * .05:.0f}" fill="#fff">{bank} — INCOMING WIRE</text>'
            f'<text x="{x + 28}" y="{y + h * .36}" font-family="Inter" font-weight="700" font-size="{w * .042:.0f}" fill="#5a6470">FROM</text>'
            f'<text x="{x + 150}" y="{y + h * .36}" font-family="Inter" font-weight="800" font-size="{w * .046:.0f}" fill="{INK}">{sender}</text>'
            f'<text x="{x + 28}" y="{y + h * .5}" font-family="Inter" font-weight="700" font-size="{w * .042:.0f}" fill="#5a6470">TO</text>'
            f'<text x="{x + 150}" y="{y + h * .5}" font-family="Inter" font-weight="800" font-size="{w * .046:.0f}" fill="{INK}">{receiver}</text>'
            f'<text x="{x + 28}" y="{y + h * .74}" font-family="Inter" font-weight="700" font-size="{w * .042:.0f}" fill="#5a6470">AMOUNT</text>'
            f'<text x="{x + 150}" y="{y + h * .76}" font-family="Fraunces" font-weight="800" font-size="{w * .08:.0f}" fill="#2a6a2a">{amount}</text>'
            f'<g id="{uid}-stamp" opacity="0" transform="rotate(-9 {x + w * .8} {y + h * .4})"><rect x="{x + w * .64}" y="{y + h * .28}" width="{w * .34}" height="{h * .22}" rx="8" fill="#f4f6f2" stroke="#2a8a3a" stroke-width="8"/>'
            f'<text x="{x + w * .82}" y="{y + h * .44}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{w * .07:.0f}" fill="#2a8a3a">RECEIVED</text></g></g>')


def term_sheet(uid: str, company: str = "BigCart.com", investor: str = "Summit Ventures", amount: str = "$20M") -> str:
    """700x560 document (map with S3.art or place in 2D): title, parties, amount, two signature lines; {uid}-sig draws on."""
    return ('<rect width="700" height="560" fill="#f6f0e2" stroke="#1b1410" stroke-width="6"/>'
            '<text x="350" y="80" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="56" fill="#1b1410">TERM SHEET</text>'
            f'<text x="350" y="140" text-anchor="middle" font-family="Inter" font-weight="800" font-size="34" fill="#2e5ab0">{company}  ·  {investor}</text>'
            f'<text x="350" y="200" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="#2a6a2a">Investment: {amount}</text>'
            + "".join(f'<rect x="70" y="{240 + k * 34}" width="{560 - (k * 71) % 170}" height="12" fill="#9a9080"/>' for k in range(4))
            + '<path d="M80 480 H310 M390 480 H620" stroke="#1b1410" stroke-width="4"/>'
            '<text x="80" y="510" font-family="Inter" font-weight="700" font-size="20" fill="#5a5048">for the company</text>'
            '<text x="390" y="510" font-family="Inter" font-weight="700" font-size="20" fill="#5a5048">for the investor</text>'
            '<path d="M100 470 C120 430 140 500 160 455 S200 440 215 468 S260 450 290 462" fill="none" stroke="#1f3a7a" stroke-width="5" stroke-linecap="round"/>'
            f'<path id="{uid}-sig" d="M410 470 C425 425 450 500 470 452 S505 438 520 466 C535 480 560 440 600 458" fill="none" stroke="#1f3a7a" stroke-width="5" stroke-linecap="round"/>')


def commercial(uid: str, sx: float, sy: float, sw: float, sh: float) -> str:
    """A 1999-style TV spot inside a screen rect: a courier hands a BigCart parcel to a delighted customer at her door,
    then the end card (logo, tagline, URL, offer). Ids: {uid}-scene, {uid}-parcel, {uid}-door, {uid}-card."""
    k = sw / 600
    def P(x, y): return f"{sx + x * k:.1f} {sy + y * k:.1f}"
    scene = (f'<g id="{uid}-scene"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#8fd0f0"/>'
             f'<rect x="{sx}" y="{sy + sh * .62}" width="{sw}" height="{sh * .38}" fill="#7ab86a"/>'
             f'<path d="M{P(300, 70)} L{P(470, 70)} L{P(470, 290)} L{P(300, 290)}Z" fill="#f4e6c8" stroke="{INK}" stroke-width="3"/>'          # house front
             f'<path d="M{P(285, 75)} L{P(385, 10)} L{P(485, 75)}Z" fill="#b8503a" stroke="{INK}" stroke-width="3"/>'
             f'<rect id="{uid}-door" x="{sx + 350 * k:.1f}" y="{sy + 160 * k:.1f}" width="{60 * k:.1f}" height="{130 * k:.1f}" fill="#7a3a2a" stroke="{INK}" stroke-width="3"/>'
             # customer at the door
             f'<g><circle cx="{sx + 380 * k:.1f}" cy="{sy + 186 * k:.1f}" r="{15 * k:.1f}" fill="#e8b48c" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M{P(366, 186)} Q{P(380, 160)} {P(396, 186)}" fill="#6a3a2a"/><path d="M{P(373, 192)} Q{P(380, 198)} {P(387, 192)}" stroke="{INK}" stroke-width="2" fill="none"/>'
             f'<rect x="{sx + 365 * k:.1f}" y="{sy + 202 * k:.1f}" width="{30 * k:.1f}" height="{60 * k:.1f}" rx="6" fill="#d9503f" stroke="{INK}" stroke-width="2"/></g>'
             # courier with cap
             f'<g><circle cx="{sx + 250 * k:.1f}" cy="{sy + 184 * k:.1f}" r="{15 * k:.1f}" fill="#c98f63" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M{P(234, 180)} Q{P(250, 160)} {P(266, 180)}Z" fill="#2e5ab0" stroke="{INK}" stroke-width="2"/>'
             f'<rect x="{sx + 234 * k:.1f}" y="{sy + 200 * k:.1f}" width="{32 * k:.1f}" height="{64 * k:.1f}" rx="6" fill="#2e5ab0" stroke="{INK}" stroke-width="2"/></g>'
             f'<g id="{uid}-parcel"><rect x="{sx + 262 * k:.1f}" y="{sy + 212 * k:.1f}" width="{50 * k:.1f}" height="{36 * k:.1f}" fill="#c9a06a" stroke="{INK}" stroke-width="2.4"/>'
             f'<rect x="{sx + 272 * k:.1f}" y="{sy + 222 * k:.1f}" width="{30 * k:.1f}" height="{12 * k:.1f}" fill="#2e5ab0"/></g>'
             f'<path d="M{P(40, 230)} h{120 * k:.1f} v{-36 * k:.1f} l{24 * k:.1f} {-10 * k:.1f} v{46 * k:.1f}" fill="#f4f6f2" stroke="{INK}" stroke-width="3"/>'   # delivery van
             f'<text x="{sx + 60 * k:.1f}" y="{sy + 222 * k:.1f}" font-family="Fraunces" font-weight="800" font-size="{16 * k:.1f}" fill="#2e5ab0">BigCart</text>'
             f'<circle cx="{sx + 70 * k:.1f}" cy="{sy + 236 * k:.1f}" r="{10 * k:.1f}" fill="{INK}"/><circle cx="{sx + 150 * k:.1f}" cy="{sy + 236 * k:.1f}" r="{10 * k:.1f}" fill="{INK}"/></g>')
    card = (f'<g id="{uid}-card" opacity="0"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#2b4f9e"/>'
            f'<text x="{sx + sw / 2}" y="{sy + sh * .36}" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="{sw * .13:.0f}" fill="#fff">BigCart.com</text>'
            f'<text x="{sx + sw / 2}" y="{sy + sh * .56}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{sw * .055:.0f}" fill="#cfe0ff">Everything. Delivered to your door.</text>'
            f'<rect x="{sx + sw * .27}" y="{sy + sh * .66}" width="{sw * .46}" height="{sh * .16}" rx="{sh * .04:.0f}" fill="#ffd56a"/>'
            f'<text x="{sx + sw / 2}" y="{sy + sh * .775}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{sw * .055:.0f}" fill="#2a1a0a">FREE SHIPPING</text></g>')
    return scene + card
