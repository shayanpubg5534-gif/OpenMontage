"""Shared builders for the cash-furnace style frames: page assembly, mapped 2D art, people sprites."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

KIT = Path(__file__).resolve().parents[3] / "kit"
from kit.diegetic import ticker_board  # noqa: E402
O = "#1b1410"


def page(out: Path, title: str, back: str, scene_js: str, cam_js: str, light_js: str, front: str, root_filter: str = "",
         fg: str = "", extra_css: str = "", after_svg: str = "") -> None:
    ws = out.parent
    (ws / "tex").mkdir(parents=True, exist_ok=True)
    for f in (KIT / "assets" / "textures").glob("*.jpg"):
        shutil.copy(f, ws / "tex" / f.name)
    shutil.copy(KIT / "scene3d.js", ws / "scene3d.js")
    fonts = KIT.parents[1] / "projects" / "ai-bubble-vs-dot-com" / "draft" / "fonts"
    if fonts.exists() and not (ws / "fonts").exists():
        shutil.copytree(fonts, ws / "fonts")
    out.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>
@font-face{{font-family:Inter;src:url(fonts/inter-latin-700-normal.woff2) format('woff2');font-weight:700}}
@font-face{{font-family:Inter;src:url(fonts/inter-latin-800-normal.woff2) format('woff2');font-weight:800}}
@font-face{{font-family:Fraunces;src:url(fonts/fraunces-latin-800-normal.woff2) format('woff2');font-weight:800}}
html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:#000}}
#frame{{position:absolute;inset:0;overflow:hidden;filter:{root_filter or 'none'}}}
#set{{position:absolute;inset:0;width:1920px;height:1080px}}
{extra_css}
</style><script src="scene3d.js"></script></head><body>
<div id="frame">{back}<svg id="set" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg"></svg><svg id="glows" viewBox="0 0 1920 1080" style="position:absolute;inset:0;mix-blend-mode:screen;opacity:.8"></svg>{after_svg}{front}{fg}</div>
<script>
const TEX = 'tex/';
const ART = {json.dumps(ART)};
{scene_js}
{cam_js}
{light_js}
document.getElementById('set').innerHTML = S3.render(sc, cam, L, {{ ow: 2.0, shadowBlur: 5 }});
if (typeof GLOWS !== 'undefined') {{ const g = GLOWS.map(([p, r, c], i) => {{ const q = cam.project(p); if (!q) return '';
  const rr = r * Math.min(2.5, 14 / q[2]) + r * .3; return `<radialGradient id="gw${{i}}"><stop offset="0" stop-color="${{c}}" stop-opacity=".95"/><stop offset=".22" stop-color="${{c}}" stop-opacity=".4"/><stop offset="1" stop-color="${{c}}" stop-opacity="0"/></radialGradient><circle cx="${{q[0]}}" cy="${{q[1]}}" r="${{rr}}" fill="url(#gw${{i}})"/>`; }}).join('');
  document.getElementById('glows').innerHTML = g; }}
</script></body></html>""")


# ── 2D art mapped onto surfaces (authored in its own pixel box) ─────────────────────────────────
def _lobby(i: int) -> str:
    """Warm lobby seen through a storefront bay: back wall, reception, the glass cash tank (bay 1)."""
    tank = ""
    if i == 1:
        tank = (f'<rect x="230" y="40" width="150" height="250" rx="40" fill="#0e1a16" stroke="#dfe6ea" stroke-width="7"/>'
                f'<rect x="236" y="150" width="138" height="134" rx="30" fill="#e8b440"/>'
                + "".join(f'<ellipse cx="{252 + (k * 29) % 110}" cy="{170 + (k * 23) % 100}" rx="14" ry="5" fill="#ffe08a" stroke="#a07a20" stroke-width="2"/>' for k in range(12))
                + '<rect x="236" y="44" width="40" height="240" rx="18" fill="#fff" opacity=".18"/>'
                f'<rect x="268" y="16" width="74" height="26" rx="4" fill="{O}"/><text x="305" y="35" text-anchor="middle" font-family="Inter" font-weight="800" font-size="18" fill="#f2c66d">CASH</text>')
    desk = '<rect x="40" y="200" width="170" height="80" fill="#7a5236" stroke="#2a1a12" stroke-width="4"/><rect x="40" y="194" width="176" height="12" fill="#a07850"/>' if i == 0 else ""
    plant = '<path d="M520 300 L540 200 L560 300Z" fill="#5a3a26"/><circle cx="540" cy="180" r="44" fill="#3a6a3a"/><circle cx="512" cy="200" r="30" fill="#2e5a30"/>' if i == 2 else ""
    return (f'<rect width="600" height="300" fill="#f6dcae"/><rect y="230" width="600" height="70" fill="#a8764a"/>'
            f'<rect x="0" y="0" width="600" height="40" fill="#fff0cf"/>{desk}{tank}{plant}'
            f'<rect x="420" y="60" width="120" height="80" fill="#2e5ab0" opacity="{.9 if i == 0 else 0}"/>'
            f'<path d="M0 0 H600 V300 H0Z" fill="none" stroke="#3a2418" stroke-width="10"/>'
            f'<path d="M200 0 V300 M400 0 V300" stroke="#3a2418" stroke-width="6"/>')


ART = {
    "lobby": [_lobby(0), _lobby(1), _lobby(2)],
    "sign": f'<rect width="440" height="30" fill="#2e5ab0"/><text x="220" y="23" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="22" fill="#fff">BigCart.com</text>',
    "summit": f'<rect width="1200" height="34" fill="#1e2a3a"/><text x="600" y="26" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="26" letter-spacing="10" fill="#e9dcbc">SUMMIT VENTURES</text>',
    "billboard": f"""<rect width="900" height="620" fill="#f4ead5"/><rect x="24" y="24" width="852" height="572" fill="#2b4f9e"/>
<radialGradient id="bbg" cx=".3" cy=".4" r=".8"><stop offset="0" stop-color="#4a76cc"/><stop offset="1" stop-color="#1e3a7a"/></radialGradient><rect x="24" y="24" width="852" height="572" fill="url(#bbg)"/>
<g transform="translate(220 320) rotate(-18)"><path d="M0 -190 C90 -110 92 90 0 190 C-92 90 -90 -110 0 -190Z" fill="#f4ead5" stroke="{O}" stroke-width="8"/>
<circle cy="-40" r="44" fill="#7fc8ee" stroke="{O}" stroke-width="7"/><path d="M-62 120 L-130 210 L-40 168Z M62 120 L130 210 L40 168Z" fill="#d9503f" stroke="{O}" stroke-width="7"/>
<path d="M-34 196 Q0 330 34 196Z" fill="#ffb03a"/><path d="M-18 196 Q0 280 18 196Z" fill="#fff0a0"/></g>
<text x="590" y="250" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="104" fill="#fff">BigCart</text>
<text x="590" y="330" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="62" fill="#ffd56a">.com</text>
<text x="590" y="430" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="#e6eeff">Everything. Delivered.</text>
<text x="590" y="486" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="#ffd56a">FREE SHIPPING</text>""",
    "board": ticker_board("TECH STOCKS", [0, 8, 6, 26, 32, 52, 60, 86, 102, 128]),
    "valve": f'<g transform="translate(100 100)"><circle r="86" fill="none" stroke="#b8322a" stroke-width="18"/>'
             + "".join(f'<path d="M0 0 L{86 * __import__("math").cos(k * 1.0472):.1f} {86 * __import__("math").sin(k * 1.0472):.1f}" stroke="#b8322a" stroke-width="12"/>' for k in range(6))
             + f'<circle r="20" fill="#7a1e18" stroke="{O}" stroke-width="4"/><circle r="86" fill="none" stroke="{O}" stroke-width="4"/></g>',
}


def people_sprites(spec) -> str:
    """spec: (id, costume, foot [x,y,z], pose, height-scale). Uses rig v3 when available."""
    try:
        from kit.rig3 import figure_svg, VIEWBOX, ASPECT
    except ImportError:
        return ""
    js = []
    looks = {"trader": (2, 0, "short"), "casual": (3, 3, "curly"), "suit_w": (1, 1, "bun"), "suit": (0, 0, "parted"), "casual2": (4, 6, "buzz"), "founder": (0, 2, "parted")}
    for n, (pid, costume, foot, pose, hs) in enumerate(spec):
        sk, hr, st = looks.get(costume, (n, n, "short"))
        mk = figure_svg(pid, costume, skin=(sk + n) % 6, hair=hr, style=st, pose=pose, inner=True).replace("`", "\\`")
        js.append(f"sc.sprite({foot}, {1.76 * hs:.3f}, `{mk}`, {ASPECT}, {{ viewBox: '{VIEWBOX}', id: '{pid}' }});")
    return "\n".join(js)
