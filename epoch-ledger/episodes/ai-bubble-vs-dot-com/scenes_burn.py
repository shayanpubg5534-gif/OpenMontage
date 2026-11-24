"""Redesign preview — "The cash furnace" (c03_03–c03_10, 3:30–4:14).

Scene brief
-----------
Message: rising stock prices hid businesses that spent far more than they earned; they survived only while
investors kept supplying capital; when confidence broke, prices fell, the capital stopped and operations died.
Audience must understand: cash out (advertising, staff, infrastructure) ≫ cash in (revenue); the gap is covered
by investor capital; the company's runway depends on that pipe staying open; confidence closes the valve.
One world, filmed by a 2D camera (mCamera): a cutaway dot-com building (billboard roof, office floor, server
room, lobby with the company's glass cash tank), a venture-capital tower across the street joined to the tank by
a capital pipe, and a market board on the skyline.
Cause → mechanism → consequence:
  "rising stock prices"        board line climbs over the dusk skyline (camera on the board)
  "beneath" / "struggling"     crane down into the building: the cash tank is barely holding level
  "advertising" / "employees" / "infrastructure"   coins climb the riser to each outlet as it is named;
                                each outlet works (billboard spotlights, staff at desks, servers blinking)
  "without earning enough revenue"   one small trickle of order revenue into the tank; monthly bars show the gap
  "investors … provide capital"      pull back: capital pours across the street through the pipe; runway fills
  "confidence … disappear"     night falls on the street; the confidence gauge drops
  "worry … valuations … profitability"   inside the boardroom: valuation bar towers over a loss; worried partners
  "Stock prices started falling"         the board line breaks and falls red
  "external financing … existential threat"   the valve closes, the pipe empties, the tank drains, runway → red
  "no longer finance their operations"        outlets go dark one by one; staff leave with boxes
All money scales are illustrative; no figures are shown.
"""
from kit.characters import OUT
from kit.rig import crowd_look, rig_svg
from floor import place
from kit.assemble import Scene
from timeline import L, W

O = OUT
WX, WY = 3840, 2160


def look(i, **o):
    c = crowd_look(i)
    c.update(o)
    return c


def staff(i):
    j = [("#4a6a8a", "#3a5470", "#6a8aaa"), ("#8a4a5a", "#6e3a48", "#aa6a7a"), ("#5a7a4a", "#465f3a", "#7a9a6a"),
         ("#c98a3a", "#a06e2e", "#e0aa5a"), ("#3a3a4a", "#2a2a38", "#5a5a6a"), ("#7a5aa0", "#604880", "#9a7ac0")][i % 6]
    return look(90 + i * 3, jacket=j[0], jacket_sh=j[1], jacket_hi=j[2], tie=None, badge=True, shirt=["#e8e2d4", "#d8e4ee", "#f4ead5"][i % 3])


def investor(i):
    return look(120 + i * 5, jacket=["#22262e", "#2e3442", "#3a3028"][i], jacket_sh="#16181e", jacket_hi="#4a5060",
                tie=["#7a1f2a", "#1f3a7a", "#5a4a1a"][i], badge=False, glasses=i == 1)


def bust(p, c, x, y, w, prop=None, flip=False):
    return place(rig_svg(p, c, "bust", prop_front=prop), x, y, w, flip=flip).replace(f"height:{w * 500 / 300:.0f}px", f"height:{w * 360 / 300:.0f}px")


# ── world art ─────────────────────────────────────────────────────────────────────────────────
def sky():
    stars = "".join(f'<circle class="bn-star" cx="{(i * 397) % 5400 - 800}" cy="{(i * 151) % 700 - 500}" r="{1.5 + (i % 3)}" fill="#fff" opacity="0"/>' for i in range(80))
    return f"""<svg viewBox="-800 -700 5440 3060" style="position:absolute;left:-800px;top:-700px;width:5440px;height:3060px" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="bn-dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2348"/><stop offset=".45" stop-color="#8a4a6a"/>
  <stop offset=".75" stop-color="#e88a5a"/><stop offset="1" stop-color="#f6c27a"/></linearGradient>
  <radialGradient id="bn-sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffe2a8"/><stop offset="1" stop-color="#ffe2a8" stop-opacity="0"/></radialGradient></defs>
 <rect x="-800" y="-700" width="5440" height="3060" fill="url(#bn-dusk)"/>
 <circle id="bn-sunc" cx="3000" cy="1250" r="420" fill="url(#bn-sun)"/>{stars}
 <g id="bn-clouds" fill="#f4d6c0" opacity=".35">{''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * .22:.0f}"/>' for x, y, rx in [(200, 240, 380), (1500, 120, 300), (2900, 300, 420), (4200, 160, 340)])}</g>
</svg>"""


def skyline(depth_id, y0, color, lit, n, seed, h0, h1):
    out = []
    for i in range(n):
        w = 140 + (i * 53 + seed) % 160
        h = h0 + (i * 97 + seed * 3) % (h1 - h0)
        x = -800 + i * 5440 / n + (i * 31 % 40)
        out.append(f'<rect x="{x:.0f}" y="{y0 - h}" width="{w}" height="{h + 600}" fill="{color}"/>')
        for r in range(2, h // 46):
            for c in range(1, w // 34):
                if (i * 7 + r * 3 + c * 5 + seed) % 5 < 2:
                    out.append(f'<rect class="{depth_id}-win" x="{x + c * 32:.0f}" y="{y0 - h + r * 44}" width="14" height="20" fill="{lit}" opacity=".75"/>')
    return (f'<svg viewBox="-800 0 5440 2160" style="position:absolute;left:-800px;top:0;width:5440px;height:2160px" xmlns="http://www.w3.org/2000/svg">'
            f'{"".join(out)}</svg>')


def board():
    """Mid-ground: tower with the market LED board (rising line, then the break)."""
    tape = "   ".join(f"{t} ▲{1 + i % 7}¼" for i, t in enumerate(["NETZ", "BYTE", "WEBQ", "CLIK", "PORT", "SURF", "CHAT", "HOST"] * 3))
    grid = "".join(f'<path d="M1790 {230 + k * 60} H2510" stroke="#173a2a" stroke-width="2"/>' for k in range(6))
    return f"""<svg viewBox="0 0 3840 2160" style="position:absolute;left:0;top:0;width:3840px;height:2160px;overflow:visible" xmlns="http://www.w3.org/2000/svg">
 <rect x="1660" y="60" width="980" height="1900" fill="#2a2638"/><rect x="1660" y="60" width="980" height="1900" fill="url(#bn-glassv)" opacity=".5"/>
 <defs><linearGradient id="bn-glassv" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4a4a6a"/><stop offset=".5" stop-color="#2a2a40"/><stop offset="1" stop-color="#3a3a58"/></linearGradient></defs>
 {''.join(f'<path d="M{1700 + k * 70} 640 V1960" stroke="#3a3650" stroke-width="4"/>' for k in range(14))}
 <rect x="1720" y="150" width="860" height="460" rx="10" fill="#050d09" stroke="#3a4a42" stroke-width="10"/>{grid}
 <text x="1800" y="214" font-family="Inter" font-weight="800" font-size="34" fill="#7cff9b" letter-spacing="4" data-deco="1">TECH STOCKS</text>
 <path id="bn-rise" d="M1790 560 L1880 545 L1960 520 L2040 528 L2120 480 L2200 450 L2270 400 L2340 330 L2400 300 L2450 250" stroke="#7cff9b" stroke-width="9" fill="none" stroke-linejoin="round"/>
 <path id="bn-fall" d="M2450 250 L2470 330 L2490 300 L2510 420 L2530 470 L2550 560" stroke="#ff5a46" stroke-width="10" fill="none" stroke-linejoin="round" opacity="0"/>
 <circle id="bn-dot" cx="2450" cy="250" r="14" fill="#7cff9b"/>
 <rect x="1720" y="610" width="860" height="56" fill="#120c06"/>
 <g style="clip-path:inset(0)"><text id="bn-tape" x="1730" y="650" font-family="Inter" font-weight="800" font-size="34" fill="#f2a541" data-deco="1">{tape}</text></g>
</svg>"""


def startup():
    """Cutaway dot-com building: roof billboard, office floor, server room, lobby with the cash tank."""
    X0, X1 = 200, 1650
    brick = '<pattern id="bn-brick" width="48" height="24" patternUnits="userSpaceOnUse"><rect width="48" height="24" fill="#8a4a36"/><path d="M0 12 H48 M0 24 H48 M24 0 V12 M0 12 V24" stroke="#6a3426" stroke-width="2"/></pattern>'
    desks = "".join(f'<g transform="translate({330 + k * 200} 0)"><rect x="-20" y="968" width="170" height="16" fill="#8a6a48"/>'
                    f'<rect x="20" y="902" width="74" height="60" rx="6" fill="#d8cfb6" stroke="{O}" stroke-width="3"/>'
                    f'<rect class="bn-crt" x="28" y="908" width="58" height="44" fill="#1f6a8a"/><rect x="46" y="962" width="22" height="8" fill="#a89c80"/></g>' for k in range(6))
    racks = "".join(f'<g transform="translate({320 + k * 175} 1110)"><rect width="130" height="246" rx="6" fill="#1a2230" stroke="#0a0e14" stroke-width="4"/>'
                    + "".join(f'<rect x="10" y="{10 + r * 23}" width="110" height="18" fill="#26303e"/><rect class="bn-led" x="104" y="{15 + r * 23}" width="10" height="7" fill="#38d6ff"/>' for r in range(10))
                    + '</g>' for k in range(6))
    lights = "".join(f'<g class="bn-lamp"><rect x="{300 + k * 230}" y="{yy}" width="120" height="8" fill="#fff6d8"/>'
                     f'<path d="M{300 + k * 230} {yy + 8} L{420 + k * 230} {yy + 8} L{480 + k * 230} {yy + 160} L{240 + k * 230} {yy + 160}Z" fill="#fff2c8" opacity=".14"/></g>'
                     for yy in (780, 1380) for k in range(6))
    return f"""<svg viewBox="0 0 3840 2160" style="position:absolute;left:0;top:0;width:3840px;height:2160px;overflow:visible" xmlns="http://www.w3.org/2000/svg">
 <defs>{brick}<linearGradient id="bn-glass" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#bfe8ff" stop-opacity=".35"/><stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#bfe8ff" stop-opacity=".4"/></linearGradient>
  <clipPath id="bn-tankclip"><rect x="830" y="1440" width="280" height="470" rx="60"/></clipPath></defs>
 <!-- billboard on the roof -->
 <g id="bn-bill"><path d="M420 640 V740 M1380 640 V740 M900 640 V740" stroke="#3a3a40" stroke-width="16"/>
  <rect x="330" y="300" width="1140" height="340" rx="8" fill="#f4ead5" stroke="{O}" stroke-width="8"/>
  <rect x="350" y="320" width="1100" height="300" fill="#2e5ab0"/>
  <g transform="translate(520 470)"><path d="M0 -110 C60 -60 60 60 0 110 C-60 60 -60 -60 0 -110Z" fill="#f4ead5" stroke="{O}" stroke-width="6"/><circle cy="-20" r="28" fill="#5fb3e6" stroke="{O}" stroke-width="5"/>
   <path d="M-40 70 L-90 130 L-30 100Z M40 70 L90 130 L30 100Z" fill="#d9503f" stroke="{O}" stroke-width="5"/><path id="bn-flame" d="M-22 112 Q0 190 22 112Z" fill="#f2a541"/></g>
  <text x="980" y="440" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="86" fill="#fff">BigCart.com</text>
  <text x="980" y="520" text-anchor="middle" font-family="Inter" font-weight="700" font-size="42" fill="#cfe2ff">Everything. Delivered. Free.</text>
  <g id="bn-spots">{''.join(f'<path d="M{x} 660 L{x - 120} 300 L{x + 120} 300Z" fill="#fff6c8" opacity=".22"/><rect x="{x - 26}" y="650" width="52" height="30" rx="8" fill="#2a2a2e"/>' for x in (520, 900, 1280))}</g></g>
 <!-- shell -->
 <rect x="{X0}" y="740" width="{X1 - X0}" height="1210" fill="#e9dcc0"/>
 <rect x="{X0 + 60}" y="760" width="{X1 - X0 - 120}" height="300" fill="#efe2c4"/>
 {''.join(f'<rect x="{360 + k * 300}" y="790" width="210" height="150" fill="#f6c27a" stroke="#6a5a48" stroke-width="6"/><rect x="{360 + k * 300}" y="790" width="210" height="150" fill="url(#bn-glass)"/>' for k in range(4))}
 <rect x="{X0 + 60}" y="1060" width="{X1 - X0 - 120}" height="300" fill="#1a2436"/>
 <rect x="{X0 + 60}" y="1360" width="{X1 - X0 - 120}" height="590" fill="#e4d6b8"/>
 {lights}
 <!-- office floor -->
 <rect x="300" y="822" width="300" height="56" fill="#d9503f"/><text x="450" y="860" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#fff" data-deco="1">WE'RE HIRING!</text>
 <g transform="translate(1440 960)"><rect width="140" height="70" fill="#3a7a3a" stroke="{O}" stroke-width="4"/>{''.join(f'<path d="M{20 + k * 25} -10 V80" stroke="#aaa" stroke-width="4"/>' for k in range(5))}</g>
 <!-- server room -->
 {racks}
 <!-- lobby -->
 <rect x="300" y="1400" width="420" height="70" fill="#2e5ab0"/><text x="510" y="1448" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="40" fill="#fff" data-deco="1">BigCart.com</text>
 <rect x="320" y="1760" width="300" height="140" fill="#8a6a48" stroke="{O}" stroke-width="5"/>
 <g><rect x="1250" y="1620" width="330" height="20" fill="#6a5a48"/>{''.join(f'<rect x="{1270 + k * 64}" y="{1580 - (k % 2) * 30}" width="54" height="{40 + (k % 2) * 30}" fill="#c9a06a" stroke="{O}" stroke-width="3"/>' for k in range(5))}
  <rect x="1250" y="1790" width="330" height="22" fill="#5a5a60"/><g class="bn-lbl"><rect x="1340" y="1500" width="150" height="40" rx="8" fill="#1b1410"/><text x="1415" y="1530" text-anchor="middle" font-family="Inter" font-weight="800" font-size="28" fill="#7fdc8a" data-read="1">ORDERS</text></g></g>
 <rect x="230" y="1700" width="110" height="250" fill="#3a2a1e" stroke="{O}" stroke-width="5"/>
 <!-- cash tank -->
 <g id="bn-tank"><rect x="830" y="1440" width="280" height="470" rx="60" fill="#0e1a16" stroke="#cfd6dc" stroke-width="10"/>
  <g clip-path="url(#bn-tankclip)"><rect id="bn-cash" x="830" y="1700" width="280" height="260" fill="#e0b040"/>
   {''.join(f'<ellipse class="bn-coinl" cx="{860 + (k * 47) % 240}" cy="{1720 + (k * 37) % 180}" rx="22" ry="8" fill="#f6d77a" stroke="#a07a20" stroke-width="2"/>' for k in range(16))}</g>
  <rect x="830" y="1440" width="280" height="470" rx="60" fill="url(#bn-glass)"/>
  <rect x="900" y="1912" width="140" height="30" fill="#5a5a60"/><g class="bn-lbl"><rect x="890" y="1388" width="160" height="44" rx="8" fill="#1b1410"/><text x="970" y="1420" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#f2c66d" data-read="1">CASH</text></g></g>
 <!-- slabs and walls -->
 {''.join(f'<rect x="{X0}" y="{y}" width="{X1 - X0}" height="24" fill="#8a8478"/>' for y in (740, 1048, 1348, 1940))}
 <rect x="{X0}" y="740" width="60" height="1210" fill="url(#bn-brick)"/><rect x="{X1 - 60}" y="740" width="60" height="1210" fill="url(#bn-brick)"/>
 <!-- riser and branches (coin routes) -->
 <g stroke="#b8892e" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="M1110 1520 H1540 V700 H1380"/><path d="M1540 1000 H1420"/><path d="M1540 1290 H1320"/></g>
 <g stroke="#f2c66d" stroke-width="6" fill="none" opacity=".5"><path d="M1110 1520 H1540 V700 H1380"/></g>
 <path id="bn-p-ad" d="M1100 1520 H1540 V690 H1300 V640" fill="none" stroke="none"/>
 <path id="bn-p-staff" d="M1100 1520 H1540 V1000 H1360" fill="none" stroke="none"/>
 <path id="bn-p-infra" d="M1100 1520 H1540 V1290 H1280" fill="none" stroke="none"/>
 <path id="bn-p-rev" d="M1300 1800 Q1200 1760 1110 1760" fill="none" stroke="#5fb36a" stroke-width="6" stroke-dasharray="10 10"/>
</svg>"""


def tower():
    """Venture-capital tower with the boardroom cutaway, the capital pipe and its valve; the street."""
    mull = "".join(f'<path d="M{2330 + k * 64} 760 V1950" stroke="#5a7a9a" stroke-width="3" opacity=".6"/>' for k in range(19))
    wins = "".join(f'<rect class="bn-twin" x="{2340 + c * 64}" y="{780 + r * 60}" width="44" height="34" fill="#ffe3a3" opacity="{.15 + ((r * 7 + c * 3) % 5) * .14:.2f}"/>'
                   for r in range(5) for c in range(18) if (r * 5 + c) % 4)
    return f"""<svg viewBox="0 0 3840 2160" style="position:absolute;left:0;top:0;width:3840px;height:2160px;overflow:visible" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="bn-tglass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7aa8d0"/><stop offset=".5" stop-color="#3a5a80"/><stop offset="1" stop-color="#22385a"/></linearGradient></defs>
 <rect x="2300" y="720" width="1260" height="1230" fill="url(#bn-tglass)"/>{mull}{wins}
 <rect x="2300" y="720" width="1260" height="40" fill="#1e2a3a"/>
 <text x="2930" y="700" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="56" fill="#f3e3c3" data-deco="1">SUMMIT VENTURES</text>
 <!-- boardroom cutaway -->
 <rect x="2400" y="1090" width="1060" height="370" fill="#6a4630"/><radialGradient id="bn-warm" cx=".6" cy=".1" r=".9"><stop offset="0" stop-color="#ffe0a8" stop-opacity=".45"/><stop offset="1" stop-color="#ffe0a8" stop-opacity="0"/></radialGradient><rect x="2400" y="1090" width="1060" height="370" fill="url(#bn-warm)"/>
 {''.join(f'<path d="M{2400 + k * 106} 1090 V1460" stroke="#4a2e1e" stroke-width="4"/>' for k in range(10))}
 <rect x="2440" y="1120" width="420" height="260" rx="8" fill="#0b1220" stroke="#8f9bb0" stroke-width="6"/>
 <path d="M2470 1340 H2830" stroke="#8fa3b8" stroke-width="3"/>
 <rect id="bn-val" x="2520" y="1340" width="110" height="0" fill="#f2c66d"/><rect id="bn-prof" x="2690" y="1340" width="110" height="0" fill="#d9503f"/>
 <text x="2575" y="1370" text-anchor="middle" font-family="Inter" font-weight="800" font-size="22" fill="#e8f3ff">VALUE</text>
 <text x="2745" y="1370" text-anchor="middle" font-family="Inter" font-weight="800" font-size="22" fill="#e8f3ff">PROFIT</text>
 <rect x="2380" y="1458" width="1100" height="22" fill="#8a8478"/>
 <!-- street -->
 <rect x="-400" y="1950" width="4640" height="210" fill="#2e2c32"/><rect x="-400" y="1950" width="4640" height="26" fill="#8a8478"/>
 {''.join(f'<rect x="{x}" y="2060" width="90" height="10" fill="#e8e2c8" opacity=".7"/>' for x in range(-380, 4240, 200))}
 {''.join(f'<g><rect x="{x}" y="1700" width="12" height="250" fill="#2a2a2e"/><path d="M{x + 6} 1700 q30 -10 50 6" stroke="#2a2a2e" stroke-width="10" fill="none"/>'
          f'<circle class="bn-lampg" cx="{x + 56}" cy="1712" r="12" fill="#ffe3a3"/><path class="bn-lampg" d="M{x + 56} 1716 L{x + 6} 1950 L{x + 106} 1950Z" fill="#ffe3a3" opacity=".12"/></g>' for x in (1720, 2150, 3650))}
 <!-- capital pipe -->
 <g stroke-linecap="round"><path d="M2300 1560 H1650" stroke="#8a6a1c" stroke-width="40"/><path d="M2300 1560 H1650" stroke="#d4a24c" stroke-width="28"/>
  <path d="M2300 1552 H1650" stroke="#f2d48a" stroke-width="6" opacity=".7"/>
  {''.join(f'<rect x="{x}" y="1528" width="16" height="64" fill="#8a6a1c"/>' for x in (1700, 1900, 2100, 2260))}</g>
 <path id="bn-p-cap" d="M2300 1560 H1650 L1110 1560" fill="none" stroke="none"/>
 <g id="bn-valve" transform="translate(2000 1560)"><circle r="58" fill="none" stroke="#c03a2a" stroke-width="14"/>
  {''.join(f'<path d="M0 0 L{58 * __import__("math").cos(k * 1.047):.1f} {58 * __import__("math").sin(k * 1.047):.1f}" stroke="#c03a2a" stroke-width="10"/>' for k in range(6))}
  <circle r="14" fill="#8a2a1e"/></g>
 <rect x="1984" y="1560" width="32" height="70" fill="#8a6a1c"/>
</svg>"""


def cars():
    return "".join(f'<div class="bn-car" id="bn-car{i}" style="position:absolute;left:{x}px;top:{2000 + (i % 2) * 70}px;width:220px;height:70px">'
                   f'<svg viewBox="0 0 220 70" width="220" height="70"><rect x="10" y="20" width="200" height="38" rx="12" fill="{c}" stroke="{O}" stroke-width="4"/>'
                   f'<path d="M50 20 L80 2 H150 L175 20Z" fill="{c}" stroke="{O}" stroke-width="4"/><circle cx="55" cy="60" r="12" fill="#111"/><circle cx="165" cy="60" r="12" fill="#111"/>'
                   f'<circle cx="208" cy="36" r="6" fill="#fff3c0"/></svg></div>'
                   for i, (x, c) in enumerate([(-300, "#c9a06a"), (1200, "#3a6ab0"), (2600, "#7a3a3a"), (3900, "#5a7a5a")]))


CSS = """
#bn-world{position:absolute;left:0;top:0;width:3840px;height:2160px}
#bn-world > div{position:absolute;left:0;top:0;width:3840px;height:2160px}
.bn-hud{position:absolute;right:56px;top:56px;width:700px;padding:24px 30px;border-radius:16px;background:rgba(14,12,20,.86);
  border:3px solid rgba(242,198,109,.8);color:#f3e3c3;font:800 34px Inter;opacity:0;box-shadow:0 12px 40px rgba(0,0,0,.45)}
.bn-hud h4{margin:0 0 16px;font:800 42px Fraunces;color:#fff}.bn-hud h4 small{font:700 22px Inter;letter-spacing:.12em;opacity:.7;margin-left:10px}
.bn-row{display:flex;align-items:center;gap:14px;height:58px}.bn-row span.k{width:170px}
.bn-bar{display:flex;height:34px;border-radius:6px;overflow:hidden;background:rgba(255,255,255,.08);flex:1}
.bn-seg{height:100%;width:0}
"""


def build():
    l = {k: L(k) for k in ["c03_03", "c03_04", "c03_05", "c03_06", "c03_07", "c03_08", "c03_09", "c03_10"]}
    s, e = l["c03_03"][0] - .5, l["c03_10"][1] + .35
    w = lambda word, line: W(word, line)
    t_rise, t_bene, t_bus, t_strug = w("rising", "c03_03"), w("beneath", "c03_03"), w("businesses", "c03_03"), w("struggling", "c03_03")
    t_ad, t_emp, t_inf = w("advertising", "c03_04"), w("employees", "c03_04"), w("infrastructure", "c03_04")
    t_earn, t_rev, t_sust = w("earning", "c03_04"), w("revenue", "c03_04"), w("sustain", "c03_04")
    t_surv, t_invs, t_prov, t_cap = w("survival", "c03_05"), w("investors", "c03_05"), w("provide", "c03_05"), w("capital", "c03_05")
    t_conf, t_dis = w("confidence", "c03_06"), w("disappear", "c03_06")
    t_inv7, t_worry, t_val, t_prof = w("Investors", "c03_07"), w("worry", "c03_07"), w("valuations", "c03_07"), w("profitability", "c03_07")
    t_stock, t_fall = w("Stock", "c03_08"), w("falling", "c03_08")
    t_ext, t_fin, t_decl, t_exist = w("external", "c03_09"), w("financing", "c03_09"), w("declining", "c03_09"), w("existential", "c03_09")
    t_without, t_fresh, t_fin2, t_ops = w("Without", "c03_10"), w("fresh", "c03_10"), w("finance", "c03_10"), w("operations", "c03_10")

    chars = []
    # office floor: six staff at desks (busts; desk fronts are drawn over them)
    for k in range(6):
        chars.append(bust(f"bns{k}", staff(k), 315 + k * 200, 812, 150, flip=k % 2 == 1))
    desk_fronts = "".join(f'<rect x="{310 + k * 200}" y="976" width="170" height="84" fill="#7a5a3a" stroke="{O}" stroke-width="3"/>' for k in range(6))
    # two staff standing (they leave at the end) — wrap for walking
    for k, x in enumerate((1300, 1420)):
        chars.append(f'<div id="bnw{k}-wrap" style="position:absolute;inset:0">' + place(rig_svg(f"bnw{k}", staff(k + 6), "full", prop_front=None), x, 820, 140, flip=True) + '</div>')
    # server technician and lobby staff
    chars.append(place(rig_svg("bnt", staff(9), "full", prop_front="tablet"), 1330, 1112, 140))
    chars.append(bust("bnr", staff(10), 400, 1600, 160))
    chars.append(place(rig_svg("bnk", staff(11), "full", prop_front="box"), 1300, 1555, 150, flip=True))
    # boardroom partners (legs behind the table)
    for k, x in enumerate((2900, 3080, 3260)):
        chars.append(place(rig_svg(f"bni{k}", investor(k), "full"), x, 1150, 150, flip=True))
    table = f'<rect x="2880" y="1340" width="520" height="120" rx="10" fill="#3a2418" stroke="{O}" stroke-width="4"/>'
    front = f'<svg viewBox="0 0 3840 2160" style="position:absolute;left:0;top:0;width:3840px;height:2160px;overflow:visible">{desk_fronts}{table}</svg>'
    night = ('<div id="bn-night" style="position:absolute;left:-800px;top:-700px;width:5440px;height:3060px;opacity:0;'
             'background:linear-gradient(180deg,rgba(6,10,30,.92),rgba(12,18,44,.7) 60%,rgba(8,12,34,.8));mix-blend-mode:multiply"></div>')
    floors_dark = ('<svg viewBox="0 0 3840 2160" style="position:absolute;left:0;top:0;width:3840px;height:2160px;overflow:visible;pointer-events:none">'
                   '<rect id="bn-street-dark" x="-400" y="1950" width="4640" height="210" fill="#0a1028" opacity="0"/>'
                   '<rect id="bn-tower-dark" x="2300" y="720" width="1260" height="370" fill="#0a1028" opacity="0"/>'
                   '<rect id="bn-tower-dark2" x="2300" y="1480" width="1260" height="470" fill="#0a1028" opacity="0"/>'
                   + "".join(f'<rect class="bn-floor-dark" id="bn-fd{i}" x="260" y="{y}" width="1330" height="{h}" fill="#05070c" opacity="0"/>'
                             for i, (y, h) in enumerate([(764, 284), (1072, 276), (1372, 568)])) + '</svg>')
    coins = "".join(f'<circle class="bn-coin" r="10" fill="#f2c66d" stroke="#8a6a1c" stroke-width="2" opacity="0"/>' for _ in range(1))
    world = (f'<div id="bn-world"><div id="bn-sky">{sky()}</div>'
             f'<div id="bn-far">{skyline("bnf", 1550, "#3a3048", "#ffd99a", 26, 11, 300, 760)}</div>'
             f'<div id="bn-mid">{board()}</div>'
             f'{night}<div id="bn-near">{skyline("bnn", 1950, "#2a2232", "#ffe3a3", 12, 5, 500, 900).replace("<svg ", "<svg style=" + chr(34) + "opacity:.0" + chr(34) + " ", 1)}</div>'
             f'<div id="bn-main">{tower()}{startup()}{"".join(chars)}{front}'
             f'<svg id="bn-fx" viewBox="0 0 3840 2160" style="position:absolute;left:0;top:0;width:3840px;height:2160px;overflow:visible">'
             f'<path id="bn-p-ad2" d="M1100 1520 H1540 V690 H1300 V640" fill="none"/><path id="bn-p-staff2" d="M1100 1520 H1540 V1000 H1360" fill="none"/>'
             f'<path id="bn-p-infra2" d="M1100 1520 H1540 V1290 H1280" fill="none"/><path id="bn-p-cap2" d="M2300 1560 H1650 L1110 1560" fill="none"/>'
             f'<path id="bn-p-rev2" d="M1300 1800 Q1200 1760 1110 1760" fill="none"/>{coins}</svg>'
             f'{cars()}{floors_dark}</div></div>')
    hud = f"""
<div class="bn-hud" id="bn-cf"><h4>Each month<small>ILLUSTRATIVE</small></h4>
 <div class="bn-row"><span class="k">Spending</span><div class="bn-bar"><div class="bn-seg" id="bn-s-ad" style="background:#e07a5f"></div><div class="bn-seg" id="bn-s-st" style="background:#f2c66d"></div><div class="bn-seg" id="bn-s-in" style="background:#7fd8ff"></div></div></div>
 <div class="bn-row"><span class="k">Revenue</span><div class="bn-bar"><div class="bn-seg" id="bn-s-rv" style="background:#5fb36a"></div></div></div>
 <div class="bn-row" style="font:700 26px Inter;opacity:.9;gap:20px"><span style="color:#e07a5f">■ ads</span><span style="color:#f2c66d">■ staff</span><span style="color:#7fd8ff">■ servers</span><span style="color:#5fb36a">■ orders</span></div>
 <div id="bn-gap" style="margin-top:10px;font:800 38px Inter;color:#ff7a66;opacity:0">Burning cash every month</div></div>
<div class="bn-hud" id="bn-rw"><h4>Cash runway<small>ILLUSTRATIVE</small></h4>
 <div class="bn-bar" style="height:34px"><div class="bn-seg" id="bn-rwbar" style="background:linear-gradient(90deg,#b8892e,#f2c66d);width:22%"></div></div>
 <div style="display:flex;justify-content:space-between;font:700 26px Inter;opacity:.85;margin-top:10px"><span>out of cash</span><span>funded</span></div></div>
<div class="bn-hud" id="bn-cg" style="width:480px"><h4>Investor confidence</h4>
 <svg viewBox="0 0 360 190" width="420" height="222"><path d="M30 170 A150 150 0 0 1 330 170" stroke="#3a3448" stroke-width="26" fill="none"/>
  <path d="M30 170 A150 150 0 0 1 100 45" stroke="#d9503f" stroke-width="26" fill="none"/><path d="M260 45 A150 150 0 0 1 330 170" stroke="#5fb36a" stroke-width="26" fill="none"/>
  <g id="bn-needle"><path d="M180 170 L180 40" stroke="#fff" stroke-width="8" stroke-linecap="round"/></g><circle cx="180" cy="170" r="14" fill="#fff"/></svg></div>"""
    html = world + hud + '<div class="tag v" id="bn-tag" style="top:52px">The year 2000</div>'

    # camera keys: [arrive t, x, y, scale, move]
    keys = [[s, 1180, -40, 1.0], [t_bus + .5, -230, 560, .8, 1.5], [t_ad + .2, 140, 40, 1.25, 1.0], [t_emp + .1, 150, 470, 1.25, .8],
            [t_inf + .15, 150, 790, 1.25, .8], [t_earn + .3, 170, 1150, 1.15, 1.0], [t_invs, 0, 40, .5, 1.6],
            [t_inv7 + .3, 2440, 1000, 1.75, 1.4], [t_stock + .2, 1270, 60, 1.1, .7], [t_ext + .3, 380, 740, .75, 1.2],
            [t_without + .3, -230, 560, .8, 1.2]]
    js = [f"tl.fromTo('#bn',{{opacity:0}},{{opacity:1,duration:.5}},{s});",
          f"mCamera('#bn-world',{keys},{{layers:[['#bn-sky',.15],['#bn-far',.35],['#bn-mid',.7]],end:{e},drift:.03}});",
          f"gsap.set('.bn-lbl',{{opacity:0}}); show('.bn-lbl',{t_earn + .3},.3); hide('.bn-lbl',{t_invs - 1.7},.2); show('.bn-lbl',{t_ext + .35},.3); hide('.bn-lbl',{t_without - .9},.2);",
          f"show('#bn-tag',{s + .3}); hide('#bn-tag',{t_bus - .7});",
          # rising market over the dusk skyline; tape scrolls
          f"mDrawOn('#bn-rise',{t_rise - .5},{{dur:2.6,ease:'power1.in'}}); tl.fromTo('#bn-dot',{{attr:{{cx:1790,cy:560}}}},{{attr:{{cx:2450,cy:250}},duration:2.6,ease:'power1.in'}},{t_rise - .5});",
          f"tl.fromTo('#bn-tape',{{x:0}},{{x:-1400,duration:{e - s},ease:'none'}},{s});",
          # ambient life: clouds, window flicker, cars, billboard spot sweep, CRT and LED twinkle
          f"mAmbient('#bn-clouds ellipse',{s},{e},{{drift:[80,6],period:6,seed:3}});",
          f"mAmbient('.bnf-win',{s},{e},{{flicker:.5,period:2.6,seed:5}});",
          f"mAmbient('.bn-twin',{s},{e},{{flicker:.4,period:3.1,seed:8}});",
          f"document.querySelectorAll('.bn-car').forEach((c,i)=>tl.fromTo(c,{{x:0}},{{x:i%2?-1400:1400,duration:{e - s},ease:'none'}},{s}));",
          f"mAmbient('#bn-spots path',{s},{t_ops},{{rotate:6,period:1.6,seed:2}});",
          f"mAmbient('.bn-led',{s},{t_ops},{{flicker:.9,period:.5,seed:9}});",
          f"tl.fromTo('#bn-flame',{{scaleY:.8,transformOrigin:'50% 0%'}},{{scaleY:1.2,duration:.18,yoyo:true,repeat:{int((e - s) / .18)},ease:'sine.inOut'}},{s});",
          # office life: typing, talking, packing orders, tech working
          *[f"ambient('bns{k}',{s},{t_fin2},{300 + k},['type','type','hold','point']);" for k in range(6)],
          f"ambient('bnw0',{s},{t_fresh},310,['shout','point','hold']); ambient('bnw1',{s},{t_fresh},311,['hold','phone']);",
          f"ambient('bnt',{s},{t_ops},320,['type','hold']); ambient('bnr',{s},{t_ops},321,['phone','write']);",
          f"rcycle('bnk','carry','hold',{s},{t_ops},1.4,.2);",
          # outlets come alive as they are named; coins climb the riser to each
          f"mFlow('#bn-p-ad2',{t_ad - .3},{t_ops},{{dash:false,dots:5,r:17,color:'#ffd75a',speed:520}});",
          f"mFlow('#bn-p-staff2',{t_emp - .2},{t_ops},{{dash:false,dots:4,r:17,color:'#ffd75a',speed:480}});",
          f"mFlow('#bn-p-infra2',{t_inf - .2},{t_ops},{{dash:false,dots:4,r:17,color:'#ffd75a',speed:480}});",
          f"tl.fromTo('#bn-spots',{{opacity:.5}},{{opacity:1,duration:.4}},{t_ad});",
          f"mFocus(['#bns0','#bns1','#bns2','#bns3','#bns4','#bns5'],[],{t_emp});",
          # revenue trickle (one coin) into the tank
          f"mFlow('#bn-p-rev2',{t_rev - .2},{t_ops},{{dash:false,dots:1,r:15,color:'#7fdc8a',speed:90}});",
          # tank level: drains while spending, refills from capital, then drains to empty
          f"tl.fromTo('#bn-cash',{{attr:{{y:1640,height:300}}}},{{attr:{{y:1800,height:140}},duration:{t_invs - t_ad},ease:'none'}},{t_ad});",
          f"tl.to('#bn-cash',{{attr:{{y:1560,height:380}},duration:{t_dis - t_cap + 1},ease:'power1.out'}},{t_cap - .4});",
          f"tl.to('#bn-cash',{{attr:{{y:1905,height:5}},duration:{t_ops - t_decl},ease:'power1.in'}},{t_decl});",
          # capital pipe: investors supply capital; the valve closes on 'declining'
          f"mFlow('#bn-p-cap2',{t_invs - .4},{t_decl + .6},{{dash:false,dots:8,r:22,color:'#ffd75a',speed:650}});",
          f"tl.to('#bn-valve',{{rotation:300,svgOrigin:'2000 1560',duration:1.2,ease:'power2.inOut'}},{t_decl});",
          # night falls with confidence
          f"tl.to('#bn-night',{{opacity:1,duration:2.2,ease:'sine.inOut'}},{t_conf - .2}); tl.to(['#bn-street-dark','#bn-tower-dark','#bn-tower-dark2'],{{opacity:.55,duration:2.2}},{t_conf - .2}); tl.to('.bn-star',{{opacity:.8,duration:2,stagger:.01}},{t_conf});",
          f"tl.to('#bn-sunc',{{attr:{{cy:1700}},opacity:0,duration:2.4,ease:'sine.in'}},{t_conf - .2});",
          # boardroom: optimism, then worry
          f"ambient('bni0',{t_invs - 1},{t_worry},330,['point','hold']); ambient('bni1',{t_invs - 1},{t_worry},331,['hold','write']); ambient('bni2',{t_invs - 1},{t_worry},332,['phone','hold']);",
          f"rexpress('bni0','worry',{t_worry}); rexpress('bni1','worry',{t_worry + .2}); rexpress('bni2','shock',{t_prof});",
          f"mBars('#bn-val',[1],{t_val - .1},{{scale:210,baseline:1340}}); tl.to('#bn-prof',{{attr:{{y:1340,height:60}},duration:.6,ease:MOTION.ease.data}},{t_prof});",
          f"rpose('bni0','point',{t_val},.3); rpose('bni2','handsHead',{t_prof + .2},.35); rpose('bni1','slump',{t_prof + .4},.4);",
          f"rpose('bni0','shrug',{t_decl},.3); rpose('bni1','neutral',{t_decl},.3);",
          # the market breaks
          f"tl.to('#bn-rise',{{stroke:'#c8d0c8',duration:.3}},{t_stock}); tl.set('#bn-fall',{{opacity:1}},{t_stock}); mDrawOn('#bn-fall',{t_stock},{{dur:1.3,ease:'power2.in'}});",
          f"tl.to('#bn-dot',{{attr:{{cx:2550,cy:560}},fill:'#ff5a46',duration:1.3,ease:'power2.in'}},{t_stock});",
          f"tl.to('#bn-tape',{{fill:'#ff5a46',duration:.3}},{t_fall});",
          # shutdown, outlet by outlet, on 'finance their operations'
          f"tl.to('#bn-spots',{{opacity:0,duration:.15}},{t_fin2}); tl.to('#bn-bill',{{filter:'brightness(.45) saturate(.5)',duration:.4}},{t_fin2});",
          f"tl.to('.bn-crt',{{fill:'#0a0a0e',duration:.1,stagger:.06}},{t_fin2 + .2}); tl.to('.bn-led',{{fill:'#1a2230',duration:.1,stagger:.004}},{t_ops});",
          f"tl.to('.bn-lamp',{{opacity:0,duration:.1,stagger:.08}},{t_fin2 + .3});",
          f"[0,1,2].forEach(i=>tl.to('#bn-fd'+i,{{opacity:.8,duration:.25}},{t_fin2 + .2}+i*.35));",
          *[f"rpose('bns{k}','slump',{t_fin2 + .1 * k},.35); rexpress('bns{k}','worry',{t_fin2 + .1 * k});" for k in range(6)],
          f"rpose('bnw0','carry',{t_fresh},.3); rpose('bnw1','carry',{t_fresh + .2},.3);",
          f"rwalk('bnw0','#bnw0-wrap',{t_fresh + .3},{int((e - t_fresh - .3) / .38)},.38,-560); rwalk('bnw1','#bnw1-wrap',{t_fresh + .6},{int((e - t_fresh - .6) / .38)},.38,-520);",
          # HUD: monthly cash flow (on the named words), runway, confidence
          f"show('#bn-cf',{t_ad - .2},.35);",
          f"tl.to('#bn-s-ad',{{width:'38%',duration:.5,ease:MOTION.ease.data}},{t_ad}); tl.to('#bn-s-st',{{width:'32%',duration:.5,ease:MOTION.ease.data}},{t_emp}); tl.to('#bn-s-in',{{width:'24%',duration:.5,ease:MOTION.ease.data}},{t_inf});",
          f"tl.to('#bn-s-rv',{{width:'14%',duration:.5,ease:MOTION.ease.data}},{t_rev});",
          f"tl.fromTo('#bn-gap',{{opacity:0,x:16}},{{opacity:1,x:0,duration:.3}},{t_sust}); hide('#bn-cf',{t_surv - .3},.3);",
          f"show('#bn-rw',{t_invs - .2},.35); tl.to('#bn-rwbar',{{width:'86%',duration:1.6,ease:'power2.out'}},{t_cap - .3}); hide('#bn-rw',{t_conf - .5},.3);",
          f"show('#bn-cg',{t_conf - .2},.3); tl.fromTo('#bn-needle',{{rotation:62,svgOrigin:'180 170'}},{{rotation:-66,svgOrigin:'180 170',duration:{t_dis + .4 - t_conf},ease:'power2.in'}},{t_conf}); hide('#bn-cg',{t_inv7 - .2},.3);",
          f"show('#bn-rw',{t_fin - .2},.35); tl.to('#bn-rwbar',{{width:'3%',duration:{t_ops - t_decl},ease:'power1.in'}},{t_decl}); tl.to('#bn-rwbar',{{background:'#d9503f',duration:.4}},{t_exist}); hide('#bn-rw',{e - .4},.3);",
          f"tl.to('#bn',{{opacity:0,duration:.35}},{e - .35});"]
    return [Scene("bn", round(s, 3), round(e - s, 3), html, css=CSS, js="\n".join(js))], [], ""
