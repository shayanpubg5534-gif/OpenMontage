// Shared by qc.mjs and isolate_check.mjs: HyperFrames clip-window emulation and a state signature of everything that
// can paint at the current time. Paths are anchored on element ids, so a document with some clips removed (render.py
// --isolate) yields the same signature as the full document when the frame is the same.

// Seek a HyperFrames composition to t (clip windows emulated with visibility, as layout_check does).
export const SEEK = (t) => {
  document.querySelectorAll('[data-start][data-duration]').forEach(c => {
    if (c.id === 'root' || c.tagName === 'AUDIO') return; const s = +c.dataset.start, d = +c.dataset.duration;
    c.style.visibility = t >= s && t < s + d ? 'visible' : 'hidden'; });
  window.__timelines.main.seek(t, false);
};

// Attributes, inline style and own text of rendered elements; inert GSAP identity values normalised away.
export const STATE = `(() => { const out = []; const N = v => (v || '').replace(/matrix\\(1,\\s*0,\\s*0,\\s*1,\\s*0,\\s*0\\)/g, '')
    .replace(/(translate|rotate|scale): none;|transform: translate\\(0px, 0px\\);|transform-origin:[^;]*;/g, '').replace(/\\s+/g, ' ').trim();
  const walk = (e, path) => { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') return;
    const at = Array.from(e.attributes).filter(a => !['style', 'data-svg-origin', 'opacity'].includes(a.name)).map(a => [a.name, N(a.value)]).filter(a => a[1] !== '').map(a => a.join('=')).join(' ');
    const txt = Array.from(e.childNodes).filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
    let px = '';                  // 2D canvases: a digest of their pixels (WebGL buffers are usually not readable here)
    if (e.tagName === 'CANVAS') { try { const u = e.toDataURL(); let h = 0; for (let i = 0; i < u.length; i += 7) h = (h * 31 + u.charCodeAt(i)) | 0; px = '|px' + h; } catch (_) { px = '|px?'; } }
    out.push(path + '|' + at + '|' + N(e.style.cssText.replace(/opacity:[^;]*;?/g, '')) + '|o' + (+cs.opacity).toFixed(3) + '|' + txt + px);
    const seen = {};
    Array.from(e.children).forEach(c => { const k = c.id ? '#' + c.id : c.tagName + (seen[c.tagName] = (seen[c.tagName] || 0) + 1);
      walk(c, c.id ? k : path + '/' + k); }); };
  walk(document.getElementById('root'), '#root'); return out.join('\\n'); })()`;

export async function openComposition(browser, url) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(url, { waitUntil: 'load' });
  for (let k = 0; k < 120 && !(await page.evaluate(() => !!(window.__timelines && window.__timelines.main))); k++) await page.waitForTimeout(250);
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all(Array.from(document.images).map(i => i.decode().catch(() => {}))); });
  return { page, errors };
}
