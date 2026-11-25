#!/usr/bin/env node
// Verifies render.py --isolate documents: each reduced per-chunk document must paint the same element state as the
// full composition at sample frames inside its chunk, and must load without page errors.
//   node epoch-ledger/scripts/isolate_check.mjs FULL/index.html spec.json      (spec: [{key, html, start, end}, ...])
// Prints JSON {key: {ok, frames, mismatch: [t...], errors: [...]}} on stdout.
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { readFileSync } from 'node:fs';
import { SEEK, STATE, openComposition, compositionURL } from './lib/frame_state.mjs';

const [full, specFile] = process.argv.slice(2);
const spec = JSON.parse(readFileSync(specFile, 'utf8'));
const { chromium } = createRequire(import.meta.url)('playwright');
const browser = await chromium.launch({ args: ['--disable-partial-raster'] });
const F = await openComposition(browser, await compositionURL(full));
const fps = 30, snap = t => Math.round(t * fps) / fps;
const out = {};
for (const c of spec) {
  const I = await openComposition(browser, await compositionURL(c.html));
  const ts = [...new Set([c.start, (c.start + c.end) / 2, c.end - 1 / fps].map(snap))].filter(t => t >= c.start && t < c.end);
  const mismatch = [];
  for (const t of ts) {
    const state = async (p) => { await p.evaluate(`(${SEEK})(${t})`); return p.evaluate(STATE); };
    if ((await state(F.page)) !== (await state(I.page))) mismatch.push(t);
  }
  out[c.key] = { ok: !mismatch.length && !I.errors.length, frames: ts, mismatch, errors: I.errors.slice(0, 3) };
  await I.page.close();
}
await browser.close();
console.log(JSON.stringify(out));
