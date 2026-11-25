"""Stage 4 benchmark: full-document chunks vs per-shot isolated documents (HyperFrames, same settings).

  python bench.py WORKSPACE OUT_DIR {full,shots,isolated,isolated-par} [WORKERS]
Experimental; not wired into scripts/render.py."""
import importlib.util, json, os, shutil, subprocess, sys, time
from pathlib import Path
spec = importlib.util.spec_from_file_location("el_render", "/home/user/OpenMontage/epoch-ledger/scripts/render.py")
R = importlib.util.module_from_spec(spec); sys.modules["el_render"] = R; spec.loader.exec_module(R)

WS = Path(sys.argv[1]).resolve(); OUT = Path(sys.argv[2]).resolve(); MODE = sys.argv[3]; WORKERS = sys.argv[4] if len(sys.argv) > 4 else "2"
OUT.mkdir(parents=True, exist_ok=True)
html = (WS / "index.html").read_text(); comp = R.parse(html); fps = 30

def shot_chunks():
    shots = sorted({c.start for c in comp.clips if c.tag != "audio" and not c.id.startswith("cap")} | {comp.duration})
    return [(R.frame(a, fps), R.frame(b, fps)) for a, b in zip(shots, shots[1:]) if R.frame(b, fps) > R.frame(a, fps)]

def isolated_doc(t0, t1):
    doc = html
    for c in comp.clips:
        if c.tag == "audio" or not (c.start < t1 and c.end > t0):
            doc = doc.replace(c.text, "", 1)
    for r in comp.regions:
        spans = comp.deps.get("region:" + r.id)
        if spans and not any(s < t1 and e > t0 for s, e in spans):
            doc = doc.replace(r.text, "", 1)
    return doc

def ws_for(t0, t1, tag):
    d = OUT / f"iso-{tag}"; shutil.rmtree(d, ignore_errors=True); d.mkdir()
    for e in WS.iterdir():
        if e.name in ("index.html", ".render-cache", ".hyperframes") or e.suffix == ".mp4":
            continue
        subprocess.run(["cp", "-al", str(e), str(d / e.name)], check=True)     # hard links: served like real files
    (d / "index.html").write_text(isolated_doc(t0, t1))
    return d

chunks = [(0, R.frame(comp.duration, fps))] if MODE.startswith("full") else shot_chunks()
PAR = 2 if MODE.endswith("-par") else 1
env = dict(os.environ, **({"HYPERFRAMES_RENDER_LOCK": "off"} if PAR > 1 else {}))
def one(i):
    a, b = chunks[i]; t0, t1 = a / fps, b / fps
    ws = ws_for(t0, t1, i) if MODE.startswith("isolated") else WS
    out = OUT / f"{MODE}-{i}.mp4"
    cmd = R.render_command(ws, out, R.FINAL, t0, t1, WORKERS)
    t = time.time(); r = subprocess.run(cmd, cwd=ws, capture_output=True, text=True, env=env)
    if r.returncode: raise RuntimeError(r.stdout[-1500:] + r.stderr[-1500:])
    return {"chunk": i, "start": t0, "end": t1, "frames": b - a, "seconds": round(time.time() - t, 1),
            "doc_kb": round(len((ws / 'index.html').read_text()) / 1024), "got": R.frames_in(out)}
from concurrent.futures import ThreadPoolExecutor
t_all = time.time()
order = sorted(range(len(chunks)), key=lambda i: -(chunks[i][1] - chunks[i][0]))      # longest first
with ThreadPoolExecutor(PAR) as ex:
    parts = sorted(ex.map(one, order), key=lambda p: p["chunk"])
lst = OUT / f"{MODE}.txt"; lst.write_text("".join("file '%s'\n" % (OUT / ("%s-%d.mp4" % (MODE, p["chunk"]))) for p in parts))
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-an", "-c", "copy", str(OUT / f"{MODE}.mp4")], check=True)
print(json.dumps({"mode": MODE, "workers": WORKERS, "wall": round(time.time() - t_all, 1), "frames": sum(p["frames"] for p in parts), "chunks": parts}, indent=1))
