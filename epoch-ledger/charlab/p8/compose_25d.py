"""P8 2.5D still: Open Peeps characters (artist vector art, restyled) composited into the P4 cinematic bank plate,
placed by the plate's own camera (same camera as the 3D still), with floor shadows, rim and key light, shading,
grain, haze and an out-of-focus foreground. HTML/SVG, rendered headless by Chromium, like HyperFrames scenes.

    python3 epoch-ledger/charlab/p8/compose_25d.py PLATE.png CAST_DIR OUT.png [--demo DEMO.json]
"""
import base64
import json
import math
import os
import subprocess
import sys

plate, cast, out = sys.argv[1], sys.argv[2], sys.argv[3]
demo = json.load(open(sys.argv[sys.argv.index("--demo") + 1] if "--demo" in sys.argv else "epoch-ledger/charlab/motion/demos/p8_bank_plate.json"))
cam = demo["camera"][0]; W, H = 1920, 1080


def project(p):
    C, T = cam["pos"], cam["look"]
    f = [T[i] - C[i] for i in range(3)]; n = math.sqrt(sum(x * x for x in f)); f = [x / n for x in f]
    up = [0, 1, 0]; r = [f[1] * up[2] - f[2] * up[1], f[2] * up[0] - f[0] * up[2], f[0] * up[1] - f[1] * up[0]]
    n = math.sqrt(sum(x * x for x in r)); r = [x / n for x in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    d = [p[i] - C[i] for i in range(3)]; xc = sum(d[i] * r[i] for i in range(3)); yc = sum(d[i] * u[i] for i in range(3)); zc = sum(d[i] * f[i] for i in range(3))
    t = math.tan(math.radians(cam["fov"]) / 2)
    return ((xc / (zc * t * W / H) + 1) / 2 * W, (1 - yc / (zc * t)) / 2 * H)


# characters: world position on the floor, height in metres, mirror, file
PEOPLE = [dict(id="banker", pos=(-0.95, 0, 0.15), h=1.66, flip=False, svg="banker.svg"),
          dict(id="client", pos=(0.55, 0, 0.30), h=1.80, flip=True, svg="client.svg")]
items = []
for p in PEOPLE:
    fx, fy = project(p["pos"]); hx, hy = project((p["pos"][0], p["h"], p["pos"][2]))
    svg = open(os.path.join(cast, p["svg"])).read()
    items.append(dict(p, feet=[fx, fy], hpx=fy - hy, svg=svg))
plate_b64 = base64.b64encode(open(plate, "rb").read()).decode()

html = """<!doctype html><html><head><meta charset=utf-8><style>
html,body{margin:0;width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#000}
#stage{position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden}
#plate{position:absolute;inset:0;width:100%%;height:100%%;filter:saturate(.86) contrast(.96) brightness(.97)}
.layer{position:absolute;inset:0}
.ch{position:absolute;left:0;top:0;transform-origin:0 0}
.ch svg{overflow:visible}
#grain{position:absolute;inset:0;opacity:.07;mix-blend-mode:multiply}
#vignette{position:absolute;inset:0;background:radial-gradient(ellipse at 55%% 45%%,rgba(0,0,0,0) 55%%,rgba(20,12,6,.42) 100%%)}
</style></head><body><div id=stage>
<img id=plate src="data:image/png;base64,%(plate)s">
<svg width=0 height=0 style="position:absolute"><defs>
 <filter id="sil" x="-20%%" y="-20%%" width="140%%" height="140%%"><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"/></filter>
 <filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
 <filter id="rim" x="-10%%" y="-10%%" width="120%%" height="120%%">
   <feOffset in="SourceAlpha" dx="4" dy="7" result="o"/><feComposite in="SourceAlpha" in2="o" operator="out" result="edge"/>
   <feGaussianBlur in="edge" stdDeviation="1.6" result="e2"/><feFlood flood-color="#ffe4b8"/><feComposite in2="e2" operator="in"/></filter>
 <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/><feColorMatrix type="saturate" values="0"/></filter>
 <filter id="fgblur"><feGaussianBlur stdDeviation="14"/></filter>
</defs></svg>
<div class=layer id=people></div>
<svg class=layer viewBox="0 0 %(W)d %(H)d"><g filter="url(#fgblur)" opacity=".92">
  <path d="M-60 1080 C 40 900, 120 860, 170 700 C 190 820, 150 960, 120 1080 Z" fill="#1c2a1c"/>
  <path d="M-40 1080 C 60 960, 230 930, 300 820 C 270 960, 200 1040, 170 1080 Z" fill="#22321f"/>
  <path d="M60 1080 C 90 980, 60 880, -10 800 C 80 860, 150 960, 160 1080 Z" fill="#17221a"/></g></svg>
<svg id=grain viewBox="0 0 %(W)d %(H)d"><rect width="100%%" height="100%%" filter="url(#grain)"/></svg>
<div id=vignette></div>
</div>
<script>
const ITEMS = %(items)s;
const host = document.getElementById('people');
ITEMS.sort((a,b)=>a.feet[1]-b.feet[1]);
for (const it of ITEMS) {
  const wrap = document.createElement('div'); wrap.className='ch'; wrap.innerHTML = it.svg; host.appendChild(wrap);
  const svg = wrap.querySelector('svg'); const g = svg.querySelector('g');
  const bb = g.getBBox();                       // the artwork's own extent (feet = bottom, crown = top)
  const vb = svg.viewBox.baseVal; const s = it.hpx / bb.height;
  svg.setAttribute('width', vb.width * s); svg.setAttribute('height', vb.height * s);
  const footX = (bb.x + bb.width / 2 - vb.x) * s, footY = (bb.y + bb.height - vb.y) * s;
  wrap.style.transform = `translate(${it.feet[0]-footX}px, ${it.feet[1]-footY}px)` + (it.flip ? ` translate(${footX}px,0) scale(-1,1) translate(${-footX}px,0)` : '');
  // lighting inside the character svg: shadow (floor), shading, rim
  const NS='http://www.w3.org/2000/svg', id='c_'+it.id; g.setAttribute('id', id);
  const defs = document.createElementNS(NS,'defs'); svg.prepend(defs);
  const lg = `<linearGradient id="${id}_sh" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".55" stop-color="#3a2a22" stop-opacity=".10"/><stop offset="1" stop-color="#1d1410" stop-opacity=".42"/></linearGradient>
              <linearGradient id="${id}_warm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd9a0" stop-opacity=".22"/><stop offset=".5" stop-color="#ffd9a0" stop-opacity="0"/></linearGradient>
              <mask id="${id}_m" maskContentUnits="userSpaceOnUse"><use href="#${id}" filter="url(#white_${id})"/></mask>
              <filter id="white_${id}"><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>`;
  defs.innerHTML = lg;
  const fx = (bb.x+bb.width/2), fy = (bb.y+bb.height);
  const shadow = document.createElementNS(NS,'g');   // cast shadow: the silhouette laid on the floor toward the camera
  shadow.innerHTML = `<g transform="translate(${fx} ${fy}) matrix(1 0 ${it.flip?0.9:-0.9} -0.22 0 0) translate(${-fx} ${-fy})" opacity=".34" filter="url(#blur6)"><use href="#${id}" filter="url(#sil)"/></g>
                      <ellipse cx="${fx}" cy="${fy-4}" rx="${bb.width*0.42}" ry="${bb.width*0.07}" fill="#140c08" opacity=".45" filter="url(#blur6)"/>`;
  g.parentNode.insertBefore(shadow, g);
  const over = document.createElementNS(NS,'g');
  over.innerHTML = `<rect x="${bb.x}" y="${bb.y}" width="${bb.width}" height="${bb.height}" fill="url(#${id}_sh)" mask="url(#${id}_m)" style="mix-blend-mode:multiply"/>
                    <rect x="${bb.x}" y="${bb.y}" width="${bb.width}" height="${bb.height}" fill="url(#${id}_warm)" mask="url(#${id}_m)" style="mix-blend-mode:screen"/>
                    <use href="#${id}" filter="url(#rim)" opacity=".45" style="mix-blend-mode:screen"/>`;
  g.parentNode.appendChild(over);
  wrap.style.filter = 'saturate(.95)';
}
window.done = true;
</script></body></html>""" % dict(W=W, H=H, plate=plate_b64, items=json.dumps(items))
tmp = os.path.splitext(out)[0] + ".html"; open(tmp, "w").write(html)
js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:%d,height:%d}});
await p.goto('file://%s');await p.waitForFunction(()=>window.done);await p.waitForTimeout(400);await p.screenshot({path:'%s'});await b.close();})();""" % (W, H, os.path.abspath(tmp), os.path.abspath(out))
subprocess.run(["node", "-e", js], check=True)
print("wrote", out, [(i["id"], [round(x) for x in i["feet"]], round(i["hpx"])) for i in items])
