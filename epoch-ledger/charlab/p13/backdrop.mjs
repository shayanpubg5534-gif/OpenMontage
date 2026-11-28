// P13 storyboard: the view through the family's kitchen window, a street of similar modest houses (the neighbourhood
// the loans will be pooled from), painted procedurally. Two times of day: dusk (2006, porch lights coming on) and night
// (2008: fewer lights, one FOR SALE sign). Deterministic.
//   node epoch-ledger/charlab/p13/backdrop.mjs OUT_DIR
import { createRequire } from 'node:module'; import { mkdirSync } from 'node:fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const out = process.argv[2]; mkdirSync(out, { recursive: true });
const page = mode => `<canvas id=c width=1600 height=900></canvas><script>
const g = c.getContext('2d'), W = 1600, H = 900, night = ${mode === 'night'}; let s = 7; const r = () => (s = (s * 16807) % 2147483647) / 2147483647;
const sky = g.createLinearGradient(0, 0, 0, H * .62);
if (night) { sky.addColorStop(0, '#0d1424'); sky.addColorStop(1, '#25314a'); } else { sky.addColorStop(0, '#47587e'); sky.addColorStop(.55, '#c98d6e'); sky.addColorStop(1, '#f0c38f'); }
g.fillStyle = sky; g.fillRect(0, 0, W, H);
const ground = H * .66; g.fillStyle = night ? '#1b2230' : '#5d6150'; g.fillRect(0, ground, W, H - ground);       // lawns
g.fillStyle = night ? '#2a303b' : '#8a8577'; g.fillRect(0, ground + 70, W, 60);                                   // the street
g.fillStyle = night ? '#3b4250' : '#b3ab98'; g.fillRect(0, ground + 64, W, 6);
// two rows of houses: far (small) and near; each: walls, pitched roof, door, two windows, a porch light
const house = (x, base, w, k, far) => { const h = w * .62, wall = night ? ['#4a4f5c', '#565b66', '#3f4552'][k % 3] : ['#d9c6a5', '#cbb79a', '#e3d3b6', '#bfae96'][k % 4];
  g.fillStyle = wall; g.fillRect(x, base - h, w, h);
  g.fillStyle = night ? '#232733' : ['#6e4a3b', '#5b4a44', '#7a5a43'][k % 3]; g.beginPath(); g.moveTo(x - w * .08, base - h); g.lineTo(x + w / 2, base - h - w * .42); g.lineTo(x + w * 1.08, base - h); g.fill();
  g.strokeStyle = 'rgba(30,27,25,.75)'; g.lineWidth = far ? 1.5 : 2.5; g.strokeRect(x, base - h, w, h);
  g.beginPath(); g.moveTo(x - w * .08, base - h); g.lineTo(x + w / 2, base - h - w * .42); g.lineTo(x + w * 1.08, base - h); g.stroke();
  const lit = night ? r() < .35 : r() < .8;
  for (const wx of [.14, .62]) { g.fillStyle = lit ? (night ? '#f2c477' : '#f7d79a') : (night ? '#1c2230' : '#6d7c8f'); g.fillRect(x + w * wx, base - h * .72, w * .22, h * .3); g.strokeRect(x + w * wx, base - h * .72, w * .22, h * .3); }
  g.fillStyle = night ? '#2c2522' : '#5a3a2a'; g.fillRect(x + w * .42, base - h * .5, w * .16, h * .5); g.strokeRect(x + w * .42, base - h * .5, w * .16, h * .5);
  if (lit) { const L = g.createRadialGradient(x + w * .5, base - h * .56, 1, x + w * .5, base - h * .56, w * .3); L.addColorStop(0, 'rgba(255,214,150,.9)'); L.addColorStop(1, 'rgba(255,214,150,0)'); g.fillStyle = L; g.fillRect(x, base - h, w, h); }
  return lit; };
let k = 0; for (let x = -40; x < W; x += 150 + r() * 30) house(x, ground - 6, 120, k++, true);
let sale = night ? 3 : -1; k = 0;
for (let x = -60; x < W; x += 290 + r() * 40, k++) { house(x, ground + 60, 230, k + 2, false);
  if (k === sale) { g.fillStyle = '#f3ede0'; g.fillRect(x + 180, ground + 16, 96, 42); g.strokeRect(x + 180, ground + 16, 96, 42); g.fillStyle = '#a3241c';
    g.font = 'bold 15px Inter, Arial'; g.fillText('FOR SALE', x + 188, ground + 43); g.fillStyle = '#3a2c22'; g.fillRect(x + 222, ground + 58, 6, 24); } }
for (let i = 0; i < 9; i++) { const x = r() * W, y = ground + 8 + r() * 30; g.fillStyle = night ? '#141a22' : '#46553f'; g.beginPath(); g.arc(x, y - 40, 34 + r() * 20, 0, 7); g.fill(); }   // trees
if (night) for (const x of [380, 1180]) { const L = g.createRadialGradient(x, ground + 30, 2, x, ground + 30, 160); L.addColorStop(0, 'rgba(255,220,160,.55)'); L.addColorStop(1, 'rgba(255,220,160,0)'); g.fillStyle = L; g.fillRect(x - 160, ground - 130, 320, 300);
  g.fillStyle = '#11151c'; g.fillRect(x - 3, ground - 100, 6, 170); }
window.done = true;</script>`;
const b = await chromium.launch();
for (const m of ['dusk', 'night']) { const p = await b.newPage({ viewport: { width: 1600, height: 900 } }); p.on('pageerror', e => console.error(String(e))); await p.setContent(page(m)); await p.waitForFunction(() => window.done);
  await (await p.$('#c')).screenshot({ path: `${out}/street_${m}.png` }); }
await b.close(); console.log('backdrops', out);
