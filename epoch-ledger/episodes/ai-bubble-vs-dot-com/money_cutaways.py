"""Operation cutaways for the money-flow model (c05_02–c05_05).

Scene brief (per company: introduction → operation → transaction)
  Chip maker   "semiconductor" fab rises (3D) · "produces" wafer patterned, cut, packaged · "chips" boxed and shipped
  Cloud        "cloud" data centre rises · "purchases" chips travel, payment returns · "installs" boards slid into
               racks, capacity meter fills · "data centre" capacity on offer
  AI developer "AI" lab rises · "rents" capacity flows in, rent paid · "train" network learns (error falls) ·
               "operate" requests in → answers out
  Customers    "businesses" homes/offices rise · "pay" subscription paid · "use" AI answering real tasks
All quantities are illustrative; no company or figure is implied.
"""
from kit.characters import OUT
from kit.rig import crowd_look, rig_svg
from floor import place

O = OUT


def person(i, **o):
    c = crowd_look(i)
    c.update(dict(tie=None, badge=False))
    c.update(o)
    return c


def suit(i):
    return person(i, jacket="#e8eef4", jacket_sh="#c8d2dc", jacket_hi="#ffffff", shirt="#dfe6ee", pants="#e0e6ec", pants_sh="#c0c8d2",
                  hat="bonnet", hat_col="#f4f7fa", glasses=True)


def frame(px, title, step_labels, bg, inner):
    steps = "".join(f'<div class="mc-step" id="{px}-s{i}"><b>{i + 1}</b>{t}</div>' for i, t in enumerate(step_labels))
    return (f'<div id="{px}" class="mc-cut" style="opacity:0">{bg}{inner}'
            f'<div class="mc-title">{title}</div><div class="mc-steps">{steps}</div></div>')


CSS = """
.mc-cut{position:absolute;inset:0;overflow:hidden;clip-path:circle(0% at 50% 50%)}
.mc-title{position:absolute;left:56px;top:100px;font:800 44px Fraunces;color:#fff;background:rgba(5,10,22,.82);padding:4px 18px;border-radius:10px}
.mc-steps{position:absolute;left:56px;top:180px;display:flex;flex-direction:column;gap:10px}
.mc-step{display:flex;gap:12px;align-items:center;font:700 30px Inter;color:#e8f3ff;background:rgba(5,10,22,.72);padding:6px 16px 6px 8px;border-radius:10px;opacity:0}
.mc-step b{display:inline-flex;width:38px;height:38px;border-radius:50%;background:#38d6ff;color:#05101c;align-items:center;justify-content:center}
.mc-tok{position:absolute;opacity:0}
"""


def iris(px, t_in, t_out, cx, cy):
    """Circular cut into the interior from the company's position, and back out to the model."""
    return (f"tl.set('#{px}',{{opacity:1}},{t_in});"
            f"tl.fromTo('#{px}',{{clipPath:'circle(0% at {cx}px {cy}px)'}},{{clipPath:'circle(150% at {cx}px {cy}px)',duration:.5,ease:'power2.in'}},{t_in});"
            f"tl.to('#{px}',{{clipPath:'circle(0% at {cx}px {cy}px)',duration:.45,ease:'power2.out'}},{t_out});"
            f"tl.set('#{px}',{{opacity:0}},{t_out + .46});")


def steps_js(px, times):
    return "".join(f"tl.fromTo('#{px}-s{i}',{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.2}},{t});" for i, t in enumerate(times))


# ── 1. chip fab: pattern → cut → package → ship ─────────────────────────────────────────────────
def fab(px, t_in, t_out, t):
    """t: dict(pattern, cut, pack, ship)."""
    dies = "".join(f'<rect x="{-150 + c * 38}" y="{-150 + r * 38}" width="32" height="32" fill="#4a6ab0" opacity=".0" class="{px}-die"/>'
                   for r in range(8) for c in range(8) if (c - 3.5) ** 2 + (r - 3.5) ** 2 < 17)
    bg = f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <rect width="1920" height="1080" fill="#f4eed2"/>
 {''.join(f'<rect x="{x}" y="0" width="236" height="120" fill="#fffbe8" stroke="#d8cfa8" stroke-width="4"/>' for x in range(0, 1920, 240))}
 {''.join(f'<path d="M{x} 120 V760" stroke="#e2d9b6" stroke-width="3"/>' for x in range(0, 1920, 160))}
 <rect y="760" width="1920" height="320" fill="#d9d2b8"/>{''.join(f'<path d="M0 {y} H1920" stroke="#c9c1a4" stroke-width="2"/>' for y in range(780, 1080, 40))}
 <!-- lithography scanner -->
 <g transform="translate(560 250)"><rect width="520" height="480" rx="20" fill="#dfe3ea" stroke="{O}" stroke-width="5"/>
  <rect x="30" y="30" width="460" height="70" rx="8" fill="#8a96a8"/><rect x="200" y="100" width="120" height="120" fill="#5a6678" stroke="{O}" stroke-width="4"/>
  <path id="{px}-beam" d="M235 220 L285 220 L330 380 L190 380Z" fill="#b48cff" opacity="0"/>
  <rect x="70" y="380" width="380" height="60" rx="8" fill="#6a7486" stroke="{O}" stroke-width="4"/>
  <g transform="translate(260 340) scale(.5)"><circle r="170" fill="#9aa8c8" stroke="{O}" stroke-width="8"/>{dies}</g>
  <rect x="40" y="450" width="140" height="26" rx="6" fill="#38d6ff" opacity=".6"/></g>
 <!-- dicing + packaging line -->
 <rect x="1120" y="600" width="760" height="40" rx="8" fill="#8a96a8" stroke="{O}" stroke-width="4"/>
 {''.join(f'<circle cx="{1140 + k * 46}" cy="640" r="12" fill="#5a6678"/>' for k in range(17))}
 <g transform="translate(1180 430)"><rect width="200" height="170" rx="12" fill="#c9d0da" stroke="{O}" stroke-width="5"/><circle id="{px}-saw" cx="100" cy="120" r="44" fill="#e0e4ea" stroke="{O}" stroke-width="5"/>
  {''.join(f'<path d="M100 120 L{100 + 44 * __import__("math").cos(k * .785):.0f} {120 + 44 * __import__("math").sin(k * .785):.0f}" stroke="{O}" stroke-width="3" class="{px}-tooth"/>' for k in range(8))}</g>
 <g transform="translate(1560 470)"><rect width="260" height="130" rx="12" fill="#a8885a" stroke="{O}" stroke-width="5"/>
  <text x="130" y="76" text-anchor="middle" font-family="Inter" font-weight="800" font-size="26" fill="#fff8e0">ADVANCED CHIPS</text></g>
</svg>"""
    chips = "".join(f'<div class="mc-tok {px}-chip" style="left:1400px;top:572px;width:46px;height:30px;border-radius:5px;background:#2a3446;border:3px solid #b8892e"></div>' for _ in range(5))
    wafer = (f'<div id="{px}-wafer" class="mc-tok" style="left:780px;top:520px;width:110px;height:110px;border-radius:50%;background:radial-gradient(#b8c4dc,#7a8ab0);border:4px solid {O};opacity:1"></div>'
             f'<div id="{px}-arm" style="position:absolute;left:1000px;top:330px;width:26px;height:200px;background:#8a96a8;border:4px solid {O};border-radius:13px;transform-origin:13px 0;transform:rotate(30deg)"></div>')
    techs = (place(rig_svg(f"{px}t1", suit(3), "full", prop_front="pad"), 300, 470, 190)
             + place(rig_svg(f"{px}t2", suit(8), "full"), 1060, 480, 180, flip=True))
    html = frame(px, "Inside the chip maker", ["Pattern circuits onto a wafer", "Cut it into individual chips", "Test and package each chip", "Ship to customers"], bg, wafer + chips + techs)
    js = [iris(px, t_in, t_out, 560, 520), steps_js(px, [t["pattern"], t["cut"], t["pack"], t["ship"]]),
          f"tl.fromTo('#{px}-beam',{{opacity:0}},{{opacity:.85,duration:.1,yoyo:true,repeat:5}},{t['pattern']});",
          f"tl.to('.{px}-die',{{opacity:.95,duration:.06,stagger:.012}},{t['pattern'] + .1});",
          f"rpose('{px}t1','write',{t_in + .2},.3); rpose('{px}t1','point',{t['pattern']},.3); rpose('{px}t2','type',{t_in + .1},.3);",
          f"tl.to('#{px}-arm',{{rotation:-30,duration:.35,ease:'power2.inOut'}},{t['cut'] - .3});",
          f"tl.to('#{px}-wafer',{{x:440,y:-40,scale:.7,duration:.4,ease:'power2.inOut'}},{t['cut'] - .2});",
          f"tl.to('#{px}-saw',{{rotation:720,svgOrigin:'1280 550',duration:.8,ease:'none'}},{t['cut']});",
          f"tl.to('#{px}-wafer',{{opacity:0,duration:.15}},{t['cut'] + .5});",
          f"document.querySelectorAll('.{px}-chip').forEach((c,i)=>{{tl.fromTo(c,{{opacity:0,x:0}},{{opacity:1,x:0,duration:.1}},{t['pack']}+i*.12);"
          f"tl.to(c,{{x:200,duration:.4,ease:'none'}},{t['pack'] + .1}+i*.12);tl.to(c,{{opacity:0,duration:.1}},{t['pack'] + .5}+i*.12);}});",
          f"rpose('{px}t2','carry',{t['ship'] - .2},.25);"]
    return html, "\n".join(js)


# ── 2. cloud provider: chips installed, capacity supplied ──────────────────────────────────────
def cloud(px, t_in, t_out, t):
    rack = lambda x, rid: (f'<g transform="translate({x} 220)"><rect width="230" height="560" rx="8" fill="#1a2230" stroke="#0a0e14" stroke-width="5"/>'
                           + "".join(f'<g class="{px}-slot{rid}"><rect x="14" y="{16 + k * 52}" width="202" height="44" rx="4" fill="#232c3a"/>'
                                     f'<rect class="{px}-led" x="190" y="{30 + k * 52}" width="14" height="10" fill="#2a3446"/></g>' for k in range(10)) + '</g>')
    bg = f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <rect width="1920" height="1080" fill="#0b1220"/>
 {''.join(f'<rect x="{x}" y="60" width="140" height="40" fill="#1f2a3c"/>' for x in range(40, 1920, 200))}
 <rect y="780" width="1920" height="300" fill="#141c2a"/>{''.join(f'<path d="M{x} 780 L{x - 200} 1080" stroke="#1f2a3c" stroke-width="3"/>' for x in range(0, 2200, 120))}
 {''.join(rack(x, i) for i, x in enumerate((720, 980, 1240, 1500)))}
 <g transform="translate(160 600)">{''.join(f'<rect x="{k * 90}" y="{-k % 2 * 60}" width="80" height="60" fill="#a8885a" stroke="{O}" stroke-width="3"/>' for k in range(4))}
  <text x="160" y="110" text-anchor="middle" font-family="Inter" font-weight="800" font-size="26" fill="#c9d6e6">chips delivered</text></g>
</svg>"""
    sled = (f'<div id="{px}-sled" style="position:absolute;left:420px;top:560px;width:202px;height:44px;border-radius:4px;background:#2e6a4a;border:3px solid #7fdc8a"></div>')
    tech = f'<div id="{px}-techw" style="position:absolute;inset:0">' + place(rig_svg(f"{px}t", person(21, hat="cap", hat_col="#38d6ff"), "full"), 300, 470, 190) + '</div>'
    meter = (f'<div id="{px}-cap" style="position:absolute;right:56px;top:110px;width:440px;padding:16px 20px;border-radius:12px;background:rgba(5,10,22,.85);border:3px solid #38d6ff;'
             f'font:800 30px Inter;color:#e8f3ff">Computing capacity for rent<div style="margin-top:10px;height:28px;border-radius:14px;background:#16233a;overflow:hidden">'
             f'<div id="{px}-capbar" style="height:100%;width:0;background:linear-gradient(90deg,#38d6ff,#9ff3ff)"></div></div></div>')
    html = frame(px, "Inside the cloud provider", ["Unpack the purchased chips", "Install them in servers", "Power up: capacity ready to rent"], bg, sled + tech + meter)
    js = [iris(px, t_in, t_out, 760, 640), steps_js(px, [t_in + .3, t["install"], t["ready"]]),
          f"rpose('{px}t','carry',{t_in + .1},.2); rwalk('{px}t','#{px}-techw',{t_in + .2},4,.32,300); rpose('{px}t','lift',{t['install'] + .1},.25);",
          f"tl.fromTo('#{px}-sled',{{x:0,y:0}},{{x:316,y:-300,duration:.6,ease:'power2.inOut'}},{t['install']});",
          f"tl.to('#{px}-sled',{{opacity:0,duration:.1}},{t['install'] + .6});",
          f"document.querySelectorAll('.{px}-slot0 rect:first-child, .{px}-slot1 rect:first-child, .{px}-slot2 rect:first-child, .{px}-slot3 rect:first-child').forEach((r,i)=>"
          f"tl.to(r,{{fill:'#2e6a4a',duration:.08}},{t['install'] + .5}+i*.025));",
          f"document.querySelectorAll('.{px}-led').forEach((l,i)=>{{tl.to(l,{{fill:'#7fe9ff',duration:.05}},{t['ready']}+(i%10)*.03+Math.floor(i/10)*.08);"
          f"tl.to(l,{{fill:'#2a6a8a',duration:.12,yoyo:true,repeat:5}},{t['ready'] + .4}+(i%7)*.05);}});",
          f"tl.to('#{px}-capbar',{{width:'100%',duration:1.2,ease:'power2.out'}},{t['ready']});"]
    return html, "\n".join(js)


# ── 3. AI developer: rented compute trains the model, then serves requests ─────────────────────
def lab(px, t_in, t_out, t):
    L = [(4, 260), (6, 480), (6, 700), (3, 920)]
    nodes, edges = [], []
    pos = {}
    for li, (n, x) in enumerate(L):
        for k in range(n):
            y = 300 + (k - (n - 1) / 2) * 76
            pos[(li, k)] = (x, y)
    for li in range(3):
        for a in range(L[li][0]):
            for b in range(L[li + 1][0]):
                (x1, y1), (x2, y2) = pos[(li, a)], pos[(li + 1, b)]
                edges.append(f'<path class="{px}-e{li}" d="M{x1} {y1} L{x2} {y2}" stroke="#2a4a6a" stroke-width="3"/>')
    for (li, k), (x, y) in pos.items():
        nodes.append(f'<circle class="{px}-n{li}" cx="{x}" cy="{y}" r="22" fill="#16233a" stroke="#38d6ff" stroke-width="4"/>')
    curve = "M0 0 C60 10 100 70 160 100 C220 125 300 140 380 146"
    wall = f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <rect width="1920" height="1080" fill="#1a2232"/><rect y="760" width="1920" height="320" fill="#2a2a34"/>
 <rect x="560" y="80" width="1240" height="560" rx="18" fill="#0b1220" stroke="#3a4458" stroke-width="10"/>
 <g transform="translate(600 40)">{''.join(edges)}{''.join(nodes)}</g>
 <text x="1080" y="140" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#7fd8ff" id="{px}-mode">Training the model</text>
 <g transform="translate(1340 230)"><path d="M0 0 V170 H400" stroke="#5a6a80" stroke-width="3" fill="none"/>
  <path id="{px}-loss" d="{curve}" stroke="#f2c66d" stroke-width="6" fill="none" transform="translate(10 10)"/>
  <text x="10" y="200" font-family="Inter" font-weight="700" font-size="24" fill="#cfd8e2">errors fall as it learns</text></g>
 <rect x="0" y="700" width="1920" height="70" fill="#4a3a2e"/>
</svg>"""
    reqs = "".join(f'<div class="mc-tok {px}-rq" style="left:560px;top:{430 + k * 50}px;padding:6px 14px;border-radius:12px;background:#1f6fbf;color:#fff;font:700 24px Inter">question</div>' for k in range(3))
    ans = "".join(f'<div class="mc-tok {px}-an" style="left:1500px;top:{430 + k * 50}px;padding:6px 14px;border-radius:12px;background:#2e6a4a;color:#fff;font:700 24px Inter">answer</div>' for k in range(3))
    rent = (f'<div id="{px}-rent" style="position:absolute;right:56px;top:690px;width:440px;padding:14px 18px;border-radius:12px;background:rgba(5,10,22,.85);border:3px solid #38d6ff;'
            f'font:800 28px Inter;color:#e8f3ff">Rented computing in use<div style="margin-top:8px;display:flex;gap:6px">'
            + "".join(f'<div class="{px}-cu" style="flex:1;height:26px;border-radius:4px;background:#16233a"></div>' for _ in range(10)) + '</div></div>')
    staff = "".join(place(rig_svg(f"{px}e{k}", person(40 + k), "bust"), x, 760 - 200, 230).replace("height:383px", "height:276px") for k, x in enumerate((140, 420)))
    html = frame(px, "Inside the AI developer", ["Rent computing from the cloud", "Train: learn from data", "Operate: answer users"], wall, reqs + ans + rent + staff)
    js = [iris(px, t_in, t_out, 1060, 420), steps_js(px, [t_in + .2, t["train"], t["operate"]]),
          f"ambient('{px}e0',{t_in},{t_out},501,['type','type','point']); ambient('{px}e1',{t_in},{t_out},502,['type','hold','type']);",
          f"document.querySelectorAll('.{px}-cu').forEach((c,i)=>tl.to(c,{{background:'#38d6ff',duration:.05}},{t_in + .2}+i*.06));",
          "(function(){const p=document.getElementById('%s-loss'),n=p.getTotalLength();gsap.set(p,{strokeDasharray:n,strokeDashoffset:n});tl.to(p,{strokeDashoffset:0,duration:1.0,ease:'none'},%s);})();" % (px, t["train"]),
          f"for(let w=0;w<3;w++){{[0,1,2].forEach(li=>{{tl.to('.{px}-e'+li,{{stroke:'#38d6ff',duration:.08}},{t['train']}+w*.33+li*.09);tl.to('.{px}-e'+li,{{stroke:'#2a4a6a',duration:.15}},{t['train'] + .1}+w*.33+li*.09);}});}}",
          f"[0,1,2,3].forEach(li=>tl.to('.{px}-n'+li,{{fill:'#38d6ff',duration:.08,yoyo:true,repeat:5}},{t['train']}+li*.09));",
          f"tl.set('#{px}-mode',{{textContent:'Operating: answering users'}},{t['operate']});",
          f"document.querySelectorAll('.{px}-rq').forEach((e,i)=>{{tl.fromTo(e,{{opacity:0,x:-200}},{{opacity:1,x:0,duration:.25}},{t['operate']}+i*.15);tl.to(e,{{opacity:0,x:200,duration:.2}},{t['operate'] + .4}+i*.15);}});",
          f"document.querySelectorAll('.{px}-an').forEach((e,i)=>{{tl.fromTo(e,{{opacity:0,x:-80}},{{opacity:1,x:0,duration:.25}},{t['operate'] + .55}+i*.15);}});"]
    return html, "\n".join(js)


# ── 4. customers: use AI for real tasks and pay for it ─────────────────────────────────────────
def customers(px, t_in, t_out, t):
    bg = f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <rect width="960" height="1080" fill="#f2e2c4"/><rect x="960" width="960" height="1080" fill="#d8e4ee"/>
 <path d="M960 0 V1080" stroke="{O}" stroke-width="6"/>
 <!-- bakery counter -->
 <rect x="60" y="300" width="840" height="60" fill="#c96a4a"/>{''.join(f'<path d="M{60 + k * 70} 300 l35 60 l35 -60" fill="#f4ead5"/>' for k in range(12))}
 {''.join(f'<rect x="{100 + k * 140}" y="420" width="110" height="70" rx="30" fill="#d9a05a" stroke="{O}" stroke-width="3"/>' for k in range(5))}
 <rect x="60" y="640" width="840" height="440" fill="#8a5a3a" stroke="{O}" stroke-width="5"/><rect x="60" y="630" width="840" height="24" fill="#a87a54"/>
 <text x="700" y="270" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="40" fill="#7a3a2a">Corner Bakery</text>
 <!-- office desk -->
 <rect x="1060" y="120" width="760" height="380" fill="#b8c8d8" stroke="#7a8a9a" stroke-width="6"/>{''.join(f'<rect x="{1080 + k * 120}" y="{440 - (k * 53) % 180}" width="80" height="{(k * 53) % 180 + 40}" fill="#8aa0b8"/>' for k in range(6))}
 <rect x="960" y="640" width="960" height="440" fill="#6a5a4a"/><rect x="960" y="630" width="960" height="24" fill="#8a7a6a"/>
 <rect x="1380" y="420" width="360" height="230" rx="12" fill="#1b2433" stroke="#8f9bb0" stroke-width="8"/><path d="M1340 650 L1780 650 L1810 680 L1310 680Z" fill="#8f9bb0"/>
</svg>"""
    owner = place(rig_svg(f"{px}o", person(55, hat=None, jacket="#f4ead5", jacket_sh="#d8ccb4", jacket_hi="#fff", shirt="#c96a4a"), "bust", prop_front="tablet"), 260, 420, 300).replace("height:500px", "height:360px")
    worker = place(rig_svg(f"{px}w", person(58), "bust"), 1040, 420, 300).replace("height:500px", "height:360px")
    bub = lambda i, x, y, txt, col: f'<div class="mc-tok" id="{px}-{i}" style="left:{x}px;top:{y}px;max-width:400px;padding:12px 18px;border-radius:16px;background:{col};color:#fff;font:700 28px Inter">{txt}</div>'
    html = frame(px, "Customers using AI", ["Pay a subscription", "Use it for real work"], bg,
                 owner + worker
                 + bub("q1", 520, 360, "Plan tomorrow's orders", "#1f6fbf") + bub("a1", 520, 450, "Bake 40 loaves, 60 rolls…", "#2e6a4a")
                 + bub("q2", 1420, 300, "Draft the quarterly report", "#1f6fbf") + bub("a2", 1420, 470, "Draft ready — 3 key risks…", "#2e6a4a")
                 + f'<div id="{px}-pay" class="mc-tok" style="left:600px;top:760px;padding:12px 20px;border-radius:14px;background:#f2c66d;color:#3a2a18;font:800 30px Inter;border:3px solid #8a6a1c">Subscription paid →</div>'
                 + f'<div id="{px}-pay2" class="mc-tok" style="left:1500px;top:760px;padding:12px 20px;border-radius:14px;background:#f2c66d;color:#3a2a18;font:800 30px Inter;border:3px solid #8a6a1c">Licence paid →</div>')
    js = [iris(px, t_in, t_out, 1500, 600), steps_js(px, [t["pay"], t["use"]]),
          f"rpose('{px}o','pay',{t['pay'] - .2},.25); rpose('{px}o','hold',{t['use']},.25); ambient('{px}w',{t_in},{t_out},601,['type','type','hold']);",
          f"tl.fromTo('#{px}-pay',{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.2}},{t['pay']}); tl.to('#{px}-pay',{{x:300,y:-560,scale:.6,opacity:0,duration:.8,ease:'power2.in'}},{t['pay'] + .5});",
          f"tl.fromTo('#{px}-pay2',{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.2}},{t['pay'] + .2}); tl.to('#{px}-pay2',{{x:200,y:-560,scale:.6,opacity:0,duration:.8,ease:'power2.in'}},{t['pay'] + .7});",
          f"tl.fromTo('#{px}-q1',{{opacity:0,y:20}},{{opacity:1,y:0,duration:.2}},{t_in + .2}); tl.fromTo('#{px}-a1',{{opacity:0,y:20}},{{opacity:1,y:0,duration:.25}},{t['use']});",
          f"tl.fromTo('#{px}-q2',{{opacity:0,y:20}},{{opacity:1,y:0,duration:.2}},{t_in + .4}); tl.fromTo('#{px}-a2',{{opacity:0,y:20}},{{opacity:1,y:0,duration:.25}},{t['use'] + .3});"]
    return html, "\n".join(js)
