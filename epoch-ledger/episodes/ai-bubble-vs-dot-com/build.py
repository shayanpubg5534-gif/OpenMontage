"""Episode builder: Is the AI Bubble Bigger Than the Dot-Com Bubble? (Epoch Ledger).

  python epoch-ledger/scripts/narrate.py epoch-ledger/episodes/ai-bubble-vs-dot-com     # narration + timings first
  python epoch-ledger/episodes/ai-bubble-vs-dot-com/build.py                          # → projects/ai-bubble-vs-dot-com/hyperframes/index.html
  EPOCH_RESOLUTION=1440p python epoch-ledger/episodes/ai-bubble-vs-dot-com/build.py WS  # optional 2560x1440 build

Every scene is a kit.assemble.Scene with its own html/css/js so render.py can cache it.
Key every animation to narration times (`line(id)`) or Whisper word times (`word(...)`),
never to hand-typed seconds.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT_ROOT = HERE.parents[1]
sys.path.insert(0, str(KIT_ROOT))

from kit.assemble import Scene, assemble, prepare_workspace  # noqa: E402
from kit.characters import maya_svg  # noqa: E402
from kit.sets import bank_street, street_foreground  # noqa: E402

WORKSPACE = Path(sys.argv[1]) if len(sys.argv) > 1 else KIT_ROOT.parent / "projects" / "ai-bubble-vs-dot-com" / "hyperframes"
ART = HERE / "artifacts"
timing = json.loads((ART / "narration_timing.json").read_text())
words = json.loads((ART / "words.json").read_text())
pages = json.loads((ART / "caption_phrases.json").read_text())
D = timing["total"]
LINES = {s["id"]: s for s in timing["segments"]}


def line(i):
    """(start, end) of a narration line by id."""
    return LINES[i]["start"], LINES[i]["end"]


def word(text, after=0.0):
    """Start time of the first Whisper word matching `text` at or after `after` seconds."""
    t = text.lower().strip(".,!?")
    return next(w["start"] for w in words if w["start"] >= after and w["word"].lower().strip(".,!?") == t)


XF = 0.3  # crossfade overlap between scenes
h0, h1 = line("hook")
c0, c1 = line("customer")
r0, r1 = line("reveal")

scenes = [
    Scene("s1", 0, round(c0 - 0.1 + XF, 2),
          html='<div class="label" id="s1-kicker" style="position:absolute;left:110px;top:100px;color:#d4a24c">The question</div>',
          js=f"tl.fromTo('#s1-kicker',{{opacity:0,y:16}},{{opacity:1,y:0,duration:.5,ease:'power3.out'}},0.1);"),
    Scene("s2", round(c0 - 0.1, 2), round(r0 - c0 + XF, 2),
          html=bank_street("s2") + '<div id="s2-wrap" style="position:absolute;inset:0">'
               + maya_svg("m2", "walk").replace('class="char "', 'class="char" style="left:150px;top:418px;width:270px;height:450px"')
               + "</div>" + street_foreground("s2"),
          js=(f"tl.fromTo('#s2',{{opacity:0}},{{opacity:1,duration:{XF}}},{c0 - 0.1});"
              f"walk('m2','#s2-wrap',{c0 + 0.8},6,.31,540);blink('#m2 .lid',[{c0 + 0.4},{c0 + 2.5}]);")),
]

vault = {"shots": [
    {"start": 0, "end": c0 + 0.2, "dur": c0, "camFrom": [-0.6, -0.5, 13.8], "camTo": [-1.9, 0.3, 10.6],
     "lookAt": [-3.4, -0.5, 0], "coins": True, "hubSpin": 0.05, "lock": False, "materialize": False},
    {"start": r0 - 0.3, "end": float("inf"), "dur": r1 - r0 + 1, "camFrom": [-4.4, -0.6, 9.0], "camTo": [-2.6, 0.4, 12.6],
     "lookAt": [-2.4, -2.2, 1.2], "coins": False, "hubSpin": 0, "lock": True, "materialize": True}],
    "materialize": {"start": r0 + 1, "dur": 1.5, "notesStart": r0 + 1.5, "notesDur": 1.0, "spinStart": r0 + 1.1,
                    "spinDur": 3.4, "glowFadeStart": r0 + 2.5, "glowFadeDur": 1.5, "at": [-2.4, 3.6]}}

CONFIG = json.loads((KIT_ROOT / "config" / "production.json").read_text())
engine = CONFIG["captions"]["engine"]
# 1080p is the default; EPOCH_RESOLUTION=1440p builds the optional QHD variant (not default until benchmarked).
resolution = os.environ.get("EPOCH_RESOLUTION", CONFIG["render"]["default_resolution"])
html = assemble(title="Is the AI Bubble Bigger Than the Dot-Com Bubble?", duration=D, scenes=scenes, vault=vault, resolution=resolution,
                caption_pages=pages if engine == "hyperframes" else None)
prepare_workspace(WORKSPACE)
(WORKSPACE / "index.html").write_text(html)
print("wrote", WORKSPACE / "index.html")
