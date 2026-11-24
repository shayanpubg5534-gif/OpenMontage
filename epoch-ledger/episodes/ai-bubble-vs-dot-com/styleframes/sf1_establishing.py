"""Style frame 1 — cinematic establishing shot (c03_03 "beneath the rising stock prices", ~3:31).

Scene plan: establishing / low-angle two-point street at dusk. Focal point: the BigCart.com building (left third)
with the capital pipe bridging to Summit Ventures (right); the market board glows at the vanishing point, its
line rising. Technique: illustrated vector 3D (kit/scene3d.js) — real perspective, CC0 brick/asphalt/concrete
textures, sun backlight + sky + lamp lighting, fog, cast shadows; lightfx sky/haze/glow/grade; rig v3 pedestrians.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from kit.lightfx import glow, grade, haze, sky  # noqa: E402
from styleframes.common import page, people_sprites, ART  # noqa: E402

SCENE = r"""
const sc = S3.scene(), T = (n) => TEX + n + '.jpg';
const brick = { color: '#c9826a', tex: T('brick'), texScale: 2.2, sub: 5, tint: '#ffd9c8' };
const asphalt = { color: '#3a3640', tex: T('asphalt'), texScale: 6, sub: 6, receiver: true, outline: false, tint: '#a8a0b0' };
const walk = { color: '#9a9088', tex: T('concrete'), texScale: 2.5, sub: 5, receiver: true, outline: false };
const stone = { color: '#d8cbb0' }, trim = { color: '#6a3a2a' }, glassT = { color: '#3a5a86', emissive: .15, gloss: .35 };
// ground: street + sidewalks + curbs
sc.ground(-6, -220, 6, 12, 0, 6, Object.assign({}, asphalt, { sub: 2 }));
sc.ground(-12, -220, -6, 12, .16, 3, Object.assign({}, walk, { sub: 1 })); sc.ground(6, -220, 14, 12, .16, 3, Object.assign({}, walk, { sub: 1 }));
sc.box([-6.2, 0, -220], [-6, .16, 12], { color: '#8a8278' }, { faces: ['right'], shadow: false }); sc.box([6, 0, -220], [6.2, .16, 12], { color: '#8a8278' }, { faces: ['left'], shadow: false });
// lane markings
for (let z = 30; z > -200; z -= 7) sc.quad([-.1, .005, z], [.1, .005, z], [.1, .005, z - 3.5], [-.1, .005, z - 3.5], { color: '#e8e0c0', outline: false, receiver: true });
// BigCart.com — 5 storeys of brick with stone base, cornice and a rooftop billboard (street face at x = -6)
sc.box([-22, 0, -30], [-6, 18, -4], brick, { faces: ['right', 'front', 'top'], name: 'bigcart', bias: -3 });
sc.facade({ origin: [-22, 3.6, -3.98], u: [1, 0, 0], width: 16, height: 13.6, cols: 5, rows: 4, base: .4, top: .6, margin: .9, inset: .25, seed: 12, lit: .5,
  wall: { color: '#0000', alpha: 0, outline: false }, frame: { color: '#4a2e24' }, sill: { color: '#e2d6bc' } });
sc.box([-6.05, 0, -30], [-5.75, 3.6, -4], stone, { faces: ['right', 'front', 'top'], shadow: false });
sc.box([-6.4, 17.2, -30.3], [-5.5, 18.4, -3.7], { color: '#e2d6bc' }, { faces: ['right', 'front', 'bottom', 'top'] });
sc.box([-6.2, 6.9, -30.1], [-5.8, 7.2, -3.9], { color: '#d8cbb0' }, { faces: ['right', 'front', 'bottom'], shadow: false });
for (let z = -4; z >= -30; z -= 6.5) sc.box([-6.3, 3.6, z - .4], [-5.7, 17.2, z + .0], { color: '#b8705a', tex: T('brick'), texScale: 2.2, sub: 2 }, { faces: ['right', 'front'], shadow: false });
sc.facade({ origin: [-5.98, 3.6, -4], u: [0, 0, -1], width: 26, height: 13.6, cols: 8, rows: 4, base: .4, top: .6, margin: .9, inset: .25, seed: 11, lit: .55,
  wall: { color: '#00000000', alpha: 0, outline: false }, frame: { color: '#4a2e24' }, sill: { color: '#e2d6bc' } });
// ground-floor storefront: three tall lit bays showing the lobby and its cash tank
[[-6, -11], [-12, -17], [-18, -23]].forEach(([z0, z1], i) => {
  sc.quad([-5.72, .5, z0 - .4], [-5.72, .5, z1 + .4], [-5.72, 3.2, z1 + .4], [-5.72, 3.2, z0 - .4], { color: '#ffd48a', emissive: .9, outline: '#2a1a12' }, { bias: .1 });
  sc.art([-5.70, .5, z0 - .4], [-5.70, .5, z1 + .4], [-5.70, 3.2, z0 - .4], 600, 300, ART.lobby[i], { bias: .12 });
});
sc.quad([-5.7, 3.25, -4.2], [-5.7, 3.25, -9], [-5.7, 3.55, -9], [-5.7, 3.55, -4.2], { color: '#2e5ab0', emissive: .6 }, { bias: .1 });
sc.art([-5.68, 3.25, -4.4], [-5.68, 3.25, -8.8], [-5.68, 3.55, -4.4], 440, 30, ART.sign, { bias: .12 });
// rooftop billboard (faces the street at an angle toward the camera)
sc.box([-19, 18, -7.2], [-18.7, 20.4, -6.9], { color: '#2a2a2e' }); sc.box([-11.3, 18, -7.2], [-11, 20.4, -6.9], { color: '#2a2a2e' });
sc.quad([-20, 20.3, -6.9], [-10, 20.3, -6.9], [-10, 25.0, -6.9], [-20, 25.0, -6.9], { color: '#f4ead5' }, { bias: -1 });
sc.art([-19.8, 20.5, -6.8], [-10.2, 20.5, -6.8], [-19.8, 24.8, -6.8], 900, 620, ART.billboard, { bias: .3 });
// Summit Ventures — glass tower (street face at x = +6), stone podium
sc.box([6, 0, -34], [24, 46, -6], { color: '#3a5a86', gloss: .3 }, { faces: ['left', 'front', 'top'], name: 'summit', bias: -3 });
sc.facade({ origin: [6.02, 4.5, -34], u: [0, 0, 1], width: 28, height: 41, cols: 14, rows: 13, base: .2, top: .4, margin: .3, inset: .12, seed: 23, lit: .35,
  winW: 1.7, winH: 2.6, wall: { color: '#00000000', alpha: 0, outline: false }, frame: { color: '#1e2a3a' }, sill: { color: '#506078' }, lintel: false,
  dark: '#6a6a9e', litColors: ['#ffd8a0', '#f2c890', '#d8e0f8'] });
sc.facade({ origin: [6, 4.5, -5.98], u: [1, 0, 0], width: 18, height: 41, cols: 9, rows: 13, base: .2, top: .4, margin: .3, inset: .12, seed: 29, lit: .35,
  winW: 1.6, winH: 2.6, wall: { color: '#0000', alpha: 0, outline: false }, frame: { color: '#1e2a3a' }, sill: { color: '#506078' }, lintel: false,
  dark: '#6a6a9e', litColors: ['#ffd8a0', '#f2c890', '#d8e0f8'] });
sc.box([5.6, 0, -34.3], [7, 4.5, -5.7], { color: '#cfc4ae', tex: T('concrete'), texScale: 3, sub: 3 }, { faces: ['left', 'front', 'top'] });
sc.quad([5.58, .4, -10], [5.58, .4, -20], [5.58, 3.8, -20], [5.58, 3.8, -10], { color: '#ffe0a8', emissive: .8 }, { bias: .1 });
sc.art([5.55, 3.9, -26], [5.55, 3.9, -8], [5.55, 4.4, -26], 1200, 34, ART.summit, { bias: .12 });
// the capital pipe: from Summit's podium across the street into BigCart's wall, with flanges and a red valve wheel
sc.tube('x', -5.7, 5.6, 6.2, -16, .42, { color: '#c7953f', gloss: .5, outline: false }, { seg: 14 });
[-4, -1.2, 1.6, 4].forEach(x => sc.tube('x', x - .1, x + .1, 6.2, -16, .5, { color: '#8a6420', outline: false }, { seg: 14 }));
sc.cyl([1.6, 0, -16], .08, 6.6, 7.4, { color: '#5a4a3a' }, { seg: 8, shadow: false });
sc.art([1.0, 7.0, -15.7], [2.2, 7.0, -15.7], [1.0, 8.2, -15.7], 200, 200, ART.valve, { bias: .2 });
// skyline down the street and the market board at the vanishing point
const r = S3.seed(9);
for (let i = 0; i < 14; i++) { const side = i % 2 ? 1 : -1, z0 = -40 - i * 11, h = 12 + r() * 34, x0 = side > 0 ? 7 + r() * 3 : -7 - r() * 3 - 12;
  sc.box([x0, 0, z0 - 9], [x0 + 12, h, z0], { color: ['#6a5468', '#58506a', '#7a6070', '#4e4a64'][i % 4] }, { faces: [side > 0 ? 'left' : 'right', 'front', 'top'] });
  sc.facade({ origin: side > 0 ? [x0 - .01, 2, z0 - 9] : [x0 + 12.01, 2, z0], u: side > 0 ? [0, 0, 1] : [0, 0, -1], width: 9, height: h - 3, cols: 4, rows: Math.floor(h / 3.4), seed: 40 + i, lit: .4,
    wall: { color: '#0000', alpha: 0, outline: false }, frame: { color: '#2a2030' }, sill: { color: '#7a6a70' }, lintel: false }); }
sc.box([-6, 0, -125], [6, 36, -112], { color: '#3a3448' }, { faces: ['front', 'top'], bias: -2 });
sc.art([-5, 27, -111.8], [5, 27, -111.8], [-5, 34, -111.8], 1400, 1000, ART.board, { bias: .5 });
// street furniture: lamps (posts + heads), hydrant, newspaper box, a parked cab and a delivery van
[[-5.2, -2], [-5.2, -26], [5.2, -12], [5.2, -38], [-5.2, -52]].forEach(([x, z]) => { sc.cyl([x, 0, z], .09, .16, 5.6, { color: '#26242a' }, { seg: 8 });
  sc.box([x - .5 * Math.sign(x) - .25, 5.4, z - .18], [x - .5 * Math.sign(x) + .25, 5.62, z + .18], { color: '#1e1c22' }); });
// period cars: profile extrusions (sedan silhouette), glass, wheels on axles
const car = (x, z, col, L_, dir) => { const h = L_ / 2, k = dir || 1, prof = [[-h, .32], [h, .32], [h, .78], [h * .78, .92], [h * .42, .95], [h * .22, 1.42], [-h * .38, 1.44], [-h * .62, .98], [-h, .88]].map(q => [z + q[0] * k, q[1]]);
  sc.extrude(prof, 'x', x - .9, x + .9, { color: col, gloss: .4 }, { base: 0 });
  sc.extrude([[h * .2, 1.0], [-h * .36, 1.02], [-h * .2, 1.38], [h * .12, 1.37]].map(q => [z + q[0] * k, q[1]]), 'x', x - .92, x + .92, { color: '#24324a', gloss: .7, emissive: .05 }, { shadow: false, bias: .05 });
  [[-.62, -1], [.62, -1]].forEach(([f]) => [-1, 1].forEach(sd => sc.wheel([x + sd * .92, .33, z + f * h * k * 1.0], .33, .22, 'x', { color: '#121214' }, { capMat: { color: '#7a7a80' } }))); };
car(-3.0, -21, '#7a2424', 4.6, -1); car(3.1, -34, '#c89a2a', 4.6, 1); car(3.1, -52, '#2e4a6a', 4.6, 1);
// fire escapes on BigCart's street face (floors 2–5): platforms, railings, stair diagonals
for (let f = 0; f < 4; f++) { const y = 6.9 + f * 3.4, z0 = -13.6, z1 = -18.4;
  sc.box([-5.98, y, z1], [-4.9, y + .08, z0], { color: '#1e1c20' }, { shadow: true, soft: true });
  sc.box([-4.95, y + .08, z1], [-4.9, y + 1.0, z0], { color: '#1e1c20', alpha: .9 }, { faces: ['right', 'front', 'back', 'top'], shadow: false });
  sc.poly([[-4.92, y + .1, z0 - .3], [-4.92, y + .1, z0 - .45], [-4.92, y + 3.45, z1 + .5], [-4.92, y + 3.45, z1 + .65]], { color: '#1e1c20', doubleSided: true }, { allowBack: true }); }
// rooftop water tower (iconic New York silhouette) and parapet
sc.cyl([-17, 18, -20], 1.6, 21.4, 24.6, { color: '#6a4a30', tex: T('wood_floor'), texScale: 2 }, { seg: 14 });
sc.poly(Array.from({ length: 14 }, (_, i) => [-17 + Math.cos(-i / 14 * Math.PI * 2) * 1.75, 24.6, -20 + Math.sin(-i / 14 * Math.PI * 2) * 1.75]), { color: '#3a2a20' });
[[-15.8, -18.8], [-18.2, -18.8], [-15.8, -21.2], [-18.2, -21.2]].forEach(([x, z]) => sc.box([x - .08, 18, z - .08], [x + .08, 21.4, z + .08], { color: '#2a2224' }, { shadow: false }));
// storefront awnings (striped canvas)
[[-6, -11], [-12, -17], [-18, -23]].forEach(([z0, z1]) => sc.extrude([[-5.75, 3.4], [-4.6, 2.9], [-4.6, 2.75], [-5.75, 3.25]], 'z', z1 + .2, z0 - .2, { color: '#2e5ab0' }, { base: 0, soft: true }));
sc.box([-7.4, .16, 3.2], [-6.6, 1.3, 3.8], { color: '#2a6a4a', gloss: .3 });
""" + "\n" + "{people}"


def build(out: Path):
    sprites = people_sprites([
        ("p1", "trader", [-4.4, .16, -2.0], "walk", 1.0), ("p2", "casual", [-4.6, .16, -8.5], "phone", 1.0),
        ("p3", "suit_w", [4.6, .16, 1.5], "walk", 1.0), ("p4", "suit", [5.0, .16, -6.0], "talk", 1.0),
        ("p5", "casual2", [-4.8, .16, -19], "stand", .98), ("p6", "suit", [-5.0, .16, -24], "fold", 1.0)])
    cam = "const GLOWS = [[[-4.9,5.3,-2],90,'#ffd28a'],[[4.9,5.3,-12],80,'#ffd28a'],[[-4.9,5.3,-26],60,'#ffd28a'],[[4.9,5.3,-38],40,'#ffd28a'],[[0,30.5,-111],200,'#7cff9b'],[[-5.72,1.8,-14],160,'#ffd48a']];\nconst cam = S3.camera({ pos: [3.4, 1.6, 13], look: [-6.5, 1.6, -26], fov: 60, shift: [0, 360] });"
    light = ("const L = { sun: { dir: [.18, .32, -1], color: '#ffb36a', intensity: 1.15 }, sky: '#8a86b8', ground: '#5a3a3a', ambient: .62, "
             "points: [{pos:[-4.9,5.3,-2],color:'#ffd28a',intensity:1.2,range:7},{pos:[4.9,5.3,-12],color:'#ffd28a',intensity:1.2,range:7},{pos:[-4.9,5.3,-26],color:'#ffd28a',intensity:1.1,range:7}], "
             "fog: { color: '#e9a07a', near: 25, far: 210, max: .78 }, shadowOpacity: .5, shadowColor: '#2a1830' };")
    over_grade, root_filter = grade(vignette=.62, grain=.06, contrast=1.05, saturate=1.06)
    layers_back = sky("dusk", sun=(1010, 760), sun_r=620, clouds=7)
    layers_front = (haze(y=780, height=300, color="#f6a878", strength=.45)
                    + over_grade)
    page(out, "Style frame 1 — establishing", layers_back, SCENE.replace("{people}", sprites), cam, light, layers_front, root_filter,
         fg='<div style="position:absolute;left:-60px;top:560px;width:300px;height:560px;filter:blur(7px);opacity:.92">'
            '<svg viewBox="0 0 300 560" width="300" height="560"><rect x="120" y="0" width="34" height="560" fill="#141016"/>'
            '<rect x="40" y="300" width="200" height="260" rx="10" fill="#1d3a2a"/><rect x="60" y="330" width="160" height="90" fill="#0d1a12"/></svg></div>')


if __name__ == "__main__":
    build(Path(sys.argv[1]))
