"""Railway analogy 12:43–13:00 (storyboard s063): a working main line between productive towns vs an
abandoned branch. Beats are keyed to spoken words: the camera rides beside the driving wheels, pulls back
on "enormous investment", the towns light up and the factories smoke on "returns"; the cut to the
abandoned branch lands on the line start and the station sign drops on "disaster"."""
from kit.assemble import Scene
from timeline import L, W


def build():
    a, b = L("c07_12"), L("c07_13")
    s, e = a[0] - .5, b[1] + .6
    w_prod, w_enorm, w_ret = W("productive", "c07_12"), W("enormous", "c07_12"), W("returns", "c07_12")
    w_insuf, w_dis = W("insufficient", "c07_13"), W("disaster", "c07_13")
    # main line: offsets relative to the moving train (tracking camera)
    keysA = [[s, [6.5, 1.2, 5.2], [1.5, 1.3, 0], 34], [w_prod, [2.5, 1.5, 6.4], [-.5, 1.6, 0], 34],
             [w_enorm + .3, [14, 8, 24], [-6, 3, 0], 38], [w_ret, [-16, 13, 28], [60, 3, -14], 40], [b[0], [-10, 17, 34], [80, 4, -16], 40]]
    # abandoned branch: absolute offsets from the branch set
    keysB = [[b[0], [-78, 1.5, 3.2], [-30, 1.1, 0], 36], [w_insuf, [-60, 2.0, 4.2], [-24, 1.4, -2], 36],
             [w_dis - .2, [-47, 3.0, 7.5], [-43, 4, -8], 38], [e, [-34, 4.2, 10], [30, 1, 0], 42]]
    regions = [("railway", [(s, e)], f"""AI3D.add('railway',{{start:{s},end:{e},world:'railway2',turn:{b[0]},
 keysA:{keysA},keysB:{keysB},returns:{w_ret},sign:{w_dis}}});""")]
    html = ('<div id="rw-dip" class="fill" style="background:#1a120a;opacity:0"></div>'
            '<div class="tag v" id="rw-tag">Analogy</div>'
            '<div class="src" id="rw-src" style="top:120px">Northern Pacific Railway, 1870–1890:<br>≈ 2.24% of US GDP a year · ECB FSR Nov 2026</div>'
            '<div class="lbl" id="rw-l1" style="left:120px;top:640px">Strong demand</div><div class="lbl" id="rw-l2" style="left:120px;top:640px">Weak demand</div>')
    js = f"""
tl.fromTo('#rw-dip',{{opacity:1}},{{opacity:0,duration:.5}},{s});
show('#rw-tag',{s + .4}); show('#rw-src',{w_enorm}); hide('#rw-src',{b[0] - .6});
show('#rw-l1',{w_prod}); hide('#rw-l1',{b[0] - .4},.25);
tl.fromTo('#rw-dip',{{opacity:0}},{{opacity:1,duration:.2}},{b[0] - .2}); tl.to('#rw-dip',{{opacity:0,duration:.35}},{b[0]});
show('#rw-l2',{w_insuf});
"""
    return [Scene("rw", round(s, 3), round(e - s, 3), html, js=js)], regions, ""
