"""3D AI infrastructure 5:53–6:28 (storyboard s032–s036): from a chat window down to the physical stack."""
from kit.assemble import Scene
from timeline import L, W


def laptop():
    """Home office at night: the user at a laptop; through the window, the city and a data centre on
    the horizon; a router on the shelf. The request's path out to the data centre is drawn later."""
    sky = "".join(f'<rect x="{1290 + x}" y="{470 - h}" width="{w}" height="{h}" fill="#141c2c"/>'
                  + "".join(f'<rect x="{1296 + x + j * 14}" y="{480 - h + r * 22}" width="7" height="10" fill="#ffd27a" opacity="{.25 + ((x + j + r) % 5) * .12:.2f}"/>'
                            for j in range(max(1, (w - 8) // 14)) for r in range(max(1, h // 26)))
                  for x, w, h in [(0, 70, 140), (80, 50, 200), (140, 90, 110), (240, 60, 170), (310, 80, 90), (400, 60, 150), (470, 90, 120)])
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="i1-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c2638"/><stop offset="1" stop-color="#121a28"/></linearGradient>
  <linearGradient id="i1-night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1226"/><stop offset="1" stop-color="#2a2a48"/></linearGradient>
  <radialGradient id="i1-lamp" cx=".2" cy=".2" r=".6"><stop offset="0" stop-color="#ffd8a0" stop-opacity=".35"/><stop offset="1" stop-color="#ffd8a0" stop-opacity="0"/></radialGradient>
  <pattern id="i1-wood" width="240" height="30" patternUnits="userSpaceOnUse"><rect width="240" height="30" fill="#5a3e2a"/><path d="M0 29 H240 M90 0 V30" stroke="#4a3222" stroke-width="2"/></pattern></defs>
 <rect width="1920" height="1080" fill="url(#i1-wall)"/>
 <g><rect x="1270" y="80" width="600" height="440" fill="url(#i1-night)" stroke="#3a4458" stroke-width="14"/>
  <circle cx="1780" cy="150" r="26" fill="#e8e6d8" opacity=".8"/>{sky}
  <g id="i1-dc" transform="translate(1720 430) scale(1.6)"><rect x="-70" y="-26" width="140" height="30" fill="#2a3448"/><rect x="-70" y="-10" width="140" height="4" fill="#38d6ff"/>
   <rect x="-60" y="-40" width="18" height="14" fill="#3a4458"/><rect x="-30" y="-40" width="18" height="14" fill="#3a4458"/><rect x="0" y="-40" width="18" height="14" fill="#3a4458"/></g>
  <path d="M1570 80 V520 M1270 300 H1870" stroke="#3a4458" stroke-width="10"/></g>
 <rect x="1280" y="560" width="560" height="16" fill="#4a3426"/>
 <g transform="translate(1420 520)"><rect width="110" height="40" rx="8" fill="#22262e" stroke="#0a0c10" stroke-width="3"/>
  {''.join(f'<circle id="i1-led{k}" cx="{22 + k * 20}" cy="20" r="5" fill="#38d6ff" opacity=".4"/>' for k in range(4))}
  <path d="M20 0 L14 -40 M90 0 L96 -40" stroke="#22262e" stroke-width="6" stroke-linecap="round"/></g>
 <g transform="translate(1640 530) scale(.8)">{''.join(f'<rect x="{k * 34}" y="{-60 - (k % 3) * 14}" width="28" height="{90 + (k % 3) * 14}" fill="{["#7a3a3a", "#3a5a7a", "#6a6a3a", "#4a3a6a"][k % 4]}"/>' for k in range(7))}</g>
 <rect x="0" y="0" width="1920" height="1080" fill="url(#i1-lamp)"/>
 <g transform="translate(90 330)"><path d="M60 0 L150 -110 L210 -70" stroke="#2a2e36" stroke-width="12" fill="none" stroke-linecap="round"/>
  <path d="M190 -100 L270 -60 L230 -20Z" fill="#2a2e36"/><path d="M240 -40 L330 230 L130 230Z" fill="#ffd8a0" opacity=".12"/></g>
 <rect x="0" y="842" width="1920" height="238" fill="url(#i1-wood)"/><rect x="0" y="836" width="1920" height="14" fill="#7a5638"/>
 <g transform="translate(1560 760)"><rect x="0" y="0" width="70" height="80" rx="8" fill="#e8e2d4" stroke="#1b2230" stroke-width="4"/>
  <path d="M70 18 C96 18 96 56 70 56" stroke="#1b2230" stroke-width="5" fill="none"/>
  <path id="i1-steam" d="M20 -10 C10 -40 40 -50 28 -80 M44 -10 C34 -40 64 -50 52 -80" stroke="#ffffff" stroke-width="5" fill="none" opacity=".35" stroke-linecap="round"/></g>
 <path d="M520 840 L1400 840 L1520 900 L400 900Z" fill="#8f9bb0" stroke="#1b2230" stroke-width="4"/>
 <path d="M560 848 L1380 848 L1440 880 L500 880Z" fill="#6a768a"/>
 <rect x="560" y="230" width="800" height="610" rx="24" fill="#1b2433" stroke="#8f9bb0" stroke-width="10"/>
 <rect x="590" y="260" width="740" height="550" rx="10" fill="#0b1220"/>
 <path id="i1-path" d="M1300 300 C1340 200 1440 560 1475 540 C1530 470 1580 420 1640 390 C1680 370 1700 420 1720 400" stroke="#38d6ff" stroke-width="6" fill="none" stroke-dasharray="14 12" opacity="0"/>
 <circle id="i1-pkt" r="12" fill="#9ff3ff" opacity="0"/>
 <g id="i1-dclbl" opacity="0"><rect x="1350" y="10" width="500" height="54" rx="10" fill="rgba(5,10,22,.85)" stroke="#38d6ff" stroke-width="3"/>
  <text x="1600" y="46" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="#e8f3ff">Answered by a data centre</text></g>
</svg>"""


def chat():
    return """<div id="i1-chat" style="position:absolute;left:600px;top:270px;width:720px;height:530px;overflow:hidden;font-family:Inter">
 <div id="i1-q" style="margin:26px 30px 0 auto;width:420px;padding:18px 22px;border-radius:18px;background:#1f6fbf;color:#fff;font:600 30px Inter;opacity:0">Summarise this report</div>
 <div id="i1-ans" style="margin:24px 30px;width:560px;padding:18px 22px;border-radius:18px;background:#16233a;color:#e8f3ff;font:500 28px Inter;line-height:1.45;clip-path:inset(0 100% 0 0)">
  Key points: revenue grew, costs fell, and three risks need attention…</div>
 <div id="i1-dots" style="margin:0 30px;font:800 40px Inter;color:#38d6ff;opacity:0">• • •</div>
 <div style="position:absolute;left:20px;right:20px;bottom:18px;height:62px;border-radius:14px;background:#16233a;border:2px solid #2a3a56;display:flex;align-items:center;padding:0 18px">
  <span id="i1-typed" style="font:500 28px Inter;color:#e8f3ff;white-space:nowrap;overflow:hidden;width:0;display:inline-block">Summarise this report</span>
  <span id="i1-caret" style="width:3px;height:32px;background:#38d6ff;margin-left:4px"></span>
  <span id="i1-send" style="margin-left:auto;width:44px;height:44px;border-radius:50%;background:#2a3a56;color:#fff;font:800 26px Inter;display:flex;align-items:center;justify-content:center">↑</span></div>
</div>"""


def build():
    a5s, _ = L("c04_05")
    a6s, a6e = L("c04_06")
    a7s, a7e = L("c04_07")
    a8s, _ = L("c04_08")
    a9s, _ = L("c04_09")
    a10s, _ = L("c04_10")
    a11s, a11e = L("c04_11")
    w_phys = W("physical", "c04_06")
    w_calc = W("calculations", "c04_07")
    w_over = W("overheating", "c04_09")
    w_energy = W("energy", "c04_10")
    scenes, regions = [], []
    # Scene brief (c04_05): the AI the user sees is software, but every answer is computed on physical
    # machines. Typing → submit on "intelligence" → processing on "requires" → on "more than software"
    # the request visibly leaves the room (router → city → data centre) and the answer comes back.
    from rig_people import modern_user
    w_int, w_req, w_more, w_soft = W("intelligence", "c04_05"), W("requires", "c04_05"), W("more", "c04_05"), W("software", "c04_05")
    i0 = a5s - .45
    user = modern_user("i1u")
    scenes.append(Scene("i1", round(i0, 3), round(w_phys - a5s + .9, 3),
        f'<div id="i1-cam" class="cam">{laptop()}{chat()}{user}</div>'
        '<div id="i1-flash" class="fill" style="background:radial-gradient(circle,#9ff3ff,#0b1220 70%);opacity:0"></div>',
        js=f"""
tl.fromTo('#i1',{{opacity:0}},{{opacity:1,duration:.45}},{i0});
tl.fromTo('#i1-cam',{{scale:1.12,x:140,y:40}},{{scale:1.0,x:0,y:0,duration:{a6s - i0},ease:'sine.inOut'}},{i0});
rcycle('i1u','type','hold',{i0},{w_int},.24,0); ambient('i1u',{w_soft + .4},{a6s + .3},404,['hold','type']);
tl.fromTo('#i1-typed',{{width:0}},{{width:300,duration:{w_int - i0 - .2},ease:'steps(21)'}},{i0 + .1});
tl.fromTo('#i1-caret',{{opacity:1}},{{opacity:0,duration:.25,yoyo:true,repeat:{int((a6s - i0) / .25)},ease:'steps(1)'}},{i0});
rpose('i1u','point',{w_int},.18); rpose('i1u','hold',{w_int + .35},.25);
tl.to('#i1-send',{{background:'#38d6ff',scale:1.15,duration:.1,yoyo:true,repeat:1}},{w_int + .1});
tl.set('#i1-typed',{{opacity:0}},{w_int + .2}); tl.fromTo('#i1-q',{{opacity:0,y:120}},{{opacity:1,y:0,duration:.3,ease:'power2.out'}},{w_int + .2});
tl.fromTo('#i1-dots',{{opacity:.2}},{{opacity:1,duration:.3,yoyo:true,repeat:5}},{w_req});
// "more than software": the request leaves the laptop, through the router, across the city, to a data centre — and back
(function(){{const p=document.getElementById('i1-path'),n=p.getTotalLength();gsap.set(p,{{strokeDashoffset:0}});
 tl.to(p,{{opacity:.9,duration:.2}},{w_more - .2});
 const k={{u:0}}; tl.to(k,{{u:1,duration:1.0,ease:'power1.inOut',onUpdate:()=>{{const q=p.getPointAtLength(k.u*n);gsap.set('#i1-pkt',{{attr:{{cx:q.x,cy:q.y}}}});}}}},{w_more - .1});
 const r={{u:1}}; tl.to(r,{{u:0,duration:.9,ease:'power1.inOut',onUpdate:()=>{{const q=p.getPointAtLength(r.u*n);gsap.set('#i1-pkt',{{attr:{{cx:q.x,cy:q.y}},fill:'#f2c66d'}});}}}},{w_soft + .2});}})();
tl.to('#i1-pkt',{{opacity:1,duration:.1}},{w_more - .1}); tl.to('#i1-pkt',{{opacity:0,duration:.15}},{w_soft + 1.1});
[0,1,2,3].forEach(i=>tl.fromTo('#i1-led'+i,{{opacity:.3}},{{opacity:1,duration:.08,yoyo:true,repeat:5}},{w_more}+i*.05));
tl.fromTo('#i1-dc',{{scale:1}},{{scale:1.25,transformOrigin:'50% 50%',duration:.4,yoyo:true,repeat:1}},{w_more + .7});
tl.fromTo('#i1-dclbl',{{opacity:0,y:-10}},{{opacity:1,y:0,duration:.3}},{w_more + .6}); tl.to('#i1-dclbl',{{opacity:0,duration:.3}},{a6s});
tl.to('#i1-dots',{{opacity:0,duration:.1}},{w_soft + 1.0});
tl.fromTo('#i1-ans',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:1.0,ease:'steps(24)'}},{w_soft + 1.0});
tl.fromTo('#i1-steam',{{y:0,opacity:.35}},{{y:-20,opacity:.1,duration:1.6,yoyo:true,repeat:3}},{i0});
// existing transition: push into the screen, flash into the processor on "physical"
tl.to('#i1-path,#i1-dclbl',{{opacity:0,duration:.3}},{a6s});
tl.fromTo('#i1-cam',{{scale:1}},{{scale:5.5,transformOrigin:'960px 520px',duration:{w_phys - a6s + .5},ease:'power3.in'}},{a6s});
tl.fromTo('#i1-flash',{{opacity:0}},{{opacity:1,duration:.35}},{w_phys});
"""))
    # chip (physical infrastructure + processors), data hall (servers + cooling), campus (power + investment)
    regions.append(("chip-infra", [(w_phys + .4, a8s)], f"""AI3D.add('chip-infra',{{start:{w_phys + .4},end:{a8s},world:'chip',
 cam:{{from:[1.2,7.5,1.4],to:[5.2,3.6,5.4],look:[0,.3,0],dur:{a8s - w_phys - .4}}},spin:.1,explode:[{a7s + .6},{w_calc}],glow:{a7s}}});"""))
    # Servers + cooling: a macro on ONE rack (not the opening's data-hall corridor) — the hero sled slides out
    # as "servers" is spoken, heat blooms on the GPUs just before "cooling", and coolant flows on "prevent".
    w_serv, w_cool, w_prev = W("Servers", "c04_08"), W("Cooling", "c04_09"), W("prevent", "c04_09")
    keys = [[a8s, [3.2, 2.2, 4.6], [0, 1.3, 0], 46], [w_serv + .5, [2.0, 1.9, 3.0], [0, 1.4, .2], 40],
            [a9s - .9, [1.1, 1.85, 2.0], [0, 1.45, .6], 36], [w_cool + .2, [.5, 2.15, 1.45], [0, 1.47, .7], 34],
            [a10s, [-.35, 1.95, 1.55], [.05, 1.46, .65], 34]]
    regions.append(("rack-infra", [(a8s, a10s)], f"""AI3D.add('rack-infra',{{start:{a8s},end:{a10s},world:'serverRack',
 keys:{keys},slide:[{w_serv},{w_serv + 1.4}],thermal:{w_cool - .8},cool:{w_prev}}});"""))
    regions.append(("campus-infra", [(a10s, a11e + .6)], f"""AI3D.add('campus-infra',{{start:{a10s},end:{a11e + .6},world:'campus',
 cam:{{from:[150,22,95],to:[-70,70,150],look:[85,14,20],lookTo:[0,6,-25],dur:{a11e + .6 - a10s}}},power:{w_energy},invest:[{a11s},{a11e + .6}]}});"""))
    scenes.append(Scene("i2", round(w_phys + .3, 3), round(a11e + .6 - w_phys - .3, 3),
        '<div id="i2-flash" class="fill" style="background:#9ff3ff;opacity:0"></div><div id="i2-dip" class="fill" style="background:#02040a;opacity:0"></div>'
        '<div class="tag m" id="i2-t1">Processors</div><div class="tag m" id="i2-t2">Servers</div><div class="tag m" id="i2-t3">Cooling</div>'
        '<div class="tag m" id="i2-t4">Power</div><div class="tag m" id="i2-t5">Investment</div>',
        js=f"""
tl.fromTo('#i2-flash',{{opacity:1}},{{opacity:0,duration:.6,ease:'power2.out'}},{w_phys + .4});
[[{a8s},.22],[{a10s},.22]].forEach(([t,d])=>{{tl.fromTo('#i2-dip',{{opacity:0}},{{opacity:1,duration:d}},t-d);tl.to('#i2-dip',{{opacity:0,duration:.3}},t);}});
show('#i2-t1',{W('processors', 'c04_07')}); hide('#i2-t1',{a8s - .3},.2); show('#i2-t2',{W('Servers', 'c04_08')}); hide('#i2-t2',{a9s - .2},.2);
show('#i2-t3',{W('Cooling', 'c04_09')}); hide('#i2-t3',{a10s - .3},.2); show('#i2-t4',{w_energy}); hide('#i2-t4',{a11s - .1},.2); show('#i2-t5',{W('investment', 'c04_11')});
"""))
    return scenes, regions, ""
