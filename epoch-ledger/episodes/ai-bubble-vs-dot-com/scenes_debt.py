"""Debt explanation 9:37–10:17 (storyboard s051–s052): hypothetical cash-flow waterfall and the funding gap."""
from kit.assemble import Scene
from kit.characters import person_svg
from timeline import L, W


def office():
    return """<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="d-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1424"/><stop offset="1" stop-color="#13233a"/></linearGradient></defs>
 <rect width="1920" height="1080" fill="url(#d-bg)"/>
 <g opacity=".35">""" + "".join(f'<rect x="{40 + i * 120}" y="{120 + (i * 37) % 120}" width="70" height="{300 + (i * 53) % 260}" fill="#1b2a44"/>' for i in range(16)) + """</g>
 <rect x="0" y="0" width="1920" height="1080" fill="#0b1424" opacity=".55"/>
 <rect y="790" width="1920" height="290" fill="#0a1220"/><rect x="40" y="740" width="560" height="26" rx="10" fill="#2a3a56"/>
</svg>"""


def chart():
    Z, K = 700, 40  # zero line y, px per $1B
    bar = lambda i, x, y, h, c, cls="": f'<rect id="{i}" class="{cls}" x="{x}" y="{y}" width="190" height="{h}" rx="8" fill="{c}"/>'
    return f"""<svg id="d-chart" viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg">
 <path d="M640 {Z} H1640" stroke="#8fa3b8" stroke-width="4"/><text x="626" y="{Z + 12}" text-anchor="end" font-family="Inter" font-weight="700" font-size="30" fill="#8fa3b8">$0</text>
 {bar('d-ocf', 700, Z, 0, '#4ee28a')}{bar('d-capex', 1000, Z - 10 * K, 0, '#e0603a')}{bar('d-fcf', 1300, Z, 0, '#4ee28a')}
 <path id="d-c1" d="M890 {Z - 10 * K} H1000" stroke="#8fa3b8" stroke-width="3" stroke-dasharray="8 6" opacity="0"/>
 <g font-family="Fraunces" font-weight="800" font-size="52" fill="#e8f3ff" text-anchor="middle">
  <text id="d-v1" x="795" y="{Z - 10 * K - 24}" opacity="0">$10B</text><text id="d-v2" x="1095" y="{Z - 10 * K - 24}" opacity="0">−$6B</text><text id="d-v3" x="1395" y="{Z - 4 * K - 24}" opacity="0">$4B</text></g>
 <g font-family="Inter" font-weight="700" font-size="28" fill="#c9d6e8" text-anchor="middle">
  <text id="d-l1" x="795" y="{Z + 50}" opacity="0">Operating cash flow</text><text id="d-l2" x="1095" y="{Z + 50}" opacity="0">Capital spending</text><text id="d-l3" x="1395" y="{Z + 50}" opacity="0">Free cash flow</text></g>
</svg>"""


def tile(i, icon, label):
    return (f'<div class="d-tile" id="d-tile{i}" style="position:absolute;left:{1180 + (i % 2) * 350}px;top:{170 + (i // 2) * 300}px;width:320px;height:270px;'
            f'border-radius:22px;background:rgba(22,35,58,.92);border:3px solid #2f4a70;opacity:0;text-align:center">'
            f'<svg viewBox="0 0 200 140" style="width:200px;height:140px;margin-top:24px">{icon}</svg>'
            f'<div style="font:800 40px Fraunces;color:#e8f3ff;margin-top:8px">{label}</div></div>')


ICONS = [
    '<rect x="40" y="20" width="120" height="100" rx="12" fill="none" stroke="#9fb7d9" stroke-width="10"/><circle cx="100" cy="70" r="26" fill="none" stroke="#9fb7d9" stroke-width="8"/>',
    '<path d="M60 120 V40 H150 V80 H60" fill="none" stroke="#9fb7d9" stroke-width="10"/><path d="M60 40 V20" stroke="#9fb7d9" stroke-width="10"/>',
    '<rect x="40" y="30" width="120" height="86" rx="6" fill="none" stroke="#9fb7d9" stroke-width="10"/><path d="M60 60 H140 M60 86 H120" stroke="#9fb7d9" stroke-width="8"/>',
    '<path d="M30 60 L100 20 L170 60Z" fill="#f2c66d"/><rect x="45" y="68" width="20" height="44" fill="#f2c66d"/><rect x="90" y="68" width="20" height="44" fill="#f2c66d"/><rect x="135" y="68" width="20" height="44" fill="#f2c66d"/><rect x="30" y="116" width="140" height="12" fill="#f2c66d"/>',
]


def build():
    c2, c3, c4, c5, c6 = (L(f"c06_0{i}") for i in range(2, 7))
    w_six, w_four, w_free = W("$6", "c06_03"), W("$4", "c06_03"), W("free", "c06_03")
    w_14 = W("$14", "c06_04")
    opts = [W(x, "c06_06") for x in ("existing", "sell", "raise", "borrow")]
    Z, K = 700, 40
    cfo = person_svg("cfo", "cfo_modern", "bust").replace('class="char "', 'class="char" style="left:60px;top:360px;width:440px;height:528px"')
    html = (f'<div id="d-cam" class="cam">{office()}{cfo}{chart()}'
            + "".join(tile(i, ICONS[i], lab) for i, lab in enumerate(["Cash reserves", "Sell assets", "Raise equity", "Borrow"]))
            + '</div><div class="tag l" id="d-tag">Hypothetical company</div>')
    js = f"""
tl.fromTo('#db',{{opacity:0}},{{opacity:1,duration:.45}},{c2[0] - .45});
tl.fromTo('#d-cam',{{scale:1.05}},{{scale:1.0,duration:{c6[1] - c2[0]},ease:'sine.out'}},{c2[0] - .45});
show('#d-tag',{c2[0] + .2});
tl.to('#d-ocf',{{attr:{{y:{Z - 10 * K},height:{10 * K}}},duration:.9,ease:'power3.out'}},{W('$10', 'c06_02')});
show('#d-v1',{W('$10', 'c06_02') + .5}); show('#d-l1',{W('$10', 'c06_02') + .3});
show('#d-c1',{w_six - .2}); tl.to('#d-capex',{{attr:{{height:{6 * K}}},duration:.8,ease:'power2.out'}},{w_six});
show('#d-v2',{w_six + .4}); show('#d-l2',{w_six + .3});
tl.to('#d-fcf',{{attr:{{y:{Z - 4 * K},height:{4 * K}}},duration:.8,ease:'power3.out'}},{w_four}); show('#d-v3',{w_four + .4}); show('#d-l3',{w_free});
tl.to('#d-capex',{{attr:{{height:{14 * K}}},duration:1.6,ease:'power2.inOut'}},{w_14});
tl.to('#d-v2',{{opacity:0,duration:.2}},{w_14}); tl.call(()=>{{}},[],{w_14});
const dv={{v:6}}; tl.to(dv,{{v:14,duration:1.6,ease:'power2.inOut',onUpdate:()=>{{const e=document.getElementById('d-v2');e.textContent='−$'+Math.round(dv.v)+'B';}}}},{w_14});
tl.to('#d-v2',{{opacity:1,duration:.3}},{w_14 + .2});
tl.to('#d-fcf',{{attr:{{y:{Z},height:{4 * K}}},fill:'#e0603a',duration:1.0,ease:'power2.inOut'}},{c5[0]});
tl.to('#d-v3',{{attr:{{y:{Z + 4 * K + 60}}},fill:'#ff8a6a',duration:1.0,ease:'power2.inOut'}},{c5[0]});
tl.call(()=>{{}},[],{c5[0]}); const fv={{v:4}}; tl.to(fv,{{v:-4,duration:1.0,ease:'power2.inOut',onUpdate:()=>{{const e=document.getElementById('d-v3');e.textContent=(fv.v<0?'−':'')+'$'+Math.abs(Math.round(fv.v))+'B';}}}},{c5[0]});
tl.to('#d-l3',{{attr:{{y:{Z - 22}}},duration:.6}},{c5[0]});
tl.to('#cfo-brows',{{y:-6,duration:.3}},{c5[0] + .3}); tl.to('#cfo-mouth',{{scaleY:-1,transformOrigin:'50% 50%',duration:.3}},{c5[0] + .3}); blink('#cfo .lid',[{c2[0] + 1.2},{c4[0] + 2},{c5[0] + 1.4}]);
tl.to('#d-chart',{{scale:.66,x:-140,y:-120,transformOrigin:'0px 0px',duration:.9,ease:'power2.inOut'}},{c6[0]});
{"".join(f"pop('#d-tile{i}',{t});" for i, t in enumerate(opts))}
tl.to('#d-tile3',{{borderColor:'#f2c66d',boxShadow:'0 0 40px rgba(242,198,109,.6)',duration:.5}},{opts[3] + .4});
"""
    return [Scene("db", round(c2[0] - .45, 3), round(c6[1] + .6 - c2[0] + .45, 3), html, js=js)], [], ""
