"""Epoch Ledger reusable set pieces (hand-authored SVG).

Every function returns an SVG string sized for a 1920x1080 canvas (class="full").
Defaults reproduce the "How Banks Create Money" pilot exactly; pass a new
prefix per scene so element ids stay unique and GSAP selectors stay stable.
"""

from .characters import OUT

# ── Scene 2: street + bank facade ──────────────────────────────────────
def columns():
    out = []
    for i, x in enumerate([790, 900, 1010, 1190, 1300, 1410]):
        out.append(f'<g><rect x="{x-6}" y="468" width="72" height="16" fill="#e7dcc5" stroke="{OUT}" stroke-width="2.5"/>'
                   f'<rect x="{x}" y="484" width="60" height="292" fill="#f1e8d6" stroke="{OUT}" stroke-width="2.5"/>'
                   f'<path d="M{x+15} 490 V770 M{x+30} 490 V770 M{x+45} 490 V770" stroke="#cdbf9f" stroke-width="3"/>'
                   f'<rect x="{x}" y="484" width="12" height="292" fill="#d9ccb0" opacity=".7"/>'
                   f'<rect x="{x-8}" y="774" width="76" height="16" fill="#e7dcc5" stroke="{OUT}" stroke-width="2.5"/></g>')
    return "".join(out)


def skyline(base, color, seed, n, hmin, hmax, wmin, wmax, windows=False):
    # deterministic pseudo-random skyline
    s = seed
    def rnd():
        nonlocal s
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        return s / 0x7FFFFFFF
    x, out = -40, []
    while x < 2000 and len(out) < n:
        w = wmin + rnd() * (wmax - wmin); h = hmin + rnd() * (hmax - hmin)
        out.append(f'<rect x="{x:.0f}" y="{base-h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{color}"/>')
        if windows:
            for wy in range(int(base - h + 18), int(base - 14), 30):
                for wx in range(int(x + 12), int(x + w - 14), 26):
                    if rnd() > .45:
                        out.append(f'<rect x="{wx}" y="{wy}" width="12" height="16" fill="#f6d58f" opacity=".75"/>')
        x += w + 6 + rnd() * 20
    return "".join(out)


def tree(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<rect x="-10" y="-10" width="20" height="90" fill="#6b4226" stroke="{OUT}" stroke-width="3"/>'
            f'<circle cx="0" cy="-60" r="62" fill="#2f7d5b" stroke="{OUT}" stroke-width="3"/>'
            f'<circle cx="-40" cy="-20" r="42" fill="#2a6e50" stroke="{OUT}" stroke-width="3"/>'
            f'<circle cx="42" cy="-26" r="44" fill="#358c66" stroke="{OUT}" stroke-width="3"/>'
            f'<circle cx="18" cy="-84" r="20" fill="#4aa57c" opacity=".7"/>'
            f'<rect x="-46" y="70" width="92" height="44" rx="6" fill="#9c6b45" stroke="{OUT}" stroke-width="3"/></g>')


def lamp(x):
    return (f'<g><rect x="{x-7}" y="420" width="14" height="460" fill="#1e2a3a" stroke="{OUT}" stroke-width="2"/>'
            f'<rect x="{x-20}" y="866" width="40" height="18" rx="4" fill="#1e2a3a"/>'
            f'<path d="M{x-26} 420 L{x+26} 420 L{x+18} 372 L{x-18} 372Z" fill="#2b3a52" stroke="{OUT}" stroke-width="3"/>'
            f'<rect x="{x-14}" y="380" width="28" height="34" fill="#ffe3a3"/>'
            f'<circle cx="{x}" cy="396" r="60" fill="#ffe3a3" opacity=".18"/></g>')


def bank_street(prefix="s2", bank_name="LEDGER BANK"):
    """Daylight street with a classical bank facade; layered groups for parallax:
    {prefix}-clouds, {prefix}-far, {prefix}-mid, {prefix}-bank."""
    return f"""
<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fc0e3"/><stop offset=".62" stop-color="#cfe1ea"/><stop offset="1" stop-color="#f6c59a"/></linearGradient>
  <radialGradient id="sun"><stop offset="0" stop-color="#fff4d0"/><stop offset=".35" stop-color="#ffe3a3" stop-opacity=".8"/><stop offset="1" stop-color="#ffe3a3" stop-opacity="0"/></radialGradient>
  <linearGradient id="walk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9cbb0"/><stop offset="1" stop-color="#b9a98c"/></linearGradient>
 </defs>
 <rect width="1920" height="1080" fill="url(#sky)"/>
 <circle cx="1560" cy="250" r="230" fill="url(#sun)"/><circle cx="1560" cy="250" r="64" fill="#fff1c9"/>
 <g id="{prefix}-clouds" fill="#fff" opacity=".85">
  <g><ellipse cx="300" cy="170" rx="120" ry="34"/><ellipse cx="360" cy="150" rx="70" ry="40"/><ellipse cx="250" cy="160" rx="60" ry="30"/></g>
  <g><ellipse cx="1180" cy="120" rx="100" ry="26"/><ellipse cx="1230" cy="104" rx="56" ry="30"/></g>
  <g opacity=".7"><ellipse cx="760" cy="230" rx="90" ry="20"/><ellipse cx="800" cy="216" rx="44" ry="22"/></g>
 </g>
 <g id="{prefix}-far" opacity=".55">{skyline(700, "#7d9bb8", 7, 40, 160, 380, 70, 150)}</g>
 <g id="{prefix}-mid">{skyline(820, "#4f6d8c", 19, 30, 200, 420, 110, 190, windows=True)}</g>
 <g id="{prefix}-bank">
  <rect x="640" y="440" width="920" height="420" fill="#4f6d8c" opacity="0"/>
  <rect x="700" y="470" width="800" height="330" fill="#e6dac1" stroke="{OUT}" stroke-width="3"/>
  <rect x="700" y="470" width="800" height="330" fill="#cdbf9f" opacity=".25"/>
  <path d="M1040 790 L1040 640 Q1100 584 1160 640 L1160 790Z" fill="#3b2416" stroke="{OUT}" stroke-width="3"/>
  <path d="M1052 788 L1052 646 Q1100 600 1148 646 L1148 788Z" fill="#ffd98f" opacity=".85"/>
  <path d="M1100 600 V788" stroke="#8a5a3c" stroke-width="5"/>
  <circle cx="1088" cy="716" r="5" fill="#d4a24c"/><circle cx="1112" cy="716" r="5" fill="#d4a24c"/>
  <rect x="860" y="560" width="36" height="120" fill="#5a7898" stroke="{OUT}" stroke-width="2.5"/>
  <rect x="1304" y="560" width="36" height="120" fill="#5a7898" stroke="{OUT}" stroke-width="2.5"/>
  {columns()}
  <path d="M686 470 L1514 470 L1514 420 L686 420Z" fill="#efe5cf" stroke="{OUT}" stroke-width="3"/>
  <text x="1100" y="457" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="32" letter-spacing="10" fill="#14213d">{bank_name}</text>
  <path d="M670 420 L1100 286 L1530 420Z" fill="#f4ead5" stroke="{OUT}" stroke-width="3"/>
  <path d="M736 408 L1100 300 L1464 408Z" fill="#e2d4b5"/>
  <circle cx="1100" cy="366" r="34" fill="#d4a24c" stroke="{OUT}" stroke-width="3"/>
  <text x="1100" y="380" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="40" fill="#14213d">$</text>
  <rect x="680" y="796" width="840" height="20" fill="#d8ccb2" stroke="{OUT}" stroke-width="2.5"/>
  <rect x="660" y="816" width="880" height="20" fill="#cfc2a6" stroke="{OUT}" stroke-width="2.5"/>
  <rect x="640" y="836" width="920" height="24" fill="#c5b799" stroke="{OUT}" stroke-width="2.5"/>
  {tree(600, 760, .9)}{tree(1620, 760, .9)}
 </g>
 <rect x="0" y="856" width="1920" height="224" fill="url(#walk)"/>
 <path d="M0 860 H1920" stroke="{OUT}" stroke-width="3" opacity=".5"/>
 <path d="M0 960 H1920" stroke="#a8977a" stroke-width="3"/>
 <path d="M240 860 L180 1080 M640 860 L620 1080 M1040 860 L1060 1080 M1440 860 L1500 1080 M1840 860 L1940 1080" stroke="#a8977a" stroke-width="2.5"/>
</svg>"""

def street_foreground(prefix="s2", lamps=(40, 1860)):
    """Foreground lamp posts (group {prefix}-fg) — draw above characters for depth."""
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg"><g id="{prefix}-fg">{"".join(lamp(x) for x in lamps)}</g></svg>"""

# ── Scene 3: loan office ───────────────────────────────────────────────
def office_background():
    """Loan-office interior: wall, wainscot, window light shaft, painting, plant."""
    return f"""
<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3e8cf"/><stop offset="1" stop-color="#e3d3b2"/></linearGradient>
  <linearGradient id="shaft" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff6dc" stop-opacity=".55"/><stop offset="1" stop-color="#fff6dc" stop-opacity="0"/></linearGradient>
 </defs>
 <rect width="1920" height="1080" fill="url(#wall)"/>
 <g opacity=".18" stroke="#b89f74" stroke-width="2">{''.join(f'<path d="M{x} 0 V640"/>' for x in range(30, 1920, 60))}</g>
 <rect x="0" y="640" width="1920" height="260" fill="#7a4e33"/>
 <g stroke="#5e3a25" stroke-width="4" fill="none">{''.join(f'<rect x="{x}" y="670" width="200" height="190" rx="6"/>' for x in range(40, 1900, 240))}</g>
 <rect x="0" y="636" width="1920" height="14" fill="#5e3a25"/>
 <rect x="0" y="880" width="1920" height="200" fill="#4a2f1f"/>
 <rect x="1480" y="110" width="340" height="420" fill="#a9d2ef" stroke="{OUT}" stroke-width="4"/>
 <rect x="1480" y="110" width="340" height="420" fill="#fff" opacity=".18"/>
 <g stroke="#e9dcc0" stroke-width="8">{''.join(f'<path d="M1480 {y} H1820"/>' for y in range(140, 520, 34))}</g>
 <rect x="1468" y="98" width="364" height="18" fill="#8a5a3c"/><rect x="1468" y="526" width="364" height="18" fill="#8a5a3c"/>
 <path d="M1480 120 L1820 120 L1300 1080 L700 1080Z" fill="url(#shaft)" opacity=".6"/>
 <rect x="120" y="150" width="300" height="230" fill="#c99b4a" stroke="{OUT}" stroke-width="4"/>
 <rect x="142" y="172" width="256" height="186" fill="#2c4a63"/>
 <path d="M142 330 Q220 250 300 300 T398 280 V358 H142Z" fill="#3f7a5f"/><circle cx="350" cy="210" r="22" fill="#ffe3a3"/>
 <g transform="translate(1700 640)"><rect x="-60" y="140" width="120" height="100" rx="10" fill="#c2643c" stroke="{OUT}" stroke-width="3"/>
  <path d="M0 140 C-40 60 -120 40 -110 -40 C-60 0 -20 40 0 140Z" fill="#2f7d5b" stroke="{OUT}" stroke-width="3"/>
  <path d="M0 140 C40 40 110 0 120 -70 C60 -30 20 30 0 140Z" fill="#358c66" stroke="{OUT}" stroke-width="3"/>
  <path d="M0 140 C-10 40 0 -40 20 -110 C40 -20 20 60 0 140Z" fill="#4aa57c" stroke="{OUT}" stroke-width="3"/></g>
</svg>"""

def office_foreground(nameplate="LOAN OFFICER"):
    """Client chair + desk with nameplate, monitor, lamp, papers (draw over characters)."""
    return f"""
<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <path d="M400 680 Q400 650 430 650 L720 650 Q750 650 750 680 L760 900 L390 900Z" fill="#7d2f2f" stroke="{OUT}" stroke-width="4"/>
 <path d="M420 680 L730 680" stroke="#5f2121" stroke-width="6"/>
 <g fill="#d4a24c">{''.join(f'<circle cx="{x}" cy="665" r="5"/>' for x in range(430, 740, 30))}</g>
 <path d="M820 640 L1640 640 L1680 700 L780 700Z" fill="#a36d48" stroke="{OUT}" stroke-width="4"/>
 <rect x="800" y="700" width="860" height="200" fill="#8a5a3c" stroke="{OUT}" stroke-width="4"/>
 <path d="M800 720 H1660" stroke="#6e4630" stroke-width="5"/>
 <rect x="1140" y="760" width="200" height="54" rx="6" fill="#d4a24c" stroke="{OUT}" stroke-width="3"/>
 <text x="1240" y="796" text-anchor="middle" font-family="Inter" font-weight="700" font-size="20" letter-spacing="3" fill="#14213d">{nameplate}</text>
 <rect x="1430" y="520" width="150" height="110" rx="8" fill="#22262e" stroke="{OUT}" stroke-width="4"/>
 <rect x="1442" y="532" width="126" height="86" rx="4" fill="#3c6e8f"/>
 <rect x="1490" y="630" width="30" height="20" fill="#22262e"/>
 <path d="M860 520 L880 640 M860 520 L920 520" stroke="#2b2b2b" stroke-width="7" fill="none"/>
 <path d="M900 500 L960 500 L940 530 L920 530Z" fill="#2f7d5b" stroke="{OUT}" stroke-width="3"/>
 <path d="M900 650 L1060 650 L1080 680 L880 680Z" fill="#f7f1e3" stroke="{OUT}" stroke-width="2.5"/>
</svg>"""

def credit_gauge(prefix="s3"):
    """Semicircle credit gauge; rotate #{prefix}-needle with svgOrigin '160 180'."""
    return f"""
<svg viewBox="0 0 320 220" class="card-svg" xmlns="http://www.w3.org/2000/svg">
 <path d="M40 180 A120 120 0 0 1 280 180" stroke="#e5dccb" stroke-width="26" fill="none"/>
 <path d="M40 180 A120 120 0 0 1 100 76" stroke="#e0603a" stroke-width="26" fill="none"/>
 <path d="M100 76 A120 120 0 0 1 220 76" stroke="#d4a24c" stroke-width="26" fill="none"/>
 <path d="M220 76 A120 120 0 0 1 280 180" stroke="#2f7d5b" stroke-width="26" fill="none"/>
 <g id="{prefix}-needle"><path d="M160 180 L156 84 L164 84Z" fill="#14213d"/></g>
 <circle cx="160" cy="180" r="12" fill="#14213d"/>
</svg>"""

# ── Scene 4: ledger ────────────────────────────────────────────────────
def ledger_sheet(prefix="s4"):
    """T-account rules + ink lines + connector arrow. Ids: {prefix}-hline, -vline, -ink-l, -ink-r, -arrow, -arrowhead."""
    return f"""
<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><filter id="ink"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="1" seed="4"/><feDisplacementMap in="SourceGraphic" scale="2.5"/></filter></defs>
 <g filter="url(#ink)" stroke="#14213d" stroke-linecap="round" fill="none">
  <path id="{prefix}-hline" d="M240 352 H1680" stroke-width="5"/>
  <path id="{prefix}-vline" d="M960 250 V650" stroke-width="5"/>
  <path id="{prefix}-ink-l" d="M290 560 H900" stroke="#2f7d5b" stroke-width="6"/>
  <path id="{prefix}-ink-r" d="M1020 560 H1630" stroke="#e0603a" stroke-width="6"/>
 </g>
 <path id="{prefix}-arrow" d="M640 600 C760 740 1160 740 1290 600" stroke="#d4a24c" stroke-width="6" fill="none" stroke-dasharray="14 12"/>
 <path id="{prefix}-arrowhead" d="M1272 590 L1300 590 L1294 618Z" fill="#d4a24c"/>
</svg>"""

# ── Scene 5: keyboard → phone ──────────────────────────────────────────
def bank_keyboard(prefix="s5"):
    """Terminal keyboard with banker hands and keyboard→phone arrow. Keys are #k0..#k29."""
    keys = "".join(
        f'<g class="key" id="k{i}"><rect x="{170 + (i % 10) * 58 + (i // 10) * 18}" y="{600 + (i // 10) * 58}" width="50" height="48" rx="8" fill="#2b3a52" stroke="{OUT}" stroke-width="2.5"/>'
        f'<rect x="{176 + (i % 10) * 58 + (i // 10) * 18}" y="{604 + (i // 10) * 58}" width="38" height="8" rx="3" fill="#3f5273"/></g>'
        for i in range(30))
    return f"""
<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <path id="{prefix}-arrow" d="M800 585 C880 380 950 290 1040 330" stroke="#7fe0c4" stroke-width="7" fill="none" stroke-dasharray="16 14" stroke-linecap="round"/>
 <path id="{prefix}-pulse" d="M800 585 C880 380 950 290 1040 330" stroke="#fff6c9" stroke-width="12" fill="none" stroke-linecap="round" stroke-dasharray="70 2000" stroke-dashoffset="70"/>
 <path id="{prefix}-ahead" d="M1024 312 L1056 334 L1022 350Z" fill="#7fe0c4"/>
 <rect x="140" y="580" width="680" height="210" rx="22" fill="#1b2638" stroke="{OUT}" stroke-width="4"/>
 {keys}
 <g id="{prefix}-hands">
  <path d="M250 820 C250 760 300 730 330 740 L360 700 C372 690 388 700 380 716 L360 760 C380 760 392 790 380 820Z" fill="#e7b08a" stroke="{OUT}" stroke-width="3"/>
  <rect x="236" y="814" width="160" height="60" rx="10" fill="#2a3550" stroke="{OUT}" stroke-width="3"/>
  <path d="M640 820 C640 760 600 730 570 740 L540 700 C528 690 512 700 520 716 L540 760 C520 760 508 790 520 820Z" fill="#e7b08a" stroke="{OUT}" stroke-width="3"/>
  <rect x="504" y="814" width="160" height="60" rx="10" fill="#2a3550" stroke="{OUT}" stroke-width="3"/>
 </g>
</svg>"""


def bokeh(n=22):
    """Soft deterministic bokeh circles for dark backgrounds."""
    return "".join(
    f'<circle cx="{(i * 397) % 1920}" cy="{(i * 211) % 1080}" r="{20 + (i * 37) % 60}" fill="{["#7fe0c4", "#d4a24c", "#9cc9e6"][i % 3]}" opacity=".10"/>'
        for i in range(n))
