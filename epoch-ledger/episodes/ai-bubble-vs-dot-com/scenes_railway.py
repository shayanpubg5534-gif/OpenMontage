"""Railway analogy 12:43–13:00 (storyboard s063): busy line between productive towns vs an empty branch."""
from kit.assemble import Scene
from timeline import L


def build():
    a, b = L("c07_12"), L("c07_13")
    s, e = a[0] - .5, b[1] + .6
    regions = [("railway", [(s, e)], f"""AI3D.add('railway',{{start:{s},end:{e},world:'railway',turn:{b[0]},
 camA:{{from:[-95,34,70],to:[-30,16,34],look:[-60,4,0],lookTo:[0,3,0],dur:{b[0] - s}}},
 camB:{{from:[-6,22,28],to:[18,10,-58],look:[12,2,-50],lookTo:[34,2,-100],dur:{e - b[0]}}}}});""")]
    html = ('<div id="rw-dip" class="fill" style="background:#1a120a;opacity:0"></div>'
            '<div class="tag v" id="rw-tag">Analogy</div>'
            '<div class="src" id="rw-src" style="top:120px">Northern Pacific Railway, 1870–1890:<br>≈ 2.24% of US GDP a year · ECB FSR Nov 2026</div>'
            '<div class="lbl" id="rw-l1" style="left:120px;top:640px">Strong demand</div><div class="lbl" id="rw-l2" style="left:120px;top:640px">Weak demand</div>')
    js = f"""
tl.fromTo('#rw-dip',{{opacity:1}},{{opacity:0,duration:.5}},{s});
show('#rw-tag',{s + .4}); show('#rw-src',{a[0] + 1.5}); hide('#rw-src',{a[0] + 7.5});
show('#rw-l1',{a[0] + 3}); hide('#rw-l1',{b[0] - .4},.25);
tl.fromTo('#rw-dip',{{opacity:0}},{{opacity:1,duration:.2}},{b[0] - .2}); tl.to('#rw-dip',{{opacity:0,duration:.35}},{b[0]});
show('#rw-l2',{b[0] + 2});
"""
    return [Scene("rw", round(s, 3), round(e - s, 3), html, js=js)], regions, ""
