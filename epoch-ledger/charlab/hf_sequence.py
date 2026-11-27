#!/usr/bin/env python3
"""Character lab (M5): build a HyperFrames workspace for a narration-driven sequence (lab only; production untouched).

    python3 epoch-ledger/charlab/hf_sequence.py SEQUENCE.py CHARS_DIR WORKSPACE [--quality balanced] [--close standard]

A sequence module defines DURATION, EPISODE (a narrate.py episode dir, after splice_dialogue.py), SHOTS (3D shots:
{"id", "demo", "start", "quality"?}) and scenes(T) → list[kit.assemble.Scene] (2D storytelling: documents, diagrams,
timelines), where T is the episode's timeline.json (beat and word times), so every visual is keyed to what the narrator
says. Each 3D shot is its own canvas layer with its own loadShot (characters, set, compiled performance), visible in its
window and drawn by a driver tween in a js_region spanning that window (render.py caches each window separately); all of
them are behind the readiness gate. Assets are copied in and named literally (render.py's dependency scan).
Extends M4.2's hf_build.py (single shot), which is unchanged.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "epoch-ledger")); sys.path.insert(0, str(HERE))
from kit.assemble import assemble, prepare_workspace  # noqa: E402
from hf_build import bundle  # noqa: E402

PLATES = {"bank": "/projects/profitable-and-broke/hyperframes/plates/bank-bg-b758bcbed821.png",
          "bakery": "/projects/profitable-and-broke/hyperframes/plates/shop-bg-6302a081a386.png"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sequence", type=Path); ap.add_argument("chars", type=Path); ap.add_argument("ws", type=Path)
    ap.add_argument("--quality", default="balanced", choices=["standard", "balanced", "msaa2", "lean", "cin_fast", "cin_balanced", "cin_cinematic"],
                    help="preset for shots that do not name their own")
    ap.add_argument("--force-quality", help="override every shot's preset (e.g. lean for drafts)")
    ap.add_argument("--vendor-from", type=Path, default=REPO / "projects/profitable-and-broke/hyperframes")
    ap.add_argument("--prerender", action="store_true",
                    help="P5 (opt-in): render each 3D shot in one continuous browser session (shot_render.mjs, cached by "
                         "fingerprint) and composite it as a video layer; default: the M4.2 live canvas path")
    ap.add_argument("--three", default=".runtime/charlab/three/r0.186.1", help="three.js package dir for --prerender")
    ap.add_argument("--shot-cache", default=str(REPO / ".runtime/charlab/shotcache"))
    a = ap.parse_args(argv)
    spec = importlib.util.spec_from_file_location("seq", a.sequence); seq = importlib.util.module_from_spec(spec); spec.loader.exec_module(seq)
    ws = a.ws.resolve(); ws.mkdir(parents=True, exist_ok=True)
    for d in ("vendor", "fonts"):
        if (a.vendor_from / d).exists():
            shutil.copytree(a.vendor_from / d, ws / d, dirs_exist_ok=True)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(a.vendor_from / f, ws / f)
    prepare_workspace(ws)
    bundle(ws / "el3d.js")
    assets = ["el3d.js"]
    (ws / "shot").mkdir(exist_ok=True); (ws / "plates").mkdir(exist_ok=True)

    def local(url, sub="plates"):
        src = REPO / url.lstrip("/"); dst = ws / sub / src.name
        if src.name == "visemes.json": dst = ws / sub / f"{src.parent.name}_visemes.json"
        shutil.copy(src, dst); rel = f"{sub}/{dst.name}"
        if rel not in assets: assets.append(rel)
        return rel
    layers, regions, gate, chars = [], [], [], set()
    shot_timings = {}
    for k, S in enumerate(seq.SHOTS):
        sid = S["id"]; shot = json.loads((REPO / S["demo"]).read_text())
        if a.prerender:   # P5: one continuous session per shot → a cached mp4 → a muted, timed <video> clip
            import subprocess
            q = a.force_quality or S.get("quality", a.quality)
            if q in ("standard", "balanced", "msaa2", "lean") and shot.get("look") == "cinematic": q = "cin_" + ("cinematic" if q == "standard" else "balanced")
            r = subprocess.run(["node", str(HERE / "shot_render.mjs"), "--demo", S["demo"], "--chars", str(a.chars), "--three", a.three,
                                "--quality", q, "--cache", a.shot_cache], cwd=str(REPO), capture_output=True, text=True)
            if r.returncode != 0: raise SystemExit(f"shot_render failed for {sid}:\n{r.stderr[-2000:]}")
            res = json.loads(r.stdout.strip().splitlines()[-1]); shot_timings[sid] = res
            (ws / "shots").mkdir(exist_ok=True); name = f"shots/{sid}_{res['fingerprint'][:12]}.mp4"
            shutil.copy(res["mp4"], ws / name); assets.append(name)
            D, t0 = float(shot["duration"]), float(S["start"])
            layers.append(f'<video id="v_{sid}" class="clip" src="{name}" data-start="{t0}" data-duration="{D}" data-track-index="{k}" muted playsinline '
                          f'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"></video>')
            continue
        shot["plate"] = local(PLATES[shot.get("env", "bank")])
        if shot.get("set"):
            st = json.loads((REPO / shot["set"].lstrip("/")).read_text())
            if st.get("window", {}).get("backdrop"):
                st["window"]["backdrop"]["image"] = local(st["window"]["backdrop"]["image"])
            for it in st.get("items", []):
                if it.get("image"): it["image"] = local(it["image"])
            cin = st.get("cinematic")
            if cin and shot.get("look") == "cinematic":   # P3: the texture sets the cinematic look uses, copied in by name
                tdir = REPO / cin.get("textures", "/.runtime/charlab/textures").lstrip("/")
                for setname in sorted({r["set"] for r in cin.get("materials", {}).values() if r.get("set")}):
                    for f in sorted((tdir / setname).glob("*.jpg")):
                        (ws / "tex" / setname).mkdir(parents=True, exist_ok=True); shutil.copy(f, ws / "tex" / setname / f.name)
                        if f"tex/{setname}/{f.name}" not in assets: assets.append(f"tex/{setname}/{f.name}")
                cin["textures"] = "tex"
            (ws / f"shot/{sid}_set.json").write_text(json.dumps(st)); shot["set"] = f"shot/{sid}_set.json"; assets.append(f"shot/{sid}_set.json")
        for act in shot["actors"].values():
            for sp in act.get("speech", []):
                if sp.get("src"): sp["src"] = local(sp["src"], "shot")
        (ws / f"shot/{sid}.json").write_text(json.dumps(shot)); assets.append(f"shot/{sid}.json")
        chars.update(shot["actors"])
        D, t0 = float(shot["duration"]), float(S["start"])
        q = a.force_quality or S.get("quality", a.quality)
        name = f"el3d_{sid}"; gate.append(name)
        layers.append(f"""<canvas id="{name}" class="clip" data-start="{t0}" data-duration="{D}" data-track-index="{k}" width="1920" height="1080" style="position:absolute;inset:0;width:100%;height:100%"></canvas>
<script type="module">
import {{ loadShot, QUALITY }} from './el3d.js';
try {{
  const demo = await (await fetch('shot/{sid}.json')).json();
  const SH = await loadShot({{ demo, OUT: 'chars', canvas: document.getElementById('{name}') }});
  const Q = QUALITY[{json.dumps(q)}];
  (window.__el3dDraw = window.__el3dDraw || {{}})['{sid}'] = (t, q) => SH.frame(t, q ? QUALITY[q] : Q);
  SH.frame(0, Q);
  (window.__el3dInfo = window.__el3dInfo || {{}})['{sid}'] = {{ load: SH.loadMs, compile: SH.compileMs, quality: {json.dumps(q)} }};
  if (window.__elReady) window.__elReady('{name}'); else (window.__elPending = window.__elPending || []).push('{name}');
}} catch (e) {{ if (window.__elFail) window.__elFail('{name}', String(e && e.stack || e)); else throw e; }}
</script>""")
        # windows: split a shot at its cuts so each part is its own cached chunk (rendered in parallel), each with its
        # own preset (e.g. Standard for a lip-sync close-up, Balanced for the wide that follows)
        wins = S.get("windows") or [{"to": D}]
        a0 = 0.0
        for j, w in enumerate(wins):
            a1 = min(D, float(w["to"])); wq = a.force_quality or w.get("quality", q); rid = f"{name}_w{j}" if len(wins) > 1 else name
            regions.append((rid, [(t0 + a0, t0 + a1)],
                            f"const E_{sid}_{j} = {{ t: {a0} }};\n"
                            f"tl.fromTo(E_{sid}_{j}, {{ t: {a0} }}, {{ t: {a1}, duration: {a1 - a0:.4f}, ease: 'none', immediateRender: false, "
                            f"onUpdate: () => window.__el3dDraw && window.__el3dDraw['{sid}'] && window.__el3dDraw['{sid}'](E_{sid}_{j}.t, {json.dumps(wq)}) }}, {t0 + a0});"))
            a0 = a1
    for cid in sorted(chars):   # live-canvas shots only (prerendered shots carry no runtime assets)
        (ws / "chars" / f"{cid}_tex").mkdir(parents=True, exist_ok=True)
        shutil.copy(a.chars / f"{cid}.glb", ws / "chars" / f"{cid}.glb"); assets.append(f"chars/{cid}.glb")
        if not (a.chars / f"{cid}_tex/treatments.json").exists(): continue   # converted (pbr) characters carry their own materials
        tr = json.loads((a.chars / f"{cid}_tex/treatments.json").read_text())
        shutil.copy(a.chars / f"{cid}_tex/treatments.json", ws / "chars" / f"{cid}_tex/treatments.json"); assets.append(f"chars/{cid}_tex/treatments.json")
        for e in tr.values():
            if e.get("flat"):
                shutil.copy(a.chars / f"{cid}_tex" / e["flat"], ws / "chars" / f"{cid}_tex" / e["flat"]); assets.append(f"chars/{cid}_tex/{e['flat']}")
    if "<script type=\"module\">" in layers[0]:
        layers[0] = layers[0].replace("<script type=\"module\">", f"<script type=\"module\">\n// runtime assets, named literally for render.py's dependency scan: {json.dumps(assets)}", 1)
    ep = REPO / seq.EPISODE
    T = json.loads((ep / "artifacts/timeline.json").read_text())
    pages = json.loads((ep / "artifacts/caption_phrases.json").read_text())
    html = assemble(title=getattr(seq, "TITLE", "M5 sequence"), duration=seq.DURATION, scenes=seq.scenes(T), layers=layers,
                    caption_pages=pages, js_regions=regions or None, ready_gate=gate or None, ready_timeout=40.0,
                    extra_css=getattr(seq, "CSS", ""), audio="narration.wav")
    (ws / "index.html").write_text(html)
    src = REPO / seq.NARRATION_WAV
    if src.resolve() != (ws / "narration.wav").resolve(): shutil.copy(src, ws / "narration.wav")
    print(json.dumps({"workspace": str(ws), "duration": seq.DURATION, "regions": [(r[0], r[1]) for r in regions], "assets": len(assets),
                      "prerendered": shot_timings}))


if __name__ == "__main__":
    main()
