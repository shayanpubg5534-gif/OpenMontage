#!/usr/bin/env python3
"""Epoch Ledger render orchestrator — scene-level cache, range renders, no re-encode assembly.

A HyperFrames composition is split at every top-level clip boundary into frame-aligned
segments, which are grouped into chunks of at least --chunk-min seconds. Each chunk's cache
key hashes only what can change its pixels:

  * the shared document (everything outside top-level clips and outside marker regions),
  * workspace assets (vendor JS, fonts, images — audio is excluded; narration is muxed last),
  * the source of every clip / marker region that overlaps the chunk,
  * the chunk's time range and the render settings.

So editing one scene re-renders only the chunk(s) that scene overlaps. Chunks are rendered
with `hyperframes render --start/--end`, stripped of audio, concatenated with stream copy,
and the narration is muxed once. Nothing is re-encoded at assembly time.

Marker regions let CSS/JS belong to a scene instead of the shared document:
    /*scene:s3*/ ... /*/scene:s3*/                 (in <style> or <script>)
    /*scene:vault3d spans=0-4.8,25.15-31.44*/ ... /*/scene:vault3d*/
A region whose id matches a top-level clip id inherits that clip's span; a region with
`spans=` uses those; any other region is global (affects every chunk).

Usage:
  render.py plan    WORKSPACE [--preview]
  render.py render  WORKSPACE -o OUT.mp4 [--audio narration.wav] [--preview] [--jobs N]
  render.py scene   WORKSPACE SCENE_ID -o OUT.mp4 [--preview]   # one scene, cached
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

HF_VERSION = os.environ.get("EPOCH_HF_VERSION", "0.9.88")
FINAL = {"fps": 30, "quality": "looks"}       # CRF 16 — the approved pilot setting
PREVIEW = {"fps": 24, "quality": "draft"}     # range renders need 24/25/30/60 fps
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
SKIP_DIRS = {".hyperframes", ".render-cache", "renders", "node_modules", "__pycache__"}
MARK = re.compile(r"/\*scene:([\w-]+)(?:\s+spans=([\d.,\-]+))?\*/(.*?)/\*/scene:\1\*/", re.S)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


# ── parsing ────────────────────────────────────────────────────────────
@dataclass
class Clip:
    id: str
    tag: str
    start: float
    end: float
    text: str


@dataclass
class Region:
    id: str
    text: str
    spans: list[tuple[float, float]] | None  # None → inherit clip span or global


@dataclass
class Composition:
    duration: float
    clips: list[Clip]
    regions: list[Region]
    shared: str
    deps: dict[str, list[tuple[float, float]]] = field(default_factory=dict)  # id → spans; [] = global


class _TopLevel(HTMLParser):
    """Find byte offsets of the direct children of the composition root that carry data-start."""

    def __init__(self, src: str):
        super().__init__(convert_charrefs=False)
        self.src, self.lines = src, src.splitlines(keepends=True)
        self.offsets = [0]
        for line in self.lines:
            self.offsets.append(self.offsets[-1] + len(line))
        self.depth, self.root_depth, self.duration = 0, None, None
        self.open: dict | None = None
        self.found: list[dict] = []

    def _pos(self):
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in VOID:
            if self.root_depth is not None and self.depth == self.root_depth + 1 and "data-start" in a:
                start = self._pos()
                self.found.append({**a, "tag": tag, "s": start, "e": self.src.index(">", start) + 1})
            return
        self.depth += 1
        if self.root_depth is None and "data-composition-id" in a:
            self.root_depth, self.duration = self.depth, float(a.get("data-duration", 0))
        elif self.root_depth is not None and self.depth == self.root_depth + 1 and "data-start" in a:
            self.open = {**a, "tag": tag, "s": self._pos()}

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.open is not None and self.depth == self.root_depth + 1:
            end = self.src.index(">", self._pos()) + 1
            self.found.append({**self.open, "e": end})
            self.open = None
        self.depth -= 1


def parse(html: str) -> Composition:
    p = _TopLevel(html)
    p.feed(html)
    clips = []
    for f in p.found:
        start = float(f.get("data-start", 0))
        dur = float(f.get("data-duration", p.duration - start))
        clips.append(Clip(f.get("id") or f"{f['tag']}@{f['s']}", f["tag"], start, start + dur, html[f["s"]:f["e"]]))
    regions = [Region(m.group(1), m.group(0),
                      [tuple(map(float, s.split("-"))) for s in m.group(2).split(",")] if m.group(2) else None)
               for m in MARK.finditer(html)]
    shared = html
    for c in clips:
        shared = shared.replace(c.text, f"<!--clip:{c.id}-->", 1)
    for r in regions:
        shared = shared.replace(r.text, f"/*region:{r.id}*/", 1)
    comp = Composition(p.duration, clips, regions, shared)
    by_id = {c.id: c for c in clips}
    for c in clips:
        comp.deps[c.id] = [(c.start, c.end)]
    for r in regions:
        if r.spans:
            comp.deps["region:" + r.id] = r.spans
        elif r.id in by_id:
            comp.deps["region:" + r.id] = [(by_id[r.id].start, by_id[r.id].end)]
        else:
            comp.deps["region:" + r.id] = []  # global
    return comp


# ── planning ───────────────────────────────────────────────────────────
def frame(t: float, fps: int) -> int:
    return int(round(t * fps))


def assets_digest(ws: Path, html: str) -> str:
    """Hash every workspace file the document references (vendor JS, fonts, images, sub-compositions).

    Files the document never names cannot change its pixels, so outputs or scratch files
    dropped into the workspace do not invalidate the cache. Audio is excluded: narration
    is muxed after rendering.
    """
    h = hashlib.sha256()
    for path in sorted(ws.rglob("*")):
        rel = path.relative_to(ws)
        if (path.is_dir() or rel.parts[0] in SKIP_DIRS or path.name == "index.html"
                or path.suffix.lower() in AUDIO_EXT or rel.as_posix() not in html):
            continue
        h.update(str(rel).encode())
        h.update(hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()


def plan(ws: Path, settings: dict, chunk_min: float) -> dict:
    html = (ws / "index.html").read_text()
    comp = parse(html)
    fps = settings["fps"]
    total = frame(comp.duration, fps)
    visual = [c for c in comp.clips if c.tag not in ("audio",)]
    cuts = {0, total}
    for c in visual:
        cuts |= {min(total, max(0, frame(c.start, fps))), min(total, max(0, frame(c.end, fps)))}
    for spans in comp.deps.values():
        for a, b in spans:
            cuts |= {min(total, max(0, frame(a, fps))), min(total, max(0, frame(min(b, comp.duration), fps)))}
    cuts = sorted(cuts)
    segs = [(a, b) for a, b in zip(cuts, cuts[1:]) if b > a]
    chunks, cur = [], None
    for a, b in segs:
        cur = (a, b) if cur is None else (cur[0], b)
        if (cur[1] - cur[0]) / fps >= chunk_min:
            chunks.append(cur)
            cur = None
    if cur:
        if chunks and (cur[1] - cur[0]) / fps < min(2.0, chunk_min / 2):  # only fold a tiny tail
            chunks[-1] = (chunks[-1][0], cur[1])
        else:
            chunks.append(cur)
    base = hashlib.sha256(json.dumps({"hf": HF_VERSION, **settings}).encode() + comp.shared.encode()
                          + assets_digest(ws, html).encode()).hexdigest()
    texts = {c.id: c.text for c in visual} | {"region:" + r.id: r.text for r in comp.regions}
    out = []
    for a, b in chunks:
        t0, t1 = a / fps, b / fps
        deps = sorted(k for k, spans in comp.deps.items() if k in texts and
                      (not spans or any(s < t1 and e > t0 for s, e in spans)))
        h = hashlib.sha256(f"{base}|{a}|{b}".encode())
        for k in deps:
            h.update(k.encode())
            h.update(texts[k].encode())
        out.append({"start_frame": a, "end_frame": b, "start": round(t0, 4), "end": round(t1, 4),
                    "deps": deps, "key": h.hexdigest()[:24]})
    return {"duration": comp.duration, "fps": fps, "total_frames": total, "settings": settings, "chunks": out}


# ── execution ──────────────────────────────────────────────────────────
def cache_dir(ws: Path) -> Path:
    d = ws / ".render-cache"
    d.mkdir(exist_ok=True)
    return d


def frames_in(path: Path) -> int:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                                   "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(path)])
    return int(out.strip())


def render_chunk(ws: Path, ch: dict, settings: dict, workers: str) -> float:
    dst = cache_dir(ws) / f"{ch['key']}.mp4"
    if dst.exists():
        return 0.0
    tmp = cache_dir(ws) / f"{ch['key']}.tmp.mp4"
    cmd = ["npx", "--yes", f"hyperframes@{HF_VERSION}", "render", str(ws), "-o", str(tmp),
           "--fps", str(settings["fps"]), "--quality", settings["quality"], "--quiet",
           "--start", f"{ch['start']:.4f}", "--end", f"{ch['end']:.4f}", "--workers", workers]
    t = time.time()
    subprocess.run(cmd, check=True, cwd=ws)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(tmp), "-an", "-c", "copy", str(dst)], check=True)
    tmp.unlink(missing_ok=True)
    want, got = ch["end_frame"] - ch["start_frame"], frames_in(dst)
    if got != want:
        dst.unlink()
        raise RuntimeError(f"chunk {ch['key']} has {got} frames, expected {want}")
    return time.time() - t


def run(ws: Path, p: dict, out: Path, audio: Path | None, jobs: int) -> dict:
    todo = [c for c in p["chunks"] if not (cache_dir(ws) / f"{c['key']}.mp4").exists()]
    workers = "auto" if jobs == 1 else str(max(1, (os.cpu_count() or 4) // jobs))
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        secs = list(ex.map(lambda c: render_chunk(ws, c, p["settings"], workers), todo))
    lst = cache_dir(ws) / f"concat-{os.getpid()}.txt"
    lst.write_text("".join(f"file '{(cache_dir(ws) / (c['key'] + '.mp4')).resolve()}'\n" for c in p["chunks"]))
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst)]
    if audio:
        cmd += ["-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "copy", "-t", f"{p['total_frames'] / p['fps']:.4f}", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    lst.unlink()
    got = frames_in(out)
    if got != p["total_frames"]:
        raise RuntimeError(f"assembled {got} frames, expected {p['total_frames']}")
    report = {"rendered_chunks": len(todo), "cached_chunks": len(p["chunks"]) - len(todo),
              "chunk_seconds": [round(s, 1) for s in secs], "wall_seconds": round(time.time() - t0, 1),
              "frames": got, "output": str(out)}
    log = ws / ".render-cache" / "render-log.jsonl"
    with log.open("a") as f:
        f.write(json.dumps({**report, "settings": p["settings"], "time": time.time()}) + "\n")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["plan", "render", "scene"])
    ap.add_argument("workspace", type=Path)
    ap.add_argument("scene_id", nargs="?")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--audio", type=Path, help="narration to mux (default: WORKSPACE/narration.wav if present)")
    ap.add_argument("--preview", action="store_true", help="24 fps draft quality (separate cache keys)")
    ap.add_argument("--chunk-min", type=float, default=15.0, help="minimum chunk length in seconds")
    ap.add_argument("--jobs", type=int, default=1, help="chunks rendered in parallel (split CPU workers)")
    a = ap.parse_args(argv)
    ws = a.workspace.resolve()
    settings = PREVIEW if a.preview else FINAL
    p = plan(ws, settings, a.chunk_min)
    if a.cmd == "scene":
        comp = parse((ws / "index.html").read_text())
        clip = next((c for c in comp.clips if c.id == a.scene_id), None)
        if clip is None:
            sys.exit(f"no top-level clip with id {a.scene_id!r}")
        p["chunks"] = [c for c in p["chunks"] if c["start"] < clip.end and c["end"] > clip.start]
        p["total_frames"] = sum(c["end_frame"] - c["start_frame"] for c in p["chunks"])
    cached = {c["key"] for c in p["chunks"] if (ws / ".render-cache" / f"{c['key']}.mp4").exists()}
    if a.cmd == "plan":
        for c in p["chunks"]:
            mark = "cached" if c["key"] in cached else "RENDER"
            print(f"{c['start']:8.2f}–{c['end']:8.2f}s  {mark:6}  {', '.join(c['deps'])}")
        todo = sum(c["end_frame"] - c["start_frame"] for c in p["chunks"] if c["key"] not in cached)
        print(f"{len(p['chunks'])} chunks, {len(cached)} cached, {todo} frames to render "
              f"({todo / p['fps']:.1f}s of video) at {settings}")
        return
    audio = a.audio or (ws / "narration.wav" if (ws / "narration.wav").exists() and a.cmd == "render" else None)
    print(json.dumps(run(ws, p, a.output, audio, a.jobs), indent=1))


if __name__ == "__main__":
    main()
