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

Output size follows the composition's root data-width/data-height (1920x1080 by default; an
episode built with kit.assemble(resolution="1440p") renders 2560x1440). HyperFrames' own
--resolution upscale is not used: 1080p→1440p is a non-integer scale it rejects.
  render.py scene   WORKSPACE SCENE_ID -o OUT.mp4 [--preview]   # one scene, cached

Before rendering, stale HyperFrames render locks (dead pid) are removed and an orphaned HyperFrames render of
this workspace (its parent died) is stopped (--keep-orphans only reports it). Each chunk runs in its own process
group under a watchdog (EPOCH_RENDER_TIMEOUT_BASE + _PER_FRAME seconds) and is killed with render.py on SIGTERM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
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
def render_command(ws: Path, out: Path, settings: dict, start: float, end: float, workers: str) -> list[str]:
    cmd = ["npx", "--yes", f"hyperframes@{HF_VERSION}", "render", str(ws), "-o", str(out),
           "--fps", str(settings["fps"]), "--quality", settings["quality"], "--quiet",
           "--start", f"{start:.4f}", "--end", f"{end:.4f}", "--workers", workers]
    return cmd
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
TEXT_EXT = {".css", ".js", ".mjs", ".html", ".svg", ".json"}
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
    size: tuple[int, int] = (1920, 1080)
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
        self.size = (1920, 1080)
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
            self.size = (int(a.get("data-width", 1920)), int(a.get("data-height", 1080)))
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
    comp = Composition(p.duration, clips, regions, shared, p.size)
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

    References are followed through referenced text files too (a CSS url(), a sub-composition's image, a path
    written inside a vendor script), so changing any of them invalidates the cache. Files nobody names cannot
    change pixels, so outputs or scratch files dropped into the workspace do not invalidate the cache. Audio is
    excluded: narration is muxed after rendering.
    """
    files = {}
    for path in sorted(ws.rglob("*")):
        rel = path.relative_to(ws)
        if path.is_dir() or rel.parts[0] in SKIP_DIRS or path.name == "index.html" or path.suffix.lower() in AUDIO_EXT:
            continue
        files[rel.as_posix()] = path
    # (folder, text) of every referencing document; a reference resolves against the referrer's folder
    corpus, used, frontier = [("", html)], set(), True
    while frontier:                                   # fixpoint over references (usually 1–2 rounds)
        frontier = False
        for rel, path in files.items():
            if rel in used:
                continue
            folder, _, name = rel.rpartition("/")
            if any((rel if not f else rel[len(f) + 1:] if rel.startswith(f + "/") else None) in t
                   for f, t in corpus if (not f or rel.startswith(f + "/"))) or any(rel in t for _, t in corpus):
                used.add(rel)
                frontier = True
                if path.suffix.lower() in TEXT_EXT and path.stat().st_size < 8 << 20:
                    corpus.append((folder, path.read_text(errors="replace")))
    h = hashlib.sha256()
    for rel in sorted(used):
        h.update(rel.encode())
        h.update(hashlib.sha256(files[rel].read_bytes()).digest())
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
    return {"duration": comp.duration, "fps": fps, "total_frames": total, "settings": settings,
            "width": comp.size[0], "height": comp.size[1], "chunks": out}



# ── render lock & hung-process guard ───────────────────────────────────
# HyperFrames serialises renders with ~/.cache/hyperframes/locks/render.lock ({"pid", "project"}) and waits while
# it is held. A render whose parent was killed can leave an orphaned hyperframes process (parent = init) holding the
# lock forever, so the next render waits silently. Before rendering we remove locks held by dead processes, stop
# orphaned HyperFrames renders of *this* workspace, and warn about anything else still holding the lock. Each chunk
# runs in its own process group with a watchdog timeout, and the group is killed on timeout or interruption.
LOCK_DIR = Path(os.environ.get("EPOCH_HF_LOCK_DIR", Path.home() / ".cache" / "hyperframes" / "locks"))
CHUNK_TIMEOUT_BASE = float(os.environ.get("EPOCH_RENDER_TIMEOUT_BASE", 300))     # seconds, plus per frame:
CHUNK_TIMEOUT_PER_FRAME = float(os.environ.get("EPOCH_RENDER_TIMEOUT_PER_FRAME", 3.0))
_CHILDREN: set = set()


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:                                              # a zombie is dead for our purposes
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return True


def _proc(pid: int) -> tuple[int, str] | None:
    """(parent pid, command line) from /proc, or None where /proc is unavailable."""
    try:
        ppid = int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[1])
        cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        return ppid, cmd
    except (OSError, ValueError, IndexError):
        return None


def _terminate(pid: int, grace: float = 5.0) -> None:
    for sig in (15, 9):
        try:
            pg = os.getpgid(pid)
            os.killpg(pg, sig) if sig == 9 and pg != os.getpgrp() else os.kill(pid, sig)
        except (ProcessLookupError, PermissionError):
            return
        end = time.time() + grace
        while time.time() < end and _alive(pid):
            time.sleep(.1)
        if not _alive(pid):
            return


def preflight_lock(ws: Path, kill_orphans: bool = True, lock_dir: Path | None = None) -> list[str]:
    """Clear stale HyperFrames render locks; returns notes describing what was found or done."""
    lock_dir = lock_dir or LOCK_DIR
    notes: list[str] = []
    if not lock_dir.is_dir():
        return notes
    for owner in lock_dir.glob("render.lock.owner-*"):           # render.lock.owner-<pid>-<hash>
        try:
            pid = int(owner.name.split("owner-", 1)[1].split("-", 1)[0])
        except ValueError:
            continue
        if not _alive(pid):
            owner.unlink(missing_ok=True)
            notes.append(f"removed stale lock owner file of dead pid {pid}")
    lock = lock_dir / "render.lock"
    if not lock.exists():
        return notes
    try:
        info = json.loads(lock.read_text() or "{}")
        pid, project = int(info.get("pid", 0)), str(info.get("project", ""))
    except (ValueError, OSError):
        pid, project = 0, ""
    if not pid or not _alive(pid):
        lock.unlink(missing_ok=True)
        notes.append(f"removed stale render.lock (pid {pid or '?'} is not running)")
        return notes
    proc = _proc(pid)
    ours = project and Path(project).resolve() == ws.resolve()
    if proc and proc[0] == 1 and "hyperframes" in proc[1] and ours and kill_orphans:
        _terminate(pid)
        if not _alive(pid):
            lock.unlink(missing_ok=True)
            for owner in lock_dir.glob(f"render.lock.owner-{pid}-*"):
                owner.unlink(missing_ok=True)
            notes.append(f"stopped orphaned HyperFrames render pid {pid} of this workspace and released its lock")
            return notes
    notes.append(f"render.lock is held by running pid {pid} ({project or 'unknown project'}); this render will wait for it"
                 + (" — it looks orphaned (parent is init); stop it if nothing should be rendering" if proc and proc[0] == 1 else ""))
    return notes


def _run_guarded(cmd: list[str], cwd: Path, timeout: float) -> int:
    """Run in a new process group; kill the whole group on timeout. Returns exit code (124 on timeout)."""
    pr = subprocess.Popen(cmd, cwd=cwd, start_new_session=True)
    _CHILDREN.add(pr)
    try:
        return pr.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"render step exceeded {timeout:.0f}s watchdog; stopping it", file=sys.stderr)
        _kill_group(pr)
        return 124
    except BaseException:
        _kill_group(pr)
        raise
    finally:
        _CHILDREN.discard(pr)


def _kill_group(pr) -> None:
    try:
        os.killpg(pr.pid, 15)
        try:
            pr.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(pr.pid, 9)
            pr.wait(timeout=5)
    except (ProcessLookupError, PermissionError):
        pass


def _on_signal(signum, _frame):                      # SIGTERM / SIGHUP: take our renders down with us
    for pr in list(_CHILDREN):
        _kill_group(pr)
    sys.exit(128 + signum)

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
    cmd = render_command(ws, tmp, settings, ch["start"], ch["end"], workers)
    t = time.time()
    timeout = CHUNK_TIMEOUT_BASE + CHUNK_TIMEOUT_PER_FRAME * (ch["end_frame"] - ch["start_frame"])
    for attempt in (1, 2):  # HyperFrames occasionally exits non-zero after a good capture; retry once
        code = _run_guarded(cmd, ws, timeout)
        if code == 0:
            break
        if code == 124:                               # hung: clear whatever lock it left before retrying
            for n in preflight_lock(ws):
                print("render lock:", n, file=sys.stderr)
        if attempt == 2:
            raise subprocess.CalledProcessError(code, cmd)
        print(f"chunk {ch['key']} failed (exit {code}); retrying once", file=sys.stderr)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(tmp), "-an", "-c", "copy", str(dst)], check=True)
    tmp.unlink(missing_ok=True)
    want, got = ch["end_frame"] - ch["start_frame"], frames_in(dst)
    if got != want:
        dst.unlink()
        raise RuntimeError(f"chunk {ch['key']} has {got} frames, expected {want}")
    return time.time() - t


def run(ws: Path, p: dict, out: Path, audio: Path | None, jobs: int, kill_orphans: bool = True) -> dict:
    todo = [c for c in p["chunks"] if not (cache_dir(ws) / f"{c['key']}.mp4").exists()]
    if todo:
        for n in preflight_lock(ws, kill_orphans):
            print("render lock:", n, file=sys.stderr)
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
    want_size = (p["width"], p["height"])
    size = tuple(int(v) for v in subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(out)]).decode().strip().split(","))
    if size != want_size:
        raise RuntimeError(f"assembled {size[0]}x{size[1]}, expected {want_size[0]}x{want_size[1]}")
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
    ap.add_argument("cmd", choices=["plan", "render", "scene", "range"])
    ap.add_argument("workspace", type=Path)
    ap.add_argument("scene_id", nargs="?")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--audio", type=Path, help="narration to mux (default: WORKSPACE/narration.wav if present)")
    ap.add_argument("--preview", action="store_true", help="24 fps draft quality (separate cache keys)")
    ap.add_argument("--chunk-min", type=float, default=15.0, help="minimum chunk length in seconds")
    ap.add_argument("--jobs", type=int, default=1, help="chunks rendered in parallel (split CPU workers)")
    ap.add_argument("--start", type=float, help="range: window start (s)")
    ap.add_argument("--end", type=float, help="range: window end (s)")
    ap.add_argument("--fps", type=int, help="override fps (24/25/30/60)")
    ap.add_argument("--quality", choices=["draft", "looks", "delivery"], help="override quality")
    ap.add_argument("--keep-orphans", action="store_true", help="only report orphaned HyperFrames renders, do not stop them")
    a = ap.parse_args(argv)
    for sig in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, _on_signal)
    ws = a.workspace.resolve()
    settings = dict(PREVIEW if a.preview else FINAL)
    if a.fps:
        settings["fps"] = a.fps
    if a.quality:
        settings["quality"] = a.quality
    p = plan(ws, settings, a.chunk_min)
    if a.cmd == "range":
        if a.start is None or a.end is None or not a.output:
            sys.exit("range needs --start, --end and -o")
        p["chunks"] = [c for c in p["chunks"] if c["start"] < a.end and c["end"] > a.start]
        p["total_frames"] = sum(c["end_frame"] - c["start_frame"] for c in p["chunks"])
        audio = a.audio or next((ws / f for f in ("mix.wav", "narration.wav") if (ws / f).exists()), None)
        tmp = a.output.with_suffix(".chunks.mp4")
        rep = run(ws, p, tmp, None, a.jobs, not a.keep_orphans)
        off = a.start - p["chunks"][0]["start"]
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{off:.3f}", "-t", f"{a.end - a.start:.3f}", "-i", str(tmp)]
        if audio:
            cmd += ["-ss", f"{a.start:.3f}", "-t", f"{a.end - a.start:.3f}", "-i", str(audio), "-map", "0:v", "-map", "1:a",
                    "-c:a", "aac", "-b:a", "160k"]
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(a.output)]
        subprocess.run(cmd, check=True)
        tmp.unlink(missing_ok=True)
        rep["output"] = str(a.output)
        print(json.dumps(rep, indent=1))
        return
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
    print(json.dumps(run(ws, p, a.output, audio, a.jobs, not a.keep_orphans), indent=1))


if __name__ == "__main__":
    main()
