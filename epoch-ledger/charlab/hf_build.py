#!/usr/bin/env python3
"""Character lab (M4.2): build a HyperFrames workspace for a 3D shot (lab only; production untouched).

    python3 epoch-ledger/charlab/hf_build.py SHOT.json CHARS_DIR WORKSPACE --quality standard|balanced|lean \
        [--narration EPISODE_DIR] [--vendor-from projects/profitable-and-broke/hyperframes]

The composition is made by the production assembler (kit/assemble.py, used read-only): a canvas clip for the 3D layer,
a GSAP driver tween in a js_region spanning the shot (each timeline seek draws exactly that frame), the readiness gate
(ready_gate=["el3d"]: the timeline registers only after characters, set and textures are loaded, compiled and drawn),
gold captions from the narration's caption phrases, and the narration audio. Every runtime asset is copied into the
workspace and named literally in the document, so render.py's cache keys and isolated chunk workspaces include them.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "epoch-ledger"))
from kit.assemble import assemble, prepare_workspace  # noqa: E402


def bundle(dst: Path) -> None:
    nm = REPO / ".runtime/charlab/bundle/node_modules"
    env = {**os.environ, "NODE_PATH": str(nm)}
    subprocess.run(["npx", "--yes", "esbuild@0.25.0", str(HERE / "motion/hf_entry.js"), "--bundle", "--format=esm", "--minify",
                    f"--outfile={dst}"], check=True, env=env, cwd=str(nm.parent))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("shot", type=Path); ap.add_argument("chars", type=Path); ap.add_argument("ws", type=Path)
    ap.add_argument("--quality", default="balanced", choices=["standard", "balanced", "lean"])
    ap.add_argument("--narration", type=Path, help="episode dir with artifacts/caption_phrases.json (narration.wav must be in WS or EPISODE/../hf)")
    ap.add_argument("--vendor-from", type=Path, default=REPO / "projects/profitable-and-broke/hyperframes")
    a = ap.parse_args(argv)
    ws = a.ws.resolve(); ws.mkdir(parents=True, exist_ok=True)
    for d in ("vendor", "fonts"):
        if (a.vendor_from / d).exists():
            shutil.copytree(a.vendor_from / d, ws / d, dirs_exist_ok=True)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(a.vendor_from / f, ws / f)
    prepare_workspace(ws)
    bundle(ws / "el3d.js")
    shot = json.loads(a.shot.read_text())
    assets = ["el3d.js", "shot.json"]
    # set and plate: copied in, paths made workspace-relative
    plates = ws / "plates"; plates.mkdir(exist_ok=True)
    def local_plate(url):
        src = REPO / url.lstrip("/"); dst = plates / src.name; shutil.copy(src, dst); assets.append(f"plates/{src.name}"); return f"plates/{src.name}"
    from_env = {"bank": "/projects/profitable-and-broke/hyperframes/plates/bank-bg-b758bcbed821.png",
                "bakery": "/projects/profitable-and-broke/hyperframes/plates/shop-bg-6302a081a386.png"}
    shot["plate"] = local_plate(from_env[shot.get("env", "bank")])
    if shot.get("set"):
        st = json.loads((REPO / shot["set"].lstrip("/")).read_text())
        if st.get("window", {}).get("backdrop"):
            st["window"]["backdrop"]["image"] = local_plate(st["window"]["backdrop"]["image"])
        for it in st.get("items", []):
            if it.get("image"):
                it["image"] = local_plate(it["image"])
        (ws / "set.json").write_text(json.dumps(st)); shot["set"] = "set.json"; assets.append("set.json")
    (ws / "shot.json").write_text(json.dumps(shot))
    # characters: GLB, texture treatments and the flat textures the stage loads
    for cid in shot["actors"]:
        (ws / "chars" / f"{cid}_tex").mkdir(parents=True, exist_ok=True)
        shutil.copy(a.chars / f"{cid}.glb", ws / "chars" / f"{cid}.glb"); assets.append(f"chars/{cid}.glb")
        tr = json.loads((a.chars / f"{cid}_tex/treatments.json").read_text())
        shutil.copy(a.chars / f"{cid}_tex/treatments.json", ws / "chars" / f"{cid}_tex/treatments.json"); assets.append(f"chars/{cid}_tex/treatments.json")
        for e in tr.values():
            if e.get("flat"):
                shutil.copy(a.chars / f"{cid}_tex" / e["flat"], ws / "chars" / f"{cid}_tex" / e["flat"]); assets.append(f"chars/{cid}_tex/{e['flat']}")
    D = float(shot["duration"])
    layer = f"""<canvas id="el3d" class="clip" data-start="0" data-duration="{D}" data-track-index="0" width="1920" height="1080" style="position:absolute;inset:0;width:100%;height:100%"></canvas>
<script type="module">
import {{ loadShot, QUALITY }} from './el3d.js';
// runtime assets, named literally for render.py's dependency scan: {json.dumps(assets)}
try {{
  const demo = await (await fetch('shot.json')).json();
  const SH = await loadShot({{ demo, OUT: 'chars', canvas: document.getElementById('el3d') }});
  const Q = QUALITY[{json.dumps(a.quality)}];
  window.__el3dDraw = t => SH.frame(t, Q);
  SH.frame(0, Q);
  window.__el3dInfo = {{ load: SH.loadMs, compile: SH.compileMs }};
  if (window.__elReady) window.__elReady('el3d'); else (window.__elPending = window.__elPending || []).push('el3d');
}} catch (e) {{ if (window.__elFail) window.__elFail('el3d', String(e && e.stack || e)); else throw e; }}
</script>"""
    driver = (f"const E3 = {{ t: 0 }};\n"
              f"tl.to(E3, {{ t: {D}, duration: {D}, ease: 'none', onUpdate: () => window.__el3dDraw && window.__el3dDraw(E3.t) }}, 0);")
    pages = json.loads((a.narration / "artifacts/caption_phrases.json").read_text()) if a.narration else None
    html = assemble(title=f"M4 3D shot ({a.quality})", duration=D, scenes=[], layers=[layer], caption_pages=pages,
                    js_regions=[("el3d", [(0, D)], driver)], ready_gate=["el3d"], audio="narration.wav" if pages else "")
    (ws / "index.html").write_text(html)
    if a.narration:
        for cand in (a.narration.parent / "hf/narration.wav", a.narration / "narration.wav"):
            if cand.exists() and cand.resolve() != (ws / "narration.wav").resolve():
                shutil.copy(cand, ws / "narration.wav"); break
    print(json.dumps({"workspace": str(ws), "quality": a.quality, "duration": D, "assets": len(assets)}))


if __name__ == "__main__":
    main()
