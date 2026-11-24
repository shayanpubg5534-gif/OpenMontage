"""Nasdaq collapse 4:00–4:45 (storyboard s023–s025): shutdown in the rain, the real Nasdaq chart, $10,000 illustration."""
import csv
import datetime as dt
from pathlib import Path

from kit.assemble import Scene
from kit.characters import OUT, person_svg
from timeline import L, W

HERE = Path(__file__).resolve().parent


def place(svg, style):
    return svg.replace('class="char "', f'class="char" style="{style}"')


def street_svg():
    wins = "".join(f'<rect class="c23-win" x="{560 + c * 150}" y="{200 + r * 150}" width="110" height="100" fill="#ffd98f" stroke="{OUT}" stroke-width="3"/>'
                   for r in range(3) for c in range(5))
    puddles = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * .16:.0f}" fill="#0c1a22"/>'
                      f'<path class="c23-glint" d="M{x - rx * .6} {y} H{x + rx * .2}" stroke="#38d6ff" stroke-width="3" opacity="0"/>'
                      for x, y, rx in [(300, 905, 150), (1100, 930, 210), (1700, 900, 130)])
    rain = "".join(f'<path class="c23-rain" d="M{(i * 97) % 1960} {-40 - (i * 53) % 400} l-14 46" stroke="#9fb7c9" stroke-width="2" opacity=".5"/>' for i in range(110))
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="c23-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a2230"/><stop offset="1" stop-color="#3a2f2a"/></linearGradient></defs>
 <rect width="1920" height="1080" fill="url(#c23-sky)"/>
 <rect x="500" y="120" width="830" height="720" fill="#7a3e2a" stroke="{OUT}" stroke-width="4"/>
 <g stroke="#5e2f20" stroke-width="2">{''.join(f'<path d="M500 {150 + k * 30} H1330"/>' for k in range(23))}</g>
 {wins}
 <g id="c23-neon"><rect x="760" y="70" width="300" height="90" rx="18" fill="#1a1410" stroke="{OUT}" stroke-width="4"/>
  <text x="910" y="140" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="64" fill="#ff7ad9" style="filter:drop-shadow(0 0 10px #ff7ad9)">@ .com</text></g>
 <rect x="880" y="700" width="140" height="140" fill="#2a1a12" stroke="{OUT}" stroke-width="4"/>
 <g id="c23-closed" opacity="0"><rect x="890" y="640" width="120" height="44" rx="6" fill="#f3e3c3" stroke="{OUT}" stroke-width="3"/>
  <text x="950" y="672" text-anchor="middle" font-family="Inter" font-weight="800" font-size="26" fill="#9b2f2f">CLOSED</text></g>
 <g id="c23-tank" transform="translate(1440 260)"><rect x="0" y="0" width="190" height="420" rx="24" fill="#20262e" stroke="{OUT}" stroke-width="5"/>
  <rect id="c23-cash" x="14" y="14" width="162" height="392" rx="16" fill="#4fa56e"/>
  <path d="M95 -170 V0" stroke="#8a95a6" stroke-width="26"/><path id="c23-flow" d="M95 -170 V0" stroke="#f2c66d" stroke-width="12" stroke-dasharray="18 14"/>
  <g id="c23-valve" transform="translate(95 -110)"><circle r="34" fill="none" stroke="#d4a24c" stroke-width="10"/><path d="M-34 0 H34 M0 -34 V34" stroke="#d4a24c" stroke-width="8"/></g>
  <text x="95" y="-190" text-anchor="middle" font-family="Inter" font-weight="700" font-size="30" fill="#f3e3c3">Investor capital</text>
  <text x="95" y="470" text-anchor="middle" font-family="Inter" font-weight="700" font-size="30" fill="#f3e3c3">Cash runway</text></g>
 <rect x="0" y="840" width="1920" height="240" fill="#2a2622"/>{puddles}
 <g id="c23-rainl">{rain}</g>
</svg>"""


def nasdaq_points():
    rows = [(dt.date.fromisoformat(r["date"]), float(r["close"])) for r in csv.DictReader(open(HERE / "data" / "nasdaq_composite_daily_1994-12_2004-01.csv"))]
    rows = [r for r in rows if dt.date(1995, 1, 1) <= r[0] <= dt.date(2003, 12, 31)]
    pk = max(rows, key=lambda r: r[1])
    lo = min((r for r in rows if r[0] > pk[0]), key=lambda r: r[1])
    keep = [r for i, r in enumerate(rows) if i % 5 == 0] + [pk, lo]
    keep = sorted(set(keep))
    x0, x1, y0, y1 = 220, 1700, 800, 170
    d0, d1 = dt.date(1995, 1, 1).toordinal(), dt.date(2004, 1, 1).toordinal()
    X = lambda d: x0 + (d.toordinal() - d0) / (d1 - d0) * (x1 - x0)
    Y = lambda v: y0 - v / 5500 * (y0 - y1)
    pts = [(X(d), Y(v), d) for d, v in keep]
    split = next(i for i, p in enumerate(pts) if p[2] == pk[0])
    up = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts[:split + 1])
    down = " ".join(f"{x:.1f},{y:.1f}" for x, y, d in pts[split:] if d <= lo[0])
    after = " ".join(f"{x:.1f},{y:.1f}" for x, y, d in pts if d >= lo[0])
    return up, down, after, (X(pk[0]), Y(pk[1]), pk), (X(lo[0]), Y(lo[1]), lo), X, Y


def chart_svg():
    up, down, after, PK, LO, X, Y = nasdaq_points()
    years = "".join(f'<text x="{X(dt.date(y, 1, 1)):.0f}" y="850" text-anchor="middle" font-family="Inter" font-weight="700" font-size="30" fill="#6b5634">{y}</text>'
                    f'<path d="M{X(dt.date(y, 1, 1)):.0f} 800 v12" stroke="#6b5634" stroke-width="3"/>' for y in range(1995, 2004))
    grid = "".join(f'<path d="M220 {Y(v):.0f} H1700" stroke="#c9b48a" stroke-width="2" stroke-dasharray="6 8"/>'
                   f'<text x="200" y="{Y(v) + 10:.0f}" text-anchor="end" font-family="Inter" font-weight="700" font-size="30" fill="#6b5634">{v:,}</text>' for v in (1000, 2000, 3000, 4000, 5000))
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><radialGradient id="c24-paper" cx=".5" cy=".4" r=".8"><stop offset="0" stop-color="#f6ecd2"/><stop offset="1" stop-color="#e3cf9f"/></radialGradient></defs>
 <rect width="1920" height="1080" fill="url(#c24-paper)"/>{grid}<path d="M220 800 H1700" stroke="#6b5634" stroke-width="4"/>{years}
 <text x="220" y="150" font-family="Fraunces" font-weight="800" font-size="52" fill="#2a1d12">Nasdaq Composite</text>
 <polyline id="c24-up" points="{up}" fill="none" stroke="#2f7d5b" stroke-width="7" stroke-linejoin="round"/>
 <polyline id="c24-down" points="{down}" fill="none" stroke="#c0392b" stroke-width="7" stroke-linejoin="round"/>
 <polyline id="c24-after" points="{after}" fill="none" stroke="#8a7a5a" stroke-width="5" opacity="0"/>
 <g id="c24-pk" opacity="0"><circle cx="{PK[0]:.1f}" cy="{PK[1]:.1f}" r="14" fill="#2f7d5b" stroke="#fff" stroke-width="4"/>
  <text x="{PK[0] + 26:.0f}" y="{PK[1] - 10:.0f}" font-family="Fraunces" font-weight="800" font-size="46" fill="#2a1d12">5,048.62</text>
  <text x="{PK[0] + 26:.0f}" y="{PK[1] + 30:.0f}" font-family="Inter" font-weight="700" font-size="30" fill="#6b5634">10 March 2000</text></g>
 <g id="c24-lo" opacity="0"><circle cx="{LO[0]:.1f}" cy="{LO[1]:.1f}" r="14" fill="#c0392b" stroke="#fff" stroke-width="4"/>
  <text x="{LO[0] + 24:.0f}" y="{LO[1] - 30:.0f}" font-family="Fraunces" font-weight="800" font-size="46" fill="#2a1d12">1,114.11</text>
  <text x="{LO[0] + 24:.0f}" y="{LO[1] + 6:.0f}" font-family="Inter" font-weight="700" font-size="30" fill="#6b5634">9 October 2002</text></g>
 <g id="c24-br" opacity="0"><path d="M{PK[0] - 40:.0f} {PK[1]:.0f} H{PK[0] - 70:.0f} V{LO[1]:.0f} H{PK[0] - 40:.0f}" fill="none" stroke="#c0392b" stroke-width="6"/>
  <text x="{PK[0] - 90:.0f}" y="{(PK[1] + LO[1]) / 2 + 20:.0f}" text-anchor="end" font-family="Fraunces" font-weight="800" font-size="84" fill="#c0392b">−78%</text></g>
 <g id="c25-stack" transform="translate({PK[0] - 300:.0f} {PK[1] + 40:.0f})" opacity="0">
  {''.join(f'<rect class="c25-bill" x="0" y="{-i * 9}" width="150" height="62" rx="6" fill="#7fb07a" stroke="#2f5a32" stroke-width="3"/>' for i in range(10))}
 </g>
 <g id="c25-ctr" opacity="0"><rect x="1460" y="300" width="420" height="150" rx="18" fill="#2a1d12"/>
  <text id="c25-num" x="1670" y="400" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="84" fill="#f2c66d">$10,000</text></g>
</svg>"""


def build():
    s, e = L("c03_09")[0], L("c03_11")[1]
    w_decl = W("declining", "c03_09")
    w_without = W("Without", "c03_10")
    w_shut, w_emp, w_inv = W("Companies", "c03_11"), W("Employees", "c03_11"), W("Investors", "c03_11")
    c12s, c12e = L("c03_12")
    w_peak, w_bottom, w_78 = W("peak", "c03_12"), W("bottom", "c03_12"), W("78", "c03_12")
    c13s, _ = L("c03_13")
    c14s, c14e = L("c03_14")
    w_fallen = W("fallen", "c03_14")
    scenes = []
    emp = place(person_svg("emp", "employee_1999", "box"), "left:820px;top:520px;width:250px;height:416px")
    dan = place(person_svg("dan2", "dan_1999", "box"), "left:960px;top:520px;width:250px;height:416px")
    inv = place(person_svg("inv2", "investor_1999", "bust"), "left:40px;top:330px;width:420px;height:504px")
    scenes.append(Scene("c23", round(s - .5, 3), round(e - s + .9, 3),
        f'<div id="c23-cam" class="cam">{street_svg()}<div id="c23-people" style="position:absolute;inset:0;opacity:0">{emp}{dan}</div></div>'
        f'<div id="c23-home" class="fill" style="opacity:0;background:radial-gradient(circle at 30% 40%,#3a2a1a,#140d07)">{inv}'
        f'<div id="c23-paper" style="position:absolute;left:470px;top:300px;width:560px;height:520px;background:#fbf6e8;border:4px solid #1b2230;border-radius:10px;transform:rotate(-3deg);padding:34px">'
        f'<div style="font:800 40px Fraunces;color:#2a1d12">Brokerage statement</div><div style="font:600 30px Inter;color:#6b5634;margin-top:8px">Account value</div>'
        f'<div id="c23-val" style="font:800 92px Fraunces;color:#2f7d5b;margin-top:24px">$148,200</div><div id="c23-steam" class="fill"></div></div></div>',
        js=f"""
tl.fromTo('#c23',{{opacity:0}},{{opacity:1,duration:.5}},{s - .5});
tl.fromTo('#c23-cam',{{scale:1.08}},{{scale:1.0,duration:{e - s},ease:'sine.out'}},{s - .5});
tl.fromTo('.c23-rain',{{y:0}},{{y:1200,duration:1.1,ease:'none',repeat:Math.ceil({e - s + 1}/1.1)}},{s - .5});
tl.fromTo('#c23-flow',{{strokeDashoffset:0}},{{strokeDashoffset:-320,duration:{w_without - s + 1},ease:'none'}},{s - .5});
tl.to('#c23-valve',{{rotation:270,svgOrigin:'0 0',duration:1.4,ease:'power2.inOut'}},{w_decl});
tl.to('#c23-flow',{{opacity:0,duration:.6}},{w_decl + 1.2});
tl.fromTo('#c23-cash',{{attr:{{y:14,height:392}}}},{{attr:{{y:390,height:16}},duration:{w_shut - w_without + .4},ease:'power1.in'}},{w_without});
tl.to('#c23-cash',{{fill:'#c0392b',duration:.6}},{w_shut - .6});
document.querySelectorAll('.c23-win').forEach((w,i)=>tl.to(w,{{fill:'#141a22',duration:.08}},{w_shut + .1}+((i*7)%15)*.09));
tl.to('#c23-neon text',{{opacity:.15,duration:.08,yoyo:true,repeat:5}},{w_shut + .2}); tl.to('#c23-neon text',{{opacity:.08,duration:.1}},{w_shut + .8});
pop('#c23-closed',{w_shut + 1.0});
tl.to('.c23-glint',{{opacity:.8,duration:.6}},{w_shut + .4});
show('#c23-people',{w_emp - .3},.3);
tl.fromTo('#c23-people',{{x:0}},{{x:-640,duration:{w_inv - w_emp + .3},ease:'none'}},{w_emp - .3});
['emp','dan2'].forEach((p,k)=>{{for(let i=0;i<8;i++){{const a=i%2?-18:18,t={w_emp - .3}+k*.19+i*.38;
 tl.to('#'+p+'-leg-front',{{rotation:a,svgOrigin:'150 330',duration:.38,ease:'sine.inOut'}},t);tl.to('#'+p+'-leg-back',{{rotation:-a,svgOrigin:'150 330',duration:.38,ease:'sine.inOut'}},t);}}}});
tl.set(['#emp','#dan2'],{{scaleX:-1}},{w_emp - .3});
tl.fromTo('#c23-home',{{opacity:0}},{{opacity:1,duration:.4}},{w_inv - .2});
const c23v={{v:148200}}; tl.to(c23v,{{v:31400,duration:{e - w_inv},ease:'power2.in',onUpdate:()=>{{document.getElementById('c23-val').textContent='$'+Math.round(c23v.v).toLocaleString('en-US')}}}},{w_inv + .3});
tl.to('#c23-val',{{color:'#c0392b',duration:.5}},{w_inv + .6});
(function(){{const b=document.getElementById('c23-steam');for(let i=0;i<14;i++){{const d=document.createElement('div');d.style.cssText='position:absolute;left:'+(60+i*30)+'px;top:220px;width:26px;height:26px;border-radius:50%;background:rgba(160,150,130,.5);opacity:0';b.appendChild(d);
 tl.fromTo(d,{{opacity:0,y:0,scale:.6}},{{opacity:.8,y:-160-(i%4)*30,scale:1.8,duration:1.4,ease:'power1.out'}},{w_inv + .6}+i*.07); tl.to(d,{{opacity:0,duration:.5}},{w_inv + 1.8}+i*.07);}}}})();
tl.to('#inv2-upper',{{rotation:5,svgOrigin:'150 330',duration:1,ease:'power2.out'}},{w_inv + .4}); blink('#inv2 .lid',[{w_inv + .5}]);
tl.to('#inv2-mouth',{{scaleY:-1,transformOrigin:'50% 50%',duration:.3}},{w_inv + .4});
"""))
    scenes.append(Scene("c24", round(c12s - .45, 3), round(c14e + .6 - c12s + .45, 3),
        f'<div id="c24-cam" class="cam">{chart_svg()}</div><div class="src dark" id="c24-src">Source: Nasdaq, daily closes</div>'
        '<div class="tag l" id="c25-tag">Illustration · index level only</div>',
        js=f"""
tl.fromTo('#c24',{{opacity:0}},{{opacity:1,duration:.45}},{c12s - .45});
show('#c24-src',{c12s});
['#c24-up','#c24-down'].forEach(s=>{{const el=document.querySelector(s),len=el.getTotalLength();gsap.set(el,{{strokeDasharray:len,strokeDashoffset:len}});}});
tl.to('#c24-up',{{strokeDashoffset:0,duration:{w_peak - c12s + .4},ease:'power1.in'}},{c12s - .3});
pop('#c24-pk',{w_peak + .1});
tl.to('#c24-down',{{strokeDashoffset:0,duration:{w_bottom - w_peak},ease:'power1.inOut'}},{w_peak + .2});
pop('#c24-lo',{w_bottom + .1});
tl.fromTo('#c24-br',{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.45,ease:'power3.out'}},{w_78});
tl.fromTo('#c24-cam',{{scale:1.12,x:120,y:80}},{{scale:1.0,x:0,y:0,duration:{w_bottom - c12s + 1},ease:'power2.inOut'}},{c12s - .45});
show('#c24-after',{w_78 + .8},.6);
// $10,000 illustration
show('#c25-tag',{W('Imagine', 'c03_13')}); show('#c25-stack',{W('$10', 'c03_13')}); show('#c25-ctr',{W('$10', 'c03_13') + .2});
tl.to('#c24-br',{{opacity:.25,duration:.4}},{c13s});
const c25={{v:10000}}; tl.to(c25,{{v:2207,duration:2.2,ease:'power2.inOut',onUpdate:()=>{{document.getElementById('c25-num').textContent='$'+Math.round(c25.v).toLocaleString('en-US')}}}},{w_fallen});
document.querySelectorAll('.c25-bill').forEach((b,i)=>{{if(i>=2) tl.to(b,{{opacity:0,y:-40,duration:.35}},{w_fallen}+(9-i)*.24);}});
"""))
    return scenes, [], ""
