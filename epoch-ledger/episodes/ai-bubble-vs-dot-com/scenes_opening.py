"""Opening sequence 0:00–0:52 (storyboard s001–s005).

Hook: a 1999 trading floor; within 10 s a brass ledger seam splits the frame and a live 3D AI data
hall appears beside 1999 — the two revolutions share the frame until "two decades later" wipes
1999 away. Then three modern beats: campus, accelerator chip, investors.
"""
import json
from pathlib import Path

from kit.assemble import Scene
from kit.characters import OUT, maya_svg, person_svg
from timeline import L, W, WE
from floor import CSS as FLOOR_CSS, BOARD_JS, floor_scene

HERE = Path(__file__).resolve().parent
GLOBE = json.loads((HERE / "assets" / "globe.json").read_text())

QUOTES = ["NTVX 87⅜ ▲4¼", "WEBQ 112½ ▲9¾", "CYBR 46⅛ ▲3⅝", "DOTN 203¼ ▲18½", "ISPX 64¾ ▲5⅛", "EMLX 31⅞ ▲2¼",
          "PORT 158 ▲12⅞", "CLIK 77⅝ ▲6½", "NETZ 95¼ ▲7⅜", "BYTE 129⅛ ▲10¾"]


def rng(seed):
    a = seed
    def r():
        nonlocal a
        a = (a * 1103515245 + 12345) & 0x7FFFFFFF
        return a / 0x7FFFFFFF
    return r


def crt(x, y, s, glow="#7cff9b", tilt=0):
    return (f'<g transform="translate({x} {y}) scale({s}) rotate({tilt})">'
            f'<rect x="-46" y="-40" width="92" height="74" rx="8" fill="#d8cfb8" stroke="{OUT}" stroke-width="3"/>'
            f'<rect x="-38" y="-33" width="76" height="56" rx="6" fill="#0b2416"/>'
            f'<path d="M-32 -22 H10 M-32 -12 H24 M-32 -2 H0 M-32 8 H18" stroke="{glow}" stroke-width="3" opacity=".85"/>'
            f'<rect x="-20" y="34" width="40" height="10" fill="#bfb59c" stroke="{OUT}" stroke-width="2"/></g>')


def trader(i, x, y, s, r):
    jackets = ["#2e6fbf", "#c8453b", "#e0b53a", "#3f8f5a", "#7a4bb0", "#e07a2e", "#1f8fa0"]
    skins = ["#e3b08c", "#c68a63", "#8a5a3c", "#f0c7a4", "#a56d4b"]
    hairs = ["#2b1b16", "#6b4a2b", "#1d1410", "#9a6a3a", "#3b3b3b"]
    j, sk, h = jackets[i % 7], skins[i % 5], hairs[(i * 3) % 5]
    up = r() < .6
    arm = (f'<g class="arm" id="tr{i}-arm"><path d="M18 -96 L40 -150" stroke="{j}" stroke-width="16" stroke-linecap="round"/>'
           f'<circle cx="42" cy="-156" r="9" fill="{sk}" stroke="{OUT}" stroke-width="2"/>'
           f'<rect x="34" y="-182" width="22" height="16" fill="#fffaf0" stroke="{OUT}" stroke-width="1.5" transform="rotate(-12 44 -174)"/></g>'
           if up else f'<g class="arm" id="tr{i}-arm"><path d="M18 -96 L30 -50" stroke="{j}" stroke-width="16" stroke-linecap="round"/>'
                      f'<rect x="22" y="-60" width="26" height="20" fill="#fffaf0" stroke="{OUT}" stroke-width="1.5"/></g>')
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-30 0 L-26 -104 C-20 -118 20 -118 26 -104 L30 0Z" fill="{j}" stroke="{OUT}" stroke-width="3"/>'
            f'<path d="M-8 -112 L8 -112 L0 -92Z" fill="#fffaf0"/>'
            f'<rect x="-12" y="-80" width="18" height="12" rx="2" fill="#fffaf0" stroke="{OUT}" stroke-width="1.5"/>'
            f'<circle cx="0" cy="-132" r="20" fill="{sk}" stroke="{OUT}" stroke-width="3"/>'
            f'<path d="M-20 -136 C-18 -156 18 -158 20 -138 C10 -146 -8 -146 -20 -136Z" fill="{h}"/>'
            f'<path d="M-18 -96 L-34 -40" stroke="{j}" stroke-width="16" stroke-linecap="round"/>{arm}</g>')


def floor_svg():
    r = rng(99)
    posts = "".join(
        f'<g transform="translate({x} {y}) scale({s})"><path d="M-170 0 L-140 -150 L140 -150 L170 0Z" fill="#3a2a1c" stroke="{OUT}" stroke-width="3"/>'
        f'<rect x="-150" y="-168" width="300" height="22" fill="#5a3e26" stroke="{OUT}" stroke-width="3"/>'
        + "".join(crt(-110 + k * 73, -205, .78) for k in range(4)) + "</g>"
        for x, y, s in [(330, 640, .8), (1600, 650, .85), (960, 600, .7)])
    rows = []
    for row, (y0, s, n, dark) in enumerate([(700, .82, 9, .45), (840, 1.0, 8, .2), (1010, 1.25, 6, 0)]):
        for k in range(n):
            x = 120 + k * (1700 / (n - 1)) + (r() - .5) * 60
            rows.append(f'<g opacity="{1 - dark * .6:.2f}">{trader(row * 10 + k, x, y0, s, r)}</g>')
    slips = "".join(f'<rect class="slip" x="{int(r() * 1900)}" y="{int(r() * 500)}" width="16" height="12" fill="#fffaf0" '
                    f'transform="rotate({int(r() * 90)} 0 0)" opacity=".85"/>' for _ in range(36))
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="fl-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2622"/><stop offset="1" stop-color="#3a2614"/></linearGradient>
 <radialGradient id="fl-glow" cx=".5" cy=".2" r=".7"><stop offset="0" stop-color="#f2a541" stop-opacity=".35"/><stop offset="1" stop-color="#f2a541" stop-opacity="0"/></radialGradient></defs>
 <rect width="1920" height="1080" fill="url(#fl-wall)"/><rect width="1920" height="1080" fill="url(#fl-glow)"/>
 <g id="o1-board" fill="#f2a541">{''.join(f'<rect x="{90 + c * 58}" y="{330 + rr * 26}" width="44" height="14" rx="2" opacity="{.25 + r() * .5:.2f}"/>' for rr in range(5) for c in range(30))}</g>
 <rect x="0" y="600" width="1920" height="480" fill="#2a1d12"/>
 {posts}<g id="o1-crowd">{''.join(rows)}</g><g id="o1-slips">{slips}</g>
</svg>"""


def ticker(id_, top, h, size, color="#f2a541", reps=3):
    txt = "   ·   ".join(QUOTES * reps)
    return (f'<div id="{id_}" style="position:absolute;left:0;top:{top}px;width:1920px;height:{h}px;background:#120c06;'
            f'border-top:3px solid #5a3e26;border-bottom:3px solid #5a3e26;overflow:hidden">'
            f'<div class="tk" style="position:absolute;left:0;top:{(h - size) // 2 - 4}px;white-space:nowrap;font:700 {size}px Inter;'
            f'letter-spacing:.06em;color:{color};text-shadow:0 0 14px {color}">{txt}</div>'
            f'<div style="position:absolute;inset:0;background:radial-gradient(circle,rgba(0,0,0,0) 1.4px,rgba(18,12,6,.55) 1.6px);background-size:6px 6px"></div></div>')


def crt_close():
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <rect width="1920" height="1080" fill="#2c2014"/>
 <rect x="0" y="820" width="1920" height="260" fill="#6b4a2f"/>
 <rect x="330" y="70" width="1260" height="860" rx="60" fill="#d9cfb6" stroke="{OUT}" stroke-width="6"/>
 <rect x="330" y="70" width="1260" height="60" rx="30" fill="#e9e1cb" opacity=".6"/>
 <rect x="420" y="140" width="1080" height="690" rx="40" fill="#0d0f14" stroke="#a89c80" stroke-width="10"/>
 <circle cx="1490" cy="880" r="14" fill="#7cff9b"/><rect x="420" y="860" width="200" height="30" rx="6" fill="#bfb59c"/>
</svg>"""


def portal():
    """1999 desktop that shows *how* the internet changed the world: messages arriving from other
    continents (communication) → an online order confirmed (commerce) → a lit network of cities
    (global connectivity)."""
    win = lambda pid, title, body, col="#000080": (
        f'<div id="{pid}" class="w98" style="opacity:0"><div class="w98t" style="background:linear-gradient(90deg,{col},#1084d0)">{title}'
        f'<span>_ □ ×</span></div><div class="w98b">{body}</div></div>')
    mails = "".join(f'<div class="mrow" id="o2-m{i}"><b>✉</b><span class="mf">{f}</span><span class="ms">{subj}</span><span class="mt">{t}</span></div>'
                    for i, (f, subj, t) in enumerate([("Aiko · Tokyo", "Photos from our trip", "2 min"), ("Lagos office", "Contract signed — thanks!", "1 min"),
                                                      ("Mum · London", "Call you Sunday?", "now")]))
    inbox = win("o2-p1", "Inbox — Mail 99", f'<div class="mhead">From <span>Subject</span></div>{mails}')
    shop = win("o2-p2", "Online Book Shop — ordering from home", """
 <div style="display:flex;gap:30px;align-items:flex-start">
  <div style="width:170px;height:230px;background:linear-gradient(135deg,#2e4a8a,#14284e);border:3px solid #000;color:#f2c66d;font:700 24px 'Times New Roman';padding:16px">A History of Money</div>
  <div style="flex:1;font:28px 'Times New Roman'"><div style="font:700 34px 'Times New Roman'">A History of Money</div><div>Hardcover · in stock</div>
   <div id="o2-add" class="w98btn" style="margin-top:20px">Add to cart</div>
   <div style="margin-top:16px">Cart: <b id="o2-cart">0</b> item</div>
   <div id="o2-ok" style="margin-top:14px;padding:10px 14px;background:#e8ffe8;border:3px solid #2e8a2e;color:#1a5a1a;font:700 28px 'Times New Roman';opacity:0">✔ Order confirmed — shipping tomorrow</div></div></div>
 <div id="o2-cur" style="position:absolute;left:520px;top:300px;width:0;height:0;border-left:16px solid #000;border-top:10px solid transparent;border-bottom:10px solid transparent;transform:rotate(-40deg)"></div>""", "#006a4e")
    arcs = "".join(f'<path class="o2-arc" d="{a}" fill="none" stroke="#f2c66d" stroke-width="7" stroke-linecap="round"/>' for a in GLOBE["arcs"])
    dots = "".join(f'<circle class="o2-dot" cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#fff1c9"/>' for x, y in GLOBE["dots"])
    net = win("o2-p3", "World Wide Web — connecting the world", f"""
 <svg viewBox="20 20 680 680" width="400" height="400" style="position:absolute;left:20px;top:10px;overflow:visible">
  <path d="{GLOBE['sphere']}" fill="#1c4a52" stroke="#f2a541" stroke-width="4"/><path d="{GLOBE['land']}" fill="#c9a56a" stroke="#f3e3c3" stroke-width="2"/>{arcs}{dots}</svg>
 <div style="position:absolute;left:460px;top:60px;font:700 34px 'Times New Roman';line-height:2.1;color:#000080">
  <div class="o2-li">Messages in seconds</div><div class="o2-li">Shops open all night</div><div class="o2-li">News from everywhere</div><div class="o2-li">One network, worldwide</div></div>""", "#5a1a6a")
    return f"""<div id="o2-screen" style="position:absolute;left:440px;top:160px;width:1040px;height:650px;border-radius:32px;overflow:hidden;background:#008080;font-family:'Times New Roman',serif">
 <div style="position:absolute;left:0;right:0;bottom:0;height:52px;background:#c0c0c0;border-top:3px solid #fff;display:flex;align-items:center;gap:12px;padding:0 12px;font:700 26px 'Times New Roman'">
  <div class="w98btn" style="padding:2px 14px">Start</div><div id="o2-task" style="margin-left:auto;font:24px 'Times New Roman'">Connected · 56k</div></div>
 {inbox}{shop}{net}
 <div id="o2-reflect" style="position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(56,214,255,0) 0 60px,rgba(56,214,255,.14) 60px 66px);opacity:0;mix-blend-mode:screen"></div>
 <div style="position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.18) 0 2px,rgba(0,0,0,0) 2px 5px)"></div>
</div>"""


O2_CSS = """
.w98{position:absolute;left:40px;top:30px;width:960px;height:540px;background:#c0c0c0;border:3px outset #fff;box-shadow:6px 6px 0 rgba(0,0,0,.4)}
.w98t{height:52px;color:#fff;font:700 30px 'Times New Roman';padding:8px 16px;display:flex;justify-content:space-between}
.w98b{position:relative;margin:10px;height:452px;background:#fff;border:3px inset #999;padding:18px 24px;overflow:hidden}
.w98btn{display:inline-block;background:#d4d0c8;border:3px outset #fff;padding:6px 20px;font:28px 'Times New Roman';color:#000}
.mhead{font:700 26px 'Times New Roman';color:#555;border-bottom:2px solid #999;padding-bottom:6px}.mhead span{margin-left:240px}
.mrow{display:flex;gap:18px;align-items:center;height:96px;border-bottom:1px solid #ccc;font:30px 'Times New Roman';opacity:0}
.mrow b{color:#000080;font-size:38px}.mf{width:230px;font-weight:700}.ms{flex:1}.mt{color:#800000;font-size:24px}
"""


def office_svg():
    r = rng(7)
    cubes = "".join(
        f'<g transform="translate({120 + c * 300} {470 + row * 150}) scale({.7 + row * .18})">'
        f'<rect x="-120" y="-20" width="240" height="90" fill="#8a7a62" stroke="{OUT}" stroke-width="3"/>'
        f'<rect x="-120" y="-30" width="240" height="14" fill="#a8977a" stroke="{OUT}" stroke-width="2"/>{crt(-40, -70, .8)}</g>'
        for row in range(3) for c in range(6))
    lights = "".join(f'<rect class="o3-light" id="o3-light{i}" x="{80 + i * 300}" y="40" width="220" height="26" rx="6" fill="#fff4cf"/>'
                     f'<path class="o3-cone" id="o3-cone{i}" d="M{80 + i * 300} 66 L{300 + i * 300} 66 L{360 + i * 300} 420 L{20 + i * 300} 420Z" fill="#fff4cf" opacity=".10"/>'
                     for i in range(6))
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <rect width="1920" height="1080" fill="#4a3a2a"/><rect y="0" width="1920" height="90" fill="#3a2c20"/>
 <rect y="760" width="1920" height="320" fill="#5a4630"/>{lights}{cubes}
 <rect id="o3-dark" width="1920" height="1080" fill="#0a0806" opacity="0"/>
</svg>"""


def globe_svg():
    arcs = "".join(f'<path class="o3-arc" d="{a}" fill="none" stroke="#f2c66d" stroke-width="3.5" stroke-linecap="round"/>' for a in GLOBE["arcs"])
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#fff1c9"/>' for x, y in GLOBE["dots"])
    shards = "".join(f'<path class="o3-shard" d="M0 0 L{24 + (i * 7) % 30} {10 + (i * 11) % 20} L{6 + (i * 5) % 14} {30 + (i * 3) % 18}Z" fill="#d9503f"/>' for i in range(16))
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><radialGradient id="gl-sea" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#2f5f66"/><stop offset="1" stop-color="#10262b"/></radialGradient>
 <radialGradient id="gl-bg" cx=".5" cy=".5" r=".7"><stop offset="0" stop-color="#3a2a18"/><stop offset="1" stop-color="#140d07"/></radialGradient></defs>
 <rect width="1920" height="1080" fill="url(#gl-bg)"/>
 <g id="o3-globe" transform="translate(410 70)">
  <path d="{GLOBE['sphere']}" fill="url(#gl-sea)" stroke="#f2a541" stroke-width="3"/>
  <path d="{GLOBE['grat']}" fill="none" stroke="#f2a541" stroke-opacity=".18"/>
  <path d="{GLOBE['land']}" fill="#c9a56a" stroke="#f3e3c3" stroke-width="1.2" opacity=".9"/>
  {arcs}{dots}
 </g>
 <g id="o3-balloon" transform="translate(770 300)" opacity="0">
  <path d="M0 -150 C110 -150 150 -40 120 40 C95 110 30 150 0 170 C-30 150 -95 110 -120 40 C-150 -40 -110 -150 0 -150Z" fill="#d9503f" stroke="{OUT}" stroke-width="5"/>
  <path d="M-60 -100 C-30 -130 20 -130 40 -110" stroke="#ffb3a6" stroke-width="12" fill="none" stroke-linecap="round" opacity=".7"/>
  <text x="0" y="20" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="74" fill="#fff4cf">.com</text>
  <path d="M0 170 L-10 196 L10 196Z" fill="#a63a2c"/><path d="M0 196 C30 260 -30 300 10 380" stroke="#f3e3c3" stroke-width="3" fill="none"/>
 </g>
 <g id="o3-shards" transform="translate(770 300)">{shards}</g>
</svg>"""


def screens_svg():
    import math
    panels = []
    for i in range(6):
        x, y = 640 + (i % 3) * 420, 120 + (i // 3) * 300
        pts = " ".join(f"{20 + k * 18},{230 - (k * 6 + 30 * math.sin(k * .5 + i)) * .9 - k * k * .25:.0f}" for k in range(20))
        panels.append(f'<g transform="translate({x} {y})"><rect width="390" height="260" rx="14" fill="#0a1426" stroke="#2a4a6e" stroke-width="4"/>'
                      f'<path d="M20 230 H370 M20 160 H370 M20 90 H370" stroke="#18304e" stroke-width="2"/>'
                      f'<polyline class="o5-line" points="{pts}" fill="none" stroke="{["#38d6ff", "#4ee28a", "#f2c66d"][i % 3]}" stroke-width="6" stroke-linecap="round"/>'
                      f'<g class="o5-icon" opacity="0">{icon(i)}</g></g>')
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="o5-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#07101f"/><stop offset="1" stop-color="#0f2236"/></linearGradient></defs>
 <rect width="1920" height="1080" fill="url(#o5-bg)"/><rect y="760" width="1920" height="320" fill="#0a1626"/>
 <path d="M0 760 H1920" stroke="#38d6ff" stroke-opacity=".3" stroke-width="3"/>{''.join(panels)}
 <rect x="80" y="690" width="520" height="22" rx="8" fill="#1b2a44"/><rect x="560" y="712" width="20" height="60" fill="#1b2a44"/>
</svg>"""


def icon(i):
    c = "#38d6ff"
    shapes = [
        f'<rect x="165" y="80" width="60" height="120" fill="{c}"/><rect x="135" y="110" width="120" height="60" fill="{c}"/>',  # medicine
        f'<path d="M110 200 V120 L160 145 V120 L210 145 V90 H250 V200Z" fill="{c}"/>',  # factory
        f'<path d="M110 170 L140 120 H250 L280 170 V195 H110Z" fill="{c}"/><circle cx="150" cy="198" r="16" fill="#0a1426" stroke="{c}" stroke-width="8"/><circle cx="240" cy="198" r="16" fill="#0a1426" stroke="{c}" stroke-width="8"/>',  # car
        f'<path d="M120 110 L195 70 L270 110Z" fill="{c}"/>' + "".join(f'<rect x="{132 + k * 34}" y="118" width="16" height="70" fill="{c}"/>' for k in range(4)) + f'<rect x="118" y="192" width="154" height="12" fill="{c}"/>',  # bank
        f'<path d="M110 90 H140 L165 170 H250 L270 110 H150" fill="none" stroke="{c}" stroke-width="12"/><circle cx="175" cy="195" r="12" fill="{c}"/><circle cx="240" cy="195" r="12" fill="{c}"/>',  # retail
        f'<circle cx="195" cy="135" r="62" fill="none" stroke="{c}" stroke-width="12"/><path d="M175 105 L230 135 L175 165Z" fill="{c}"/>',  # media
    ]
    return shapes[i]


def build():
    t01s, _ = L("c01_01")
    t02s, t02e = L("c01_02")
    t03s, _ = L("c01_03")
    t04s, t04e = L("c01_04")
    t05s, _ = L("c01_05")
    t06s, _ = L("c01_06")
    t07s, t07e = L("c01_07")
    w_trill, w_dis = W("trillions", "c01_03"), W("disappearing", "c01_03")
    w_comp, w_inv, w_and, w_spec = W("Companies", "c01_04"), W("Investors", "c01_04"), W("And", "c01_04"), W("spectacular", "c01_04")
    w_money = W("money", "c01_05")
    w_semi, w_inv7, w_trans = W("Semiconductor", "c01_07"), W("Investors", "c01_07"), W("transform", "c01_07")
    scenes, regions = [], []

    # ── s001: 1999 trading floor ─────────────────────────────────────
    o1_end = W("change", "c01_01") - .2
    fl_html, fl_js = floor_scene("fl", 0, round(o1_end + .3, 3), "boom",
                                 cam={"s0": 1.0, "s1": 1.16, "x0": 40, "x1": -60, "y0": 10, "y1": -20, "origin": "50% 42%"})
    scenes.append(Scene("o1", 0, round(o1_end + .3, 3),
        fl_html + '<div class="tag v" id="o1-tag">New York · 1999</div>',
        css=FLOOR_CSS,
        js=fl_js + f"""
show('#o1-tag',.4); hide('#o1-tag',{t01s + 4.2});
"""))

    # ── s002: CRT close-up "They were right." ──────────────────────────
    w_change, w_world, w_they, w_right = W("change", "c01_01"), W("world", "c01_01"), W("They", "c01_02"), W("right", "c01_02")
    scenes.append(Scene("o2", round(o1_end, 3), round(t03s + .25 - o1_end, 3),
        f'<div id="o2-cam" class="cam">{crt_close()}{portal()}</div>',
        css=O2_CSS,
        js=f"""
tl.fromTo('#o2',{{opacity:0}},{{opacity:1,duration:.15}},{o1_end});
tl.fromTo('#o2-cam',{{scale:1.12}},{{scale:1.0,duration:{t03s - o1_end + .25},ease:'power2.out'}},{o1_end});
// communication: mail from three continents arrives on "change"
tl.fromTo('#o2-p1',{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.18,ease:'steps(3)'}},{o1_end + .05});
[0,1,2].forEach(i=>tl.fromTo('#o2-m'+i,{{opacity:0,x:-80}},{{opacity:1,x:0,duration:.16}},{w_change}+i*.2));
// commerce: an order placed from home on "world"
tl.fromTo('#o2-p2',{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.18,ease:'steps(3)'}},{w_world - .15});
tl.fromTo('#o2-cur',{{x:120,y:120}},{{x:-280,y:-60,duration:.35,ease:'power2.out'}},{w_world});
tl.to('#o2-add',{{borderStyle:'inset',duration:.05}},{w_world + .38}); tl.set('#o2-cart',{{textContent:'1'}},{w_world + .42});
tl.fromTo('#o2-ok',{{opacity:0,y:10}},{{opacity:1,y:0,duration:.15}},{w_world + .5});
// connectivity: the network of cities lights up on "They were right"
tl.fromTo('#o2-p3',{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.18,ease:'steps(3)'}},{w_they - .15});
document.querySelectorAll('.o2-arc').forEach((a,i)=>{{const n=a.getTotalLength();gsap.set(a,{{strokeDasharray:n,strokeDashoffset:n}});tl.to(a,{{strokeDashoffset:0,duration:.45,ease:'power2.out'}},{w_they}+i*.07);}});
tl.fromTo('.o2-li',{{opacity:0,x:30}},{{opacity:1,x:0,duration:.15,stagger:.14}},{w_they});
tl.fromTo('.o2-dot',{{scale:0,transformOrigin:'50% 50%'}},{{scale:1,duration:.2,stagger:.05}},{w_they});
tl.fromTo('#o2-reflect',{{opacity:0}},{{opacity:1,duration:.4}},{t02e - .1});
"""))

    # ── s003: the seam — 1999 collapses beside a live AI data hall ─────
    seam_open = w_trill - .2
    s3_start, s3_end = t03s - .05, t05s + 1.7
    fp_html, fp_js = floor_scene("fp", round(s3_start, 3), round(w_comp + .2, 3), "panic", crash_at=w_trill - .3,
                                 cam={"s0": 1.12, "s1": 1.3, "x0": -80, "x1": 60, "y0": -30, "y1": 10, "origin": "30% 55%", "par": -.6})
    left = (f'<div id="o3-left" class="fill" style="background:#140d07">'
            f'<div id="o3a" class="fill">{fp_html}'
            f'<div id="o3-digits" class="fill"></div></div>'
            f'<div id="o3b" class="fill" style="opacity:0">{office_svg()}'
            f'<div id="o3-dan-wrap" style="position:absolute;inset:0">{person_svg("dan", "dan_1999", "box").replace(chr(39)+"char "+chr(39), "char").replace(chr(34)+"char "+chr(34), chr(34)+"char"+chr(34)+" style=" + chr(34) + "left:1320px;top:360px;width:300px;height:500px" + chr(34))}</div>'
            f'<div id="o3-inv" style="position:absolute;left:40px;top:420px;width:520px;height:620px;opacity:0">'
            f'<svg viewBox="0 0 520 620" class="full" style="width:520px;height:620px">{crt(330, 250, 2.2, "#d9503f")}'
            f'<polyline id="o3-crash" points="-60,-20 -40,-28 -20,-18 0,-30 20,10 40,24" transform="translate(330 250) scale(2.2)" fill="none" stroke="#ff6a55" stroke-width="3"/></svg>'
            f'{person_svg("inv", "investor_1999", "bust").replace(chr(34)+"char "+chr(34), chr(34)+"char"+chr(34)+" style=" + chr(34) + "left:-40px;top:200px;width:360px;height:432px" + chr(34))}</div></div>'
            f'<div id="o3d" class="fill" style="opacity:0">{globe_svg()}</div></div>')
    scenes.append(Scene("o3", round(s3_start, 3), round(s3_end - s3_start, 3),
        left + '<div id="o3-seam" style="position:absolute;top:0;width:6px;height:1080px;left:1914px;background:linear-gradient(#f2c66d,#d4a24c);box-shadow:0 0 22px #f2c66d,0 0 60px rgba(242,198,109,.6)"></div>'
        '<div class="year" id="o3-y99" style="left:70px;top:52px;color:#f2a541">1999</div>'
        '<div class="year" id="o3-y26" style="right:60px;top:52px;color:#38d6ff;text-shadow:0 0 18px rgba(56,214,255,.7)">2026</div>',
        css="#o3-left{clip-path:inset(0 0 0 0)}",
        js=fp_js + f"""
(function(){{const box=document.getElementById('o3-digits');
 for(let i=0;i<40;i++){{const d=document.createElement('div');d.className='dg';d.textContent=['⅛','¼','½','$','▼','7','3','9','⅞','%'][i%10];
  d.style.cssText='position:absolute;left:'+((i*137)%1860)+'px;top:'+(240+(i%2)*200)+'px;font:800 '+(40+(i*7)%40)+'px Inter;color:#ff5a46;opacity:0';box.appendChild(d);
  tl.fromTo(d,{{opacity:0,y:0,rotation:0}},{{opacity:1,duration:.15}},{w_trill}+(i%13)*.12);
  tl.to(d,{{y:520+(i%5)*60,rotation:(i%2?1:-1)*(60+i*7),opacity:0,duration:1.8+(i%4)*.2,ease:'power2.in'}},{w_trill + .15}+(i%13)*.12);}}}})();
tl.fromTo('#o3-left',{{clipPath:'inset(0 0% 0 0)'}},{{clipPath:'inset(0 22% 0 0)',duration:.9,ease:'power3.inOut'}},{seam_open});
tl.fromTo('#o3-seam',{{x:0,opacity:0}},{{x:-422,opacity:1,duration:.9,ease:'power3.inOut'}},{seam_open});
show('#o3-y99',{seam_open + .5}); show('#o3-y26',{seam_open + .7});
// Companies collapsed → office goes dark, the founder walks out with his box
tl.to('#o3a',{{opacity:0,duration:.35}},{w_comp - .2}); tl.fromTo('#o3b',{{opacity:0}},{{opacity:1,duration:.35}},{w_comp - .2});
[0,1,2,3,4,5].forEach(i=>{{tl.to(['#o3-light'+i,'#o3-cone'+i],{{opacity:0,duration:.08}},{w_comp + .25}+i*.22);}});
tl.to('#o3-dark',{{opacity:.45,duration:1.2}},{w_comp + .2});
tl.fromTo('#o3-dan-wrap',{{x:0}},{{x:-900,duration:{w_and - w_comp - .2},ease:'none'}},{w_comp + .2});
for(let i=0;i<10;i++){{const a=i%2?-18:18,t={w_comp + .2}+i*.38;
 tl.to('#dan-leg-front',{{rotation:a,svgOrigin:'150 330',duration:.38,ease:'sine.inOut'}},t);
 tl.to('#dan-leg-back',{{rotation:-a,svgOrigin:'150 330',duration:.38,ease:'sine.inOut'}},t);
 tl.to('#dan-upper',{{y:-5,duration:.19,yoyo:true,repeat:1,ease:'sine.inOut'}},t);}}
tl.set('#dan',{{scaleX:-1}},{w_comp});
// Investors lost fortunes → foreground investor, red crash on his screen
show('#o3-inv',{w_inv - .15},.35);
tl.fromTo('#o3-crash',{{strokeDasharray:'200 200',strokeDashoffset:200}},{{strokeDashoffset:0,duration:.9,ease:'power2.in'}},{w_inv});
tl.to('#inv-upper',{{rotation:6,svgOrigin:'150 330',duration:.8,ease:'power2.out'}},{w_inv + .7});
tl.to('#inv-mouth',{{scaleY:-1,transformOrigin:'50% 50%',duration:.3}},{w_inv + .5});
blink('#inv .lid',[{w_inv + .3},{w_inv + 1.4}]);
// …one of the greatest technological revolutions → the internet globe; "spectacular disasters" → .com balloon pops
tl.to('#o3b',{{opacity:0,duration:.45}},{w_and - .2}); tl.fromTo('#o3d',{{opacity:0}},{{opacity:1,duration:.45}},{w_and - .2});
tl.fromTo('#o3-globe',{{scale:.9,transformOrigin:'360px 360px'}},{{scale:1.04,duration:{w_spec - w_and + 2},ease:'sine.out'}},{w_and - .2});
document.querySelectorAll('.o3-arc').forEach((a,i)=>{{const len=a.getTotalLength();tl.fromTo(a,{{strokeDasharray:len,strokeDashoffset:len}},{{strokeDashoffset:0,duration:.9,ease:'power2.out'}},{w_and}+i*.28);}});
tl.fromTo('#o3-balloon',{{opacity:0,scale:.2,transformOrigin:'0px 170px'}},{{opacity:1,scale:1.15,duration:1.6,ease:'power1.in'}},{w_spec - .6});
tl.to('#o3-balloon',{{scale:1.3,duration:.25,ease:'power4.in'}},{t04e - 1.3}); tl.to('#o3-balloon',{{opacity:0,duration:.05}},{t04e - 1.05});
document.querySelectorAll('.o3-shard').forEach((s,i)=>{{const a=i/16*Math.PI*2;tl.fromTo(s,{{x:0,y:0,opacity:0}},{{x:Math.cos(a)*(260+i*9),y:Math.sin(a)*(220+i*7)+120,rotation:i*40,opacity:1,duration:.9,ease:'power2.out'}},{t04e - 1.05});tl.to(s,{{opacity:0,duration:.4}},{t04e - .25});}});
tl.to('#o3-globe path',{{filter:'grayscale(1)',duration:.6}},{t04e - 1});
// two decades later → seam sweeps 1999 away; the AI hall fills the frame
tl.to('#o3-left',{{clipPath:'inset(0 100% 0 0)',duration:1.6,ease:'power2.inOut'}},{t05s});
tl.to('#o3-seam',{{x:-1940,duration:1.6,ease:'power2.inOut'}},{t05s}); hide('#o3-seam',{t05s + 1.5},.2);
hide('#o3-y99',{t05s + .2}); tl.to('#o3-y26',{{x:-1560,duration:1.6,ease:'power2.inOut'}},{t05s}); hide('#o3-y26',{t05s + 3.5});
"""))
    regions.append(("hall-open", [(s3_start, t07s + .05)], f"""AI3D.add('hall-open',{{start:{s3_start},end:{t07s + .05},world:'dataHall',
 keys:[[{s3_start},[1.2,1.6,2.5],[-5.5,1.5,-9],52],[{t05s - .1},[1.0,1.6,0.5],[-5.0,1.5,-11],52],[{t05s + 1.6},[0,1.55,-2],[.3,1.45,-14],52],[{t07s + .05},[0,1.5,-14],[0,1.4,-40],52]],
 gold:[{w_money - 3.2},{t06s + .3}],pulse:{t06s}}});"""))

    # ── s005: campus → chip → investors & industries ──────────────────
    regions.append(("campus-open", [(t07s, w_semi)], f"""AI3D.add('campus-open',{{start:{t07s},end:{w_semi},world:'campus',
 cam:{{from:[-112,2.4,52],to:[-90,3.6,45],look:[-60,7,0],lookTo:[-38,22,-58],dur:{w_semi - t07s}}},build:[{W('constructing', 'c01_07') - .3},{w_semi - .9}]}});"""))
    regions.append(("chip-open", [(w_semi, w_inv7)], f"""AI3D.add('chip-open',{{start:{w_semi},end:{w_inv7},world:'chip',
 cam:{{from:[-6,2.6,5.2],to:[1.5,2.0,4.4],look:[-3,0,-.6],lookTo:[3.5,0,-.8],dur:{w_inv7 - w_semi}}},batch:true,glow:{w_semi}}});"""))
    scenes.append(Scene("o5dip", round(t07s - .25, 3), round(w_inv7 - t07s + .5, 3),
        '<div id="o5-dip" class="fill" style="background:#02040a;opacity:0"></div>'
        '<div class="tag m" id="o5-tag1">Data centres</div><div class="tag m" id="o5-tag2" style="top:52px">Processors</div>',
        js=f"""
tl.fromTo('#o5-dip',{{opacity:0}},{{opacity:1,duration:.22}},{t07s - .25}); tl.to('#o5-dip',{{opacity:0,duration:.3}},{t07s});
tl.fromTo('#o5-dip',{{opacity:0}},{{opacity:1,duration:.18}},{w_semi - .2}); tl.to('#o5-dip',{{opacity:0,duration:.25}},{w_semi});
show('#o5-tag1',{t07s + .5}); hide('#o5-tag1',{w_semi - .4},.2); show('#o5-tag2',{w_semi + .4}); hide('#o5-tag2',{w_inv7 - .4},.2);
"""))
    maya = maya_svg("mo", "bust").replace('class="char "', 'class="char" style="left:120px;top:330px;width:460px;height:552px"')
    scenes.append(Scene("o5", round(w_inv7 - .25, 3), round(t07e + .5 - w_inv7 + .25, 3),
        f'<div id="o5-cam" class="cam">{screens_svg()}{maya}</div><div class="tag m" id="o5-tag3">Illustrative</div>',
        js=f"""
tl.fromTo('#o5',{{opacity:0}},{{opacity:1,duration:.3}},{w_inv7 - .25});
tl.fromTo('#o5-cam',{{scale:1.08,x:40}},{{scale:1.0,x:0,duration:{t07e - w_inv7 + .5},ease:'sine.out'}},{w_inv7 - .25});
document.querySelectorAll('.o5-line').forEach((l,i)=>{{const len=l.getTotalLength();tl.fromTo(l,{{strokeDasharray:len,strokeDashoffset:len}},{{strokeDashoffset:0,duration:1.6,ease:'power2.out'}},{w_inv7}+i*.15);}});
show('#o5-tag3',{w_inv7 + .3}); hide('#o5-tag3',{w_trans - .3});
tl.to('.o5-line',{{opacity:0,duration:.3}},{w_trans - .1});
document.querySelectorAll('.o5-icon').forEach((g,i)=>tl.fromTo(g,{{opacity:0,scale:.5,transformOrigin:'195px 135px'}},{{opacity:1,scale:1,duration:.45,ease:'back.out(2)'}},{w_trans}+i*.16));
tl.to('#mo-upper',{{rotation:-4,svgOrigin:'150 330',duration:.8,ease:'sine.inOut'}},{w_trans - .2});
blink('#mo .lid',[{w_inv7 + .6},{w_trans + .9}]);
"""))
    return scenes, regions, ""
