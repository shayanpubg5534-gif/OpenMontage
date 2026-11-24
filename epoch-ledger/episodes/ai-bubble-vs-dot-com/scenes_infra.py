"""3D AI infrastructure 5:53–6:28 (storyboard s032–s036): from a chat window down to the physical stack."""
from kit.assemble import Scene
from timeline import L, W


def laptop():
    return """<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><radialGradient id="i1-bg" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="#16243b"/><stop offset="1" stop-color="#050a16"/></radialGradient></defs>
 <rect width="1920" height="1080" fill="url(#i1-bg)"/><rect y="820" width="1920" height="260" fill="#0c1524"/>
 <path d="M520 840 L1400 840 L1520 900 L400 900Z" fill="#8f9bb0" stroke="#1b2230" stroke-width="4"/>
 <rect x="560" y="230" width="800" height="610" rx="24" fill="#1b2433" stroke="#8f9bb0" stroke-width="10"/>
 <rect x="590" y="260" width="740" height="550" rx="10" fill="#0b1220"/>
</svg>"""


def chat():
    return """<div id="i1-chat" style="position:absolute;left:600px;top:270px;width:720px;height:530px;overflow:hidden;font-family:Inter">
 <div style="margin:26px 30px 0 auto;width:420px;padding:18px 22px;border-radius:18px;background:#1f6fbf;color:#fff;font:600 30px Inter">Summarise this report</div>
 <div id="i1-ans" style="margin:24px 30px;width:560px;padding:18px 22px;border-radius:18px;background:#16233a;color:#e8f3ff;font:500 28px Inter;line-height:1.45;clip-path:inset(0 100% 0 0)">
  Key points: revenue grew, costs fell, and three risks need attention…</div>
 <div id="i1-dots" style="margin:0 30px;font:800 40px Inter;color:#38d6ff">• • •</div>
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
    scenes.append(Scene("i1", round(a5s - .45, 3), round(w_phys - a5s + .9, 3),
        f'<div id="i1-cam" class="cam">{laptop()}{chat()}</div>'
        '<div id="i1-flash" class="fill" style="background:radial-gradient(circle,#9ff3ff,#0b1220 70%);opacity:0"></div>',
        js=f"""
tl.fromTo('#i1',{{opacity:0}},{{opacity:1,duration:.45}},{a5s - .45});
tl.fromTo('#i1-ans',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:2.2,ease:'steps(24)'}},{a5s + .4});
tl.fromTo('#i1-dots',{{opacity:1}},{{opacity:.2,duration:.4,yoyo:true,repeat:5}},{a5s});
tl.fromTo('#i1-cam',{{scale:1}},{{scale:5.5,transformOrigin:'960px 520px',duration:{w_phys - a6s + .5},ease:'power3.in'}},{a6s});
tl.fromTo('#i1-flash',{{opacity:0}},{{opacity:1,duration:.35}},{w_phys});
"""))
    # chip (physical infrastructure + processors), data hall (servers + cooling), campus (power + investment)
    regions.append(("chip-infra", [(w_phys + .4, a8s)], f"""AI3D.add('chip-infra',{{start:{w_phys + .4},end:{a8s},world:'chip',
 cam:{{from:[1.2,7.5,1.4],to:[5.2,3.6,5.4],look:[0,.3,0],dur:{a8s - w_phys - .4}}},spin:.1,explode:[{a7s + .6},{w_calc}],glow:{a7s}}});"""))
    regions.append(("hall-infra", [(a8s, a10s)], f"""AI3D.add('hall-infra',{{start:{a8s},end:{a10s},world:'dataHall',
 cam:{{from:[0,2.6,3],to:[.4,1.3,-14],look:[0,1.3,-30],lookTo:[1.6,1.2,-30],dur:{a10s - a8s}}},thermal:{a9s + .2}}});"""))
    regions.append(("campus-infra", [(a10s, a11e + .6)], f"""AI3D.add('campus-infra',{{start:{a10s},end:{a11e + .6},world:'campus',
 cam:{{from:[160,24,80],to:[-40,80,170],look:[90,14,10],lookTo:[0,4,-20],dur:{a11e + .6 - a10s}}},power:{w_energy},build:[{a11s - .2},{a11e}]}});"""))
    scenes.append(Scene("i2", round(w_phys + .3, 3), round(a11e + .6 - w_phys - .3, 3),
        '<div id="i2-flash" class="fill" style="background:#9ff3ff;opacity:0"></div><div id="i2-dip" class="fill" style="background:#02040a;opacity:0"></div>'
        '<div class="tag m" id="i2-t1">Processors</div><div class="tag m" id="i2-t2">Servers</div><div class="tag m" id="i2-t3">Cooling</div>'
        '<div class="tag m" id="i2-t4">Power</div><div class="tag m" id="i2-t5">Investment</div>'
        '<div id="i2-coins" class="fill"></div>',
        js=f"""
tl.fromTo('#i2-flash',{{opacity:1}},{{opacity:0,duration:.6,ease:'power2.out'}},{w_phys + .4});
[[{a8s},.22],[{a10s},.22]].forEach(([t,d])=>{{tl.fromTo('#i2-dip',{{opacity:0}},{{opacity:1,duration:d}},t-d);tl.to('#i2-dip',{{opacity:0,duration:.3}},t);}});
show('#i2-t1',{a7s}); hide('#i2-t1',{a8s - .3},.2); show('#i2-t2',{a8s + .2}); hide('#i2-t2',{a9s - .2},.2);
show('#i2-t3',{a9s + .1}); hide('#i2-t3',{a10s - .3},.2); show('#i2-t4',{w_energy}); hide('#i2-t4',{a11s - .1},.2); show('#i2-t5',{a11s + .2});
(function(){{const b=document.getElementById('i2-coins');for(let i=0;i<26;i++){{const c=document.createElement('div');
 c.style.cssText='position:absolute;left:'+(760+(i*37)%400)+'px;top:-60px;width:34px;height:34px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#fff1c9,#f2c66d 45%,#b07a10);box-shadow:0 0 12px rgba(242,198,109,.8);opacity:0';b.appendChild(c);
 tl.fromTo(c,{{y:-60,opacity:0}},{{y:560+(i%5)*30,opacity:1,duration:1.1,ease:'power2.in'}},{a11s + .2}+i*.12); tl.to(c,{{opacity:0,duration:.3}},{a11s + 1.3}+i*.12);}}}})();
"""))
    return scenes, regions, ""
