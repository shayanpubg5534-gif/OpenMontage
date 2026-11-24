"""Build the Epoch Ledger motion-kit reference composition (one scene per capability).

  python epoch-ledger/scripts/motion_demo.py <workspace>      # then: npx hyperframes snapshot / layout_check

Doubles as living documentation and as the functional test fixture (tests/epoch_ledger/test_motion_kit.py).
Shows: narration-locked kinetic type, blueprint draw-on, diagram build with focus/context and flowing
connectors, exact counters and bars, isometric build, a vector map route, ambient life + parallax,
and the series end screen. No narration audio; times are illustrative.
"""
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT_ROOT))

from kit.assemble import Scene, assemble, prepare_workspace  # noqa: E402
from kit.motion import (diagram_edge, diagram_node, endscreen_html, iso_box, iso_grid, ktext,  # noqa: E402
                        projection, route_path, world_map_svg)

D = 30.0
BG = '<div class="fill" style="background:radial-gradient(ellipse at 50% 40%,#1c2638,#0a0f18)"></div>'


def svg(inner, extra=""):
    return f'<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg" style="overflow:visible{extra}">{inner}</svg>'


def build():
    scenes = []
    # 1. kinetic type locked to (illustrative) word times + masked line reveal
    scenes.append(Scene("k1", 0, 4, BG + ktext("k1-a", "Money moves through the system", style="position:absolute;left:160px;top:380px;font:800 84px Fraunces;color:#f3e3c3")
                        + ktext("k1-b", "supporting revenue|at every stage", by="line", style="position:absolute;left:160px;top:520px;font:700 54px Inter;color:#9fd8ff"),
                        js="mWordsAt('#k1-a',[.3,.55,.8,1.05,1.3],{emphasis:[0],emphasisColor:'#f2c66d'}); mReveal('#k1-b',1.8,{by:'line'});"))
    # 2. blueprint draw-on with fills after outlines
    bp = ('<rect x="560" y="300" width="800" height="420" rx="10" fill="#14243a" stroke="#7fd8ff" stroke-width="4" class="bp"/>'
          '<path d="M600 660 L1320 660 M640 340 L640 660 M1280 340 L1280 660" stroke="#7fd8ff" stroke-width="3" fill="none" class="bp"/>'
          '<circle cx="960" cy="500" r="110" fill="#1f3a5a" stroke="#f2c66d" stroke-width="4" class="bp"/>')
    scenes.append(Scene("b1", 4, 4, BG + svg(bp) + '<div class="lbl" id="b1-l" style="left:640px;top:220px">Blueprint draw-on</div>',
                        js="mDrawOn('#b1 .bp',4.2,{fillAfter:true,stagger:.3}); tl.to('#b1-l',{opacity:1,duration:.4},4.3);"))
    # 3. diagram: nodes → edges → labels, focus + context, flowing connector with dots
    dg = (diagram_node("d-a", 260, 460, 300, 120, "Chip maker") + diagram_node("d-b", 810, 460, 300, 120, "Cloud")
          + diagram_node("d-c", 1360, 460, 300, 120, "AI developer")
          + diagram_edge("d-e1", 560, 520, 810, 520, 60) + diagram_edge("d-e2", 1110, 520, 1360, 520, 60))
    scenes.append(Scene("g1", 8, 5, BG + svg(dg) + '<div class="lbl" id="g1-l" style="left:780px;top:640px">chips → capacity</div>',
                        js="mDiagram({nodes:[['#d-a',8.2],['#d-b',8.5],['#d-c',8.8]],edges:[['#d-e1',9.1],['#d-e2',9.4]],labels:[['#g1-l',9.8]]});"
                           "mFocus('#d-b',['#d-a','#d-c'],10.4); mUnfocus(['#d-a','#d-c'],11.8); mFlow('#d-e1',10.0,13.0,{dots:3});"))
    # 4. data: exact counter + bars + line
    bars = "".join(f'<rect class="bar" x="{560 + i * 170}" y="760" width="120" height="0" fill="#5fb36a"/>' for i in range(5))
    scenes.append(Scene("c1", 13, 4, BG + svg('<path d="M520 760 H1420" stroke="#8fa3b8" stroke-width="3"/>' + bars
                                              + '<path id="c1-line" d="M560 700 C760 640 960 560 1380 380" stroke="#f2c66d" stroke-width="6" fill="none"/>')
                        + '<div id="c1-n" class="lbl" style="left:560px;top:200px;font-size:90px;opacity:1">$0</div>',
                        js="mCount('#c1-n',0,10000,13.2,1.4,{prefix:'$'}); mBars('#c1 .bar',[1,2.2,3.1,4.6,6],13.3,{scale:70,baseline:760}); mLine('#c1-line',13.8,1.4);"))
    # 5. isometric build (bottom-up, lift on Z)
    iso = iso_grid(8, 60, ox=960, oy=420) + "".join(iso_box(f"iso{k}", 120, 120, k * 50, 240, 240, 46, ["#3a6ab0", "#38a0d6", "#5fb36a", "#f2c66d"][k], ox=960, oy=420) for k in range(4))
    scenes.append(Scene("i1", 17, 4, BG + svg(iso),
                        js="[0,1,2,3].forEach(k=>tl.fromTo('#iso'+k,{y:-120,opacity:0},{y:0,opacity:1,duration:.45,ease:MOTION.ease.settle},17.2+k*.25));"))
    # 6. vector map: route draw-on with editorial stutter pins, region focus
    p = projection("equirect", center=(10, 25), scale=5.2)
    mp = world_map_svg("wm", p, {"United States of America": "#d9503f", "United Kingdom": "#d9503f", "Japan": "#d9503f"}, land="#5a6a5a", stroke="#2a3a2a")
    route = route_path([(-74.0, 40.7), (-0.1, 51.5), (139.7, 35.7)], p)
    scenes.append(Scene("m1", 21, 4, '<div class="fill" style="background:#0f2a33"></div>' + svg(mp + f'<path id="m1-r" d="{route}" stroke="#f2c66d" stroke-width="5" fill="none"/>'),
                        js="mDrawOn('#m1-r',21.4,{dur:2.2}); mStutter('#m1-r',{opacity:1},21.4,2.2);"))
    # 7. ambient environment + parallax camera move + end screen
    layers = ('<div id="a-l0" class="fill" style="background:linear-gradient(#f3b36a,#3a2a3a)"></div>'
              '<div id="a-l1" class="fill">' + svg('<path d="M-200 700 C300 560 700 640 1100 580 C1500 520 1800 600 2200 560 L2200 1080 L-200 1080Z" fill="#4a3a4a"/>') + '</div>'
              '<div id="a-l2" class="fill">' + svg('<path d="M-200 820 C400 760 900 800 1400 760 C1700 740 2000 780 2200 770 L2200 1080 L-200 1080Z" fill="#2a2030"/>') + '</div>'
              '<div id="a-sun" style="position:absolute;left:1300px;top:260px;width:180px;height:180px;border-radius:50%;background:#ffd99a;box-shadow:0 0 80px #ffd99a"></div>')
    scenes.append(Scene("e1", 25, 5, layers + endscreen_html("es", "Next on The Epoch Ledger"),
                        js="mParallax([['#a-l0',.1],['#a-l1',.45],['#a-l2',1]],25,30,{dx:-90,dolly:.03}); mAmbient('#a-sun',25,30,{flicker:.12,scale:.03,period:1.8}); mEndScreen('es',26.5,{dur:3.5});"))
    return scenes


def main(ws: Path):
    prepare_workspace(ws)
    html = assemble(title="Epoch Ledger motion kit", duration=D, scenes=build(), audio=None, resolution="1080p",
                    extra_css=".lbl{position:absolute;font:800 40px Fraunces;color:#fff;opacity:0}.fill{position:absolute;inset:0}")
    (ws / "index.html").write_text(html)
    print("wrote", ws / "index.html")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
