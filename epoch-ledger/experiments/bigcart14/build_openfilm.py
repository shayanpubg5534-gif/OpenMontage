"""B — the BRIEF.md shots built as an OpenFilm project (one page per shot with window.film.frame(t), a film.html
timeline, a WebVTT caption track styled with ::cue, narration and sound effects as audio clips). Render with
`openfilm render` from the isolated scratch install. Experimental; nothing here is part of the approved kit.

  python epoch-ledger/experiments/bigcart14/build_openfilm.py OUT_DIR APRIME_WS
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shots as S  # noqa: E402
import build_aprime as A  # noqa: E402

KIT = S.ROOT / "epoch-ledger/kit"


def ts(t: float) -> str:
    h, r = divmod(max(0.0, t), 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def captions_vtt() -> str:
    """Our approved caption look, expressed as WebVTT + ::cue CSS (OpenFilm draws caption tracks natively)."""
    out = ["WEBVTT", "",
           "STYLE",
           "::cue { font-family: Inter, sans-serif; font-weight: 700; font-size: 46px; line-height: 1.4; color: rgba(248,250,252,.6);"
           " background: rgba(20,33,61,.82); padding: 14px 28px; border-radius: 12px; }",
           "::cue(:past) { color: #F8FAFC; }", ""]
    pages = S.V2.caption_pages()
    for i, p in enumerate(pages):
        nxt = pages[i + 1]["start"] if i + 1 < len(pages) else S.D
        words = " ".join(f"<{ts(w['start'])}>{w['word']}" for w in p["words"])
        out += [f"c{i}", f"{ts(p['start'])} --> {ts(min(S.D, nxt, p['end'] + .7))} line:84% position:50% align:center size:80%", words, ""]
    return "\n".join(out)


def page(sid, t0, t1, plate, dim, layers, js, over, shared_css, kit_js, shared_js):
    body = S.V2.shot(sid, plate, layers, over, dim=dim)
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=1920, height=1080">
<link rel="stylesheet" href="shared.css">
<script src="vendor/gsap.min.js"></script><script src="vendor/scene3d.js"></script><script src="vendor/rig3.js"></script><script src="vendor/finmotion.js"></script>
</head><body><div id="root">{body}</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{kit_js}
{shared_js}
{{
{js}
}}
const T0 = {t0};
window.film = {{
  duration: {round(t1 - t0, 3)},
  ready: Promise.all([document.fonts.ready, ...Array.from(document.images).map(i => i.decode().catch(() => {{}}))]),
  frame(t) {{ tl.seek(T0 + t, false); }},
}};
</script></body></html>"""


def build(out: Path, aprime_ws: Path):
    out.mkdir(parents=True, exist_ok=True)
    for d in ("plates", "tex", "fonts"):
        if (out / d).exists():
            shutil.rmtree(out / d)
        shutil.copytree(aprime_ws / d, out / d, ignore=shutil.ignore_patterns("*.html", "scene3d.js"))
    (out / "vendor").mkdir(exist_ok=True)
    for f in ("gsap.min.js", "scene3d.js", "rig3.js", "finmotion.js"):
        shutil.copy(aprime_ws / "vendor" / f, out / "vendor" / f)
    for f in ("narration.wav", "sfx.wav"):
        shutil.copy(aprime_ws / f, out / "assets" / f) if (out / "assets").exists() else ((out / "assets").mkdir(), shutil.copy(aprime_ws / f, out / "assets" / f))
    theme = (KIT / "theme.css").read_text()
    (out / "shared.css").write_text(theme + "\nhtml,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#000}#root{position:relative;width:1920px;height:1080px;overflow:hidden}"
                                    + "#root>.shot{position:absolute;inset:0}\n" + A.CSS)
    kit_js = "\n".join((KIT / f).read_text() for f in ("helpers.js", "rig.js", "motion.js"))
    shared_js = A.shared_js()
    P = {k: v for k, v in ((p.stem.rsplit("-", 1)[0], "plates/" + p.name) for p in (out / "plates").glob("*.png"))}
    clips = []
    for i, (sid, pl, dim, fn) in enumerate(S.shots()):
        t0, t1 = S.CUT[i], S.CUT[i + 1]
        layers, js, over = fn()
        (out / f"{sid}.html").write_text(page(sid, t0, t1, P.get(pl) if pl else None, dim, layers, js, over, "shared.css", kit_js, shared_js))
        clips.append(f'  <iframe id="{sid}" src="{sid}.html#t=0,{round(t1 - t0, 3)}" at="{t0}"></iframe>')
    (out / "captions.vtt").write_text(captions_vtt())
    (out / "film.html").write_text(f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1920, height=1080">
<title>BigCart 14 — B (OpenFilm)</title>
</head>
<body>
<section>
  <track kind="captions" src="captions.vtt" srclang="en" label="English">
</section>
<section>
{chr(10).join(clips)}
</section>
<section>
  <audio id="vo" src="assets/narration.wav#t=0,{S.D}"></audio>
</section>
<section>
  <audio id="fx" src="assets/sfx.wav#t=0,{S.D}"></audio>
</section>
</body>
</html>
""")
    print("wrote", out / "film.html")


if __name__ == "__main__":
    build(Path(sys.argv[1]), Path(sys.argv[2]))
