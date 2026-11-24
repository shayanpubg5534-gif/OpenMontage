"""Illustrated 1870s railway sets for the railway analogy (Ch. 7): construction (capital deployed),
a busy city station (returns) and a failing branch station (insufficient demand).

Shared drawing helpers keep one consistent period look: brick, timber and cast-iron materials via
SVG patterns, a 4-4-0 locomotive and coaches in profile, freight cars, a steam derrick.
"""
from kit.characters import OUT

O = OUT


def defs(px, cold=False):
    sky = ("#9aa6b4", "#c9ced4", "#d9d6cf") if cold else ("#f3b36a", "#f8d79a", "#fbe8c0")
    return f"""<defs>
 <linearGradient id="{px}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{sky[0]}"/><stop offset=".6" stop-color="{sky[1]}"/><stop offset="1" stop-color="{sky[2]}"/></linearGradient>
 <pattern id="{px}-brick" width="48" height="24" patternUnits="userSpaceOnUse"><rect width="48" height="24" fill="{'#7d5a4c' if cold else '#a5543a'}"/>
  <path d="M0 12 H48 M0 24 H48 M24 0 V12 M0 12 V24 M48 12 V24" stroke="{'#5d443a' if cold else '#7a3a26'}" stroke-width="2"/></pattern>
 <pattern id="{px}-plank" width="200" height="22" patternUnits="userSpaceOnUse"><rect width="200" height="22" fill="{'#6e6458' if cold else '#9a7148'}"/>
  <path d="M0 21 H200 M70 0 V22 M150 0 V22" stroke="{'#4e463e' if cold else '#6b4a2c'}" stroke-width="2"/></pattern>
 <pattern id="{px}-ballast" width="16" height="10" patternUnits="userSpaceOnUse"><rect width="16" height="10" fill="{'#77746e' if cold else '#8d8070'}"/>
  <circle cx="4" cy="4" r="2.2" fill="{'#5f5c58' if cold else '#6e6254'}"/><circle cx="11" cy="7" r="2" fill="{'#8f8c86' if cold else '#a89a86'}"/></pattern>
 <pattern id="{px}-grass" width="30" height="16" patternUnits="userSpaceOnUse"><rect width="30" height="16" fill="{'#7b7d66' if cold else '#9a9a4a'}"/>
  <path d="M3 16 L5 8 M10 16 L12 6 M18 16 L19 9 M25 16 L27 7" stroke="{'#5f624e' if cold else '#6f7a34'}" stroke-width="2"/></pattern>
 <linearGradient id="{px}-iron" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4048"/><stop offset="1" stop-color="#22262c"/></linearGradient>
</defs>"""


def locomotive(x, y, s=1.0, cold=False, steam_id=None):
    """4-4-0 in profile facing right; driving wheels get ids for rotation."""
    g = "#2e4a3a" if not cold else "#3e4a44"
    r = "#8e2a26" if not cold else "#6a3a34"
    wheels = "".join(
        f'<g class="lw" transform="translate({cx} {cy})"><circle r="{rr}" fill="{r}" stroke="{O}" stroke-width="4"/>'
        + "".join(f'<path d="M0 0 L{rr * .86:.0f} 0" transform="rotate({k * 360 / n})" stroke="#2a1a14" stroke-width="4"/>' for k in range(n))
        + f'<circle r="{rr * .22:.0f}" fill="#d4a24c" stroke="{O}" stroke-width="3"/></g>'
        for cx, cy, rr, n in [(140, 236, 52, 14), (262, 236, 52, 14), (372, 262, 26, 8), (430, 262, 26, 8)])
    return f"""<g transform="translate({x} {y}) scale({s})">
 <path d="M60 178 L470 178 L470 196 L60 196Z" fill="#1c1d22" stroke="{O}" stroke-width="4"/>
 <rect x="150" y="100" width="290" height="78" rx="38" fill="{g}" stroke="{O}" stroke-width="5"/>
 {''.join(f'<path d="M{190 + k * 60} 102 V176" stroke="#d4a24c" stroke-width="5"/>' for k in range(4))}
 <rect x="420" y="96" width="46" height="84" rx="10" fill="#1c1d22" stroke="{O}" stroke-width="5"/>
 <path d="M424 96 L408 26 L476 26 L460 96Z" fill="#1c1d22" stroke="{O}" stroke-width="5"/>
 <rect x="300" y="72" width="36" height="30" rx="14" fill="#d4a24c" stroke="{O}" stroke-width="4"/>
 <rect x="220" y="78" width="30" height="24" rx="12" fill="{g}" stroke="{O}" stroke-width="4"/>
 <rect x="456" y="62" width="40" height="34" rx="4" fill="#1c1d22" stroke="{O}" stroke-width="4"/><circle cx="494" cy="79" r="11" fill="#fff1c0"/>
 <path d="M470 196 L540 270 L470 270Z" fill="{r}" stroke="{O}" stroke-width="4"/>
 <path d="M40 60 L150 60 L150 190 L40 190Z" fill="{r}" stroke="{O}" stroke-width="5"/><path d="M28 50 L162 50 L162 66 L28 66Z" fill="#1c1d22" stroke="{O}" stroke-width="4"/>
 <rect x="62" y="80" width="64" height="48" rx="4" fill="#ffd27a" stroke="{O}" stroke-width="4"/>
 <rect x="410" y="214" width="66" height="34" rx="6" fill="#1c1d22" stroke="{O}" stroke-width="4"/>
 {wheels}
 <g class="lrod"><rect x="130" y="230" width="150" height="12" rx="6" fill="#9aa0a8" stroke="{O}" stroke-width="3"/></g>
 {f'<g id="{steam_id}"></g>' if steam_id else ''}
</g>"""


def coach(x, y, w=380, busy=True, cold=False, cid="c", seats=6):
    body = "#6e2a22" if not cold else "#5a4a44"
    win = []
    for k in range(seats):
        wx = 30 + k * (w - 60) / seats
        face = ""
        if busy:
            sk = ["#f1c9a5", "#c98f63", "#8d5a3b", "#e8b48c", "#a86b45", "#f4d3b5"][(k * 5 + len(cid)) % 6]
            hat = ["#2a2420", "#5a4a3a", "#7a3a2a", "#1e1c1c"][(k + len(cid)) % 4]
            face = (f'<circle cx="{wx + 22}" cy="{y + 70}" r="13" fill="{sk}" stroke="{O}" stroke-width="2.5"/>'
                    f'<path d="M{wx + 6} {y + 62} L{wx + 38} {y + 62} L{wx + 34} {y + 52} L{wx + 10} {y + 52}Z" fill="{hat}"/>'
                    f'<path d="M{wx + 8} {y + 96} Q{wx + 22} {y + 80} {wx + 36} {y + 96}Z" fill="{["#3a4a6a", "#6a3a3a", "#4a5a3a"][k % 3]}"/>')
        win.append(f'<rect x="{wx}" y="{y + 44}" width="44" height="52" rx="6" fill="{"#ffd99a" if busy else "#3a3a40"}" stroke="{O}" stroke-width="3"/>{face}')
    return f"""<g id="{cid}" transform="translate({x} 0)">
 <path d="M0 {y + 20} Q{w / 2} {y - 6} {w} {y + 20} L{w} {y + 130} L0 {y + 130}Z" fill="{body}" stroke="{O}" stroke-width="5"/>
 <path d="M-6 {y + 18} Q{w / 2} {y - 12} {w + 6} {y + 18}" stroke="#2a2a2a" stroke-width="10" fill="none"/>
 <path d="M0 {y + 108} H{w}" stroke="#d4a24c" stroke-width="4"/>{''.join(win)}
 <rect x="{w / 2 - 22}" y="{y + 36}" width="44" height="90" rx="4" fill="{body}" stroke="{O}" stroke-width="4"/>
 {''.join(f'<g class="lw" transform="translate({cx} {y + 150})"><circle r="22" fill="#2a2a2e" stroke="{O}" stroke-width="3"/><path d="M-18 0 H18 M0 -18 V18" stroke="#6a6a70" stroke-width="3"/></g>' for cx in (40, 90, w - 90, w - 40))}
</g>"""


def boxcar(x, y, w=300, loaded=True, cold=False, cid="b"):
    body = "#7a4a2f" if not cold else "#5e544c"
    crates = ""
    if loaded:
        crates = "".join(f'<rect x="{30 + k * 62}" y="{y + 18 - (k % 2) * 26}" width="56" height="{48 + (k % 2) * 26}" fill="{["#d9c08a", "#b0b8a0", "#c98a4a", "#a8885a"][k % 4]}" stroke="{O}" stroke-width="3"/>' for k in range(4))
    return f"""<g id="{cid}" transform="translate({x} 0)">{crates}
 <rect x="0" y="{y + 60}" width="{w}" height="70" fill="{body}" stroke="{O}" stroke-width="5"/>
 {''.join(f'<path d="M{k * w / 6} {y + 60} V{y + 130}" stroke="#4a2e1c" stroke-width="3"/>' for k in range(1, 6))}
 {''.join(f'<g class="lw" transform="translate({cx} {y + 150})"><circle r="22" fill="#2a2a2e" stroke="{O}" stroke-width="3"/><path d="M-18 0 H18 M0 -18 V18" stroke="#6a6a70" stroke-width="3"/></g>' for cx in (40, 90, w - 90, w - 40))}
</g>"""


def track(y, x0=-300, x1=2300, px="r", rusty=False):
    sl = "".join(f'<rect x="{x}" y="{y - 6}" width="24" height="22" fill="{"#5a4a3a" if rusty else "#5a3e26"}" stroke="{O}" stroke-width="2"/>' for x in range(x0, x1, 54))
    rail = "#7a4426" if rusty else "#8a8f98"
    return (f'<rect x="{x0}" y="{y - 2}" width="{x1 - x0}" height="30" fill="url(#{px}-ballast)"/>{sl}'
            f'<rect x="{x0}" y="{y - 10}" width="{x1 - x0}" height="9" fill="{rail}" stroke="{O}" stroke-width="2"/>')


def station_building(x, y, px, cold=False, name="CENTRAL STATION"):
    win = "".join(f'<path d="M{x + 60 + k * 120} {y + 250} V{y + 170} Q{x + 100 + k * 120} {y + 130} {x + 140 + k * 120} {y + 170} V{y + 250}Z" '
                  f'fill="{"#4a4f56" if cold else "#ffd99a"}" stroke="{O}" stroke-width="4"/>'
                  + (f'<path d="M{x + 60 + k * 120} {y + 200} L{x + 140 + k * 120} {y + 228} M{x + 60 + k * 120} {y + 230} L{x + 140 + k * 120} {y + 206}" stroke="#7a6248" stroke-width="10"/>' if cold and k % 2 else "")
                  for k in range(6))
    return f"""<g>
 <rect x="{x}" y="{y + 80}" width="760" height="300" fill="url(#{px}-brick)" stroke="{O}" stroke-width="5"/>
 <path d="M{x - 30} {y + 86} L{x + 380} {y - 40} L{x + 790} {y + 86}Z" fill="{'#4a4038' if cold else '#5a3626'}" stroke="{O}" stroke-width="5"/>
 <circle cx="{x + 380}" cy="{y + 30}" r="38" fill="#f3e9d2" stroke="{O}" stroke-width="5"/>
 <path d="M{x + 380} {y + 30} L{x + 380} {y + 6} M{x + 380} {y + 30} L{x + 398} {y + 40}" stroke="{O}" stroke-width="4" stroke-linecap="round"/>
 <rect x="{x + 210}" y="{y + 92}" width="340" height="46" rx="4" fill="#1e2a22" stroke="{O}" stroke-width="4"/>
 <text x="{x + 380}" y="{y + 124}" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="30" fill="#f2c66d">{name}</text>
 {win}
 <path d="M{x} {y + 260} H{x + 760}" stroke="#e8dcc4" stroke-width="8"/>
</g>"""


def canopy(x0, x1, y, px, cold=False):
    cols = "".join(f'<g><rect x="{x}" y="{y}" width="14" height="300" fill="url(#{px}-iron)" stroke="{O}" stroke-width="3"/>'
                   f'<path d="M{x - 40} {y + 6} Q{x + 7} {y + 60} {x + 54} {y + 6}" stroke="#2a2e34" stroke-width="8" fill="none"/></g>' for x in range(x0 + 40, x1, 220))
    return (f'<path d="M{x0} {y - 40} L{x1} {y - 40} L{x1 - 30} {y + 6} L{x0 + 30} {y + 6}Z" fill="{"#5a5a5e" if cold else "#3a4a5a"}" stroke="{O}" stroke-width="5"/>'
            + "".join(f'<path d="M{x} {y + 6} l14 22 l14 -22" fill="{"#4a4a4e" if cold else "#2e3a46"}"/>' for x in range(x0 + 30, x1 - 40, 28)) + cols)


def derrick(x, y):
    """Steam derrick (crane) with a jib group that can rotate (#rb-jib) and a hanging load (#rb-load)."""
    return f"""<g transform="translate({x} {y})">
 <rect x="-90" y="120" width="180" height="70" rx="6" fill="#5a3e26" stroke="{O}" stroke-width="4"/>
 <rect x="-40" y="40" width="80" height="84" fill="#3a3a40" stroke="{O}" stroke-width="4"/><rect x="-14" y="-10" width="18" height="54" fill="#1c1d22" stroke="{O}" stroke-width="3"/>
 <g id="rwb-jib"><path d="M0 60 L320 -200" stroke="#6b4a2f" stroke-width="16" stroke-linecap="round"/><path d="M0 60 L320 -200" stroke="#8a6440" stroke-width="7"/>
  <g id="rwb-load"><path d="M320 -200 L320 -60" stroke="#2a2a2a" stroke-width="3"/>
   <g transform="translate(320 -56)">{''.join(f'<rect x="-150" y="{k * 12}" width="300" height="10" fill="#8a8f98" stroke="{O}" stroke-width="2"/>' for k in range(3))}</g></g></g>
</g>"""
