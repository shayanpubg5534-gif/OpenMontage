// P10: render one 2.5D shot with several compose.mjs workers in parallel (contiguous frame ranges), then join the
// segments without re-encoding. Safe: every frame is a pure function of (shot spec, frame number), each worker has its
// own browser and output file, segments share identical encoder settings, and the join is a stream copy checked for the
// expected frame count.
//   node epoch-ledger/charlab/p10/render_shot.mjs SHOT.json OUT.mp4 [--workers 3]
import { readFileSync, writeFileSync, rmSync } from 'node:fs'; import { spawn, execFileSync } from 'node:child_process';
import path from 'node:path'; import { fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2); const [shotFile, out] = args;
const W = +(args[args.indexOf('--workers') + 1] || 0) || 3;
const shot = JSON.parse(readFileSync(shotFile, 'utf8')); const N = Math.round(shot.duration * 30);
const t0 = Date.now(), per = Math.ceil(N / W), jobs = [];
for (let w = 0; w < W && w * per < N; w++) {
  const a = w * per, b = Math.min(N - 1, a + per - 1), seg = out.replace(/\.mp4$/, `.part${w}.mp4`);
  jobs.push(new Promise((res, rej) => {
    const p = spawn('node', [path.join(HERE, 'compose.mjs'), shotFile, seg, '--from', String(a), '--to', String(b), '--threads', '1'], { stdio: ['ignore', 'pipe', 'inherit'] });
    let o = ''; p.stdout.on('data', d => o += d); p.on('close', c => c ? rej(new Error('worker ' + w + ' failed')) : res({ seg, ...JSON.parse(o.trim().split('\n').pop()) }));
  }));
}
const parts = await Promise.all(jobs);
const list = out.replace(/\.mp4$/, '.parts.txt'); writeFileSync(list, parts.map(p => `file '${path.resolve(p.seg)}'`).join('\n'));
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', '-movflags', '+faststart', out]);
const n = +execFileSync('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', out]).toString().trim();
if (n !== N) throw new Error(`joined ${n} frames, expected ${N}`);
parts.forEach(p => rmSync(p.seg)); rmSync(list);
console.log(JSON.stringify({ out, frames: N, workers: parts.length, wall_s: +((Date.now() - t0) / 1000).toFixed(1),
  worker_s_per_frame: parts.map(p => p.s_per_frame), setup_s: parts.map(p => p.setup_s) }));
