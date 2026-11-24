"""1999 trading floor (boom and panic) — layered 2.5D set with a live quote board, CRT banks, a jointed
cast acting with phones, tickets and hand signals, runners, and a parallax camera dolly."""
from kit.characters import OUT
from kit.rig import crowd_look, rig_svg

TICKERS = ["WEBQ", "NTVX", "CYBR", "DOTN", "ISPX", "EMLX", "PORT", "CLIK", "NETZ", "BYTE", "LINX", "SRCH", "HOST", "MODM",
           "PGVU", "ECOM", "SURF", "DIAL", "CHAT", "BNDW", "XSRV", "ADZN", "eSHP", "MALL"]


def place(svg, x, y, w, flip=False, extra=""):
    h = w * 500 / 300
    tr = "transform:scaleX(-1);" if flip else ""
    return svg.replace('class="char rig "', f'class="char rig" style="left:{x}px;top:{y}px;width:{w}px;height:{h:.0f}px;{tr}{extra}"')


def crt(x, y, s, sid):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-60" y="-48" width="120" height="96" rx="10" fill="#d4cab2" stroke="{OUT}" stroke-width="3"/>'
            f'<rect x="-50" y="-40" width="100" height="72" rx="6" fill="#06140b"/>'
            f'<g id="{sid}" font-family="Inter" font-weight="700" font-size="11" fill="#7cff9b">'
            + "".join(f'<text x="-44" y="{-24 + k * 14}" class="crtl">----</text>' for k in range(5)) + "</g>"
            f'<rect x="-50" y="-40" width="100" height="72" rx="6" fill="url(#crt-glare)"/></g>')


def back_wall(px):
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="{px}-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c2420"/><stop offset=".55" stop-color="#2e2418"/><stop offset="1" stop-color="#3b2a18"/></linearGradient>
  <linearGradient id="crt-glare" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".18"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <radialGradient id="{px}-haze" cx=".5" cy=".35" r=".75"><stop offset="0" stop-color="#ffcf7a" stop-opacity=".32"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/></radialGradient></defs>
 <rect x="-200" width="2320" height="1080" fill="url(#{px}-wall)"/>
 <g opacity=".5" stroke="#4a3a28" stroke-width="3">{''.join(f'<path d="M{x} 360 V1080"/>' for x in range(-180, 2120, 160))}</g>
 <rect x="-200" y="40" width="2320" height="300" fill="#0d0a07" stroke="#5a4630" stroke-width="6"/>
</svg>"""


def board(px):
    cells = "".join(f'<div class="flc" id="{px}-c{i}"><b>{TICKERS[i % len(TICKERS)]}</b><span class="px">00</span><span class="ch">▲0</span></div>'
                    for i in range(24))
    return (f'<div id="{px}-board" style="position:absolute;left:-120px;top:74px;width:2160px;height:256px;display:grid;'
            f'grid-template-columns:repeat(8,1fr);gap:6px;padding:8px;font-family:Inter">{cells}</div>'
            f'<div style="position:absolute;left:-200px;top:56px;width:2320px;height:268px;background:radial-gradient(circle,rgba(0,0,0,0) 1.5px,rgba(13,10,7,.5) 1.8px);background-size:6px 6px"></div>')


def ticker(px, top):
    txt = "   ·   ".join(f"{t} {40 + (i * 37) % 160}{['⅛', '¼', '⅜', '½', '⅝', '¾', '⅞'][i % 7]} ▲{1 + i % 9}" for i, t in enumerate(TICKERS * 2))
    return (f'<div style="position:absolute;left:-200px;top:{top}px;width:2320px;height:64px;background:#120c06;border-top:3px solid #5a3e26;'
            f'border-bottom:3px solid #5a3e26;overflow:hidden"><div id="{px}-tk" style="position:absolute;left:0;top:8px;white-space:nowrap;'
            f'font:800 40px Inter;letter-spacing:.06em;color:#f2a541;text-shadow:0 0 12px #f2a541">{txt}</div></div>')


def monitors(px):
    banks = []
    for b, (x, y, s) in enumerate([(230, 470, .9), (760, 455, .85), (1240, 462, .88), (1730, 475, .92)]):
        banks.append(f'<g><path d="M{x} 360 V{y - 60}" stroke="#3a3a3a" stroke-width="6"/><rect x="{x - 250 * s}" y="{y - 64 * s}" width="{500 * s}" height="12" fill="#2a2a2a"/>'
                     + "".join(crt(x - 186 * s + k * 124 * s, y, s, f"{px}-m{b}{k}") for k in range(4)) + "</g>")
    return f'<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">{"".join(banks)}</svg>'


def counters(px, y, dark=0):
    posts = "".join(
        f'<g transform="translate({x} {y})"><path d="M-230 0 Q0 -40 230 0 L230 120 L-230 120Z" fill="#5a3e26" stroke="{OUT}" stroke-width="4"/>'
        f'<path d="M-230 0 Q0 -40 230 0 L230 18 Q0 -22 -230 18Z" fill="#8a6440" stroke="{OUT}" stroke-width="3"/>'
        f'<rect x="-150" y="-62" width="70" height="40" rx="6" fill="#1f1f22"/><rect x="40" y="-58" width="74" height="40" rx="6" fill="#1f1f22"/>'
        f'<g fill="#e8e2cf">{"".join(f"<rect x={chr(34)}{-200 + k * 46}{chr(34)} y={chr(34)}{8 + (k % 2) * 8}{chr(34)} width={chr(34)}26{chr(34)} height={chr(34)}18{chr(34)} transform={chr(34)}rotate({(k * 17) % 30 - 15}){chr(34)}/>" for k in range(9))}</g></g>'
        for x in (300, 960, 1620))
    return f'<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;filter:brightness({1 - dark})">{posts}</svg>'


def floor_layer():
    slips = "".join(f'<rect x="{(i * 211) % 2200 - 140}" y="{760 + (i * 47) % 300}" width="28" height="20" fill="#fbf6e8" '
                    f'transform="rotate({(i * 31) % 80 - 40} {(i * 211) % 2200 - 140} {760 + (i * 47) % 300})" opacity=".9"/>' for i in range(70))
    return (f'<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">'
            f'<rect x="-200" y="740" width="2320" height="340" fill="#4a3826"/><g>{slips}</g></svg>')


CSS = """
.flc{background:#0d0a07;border:2px solid #3a2c1c;border-radius:4px;display:flex;flex-direction:column;justify-content:center;padding:2px 12px;overflow:hidden}
.flc{line-height:1.05}.flc b{font:800 24px Inter;color:#f3e3c3;letter-spacing:.05em}.flc .px{font:800 38px Inter;color:#f2a541;text-shadow:0 0 10px rgba(242,165,65,.6)}
.flc .ch{font:700 22px Inter;color:#4ee28a}
.crash .flc .px,.crash .flc .ch,.flc.dn .px{color:#ff5a46;text-shadow:0 0 10px rgba(255,90,70,.7)}.flc.dn .ch{color:#ff5a46}
"""

BOARD_JS = """
function flFrac(v){const w=Math.floor(v),f=Math.round((v-w)*8)%8;return w+(f?['','⅛','¼','⅜','½','⅝','¾','⅞'][f]:'');}
function flBoard(px,t,crash){for(let i=0;i<24;i++){const c=document.getElementById(px+'-c'+i);if(!c)return;
  const base=40+((i*37)%160),boom=1+.012+.03*Math.abs(Math.sin(t*1.3+i))+.025*t/6,dn=crash>0?Math.min(1,crash)*(.35+.25*((i*7)%5)/5):0,v=base*boom*(1-dn);
  c.querySelector('.px').textContent=flFrac(v);const d=crash>0?-(base*dn):(base*(boom-1));c.querySelector('.ch').textContent=(d<0?'▼':'▲')+flFrac(Math.abs(d));
  c.classList.toggle('dn',d<0);}}
function flCrt(px,t,crash){for(let b=0;b<4;b++)for(let k=0;k<4;k++){const g=document.getElementById(px+'-m'+b+k);if(!g)continue;
  g.setAttribute('fill',crash>0&&((b+k)%3!==0||crash>.6)?'#ff6a55':'#7cff9b');
  g.querySelectorAll('.crtl').forEach((l,j)=>{const n=Math.floor(t*6+b*7+k*3+j)%24;l.textContent=['WEBQ','NTVX','CYBR','DOTN','ISPX','EMLX','PORT','CLIK','NETZ','BYTE','LINX','SRCH','HOST','MODM','PGVU','ECOM','SURF','DIAL','CHAT','BNDW','XSRV','ADZN','eSHP','MALL'][n]+' '+(crash>0?'▼':'▲')+flFrac(1+((n*13+j)%9)*(crash>0?1.6:.7));});}}
"""


def floor_scene(px, start, end, mood, crash_at=None, cam=None):
    """mood 'boom' or 'panic'. Returns (html, js). crash_at: time the board turns red (panic)."""
    boom = mood == "boom"
    acts_mid = ["phone", "signal", "point", "write", "type", "shout", "cheer"] if boom else ["handsHead", "slump", "phone", "shout", "point", "shrug"]
    mid = []
    js = []
    # mid crowd at the trading posts (legs hidden by counters)
    spots = [(150, 470), (330, 478), (510, 466), (790, 470), (980, 462), (1160, 474), (1430, 468), (1610, 476), (1790, 466)]
    for i, (x, y) in enumerate(spots):
        cid = f"{px}m{i}"
        look = crowd_look(i + (0 if boom else 3))
        prop = ["receiver", "ticket", None, "pad", None, "receiver", "ticket", None, "pad"][i]
        mid.append(place(rig_svg(cid, look, "full", prop_front=prop), x - 75, y, 150, flip=i % 3 == 1))
        if boom or not crash_at:
            js.append(f"ambient('{cid}',{start},{end},{(1 if boom else 7) * 100 + i},{acts_mid!r});")
        else:
            busy = ["phone", "signal", "point", "write", "shout"]
            hit = crash_at + .12 * (i % 5)
            first = ["handsHead", "slump", "shout", "handsHead", "point", "slump", "handsHead", "shrug", "shout"][i]
            js.append(f"ambient('{cid}',{start},{hit},{700 + i},{busy!r});rpose('{cid}','{first}',{hit},.3);"
                      f"ambient('{cid}',{hit + 1.3},{end},{800 + i},{acts_mid!r});")
    # runners crossing the floor with tickets
    run = []
    for i, (x, y, dx, flip) in enumerate([(-160, 540, 900, False), (1880, 556, -820, True), (600, 548, 520, False)]):
        cid = f"{px}r{i}"
        run.append(f'<div id="{cid}-wrap" style="position:absolute;inset:0">{place(rig_svg(cid, crowd_look(30 + i + (0 if boom else 5)), "full", prop_front="ticket"), x, y, 186, flip=flip)}</div>')
        steps = int((end - start) / .34) - 1
        js.append(f"rwalk('{cid}','#{cid}-wrap',{start + .15 * i},{steps},{.34 if boom else .26},{dx});rpose('{cid}','hold',{start},.01);")
    # foreground: big traders (out of the focal plane)
    fg = []
    fgl = [("fgA", -60, 360, 430, False, "receiver", ["phone", "shout", "phone", "signal"] if boom else ["handsHead", "slump", "phone"]),
           ("fgB", 1500, 380, 420, True, "pad", ["write", "hold", "write", "point"] if boom else ["slump", "shrug", "handsHead"])]
    for k, (n, x, y, w, flip, prop, acts) in enumerate(fgl):
        cid = f"{px}{n}"
        fg.append(place(rig_svg(cid, crowd_look(50 + k + (0 if boom else 9)), "full", prop_front=prop, prop_back="pen" if prop == "pad" else None),
                        x, y, w, flip=flip, extra="filter:blur(1.2px) brightness(.92)"))
        if boom or not crash_at:
            js.append(f"ambient('{cid}',{start},{end},{(3 if boom else 9) * 100 + k},{acts!r},{{talk:{str(boom).lower()}}});")
        else:
            js.append(f"ambient('{cid}',{start},{crash_at},{900 + k},['phone','write','signal'],{{talk:true}});"
                      f"ambient('{cid}',{crash_at + .2},{end},{950 + k},{acts!r});")
    if not boom and crash_at:
        for i in range(len(spots)):
            js.append(f"rexpress('{px}m{i}','{['shock', 'worry'][i % 2]}',{crash_at + .1 * i});")
        js.append(f"rexpress('{px}fgA','shock',{crash_at});rexpress('{px}fgB','worry',{crash_at + .3});")
    elif boom:
        for i in range(len(spots)):
            js.append(f"rexpress('{px}m{i}','joy',{start + .2 * i});")
    c = cam or {}
    html = (f'<div id="{px}-cam" class="cam" style="transform-origin:{c.get("origin", "50% 45%")}">'
            f'<div id="{px}-L0" class="fill">{back_wall(px)}{board(px)}{ticker(px, 340)}</div>'
            f'<div id="{px}-L1" class="fill">{monitors(px)}</div>'
            f'<div id="{px}-L2" class="fill">{"".join(mid)}{counters(px, 650)}</div>'
            f'<div id="{px}-L3" class="fill">{floor_layer()}{"".join(run)}</div>'
            f'<div id="{px}-L4" class="fill">{"".join(fg)}</div>'
            f'<div class="fill" style="background:radial-gradient(ellipse at 50% 30%,rgba(255,207,122,.18),rgba(0,0,0,0) 60%),'
            f'linear-gradient(180deg,rgba(0,0,0,0) 70%,rgba(20,12,6,.45))"></div></div>')
    dur = end - start
    crash = f"Math.max(0,(P.t-{crash_at})/1.2)" if crash_at else "0"
    js.insert(0, f"""
(function(){{const P={{t:{start}}};tl.fromTo(P,{{t:{start}}},{{t:{end},duration:{dur},ease:'none',onUpdate:()=>{{flBoard('{px}',P.t,{crash});flCrt('{px}',P.t,{crash});}}}},{start});}})();
tl.fromTo('#{px}-cam',{{scale:{c.get('s0', 1.0)},x:{c.get('x0', 0)},y:{c.get('y0', 0)}}},{{scale:{c.get('s1', 1.1)},x:{c.get('x1', -30)},y:{c.get('y1', 0)},duration:{dur},ease:'sine.inOut'}},{start});
[['L0',-18],['L1',-40],['L2',-80],['L3',-130],['L4',-240]].forEach(([l,dx])=>tl.fromTo('#{px}-'+l,{{x:0}},{{x:dx*{c.get('par', 1)},duration:{dur},ease:'sine.inOut'}},{start}));
tl.fromTo('#{px}-tk',{{x:0}},{{x:-1500,duration:{dur},ease:'none'}},{start});
""")
    if crash_at:
        js.append(f"tl.set('#{px}-board',{{attr:{{class:'crash'}}}},{crash_at + .4});"
                  f"tl.to('#{px}-tk',{{color:'#ff5a46',textShadow:'0 0 14px #ff5a46',duration:.4}},{crash_at});"
                  f"tl.to('#{px}-L0',{{filter:'saturate(.75) brightness(.85)',duration:1.2}},{crash_at});")
    return html, "\n".join(js)
