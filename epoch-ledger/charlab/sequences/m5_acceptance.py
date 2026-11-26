"""M5 acceptance sequence: "Profitable, and broke" (25 s). Narration-driven: every visual is keyed to the words it shows.

Beats (times come from the episode's timeline.json, never hard-coded durations):
  A  3D bakery        "Every morning, Nadia's bakery sold out."            → the place and the person: a full display case
  L  document         "On paper, it made a profit every month."            → her ledger; twelve monthly profits tick in on "every month"
  T  payment timeline "supplier … thirty days … café chain … ninety"       → money out at day 30, money in at day 90, the gap
  C  cash chart       "more cash went out than came in … ran dry"          → monthly out vs in; the balance line crosses zero on "dry"
  B  3D bank          Nadia: "We're busy every day. I just can't pay my suppliers."  (her own line → lip sync)
                      "Profitable, and broke."  (narration → no lip sync; wide shot, the two of them, the problem on the desk)
Transitions carry meaning: the camera pushes into the bakery, the ledger takes over the frame; the ledger's date column
becomes the timeline's axis; the timeline's gap becomes the chart; the chart's zero line dissolves into the bank.
"""
from kit.assemble import Scene

TITLE = "The Epoch Ledger · M5 acceptance · Profitable, and broke"
EPISODE = "projects/charlab_m5/story"
NARRATION_WAV = "projects/charlab_m5/hf/narration.wav"
DURATION = 25.0
SHOTS = [
    {"id": "bakery", "demo": "epoch-ledger/charlab/motion/demos/m5_bakery.json", "start": 0.0},
    {"id": "bank", "demo": "epoch-ledger/charlab/motion/demos/m5_bank.json", "start": 18.6, "quality": "standard"},   # close-up: faces
]

PAPER, INK, GOLD, RED, GREEN, BROWN = "#f4ecdd", "#2b2118", "#c9963a", "#b5473a", "#3d7a52", "#6e4a30"
CSS = f"""
.m5f{{position:absolute;inset:0;overflow:hidden}}
.m5paper{{position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 40%,#f7f0e3 0%,#efe3cd 70%,#e3d3b6 100%)}}
.m5grain{{position:absolute;inset:0;opacity:.35;background-image:repeating-linear-gradient(0deg,rgba(90,60,30,.035) 0 2px,transparent 2px 5px),repeating-linear-gradient(90deg,rgba(90,60,30,.03) 0 3px,transparent 3px 7px)}}
.m5h{{position:absolute;font:700 46px Fraunces,Georgia,serif;color:{INK};letter-spacing:.2px}}
.m5s{{position:absolute;font:600 26px Inter,sans-serif;color:#6b5a48;letter-spacing:1.5px;text-transform:uppercase}}
.m5l{{position:absolute;font:600 30px Inter,sans-serif;color:{INK}}}
.m5n{{position:absolute;font:700 34px Fraunces,Georgia,serif}}
"""


def _svg(inner, vb="0 0 1920 1080"):
    return f'<svg viewBox="{vb}" width="1920" height="1080" style="position:absolute;inset:0" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'


def scenes(T):
    words = T["words"]

    def W(word, n=1, end=False):
        """time of the n-th spoken occurrence of word (case/punctuation-insensitive)"""
        k = 0
        for w in words:
            if w["word"].strip(".,!?").lower() == word.lower():
                k += 1
                if k == n:
                    return w["end" if end else "start"]
        raise KeyError(word)
    B = {b["id"]: b for b in T["beats"]}
    out = []

    # ── L: the ledger — "On paper, it made a profit every month." ───────────────────────────────────────────────────
    l0, l1 = W("paper") - .35, B["n2"]["start"] + .05
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    prof = [1240, 1310, 1180, 1420, 1390, 1510, 1460, 1330, 1290, 1480, 1550, 1620]
    rows = "".join(
        f'<g class="lr" id="lr{i}" opacity="0"><text x="640" y="{372 + i * 46}" font-family="Inter" font-weight="600" font-size="25" fill="#5a4a3a">{m}</text>'
        f'<text x="900" y="{372 + i * 46}" font-family="Inter" font-size="25" fill="#5a4a3a" text-anchor="end">{(9000 + p * 2):,}</text>'
        f'<text x="1100" y="{372 + i * 46}" font-family="Inter" font-size="25" fill="#5a4a3a" text-anchor="end">{(9000 + p):,}</text>'
        f'<text class="lp" x="1290" y="{372 + i * 46}" font-family="Fraunces" font-weight="700" font-size="27" fill="{GREEN}" text-anchor="end" opacity="0">+£{p:,}</text>'
        f'<path class="lt" opacity="0" d="M1310 {362 + i * 46} l8 9 l16 -18" stroke="{GREEN}" stroke-width="4" fill="none" stroke-linecap="round"/>'
        f'<line x1="630" y1="{384 + i * 46}" x2="1340" y2="{384 + i * 46}" stroke="#d9ccb4" stroke-width="1.5"/></g>'
        for i, (m, p) in enumerate(zip(months, prof)))
    sheet = (f'<g transform="translate(0 -75)"><g id="lsheet"><rect x="580" y="170" width="800" height="900" rx="6" fill="#fbf7ee" stroke="#cdbb98" stroke-width="2"/>'
             f'<text x="640" y="238" font-family="Fraunces" font-weight="700" font-size="40" fill="{INK}">Nadia\'s Bakery</text>'
             f'<text x="640" y="276" font-family="Inter" font-weight="600" font-size="20" fill="#8a7a64" letter-spacing="2">PROFIT AND LOSS · MONTHLY</text>'
             f'<text x="900" y="322" font-family="Inter" font-weight="700" font-size="19" fill="#8a7a64" text-anchor="end">SALES</text>'
             f'<text x="1100" y="322" font-family="Inter" font-weight="700" font-size="19" fill="#8a7a64" text-anchor="end">COSTS</text>'
             f'<text id="lph" x="1290" y="322" font-family="Inter" font-weight="700" font-size="19" fill="#8a7a64" text-anchor="end">PROFIT</text>'
             f'<line x1="630" y1="336" x2="1340" y2="336" stroke="{INK}" stroke-width="2"/>{rows}</g></g>')
    wood = ('<div class="m5f" style="background:linear-gradient(180deg,#8a5a3a,#6e4a30);"></div>'
            '<div class="m5f" style="opacity:.25;background:repeating-linear-gradient(92deg,rgba(40,20,10,.5) 0 2px,transparent 2px 38px),repeating-linear-gradient(88deg,rgba(255,220,170,.25) 0 1px,transparent 1px 23px)"></div>'
            '<div class="m5f" style="background:radial-gradient(70% 60% at 45% 35%,rgba(255,226,170,.35),transparent 70%)"></div>')
    lshadow = '<div id="lsh" style="position:absolute;left:600px;top:200px;width:800px;height:900px;border-radius:8px;box-shadow:0 30px 60px rgba(30,15,5,.45);transform:rotate(-3deg)"></div>'
    every = W("every", 2)
    js = (f"tl.fromTo('#L',{{opacity:0}},{{opacity:1,duration:.45,ease:'power2.out',immediateRender:false}},{l0});"
          f"tl.fromTo('#Lcam',{{scale:1.18,rotation:-3,y:120}},{{scale:1.0,rotation:-3,y:0,duration:{l1 - l0 + .3:.2f},ease:'power1.out',immediateRender:false}},{l0});"
          f"tl.to('#L .lr',{{opacity:1,duration:.18,stagger:.045}},{l0 + .15:.2f});"
          f"tl.fromTo('#lph',{{fill:'#8a7a64'}},{{fill:'{GREEN}',duration:.3}},{W('profit') - .05:.2f});"
          f"tl.to('#L .lp',{{opacity:1,duration:.12,stagger:{(W('month', 1, True) - every) / 12:.3f}}},{every:.2f});"
          f"tl.to('#L .lt',{{opacity:1,duration:.05,stagger:{(W('month', 1, True) - every) / 12:.3f}}},{every + .05:.2f});"
          f"mDrawOn('#L .lt',{every + .05:.2f},{{dur:.22,stagger:{(W('month', 1, True) - every) / 12:.3f}}});"
          f"tl.to('#Lcam',{{y:-260,scale:.92,opacity:0,duration:.55,ease:'power2.in'}},{l1 - .45:.2f});")
    out.append(Scene("L", l0, l1 - l0 + .2, wood + f'<div id="Lcam" class="m5f">{lshadow}<div class="m5f" style="transform:rotate(-3deg)">{_svg(sheet)}</div></div>', js=js))

    # ── T: payment timeline — "Her flour supplier wanted payment in thirty days. Her biggest customer, a café chain, paid in ninety."
    t0, t1 = B["n2"]["start"] - .2, B["n3"]["start"] + .25
    X = lambda d: 300 + d * 14.0
    ax = 600
    ticks = "".join(f'<g class="tk" opacity="0"><line x1="{X(d)}" y1="{ax - 12}" x2="{X(d)}" y2="{ax + 12}" stroke="{INK}" stroke-width="3"/>'
                    f'<text x="{X(d)}" y="{ax + 52}" font-family="Inter" font-weight="700" font-size="26" fill="#6b5a48" text-anchor="middle">DAY {d}</text></g>' for d in (0, 30, 60, 90))
    sack = (f'<g transform="translate({X(30)} 250)"><g id="tsup" opacity="0"><path d="M-62 70 C-70 10 -50 -40 -30 -55 L30 -55 C50 -40 70 10 62 70 Z" fill="#efe3c6" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M-34 -55 Q0 -75 34 -55" stroke="{INK}" stroke-width="4" fill="none"/><text y="20" font-family="Inter" font-weight="800" font-size="22" fill="{BROWN}" text-anchor="middle">FLOUR</text>'
            f'<text x="95" y="-10" font-family="Fraunces" font-weight="700" font-size="34" fill="{INK}">Flour supplier</text>'
            f'<text x="95" y="28" font-family="Inter" font-weight="600" font-size="24" fill="#6b5a48">wants payment in 30 days</text></g></g>')
    cafe = (f'<g transform="translate({X(90)} 815)"><g id="tcafe" opacity="0"><path d="M-48 -40 H40 V10 C40 45 -48 45 -48 10 Z" fill="#fbf7ee" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M40 -28 C70 -28 70 8 40 8" stroke="{INK}" stroke-width="4" fill="none"/><path d="M-60 52 H52" stroke="{INK}" stroke-width="4"/>'
            f'<path class="steam" d="M-22 -55 c-10 -14 10 -22 0 -38 M2 -55 c-10 -14 10 -22 0 -38" stroke="#8a7a64" stroke-width="3" fill="none"/>'
            f'<text x="-90" y="-10" font-family="Fraunces" font-weight="700" font-size="34" fill="{INK}" text-anchor="end">Café chain</text>'
            f'<text x="-90" y="28" font-family="Inter" font-weight="600" font-size="24" fill="#6b5a48" text-anchor="end">her biggest customer · pays in 90 days</text></g></g>')
    shop = (f'<g id="tshop" opacity="0" transform="translate({X(0)} {ax})"><circle r="16" fill="{GOLD}" stroke="{INK}" stroke-width="3"/>'
            f'<text x="-30" y="-34" font-family="Fraunces" font-weight="700" font-size="30" fill="{INK}">Nadia\'s cash</text></g>')
    outp = f'<path id="tout" d="M{X(30)} {ax - 18} C{X(30)} {ax - 120} {X(30)} {ax - 170} {X(30)} 330" stroke="{RED}" stroke-width="8" fill="none" stroke-linecap="round"/>'
    outh = f'<path id="touth" opacity="0" d="M{X(30) - 18} 352 L{X(30)} 326 L{X(30) + 18} 352" stroke="{RED}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    outl = f'<text id="toutl" opacity="0" x="{X(30) - 26}" y="{ax - 120}" font-family="Fraunces" font-weight="700" font-size="36" fill="{RED}" text-anchor="end">−£9,000 out</text>'
    inp = f'<path id="tin" d="M{X(90)} 760 C{X(90)} 720 {X(90)} 690 {X(90)} {ax + 22}" stroke="{GREEN}" stroke-width="8" fill="none" stroke-linecap="round"/>'
    inh = f'<path id="tinh" opacity="0" d="M{X(90) - 18} {ax + 46} L{X(90)} {ax + 20} L{X(90) + 18} {ax + 46}" stroke="{GREEN}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    inl = f'<text id="tinl" opacity="0" x="{X(90) + 30}" y="{ax + 130}" font-family="Fraunces" font-weight="700" font-size="36" fill="{GREEN}">+£11,000 in</text>'
    gap = (f'<g id="tgap" opacity="0"><rect x="{X(30)}" y="{ax - 26}" width="{X(90) - X(30)}" height="52" fill="{RED}" opacity=".16"/>'
           f'<path d="M{X(30)} {ax + 70} v14 H{X(90)} v-14" stroke="{RED}" stroke-width="4" fill="none"/>'
           f'<text x="{(X(30) + X(90)) / 2}" y="{ax + 128}" font-family="Fraunces" font-weight="700" font-size="38" fill="{RED}" text-anchor="middle">60 days waiting for her money</text></g>')
    head = f'<g id="thead" opacity="0"><circle cx="{X(0)}" cy="{ax}" r="11" fill="{INK}"/></g>'
    tsvg = (f'<path id="taxis" d="M{X(0) - 40} {ax} H{X(90) + 70}" stroke="{INK}" stroke-width="5" fill="none"/>{ticks}{gap}{shop}{sack}{cafe}{outp}{outh}{outl}{inp}{inh}{inl}{head}')
    pay, thirty, ninety = W("payment"), W("thirty") if any(w["word"].lower().startswith("thirty") for w in words) else W("30"), W("ninety") if any(w["word"].lower().startswith("ninety") for w in words) else W("90")
    js = (f"tl.fromTo('#T',{{opacity:0}},{{opacity:1,duration:.4,immediateRender:false}},{t0});"
          f"mDrawOn('#taxis',{t0 + .1:.2f},{{dur:.6}});tl.to('#T .tk',{{opacity:1,duration:.25,stagger:.08}},{t0 + .35:.2f});"
          f"tl.to('#tshop',{{opacity:1,duration:.3}},{t0 + .3:.2f});"
          f"tl.fromTo('#tsup',{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.45,ease:MOTION.ease.settle,immediateRender:false}},{W('flour') - .05:.2f});"
          # the day marker travels to day 30 as "payment in thirty days" is said
          f"tl.to('#thead',{{opacity:1,duration:.2}},{pay - .2:.2f});tl.fromTo('#thead',{{x:0}},{{x:{X(30) - X(0)},duration:{thirty - pay + .25:.2f},ease:'power1.inOut',immediateRender:false}},{pay:.2f});"
          f"mDrawOn('#tout',{thirty + .2:.2f},{{dur:.45}});tl.to('#touth',{{opacity:1,duration:.15}},{thirty + .6:.2f});tl.fromTo('#toutl',{{opacity:0,x:20}},{{opacity:1,x:0,duration:.35,immediateRender:false}},{thirty + .55:.2f});"
          f"tl.fromTo('#tcafe',{{opacity:0,y:30}},{{opacity:1,y:0,duration:.45,ease:MOTION.ease.settle,immediateRender:false}},{W('café') - .25:.2f});"
          f"tl.fromTo('#T .steam',{{y:0,opacity:.9}},{{y:-8,opacity:.4,duration:1.2,repeat:3,yoyo:true,ease:'sine.inOut',immediateRender:false}},{W('café'):.2f});"
          f"tl.to('#thead',{{x:{X(90) - X(0)},duration:{ninety - W('paid') + .5:.2f},ease:'power1.inOut'}},{W('paid') - .3:.2f});"
          f"mDrawOn('#tin',{ninety + .05:.2f},{{dur:.45}});tl.to('#tinh',{{opacity:1,duration:.15}},{ninety + .45:.2f});tl.fromTo('#tinl',{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.35,immediateRender:false}},{ninety + .4:.2f});"
          f"tl.fromTo('#tgap',{{opacity:0}},{{opacity:1,duration:.45}},{ninety + .75:.2f});"
          f"tl.to('#Tcam',{{scale:1.5,x:-180,y:120,opacity:0,duration:.5,ease:'power2.in'}},{t1 - .45:.2f});")
    out.append(Scene("T", t0, t1 - t0 + .1, f'<div class="m5paper"></div><div class="m5grain"></div><div id="Tcam" class="m5f">{_svg(tsvg)}'
                     f'<div class="m5s" style="left:300px;top:150px">How the money moved</div></div>', js=js))

    # ── C: cash balance — "So each month, more cash went out than came in, until the account ran dry." ─────────────────
    c0, c1 = B["n3"]["start"] - .15, B["dialogue"]["start"] - .45
    mo = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN"]
    bal = [12000, 9500, 7000, 4500, 2000, 0]     # "ran dry": exactly £0 (no overdraft is modelled)
    x0, dx, zy, sc = 420, 230, 700, 0.034            # zero line at y=700; £1 = .034 px
    px = [x0 + i * dx for i in range(6)]
    py = [zy - b * sc for b in bal]
    line = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in zip(px, py))
    area = line + f" L{px[-1]} {zy} L{px[0]} {zy} Z"
    labels = "".join(f'<text x="{x}" y="{zy + 330}" font-family="Inter" font-weight="700" font-size="24" fill="#6b5a48" text-anchor="middle">{m}</text>' for x, m in zip(px, mo))
    flows = "".join(f'<rect class="fo" x="{x - 34}" y="{zy + 70}" width="30" height="{9000 * .022:.0f}" fill="{RED}" opacity=".85"/>'
                    f'<rect class="fi" x="{x + 4}" y="{zy + 70}" width="30" height="{6500 * .022:.0f}" fill="{GREEN}" opacity=".85"/>' for x in px)
    csvg = (f'<line id="czero" x1="{x0 - 60}" y1="{zy}" x2="{px[-1] + 80}" y2="{zy}" stroke="{INK}" stroke-width="3" stroke-dasharray="10 8"/>'
            f'<text x="{x0 - 75}" y="{zy + 10}" font-family="Inter" font-weight="700" font-size="24" fill="#6b5a48" text-anchor="end">£0</text>'
            f'<clipPath id="cclip"><rect id="cclipr" x="0" y="0" width="{x0}" height="1080"/></clipPath>'
            f'<path id="carea" d="{area}" fill="{GOLD}" opacity=".22" clip-path="url(#cclip)"/>'
            f'<path id="cline" d="{line}" stroke="{BROWN}" stroke-width="7" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle id="cdot" cx="{px[-1]}" cy="{py[-1]}" r="14" fill="{RED}" opacity="0"/>'
            f'{flows}{labels}'
            f'<text x="{x0 - 60}" y="{zy + 62}" font-family="Inter" font-weight="700" font-size="20" fill="#6b5a48" letter-spacing="1.5">EACH MONTH</text>'
            f'<g id="cleg" opacity="0"><rect x="{px[-1] + 70}" y="{zy + 100}" width="22" height="22" fill="{RED}"/><text x="{px[-1] + 102}" y="{zy + 119}" font-family="Inter" font-weight="600" font-size="24" fill="{INK}">cash out</text>'
            f'<rect x="{px[-1] + 70}" y="{zy + 140}" width="22" height="22" fill="{GREEN}"/><text x="{px[-1] + 102}" y="{zy + 159}" font-family="Inter" font-weight="600" font-size="24" fill="{INK}">cash in</text></g>')
    went, dry = W("went"), W("dry")
    js = (f"tl.fromTo('#C',{{opacity:0}},{{opacity:1,duration:.4,immediateRender:false}},{c0});"
          f"tl.fromTo('#Ccam',{{scale:1.12}},{{scale:1,duration:{c1 - c0:.2f},ease:'power1.out',immediateRender:false}},{c0});"
          f"mDrawOn('#czero',{c0 + .1:.2f},{{dur:.5}});"
          # monthly flows: out (red) then in (green), month by month across "more cash went out than came in"
          f"tl.fromTo('#C .fo',{{scaleY:0,transformOrigin:'50% 0%'}},{{scaleY:1,duration:.3,stagger:.32,ease:MOTION.ease.settle}},{went - .25:.2f});"
          f"tl.fromTo('#C .fi',{{scaleY:0,transformOrigin:'50% 0%'}},{{scaleY:1,duration:.3,stagger:.32,ease:MOTION.ease.settle}},{went + .05:.2f});"
          f"tl.to('#cleg',{{opacity:1,duration:.3}},{went:.2f});"
          # the balance falls month by month and crosses zero on "dry"
          f"mLine('#cline',{went - .3:.2f},{dry - went + .45:.2f});tl.fromTo('#cclipr',{{attr:{{width:{x0}}}}},{{attr:{{width:{px[-1] + 20}}},duration:{dry - went + .45:.2f},ease:'none'}},{went - .3:.2f});"
          f"mCount('#cbal',12000,0,{went - .3:.2f},{dry - went + .45:.2f},{{prefix:'£'}});"
          f"tl.to('#cbal',{{color:'{RED}',duration:.2}},{dry + .1:.2f});tl.to('#cdot',{{opacity:1,duration:.15}},{dry + .15:.2f});"
          f"tl.fromTo('#cdot',{{attr:{{r:14}}}},{{attr:{{r:24}},duration:.35,yoyo:true,repeat:1,immediateRender:false}},{dry + .15:.2f});"
          f"tl.to('#czero',{{stroke:'{RED}',duration:.2}},{dry + .1:.2f});tl.fromTo('#cdry',{{opacity:0,y:12}},{{opacity:1,y:0,duration:.35,immediateRender:false}},{dry + .2:.2f});"
          f"tl.to('#C',{{opacity:0,duration:.45,ease:'power1.in'}},{c1 - .15:.2f});")
    out.append(Scene("C", c0, c1 - c0 + .55, f'<div class="m5paper"></div><div class="m5grain"></div><div id="Ccam" class="m5f">{_svg(csvg)}'
                     f'<div class="m5s" style="left:360px;top:120px">Bakery bank balance</div>'
                     f'<div id="cbal" class="m5h" style="left:360px;top:160px;font-size:76px">£12,000</div>'
                     f'<div id="cdry" class="m5n" style="left:1610px;top:672px;color:{RED};opacity:0">account empty</div></div>', js=js))
    return out
