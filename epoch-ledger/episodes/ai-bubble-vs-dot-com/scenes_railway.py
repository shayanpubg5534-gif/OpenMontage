"""Railway analogy 12:43–13:09 (c07_12–c07_15).

Scene brief
-----------
Message: a railway can cost a fortune and still pay off if it serves real demand; the same spending
on a line without demand loses money and fails. The question is whether returns justify spending.
Audience must understand: investment = capital deployed up front; returns = fares and freight that
accumulate over years until they exceed the cost; failure = revenue below running costs, losses
accumulating, *then* abandonment.
Actions → trigger words:
  "railway connecting productive cities"   3D 4-4-0 tracking shot, reveal of the city ahead
  "require" / "enormous investment"         track gang laying rails, derrick lowering steel, sleepers
                                            placed; ledger fills: land, steel, labour, rolling stock
  "generate" / "substantial long-term returns" busy station: passengers boarding, tickets paid, freight
                                            loaded; cumulative revenue crosses the upfront cost
  "expensive railway"                       same upfront cost bar on a cold branch station
  "insufficient demand"                     empty coaches and flatcars arrive; yearly revenue bars
                                            shrink under constant operating, maintenance and interest
  "financial disaster"                      the same station decays; its sign falls on "disaster"
  "how much money is being spent"           both lines: identical spending bars
  "returns" / "justify"                     line A's returns exceed spending (justified), B's do not
Cause → mechanism → consequence: spending → demand drives revenue (or not) → payback (or losses → ruin).
All money scales are illustrative (no figures); the ECB/Northern Pacific source stays on screen.
"""
from kit.assemble import Scene
from kit.rig import crowd_look, rig_svg
from floor import place
from railway_sets import O, boxcar, canopy, coach, defs, derrick, locomotive, station_building, track
from timeline import L, W

WORKWEAR = dict(tie=None, badge=False, hat="cap")


def look(i, **o):
    c = crowd_look(i)
    c.update(o)
    return c


def worker(i):
    jk = [("#4a5a7a", "#36435c", "#6a7a9a"), ("#7a5a3a", "#5c4228", "#9a7a54"), ("#5a6a4a", "#44523a", "#7a8a64")][i % 3]
    return look(60 + i, jacket=jk[0], jacket_sh=jk[1], jacket_hi=jk[2], shirt=["#d8c8a8", "#c9b48a", "#e0d6c0"][i % 3],
                hat_col=["#5a4a3a", "#3a3a3a", "#6a5030"][i % 3], **WORKWEAR)


def traveller(i, cold=False):
    hats = ["bowler", "top", "bonnet", "bowler", None, "cap"]
    jk = [("#2e3a5a", "#222c44", "#4a5a80"), ("#5a2e3a", "#44222c", "#804a5a"), ("#3a4a3a", "#2a382a", "#5a6a5a"),
          ("#6a5a4a", "#4e4236", "#8a7a6a")][i % 4]
    return look(80 + i, jacket=jk[0], jacket_sh=jk[1], jacket_hi=jk[2], hat=hats[i % 6], tie=["#6a1f1f", None, "#1f2a6a"][i % 3], badge=False)


def ledger_capital(px, rows, top=40):
    items = "".join(f'<div class="cap-row" id="{px}-row{i}"><span class="coins">{"".join("<i></i>" for _ in range(3 + i))}</span>{r}</div>' for i, r in enumerate(rows))
    return (f'<div class="panel parch" id="{px}-cap" style="right:56px;top:{top}px;width:520px">'
            f'<div class="ph">Capital deployed <small>illustrative</small></div>{items}'
            f'<div class="bar"><div class="fillc" id="{px}-capbar"></div></div><div class="cap-lbl">Upfront cost</div></div>')


CSS = """
.panel{position:absolute;padding:22px 26px;border-radius:14px;font:700 28px Inter;opacity:0;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.parch{background:rgba(247,238,218,.95);color:#3a2a18;border:3px solid #b8892e}
.slate{background:rgba(24,28,34,.92);color:#e8eef5;border:3px solid #5a6a7a}
.ph{font:800 32px Fraunces;margin-bottom:12px}.ph small{font:600 20px Inter;opacity:.7;margin-left:10px;letter-spacing:.06em;text-transform:uppercase}
.cap-row{display:flex;align-items:center;gap:14px;height:44px;opacity:0}
.coins{display:inline-flex;flex-direction:column-reverse;width:40px;align-items:center}
.coins i{display:block;width:34px;height:7px;margin-top:-1px;border-radius:50%;background:#f2c66d;border:2px solid #8a6a1c}
.bar{margin-top:14px;height:30px;border-radius:15px;background:rgba(0,0,0,.12);overflow:hidden}
.fillc{height:100%;width:0;background:linear-gradient(90deg,#b8892e,#f2c66d)}
.cap-lbl{font:700 22px Inter;margin-top:6px;opacity:.8}
.chart-lbl{font:700 22px Inter}
.stamp2{position:absolute;font:900 44px Fraunces;padding:6px 20px;border:5px solid;border-radius:10px;opacity:0;transform:rotate(-8deg)}
"""


def wheels_js(sel, start, dur, turns):
    return f"document.querySelectorAll('{sel}').forEach(w=>tl.to(w,{{rotation:'+={360 * turns}',transformOrigin:'50% 50%',duration:{dur},ease:'none'}},{start}));"


def build():
    a, b = L("c07_12"), L("c07_13")
    c14, c15 = L("c07_14"), L("c07_15")
    s = a[0] - .5
    w_prod, w_req, w_enorm, w_inv = W("productive", "c07_12"), W("require", "c07_12"), W("enormous", "c07_12"), W("investment", "c07_12")
    w_gen, w_subst, w_long, w_ret = W("generate", "c07_12"), W("substantial", "c07_12"), W("long-term", "c07_12"), W("returns", "c07_12")
    w_exp, w_rail2, w_places = W("expensive", "c07_13"), W("railway", "c07_13"), W("places", "c07_13")
    w_insuf, w_dem, w_become, w_dis = W("insufficient", "c07_13"), W("demand", "c07_13"), W("become", "c07_13"), W("disaster", "c07_13")
    w_much, w_spent = W("much", "c07_14"), W("spent", "c07_14")
    w_econ, w_ret2, w_just = W("economic", "c07_15"), W("returns", "c07_15"), W("justify", "c07_15")
    e = c15[1] + .6
    scenes, regions = [], []

    # ── A: 3D main line (approved locomotive), wheels → reveal the productive city ahead ────────
    tA = w_req - .05
    keysA = [[s, [6.5, 1.2, 5.2], [1.5, 1.3, 0], 34], [w_prod - .6, [3.5, 1.6, 6.8], [0, 1.6, 0], 34],
             [w_prod + .9, [-16, 11, 26], [55, 3, -10], 40], [tA + .5, [-12, 13, 30], [70, 4, -14], 40]]
    regions.append(("railway", [(s, tA + .3)], f"""AI3D.add('railway',{{start:{s},end:{tA + .3},world:'railway2',turn:1e9,
 keysA:{keysA},keysB:{keysA},returns:{w_prod + .6},sign:1e9}});"""))
    scenes.append(Scene("rwa", round(s, 3), round(tA + .3 - s, 3),
        '<div id="rwa-dip" class="fill" style="background:#1a120a;opacity:0"></div><div class="tag v" id="rwa-tag">Analogy</div>'
        '<div class="lbl" id="rwa-l1" style="left:120px;top:640px">Productive cities<small>real demand for travel and freight</small></div>',
        js=f"tl.fromTo('#rwa-dip',{{opacity:1}},{{opacity:0,duration:.5}},{s}); show('#rwa-tag',{s + .3}); show('#rwa-l1',{w_prod});"))

    # ── B: construction — capital deployed (from "require") ──────────────────────────────────────
    t0, t1 = tA, w_gen - .1
    gang = []
    js = [f"tl.fromTo('#rwb',{{opacity:0,x:120}},{{opacity:1,x:0,duration:.35,ease:'power2.out'}},{t0});",
          f"tl.fromTo('#rwb-cam',{{scale:1.32,x:60,transformOrigin:'58% 64%'}},{{scale:1.2,x:-60,transformOrigin:'58% 64%',duration:{t1 - t0 + .3},ease:'sine.inOut'}},{t0});"]
    # two-man rail carry walking toward the railhead
    carry = (f'<div id="rwb-carry" style="position:absolute;inset:0">'
             f'<div style="position:absolute;left:1360px;top:744px;width:420px;height:16px;background:#8a8f98;border:3px solid {O};border-radius:3px"></div>'
             + place(rig_svg("rwbk1", worker(1), "full"), 1310, 570, 170, flip=True) + place(rig_svg("rwbk2", worker(2), "full"), 1640, 574, 170, flip=True) + '</div>')
    for k in ("rwbk1", "rwbk2"):
        js.append(f"rpose('{k}','carry',{t0},.01);rwalk('{k}',null,{t0},{int((t1 - t0) / .42)},.42,0);")
    js.append(f"tl.fromTo('#rwb-carry',{{x:0}},{{x:-330,duration:{t1 - t0},ease:'none'}},{t0});")
    for i, (x, off) in enumerate([(930, 0), (1120, .27)]):
        gang.append(place(rig_svg(f"rwbh{i}", worker(3 + i), "full", prop_front="hammer"), x, 548, 180))
        js.append(f"rcycle('rwbh{i}','hammerUp','hammerDown',{t0},{t1 + .3},.55,{off});")
        js.append(f"for(let t={t0 + off + .5};t<{t1};t+=.55)tl.fromTo('#rwb-spark{i}',{{opacity:1,scale:.4}},{{opacity:0,scale:1.4,duration:.2}},t);")
    gang.append(place(rig_svg("rwbs", worker(6), "full", prop_front="shovel"), 1520, 552, 176, flip=True))
    js.append(f"rcycle('rwbs','carry','hammerDown',{t0},{t1 + .3},.7,.1);")
    gang.append(place(rig_svg("rwbf", look(70, hat="bowler", jacket="#3a3024", jacket_sh="#2a2218", jacket_hi="#5a4a38", tie="#6a1f1f", badge=False), "full",
                              prop_front="pad", prop_back="pen"), 330, 540, 180))
    js.append(f"ambient('rwbf',{t0},{t1 + .3},71,['point','write','point']);")
    sleepers_new = "".join(f'<rect class="rwb-sl" x="{1210 + k * 54}" y="694" width="24" height="22" fill="#5a3e26" stroke="{O}" stroke-width="2" opacity="0"/>' for k in range(10))
    bg = f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">{defs('rwb')}
 <rect x="-200" width="2320" height="1080" fill="url(#rwb-sky)"/>
 <path d="M-200 470 C200 380 520 430 820 400 C1180 360 1500 420 2120 380 L2120 640 L-200 640Z" fill="#b48a5a" opacity=".55"/>
 <path d="M-200 560 C300 500 800 540 1200 520 C1600 500 1900 540 2120 520 L2120 1080 L-200 1080Z" fill="url(#rwb-grass)"/>
 {''.join(f'<g><path d="M{x} 600 V430" stroke="#5a3e26" stroke-width="7"/><path d="M{x - 26} 444 H{x + 26}" stroke="#5a3e26" stroke-width="6"/></g>' for x in (-60, 420, 900, 1380, 1860))}
 <path d="M-200 448 Q-80 470 60 446 T420 446 T900 446 T1380 446 T1860 446" stroke="#2a2a2a" stroke-width="2" fill="none"/>
 <path d="M1150 720 L2120 720 L2120 760 L1150 760Z" fill="#9a7a52"/>
 {track(700, -300, 1210, 'rwb')}{sleepers_new}
 <rect id="rwb-newrail" x="1210" y="690" width="560" height="9" fill="#8a8f98" stroke="{O}" stroke-width="2" opacity="0"/>
 <g transform="translate(1600 600)">{''.join(f'<rect x="{k % 3 * 6}" y="{-k * 16}" width="200" height="14" fill="#6b4a2f" stroke="{O}" stroke-width="2"/>' for k in range(7))}</g>
 <g transform="translate(1800 520)"><path d="M0 120 L80 0 L160 120Z" fill="#e8dcc4" stroke="{O}" stroke-width="4"/><path d="M80 0 L80 120" stroke="{O}" stroke-width="3"/></g>
 {locomotive(-420, 430, .9, steam_id='rwb-steam')}
 <g transform="translate(60 0)">{boxcar(0, 520, 360, False, cid='rwb-flat')}</g>
 {derrick(260, 470)}
 <g id="rwb-spark0" style="opacity:0" transform="translate(1040 712)"><path d="M0 -18 L5 -5 L18 0 L5 5 L0 18 L-5 5 L-18 0 L-5 -5Z" fill="#ffd27a"/></g>
 <g id="rwb-spark1" style="opacity:0" transform="translate(1230 712)"><path d="M0 -18 L5 -5 L18 0 L5 5 L0 18 L-5 5 L-18 0 L-5 -5Z" fill="#ffd27a"/></g>
</svg>"""
    rows = ["Land &amp; grading", "Steel rails", "Labour", "Locomotives &amp; cars"]
    html = (f'<div id="rwb-cam" class="cam">{bg}{"".join(gang)}{carry}</div>' + ledger_capital("rwb", rows)
            + '<div class="tag v" id="rwb-tag">Building the line</div>')
    js += [f"show('#rwb-tag',{t0 + .2});",
           f"tl.fromTo('#rwb-jib',{{rotation:-14}},{{rotation:6,svgOrigin:'0 60',duration:1.1,ease:'power2.inOut'}},{w_enorm - .3});",
           f"tl.to('#rwb-load',{{y:150,duration:.8,ease:'power2.in'}},{w_inv});",
           f"tl.fromTo('#rwb-newrail',{{opacity:0}},{{opacity:1,duration:.2}},{w_inv + .8}); tl.to('#rwb-load',{{opacity:0,duration:.2}},{w_inv + .8});",
           f"document.querySelectorAll('.rwb-sl').forEach((e,i)=>tl.fromTo(e,{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.18}},{t0 + .2}+i*.26));",
           f"show('#rwb-cap',{w_enorm - .1},.3);",
           f"tl.to('#rwb-capbar',{{width:'100%',duration:{t1 - w_enorm},ease:'power1.inOut'}},{w_enorm});"]
    for i, t in enumerate([w_enorm + .1, w_inv, w_inv + .5, w_inv + 1.0]):
        js.append(f"tl.fromTo('#rwb-row{i}',{{opacity:0,x:30}},{{opacity:1,x:0,duration:.25}},{t});")
    scenes.append(Scene("rwb", round(t0, 3), round(t1 + .35 - t0, 3), html, css=CSS, js="\n".join(js)))

    # ── C: busy city station — returns accumulate (from "generate") ─────────────────────────────
    c0, c1 = t1, w_exp - .15
    html, js = station(px="rwc", busy=True, t0=c0, t1=c1)
    chart = f"""<div class="panel parch" id="rwc-ret" style="right:56px;top:40px;width:560px">
 <div class="ph">Returns over time <small>illustrative</small></div>
 <svg viewBox="0 0 500 250" width="500" height="250" style="overflow:visible">
  <path d="M40 10 V220 H490" stroke="#5a4a30" stroke-width="3" fill="none"/>
  <path d="M40 90 H490" stroke="#8a2a20" stroke-width="3" stroke-dasharray="10 8"/><text x="46" y="80" class="chart-lbl" fill="#8a2a20">Upfront cost</text>
  <path id="rwc-gain" d="M262 90 L300 75 L360 52 L420 32 L490 14 L490 90Z" fill="#4a8a3a" opacity="0"/>
  <path id="rwc-line" d="M40 220 L100 196 L160 168 L220 128 L262 90 L300 75 L360 52 L420 32 L490 14" stroke="#2e6a2a" stroke-width="6" fill="none" stroke-linecap="round"/>
  <text x="40" y="246" class="chart-lbl" fill="#5a4a30">Year 1</text><text id="rwc-yr" x="490" y="246" text-anchor="end" class="chart-lbl" fill="#5a4a30">Year 30</text>
  <text x="120" y="160" class="chart-lbl" fill="#2e6a2a" id="rwc-cum">fares + freight, cumulative</text>
 </svg><div class="stamp2" id="rwc-st" style="right:40px;top:330px;color:#2e6a2a;border-color:#2e6a2a">Cost recovered</div></div>"""
    html += chart + '<div class="tag v" id="rwc-tag">Strong demand</div>'
    js += f"""
show('#rwc-tag',{c0 + .2}); show('#rwc-ret',{w_subst - .1},.3);
(function(){{const el=document.getElementById('rwc-line'),n=el.getTotalLength();gsap.set(el,{{strokeDasharray:n,strokeDashoffset:n}});
 tl.to(el,{{strokeDashoffset:0,duration:{w_ret + .9 - w_subst},ease:'power1.inOut'}},{w_subst});}})();
show('#rwc-gain',{w_ret}); tl.fromTo('#rwc-st',{{opacity:0,scale:1.6}},{{opacity:1,scale:1,duration:.3,ease:'back.out(2)'}},{w_ret - .1});
"""
    scenes.append(Scene("rwc", round(c0, 3), round(c1 + .3 - c0, 3), html, css=CSS, js=js))

    # ── D: failing branch — same cost, insufficient demand, losses (from "expensive") ────────────
    d0, d1 = c1, w_become + .05
    html, js = station(px="rwd", busy=False, t0=d0, t1=d1, arrive=(w_rail2, w_places))
    years = [(60, 66), (50, 66), (41, 66), (33, 66), (27, 66), (22, 66), (18, 66), (15, 66)]
    bars = "".join(
        f'<g class="rwd-yr" opacity="0"><rect x="{60 + i * 54}" y="{220 - c}" width="40" height="{c}" fill="none" stroke="#e07a5f" stroke-width="3" stroke-dasharray="6 4"/>'
        f'<rect x="{60 + i * 54}" y="{220 - r}" width="40" height="{r}" fill="#5fb36a"/>'
        f'<rect class="rwd-gap" x="{60 + i * 54}" y="{220 - c}" width="40" height="{c - r}" fill="#d9503f" opacity=".75"/></g>'
        for i, (r, c) in enumerate(years))
    pnl = f"""<div class="panel slate" id="rwd-pl" style="right:56px;top:40px;width:560px">
 <div class="ph">Each year <small>illustrative</small></div>
 <svg viewBox="0 0 500 250" width="500" height="250" style="overflow:visible">
  <path d="M40 10 V220 H490" stroke="#8a9aaa" stroke-width="3" fill="none"/>{bars}
  <text x="60" y="246" class="chart-lbl" fill="#cfd8e2">Year 1</text><text x="490" y="246" text-anchor="end" class="chart-lbl" fill="#cfd8e2">Year 8</text>
 </svg>
 <div style="display:flex;flex-direction:column;gap:4px;font:700 26px Inter;margin-top:6px"><span><b style="color:#5fb36a">■</b> revenue</span><span><b style="color:#e07a5f">▭</b> operating + maintenance + interest</span></div>
 <div style="font:800 30px Inter;color:#ff7a66;margin-top:8px;opacity:0" id="rwd-loss">Losses accumulate</div></div>"""
    html += ledger_capital("rwd", ["Land &amp; grading", "Steel rails", "Labour", "Locomotives &amp; cars"], top=40).replace('class="panel parch"', 'class="panel slate"') \
        + pnl + '<div class="tag v" id="rwd-tag">Insufficient demand</div>'
    js += f"""
show('#rwd-cap',{w_exp},.25); document.querySelectorAll('#rwd-cap .cap-row').forEach(r=>tl.set(r,{{opacity:1}},{w_exp}));
tl.fromTo('#rwd-capbar',{{width:'0%'}},{{width:'100%',duration:.7,ease:'power2.out'}},{w_exp}); hide('#rwd-cap',{w_insuf - .4},.3);
show('#rwd-tag',{w_insuf}); show('#rwd-pl',{w_insuf - .2},.3);
document.querySelectorAll('.rwd-yr').forEach((g,i)=>tl.to(g,{{opacity:1,duration:.15}},{w_insuf}+i*.2));
tl.fromTo('.rwd-gap',{{opacity:.2}},{{opacity:.9,duration:.3,stagger:.2}},{w_dem}); show('#rwd-loss',{w_dem + .6});
"""
    scenes.append(Scene("rwd", round(d0, 3), round(d1 + .35 - d0, 3), html, css=CSS, js=js))

    # ── E: consequence — the same station decays; the sign falls on "disaster" ──────────────────
    e0, e1 = d1, c14[0] - .05
    html, js = station(px="rwe", busy=False, t0=e0, t1=e1, ruined=True, sign_t=w_dis)
    html += '<div class="tag v" id="rwe-tag">Financial disaster</div>'
    js += f"show('#rwe-tag',{w_dis});"
    scenes.append(Scene("rwe", round(e0, 3), round(e1 + .3 - e0, 3), html, css=CSS, js=js))

    # ── F: spending vs returns — the critical question ───────────────────────────────────────────
    f0 = e1
    col = lambda k, name, sub, ret, ok: f"""<div class="fcol" style="left:{180 + k * 840}px">
 <div class="ph" style="color:#f3e3c3">{name}<small style="color:#f3e3c3">{sub}</small></div>
 <div class="fbars"><div class="fb"><div class="fbf spend" id="rwf-s{k}"></div><span>Money spent</span></div>
 <div class="fb"><div class="fbf ret{'' if ok else ' bad'}" id="rwf-r{k}" data-h="{ret}"></div><span>Returns</span></div>
 <div class="fline" id="rwf-l{k}"></div></div>
 <div class="stamp2" id="rwf-v{k}" style="left:330px;top:120px;color:{'#7fdc8a' if ok else '#ff7a66'};border-color:{'#7fdc8a' if ok else '#ff7a66'}">{'Justified' if ok else 'Not justified'}</div></div>"""
    html = (f'<div class="fill" style="background:radial-gradient(ellipse at 50% 40%,#3a2a1a,#140d07)"></div>'
            + col(0, "Productive cities", "strong demand", 340, True) + col(1, "Insufficient demand", "weak demand", 120, False)
            + '<div class="tag l" id="rwf-tag">Illustrative</div>')
    css = CSS + """.fcol{position:absolute;top:110px;width:600px;height:700px}.fcol .ph{font-size:44px}.fcol .ph small{font-size:24px}
.fbars{position:relative;height:520px;margin-top:20px;display:flex;gap:80px;align-items:flex-end;padding:0 60px;border-bottom:4px solid #b8892e}
.fb{width:150px;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;font:700 26px Inter;color:#f3e3c3}
.fb span{margin-top:12px;position:absolute;bottom:-46px}.fbf{width:150px;height:0;border-radius:8px 8px 0 0}
.spend{background:linear-gradient(#f2c66d,#b8892e)}.ret{background:linear-gradient(#7fdc8a,#2e6a2a)}.ret.bad{background:linear-gradient(#e0a07a,#8a3a2a)}
.fline{position:absolute;left:30px;right:30px;bottom:240px;border-top:4px dashed #f2c66d;opacity:0}"""
    js = f"""
tl.fromTo('#rwf',{{opacity:0}},{{opacity:1,duration:.4}},{f0});
show('#rwf-tag',{f0 + .3});
tl.to(['#rwf-s0','#rwf-s1'],{{height:240,duration:1.1,ease:'power2.out'}},{w_much});
show(['#rwf-l0','#rwf-l1'],{w_spent});
tl.to('#rwf-r0',{{height:340,duration:1.3,ease:'power2.out'}},{w_econ}); tl.to('#rwf-r1',{{height:120,duration:1.0,ease:'power2.out'}},{w_econ + .1});
tl.fromTo('#rwf-v0',{{opacity:0,scale:1.6}},{{opacity:1,scale:1,duration:.3,ease:'back.out(2)'}},{w_just});
tl.fromTo('#rwf-v1',{{opacity:0,scale:1.6}},{{opacity:1,scale:1,duration:.3,ease:'back.out(2)'}},{w_just + .25});
"""
    scenes.append(Scene("rwf", round(f0, 3), round(e - f0, 3), html, css=css, js=js))
    return scenes, regions, ""


def station(px, busy, t0, t1, arrive=None, ruined=False, sign_t=None):
    """City station (busy) or branch station (cold). Returns (html, js)."""
    cold = not busy
    name = "CENTRAL STATION" if busy else "MILL CREEK"
    js = [f"tl.fromTo('#{px}',{{opacity:0}},{{opacity:1,duration:.3}},{t0});",
          f"tl.fromTo('#{px}-cam',{{scale:1.06,x:30}},{{scale:1.0,x:-30,duration:{t1 - t0 + .3},ease:'sine.inOut'}},{t0});"]
    city = ""
    if busy:
        city = "".join(f'<rect x="{x}" y="{260 - h}" width="{w}" height="{h + 200}" fill="{c}" stroke="{O}" stroke-width="3"/>'
                       + "".join(f'<rect x="{x + 12 + j * 26}" y="{280 - h + r * 34}" width="14" height="20" fill="#ffd27a" opacity=".8"/>' for j in range(max(1, (w - 20) // 26)) for r in range(3))
                       for x, w, h, c in [(-60, 160, 120, "#9a6a4a"), (1000, 140, 160, "#8a5a3a"), (1160, 180, 110, "#a87a5a"), (1360, 120, 190, "#7a4a32"), (1500, 200, 130, "#9a6a4a"), (1720, 160, 170, "#8a5a3a")])
        city += "".join(f'<g><rect x="{x}" y="40" width="34" height="220" fill="#7a3e2a" stroke="{O}" stroke-width="3"/><g id="{px}-smk{k}">'
                        + "".join(f'<circle cx="{x + 17 + j * 22}" cy="{20 - j * 30}" r="{18 + j * 8}" fill="#b0a898" opacity="{.6 - j * .1}"/>' for j in range(5)) + '</g></g>'
                        for k, x in enumerate((1100, 1300, 1640)))
    weeds = "" if busy else "".join(f'<path d="M{x} 720 l-8 -{30 + (x % 40)} M{x} 720 l9 -{24 + (x % 30)} M{x} 720 l1 -{40 + (x % 20)}" stroke="#6f7a4a" stroke-width="4"/>' for x in range(-100, 2000, 97))
    bg = f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">{defs(px, cold)}
 <rect x="-200" width="2320" height="1080" fill="url(#{px}-sky)"/>
 {city if busy else f'<path d="M-200 420 C300 360 800 400 1300 370 C1700 350 1900 380 2120 370 L2120 720 L-200 720Z" fill="url(#{px}-grass)"/>'}
 {station_building(80 if busy else 260, 150 if busy else 210, px, cold, name)}
 {track(700, -300, 2300, px, rusty=cold)}
</svg>"""
    # train (busy: standing at platform, loading; branch: arrives empty)
    if busy:
        train = (f'<div id="{px}-train" style="position:absolute;inset:0"><svg viewBox="0 0 1920 1080" class="full" style="overflow:visible">'
                 + boxcar(-120, 528, 330, False, cid=f"{px}-box") + coach(240, 528, 380, True, cid=f"{px}-c1") + coach(640, 528, 380, True, cid=f"{px}-c2")
                 + locomotive(1040, 452, .95, steam_id=f"{px}-steam") + '</svg></div>')
    elif not ruined:
        train = (f'<div id="{px}-train" style="position:absolute;inset:0"><svg viewBox="0 0 1920 1080" class="full" style="overflow:visible">'
                 + locomotive(1000, 452, .95) + boxcar(640, 528, 340, False, True, cid=f"{px}-f1") + coach(240, 528, 380, False, True, cid=f"{px}-c1")
                 + '</svg></div>')
    else:
        train = ""
    # platform (front), canopy, ticket booth
    plat = f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
 {canopy(-100, 2020, 330, px, cold) if not ruined else ''}
 <rect x="-200" y="740" width="2320" height="340" fill="url(#{px}-plank)" stroke="{O}" stroke-width="4"/>
 <rect x="-200" y="730" width="2320" height="18" fill="{'#8a8478' if cold else '#d8c8a0'}" stroke="{O}" stroke-width="3"/>
 <g transform="translate(70 520)"><rect width="300" height="230" fill="{'#5e544c' if cold else '#6b4a2f'}" stroke="{O}" stroke-width="5"/>
  <rect x="40" y="40" width="220" height="110" fill="{'#2a2c30' if cold else '#ffd99a'}" stroke="{O}" stroke-width="4"/>
  <rect x="20" y="-34" width="260" height="40" rx="4" fill="#1e2a22" stroke="{O}" stroke-width="3"/>
  <text x="150" y="-6" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="26" fill="#f2c66d">TICKETS</text>
  <rect x="30" y="150" width="240" height="16" fill="#3a2a1a"/></g>
 {weeds}
</svg>"""
    chars = []
    clerk = place(rig_svg(f"{px}k", traveller(9, cold) | dict(hat=None, tie="#1f3a2a"), "bust"), 140, 520, 160).replace("height:267px", "height:192px")
    chars.append(f'<div style="position:absolute;left:0;top:0;width:1920px;height:1080px;clip-path:inset(560px 1550px 370px 110px)">{clerk}</div>')
    if busy:
        # queue paying at the booth; travellers boarding; porter with trunks; freight crane loading the box car
        chars.append(place(rig_svg(f"{px}q0", traveller(0), "full", prop_front="coin"), 330, 560, 180, flip=True))
        chars.append(place(rig_svg(f"{px}q1", traveller(1), "full", prop_back="suitcase"), 470, 566, 176, flip=True))
        js.append(f"rpose('{px}q0','pay',{t0 + .2},.3); rpose('{px}q0','neutral',{t0 + 1.2},.3); rpose('{px}q0','pay',{t0 + 2.1},.3);")
        js.append(f"rpose('{px}k','pay',{t0 + .6},.3);rpose('{px}k','write',{t0 + 1.3},.3);rpose('{px}k','pay',{t0 + 2.5},.3);")
        for k, t in enumerate((t0 + .5, t0 + 1.4, t0 + 2.3)):
            js.append(f"tl.fromTo('#{px}-coin{k}',{{opacity:1,x:0,y:0}},{{opacity:0,x:{1500 - 360},y:-560,duration:.9,ease:'power2.in'}},{t});")
        for i, (x, prop) in enumerate([(700, "suitcase"), (900, "sack"), (1180, None), (1380, "suitcase"), (1560, "newspaper")]):
            cid = f"{px}p{i}"
            flip = i % 2 == 0
            chars.append(f'<div id="{cid}-wrap" style="position:absolute;inset:0">' + place(rig_svg(cid, traveller(2 + i), "full", prop_back=prop if prop != "newspaper" else None,
                         prop_front="newspaper" if prop == "newspaper" else None), x, 566 + (i % 2) * 8, 176, flip=flip) + '</div>')
            dx = (-1 if flip else 1) * (140 + i * 20)
            js.append(f"rwalk('{cid}','#{cid}-wrap',{t0 + .1 * i},{int((t1 - t0 - .4) / .4)},.4,{dx});")
            js.append(f"tl.to('#{cid}-wrap',{{opacity:0,y:-20,duration:.3}},{t1 - .6 + .05 * i});")
        chars.append(f'<div id="{px}-crate" style="position:absolute;left:-40px;top:300px;width:120px;height:90px;background:#c98a4a;border:4px solid {O}"></div>'
                     f'<div id="{px}-rope" style="position:absolute;left:18px;top:120px;width:4px;height:180px;background:#2a2a2a"></div>')
        js.append(f"tl.fromTo(['#{px}-crate','#{px}-rope'],{{y:-120}},{{y:150,duration:1.4,ease:'power2.inOut'}},{t0 + .3});")
        js.append(f"tl.to('#{px}-crate',{{opacity:0,duration:.2}},{t0 + 1.8}); tl.to('#{px}-box .lw',{{opacity:1}},{t0});")
        coins = "".join(f'<div id="{px}-coin{k}" style="position:absolute;left:330px;top:640px;width:30px;height:30px;border-radius:50%;background:#f2c66d;border:3px solid #8a6a1c;opacity:0"></div>' for k in range(3))
        chars.append(coins)
        js.append(f"tl.fromTo('#{px}-steam',{{opacity:.8}},{{opacity:.3,duration:.4,yoyo:true,repeat:7}},{t0});")
        for k in range(3):
            js.append(f"tl.fromTo('#{px}-smk{k}',{{x:0,y:0,opacity:.9}},{{x:60,y:-40,opacity:.5,duration:{t1 - t0},ease:'sine.out'}},{t0});")
    elif not ruined:
        # branch: empty train rolls in and stops; one waiting passenger; porter sits idle; clerk slumps
        ta, tb = arrive
        js.append(f"tl.fromTo('#{px}-train',{{x:1600}},{{x:0,duration:{tb - ta + .4},ease:'power2.out'}},{ta - .3});")
        js.append(f"document.querySelectorAll('#{px}-train .lw').forEach(w=>tl.fromTo(w,{{rotation:0}},{{rotation:-900,transformOrigin:'50% 50%',duration:{tb - ta + .4},ease:'power2.out'}},{ta - .3}));")
        chars.append(place(rig_svg(f"{px}p0", traveller(5) | dict(hat="top"), "full", prop_back="suitcase"), 1300, 566, 176, flip=True))
        js.append(f"ambient('{px}p0',{t0},{t1},91,['neutral','hold','shrug']);")
        chars.append(place(rig_svg(f"{px}po", worker(8) | dict(hat="cap"), "full"), 820, 600, 170))
        js.append(f"rpose('{px}po','sit',{t0},.01); rexpress('{px}po','worry',{t0 + 1});")
        js.append(f"rpose('{px}k','slump',{t0 + .2},.4); rexpress('{px}k','worry',{t0 + .5});")
    else:
        # decay: windows board up, canopy panels gone, weeds, sign falls on the cue
        chars = [f'<svg viewBox="0 0 1920 1080" class="full" style="overflow:visible"><g id="{px}-sign" transform="translate(470 302)">'
                 f'<rect x="0" y="0" width="340" height="46" rx="4" fill="#1e2a22" stroke="{O}" stroke-width="4"/>'
                 f'<text x="170" y="32" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="30" fill="#b8a070">MILL CREEK</text></g>'
                 + "".join(f'<path d="M{x} 760 l-12 -{60 + (x % 50)} M{x} 760 l14 -{50 + (x % 40)} M{x} 760 l2 -{80 + (x % 30)}" stroke="#5f6a3e" stroke-width="5"/>' for x in range(-100, 2000, 61))
                 + "".join(f'<path d="M{x} 700 l-10 -{40 + (x % 30)} M{x} 700 l12 -{30 + (x % 20)}" stroke="#5f6a3e" stroke-width="4"/>' for x in range(-80, 2000, 43))
                 + '</svg>']
        js.append(f"tl.fromTo('#{px}-sign',{{rotation:0}},{{rotation:68,svgOrigin:'470 302',duration:.55,ease:'bounce.out'}},{sign_t});")
        js.append(f"tl.fromTo('#{px}',{{filter:'saturate(.9) brightness(1)'}},{{filter:'saturate(.45) brightness(.75)',duration:{t1 - t0}}},{t0});")
    html = (f'<div id="{px}-cam" class="cam">{bg}{train}{plat}{"".join(chars)}</div>')
    return html, "\n".join(js)
