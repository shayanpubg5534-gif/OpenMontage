"""HyperFrames-native word-highlight captions matching the approved Remotion caption look.

The pilot burned captions with Remotion's CaptionOverlay in a second full-length pass.
This module renders the *same* design inside the HyperFrames composition instead, so
captions are captured with the scene frames (no extra pass, no re-encode) and each
caption page is its own cache unit for scripts/render.py.

Reproduced from remotion-composer/src/components/CaptionOverlay.tsx:
  * page timing: from = round(start*fps); until = min(next page start, end + 0.7 s)
  * box: centred, bottom offset, radius 12, padding 14px 28px, max-width 80%
  * text: weight 700, line-height 1.4; words inline-block, never broken
  * word state: active = highlight + glow, past = full colour, upcoming = 60 % alpha
  * entrance: spring(damping 18, stiffness 120) on opacity and a 20 px rise
"""
from __future__ import annotations

import json
import math

STYLE = {  # approved pilot caption styling (Remotion props in the pilot run)
    "font_size": 46,
    "color": "#F8FAFC",
    "highlight": "#f2c66d",
    "background": "rgba(20,33,61,0.82)",
    "font_family": "Inter, system-ui, sans-serif",
    "bottom_offset": 60,
    "max_words_per_page": 6,
}

CSS = """
.ecap{position:absolute;left:0;top:0;width:1920px;height:1080px;display:flex;justify-content:center;align-items:flex-end;pointer-events:none}
.ecap .box{border-radius:12px;padding:14px 28px;max-width:80%;text-align:center;opacity:0}
.ecap .txt{font-weight:700;line-height:1.4;white-space:pre-wrap}
.ecap .w{display:inline-block;white-space:nowrap;text-shadow:0 2px 4px rgba(0,0,0,0.5)}
"""

HELPER_JS = """
// Epoch Ledger captions — Remotion CaptionOverlay parity (seek-safe, per-page tweens)
function ecapSpring(t){const k=120,c=18,w0=Math.sqrt(k),z=c/(2*w0),wd=w0*Math.sqrt(1-z*z);
  return t<=0?0:1-Math.exp(-z*w0*t)*(Math.cos(wd*t)+(z*w0/wd)*Math.sin(wd*t));}
function ecapPage(tl,id,start,dur,pageStartMs,words,color,hl){
  const box=document.querySelector('#'+id+' .box'),spans=box.querySelectorAll('.w');
  const o={t:0};
  tl.to(o,{t:dur,duration:dur,ease:'none',onUpdate:()=>{
    const e=ecapSpring(o.t),ms=pageStartMs+o.t*1000;
    box.style.opacity=e; box.style.transform='translateY('+(20*(1-e))+'px)';
    words.forEach((w,i)=>{const s=spans[i],act=w[0]<=ms&&w[1]>ms,past=w[1]<=ms;
      s.style.color=act?hl:(past?color:color+'99');
      s.style.textShadow=act?'0 0 20px '+hl+'66, 0 2px 4px rgba(0,0,0,0.5)':'0 2px 4px rgba(0,0,0,0.5)';});
  }},start);
}
"""


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def caption_layer(pages: list[dict], fps: int = 30, style: dict | None = None, track_index: int = 20,
                  id_prefix: str = "cap") -> tuple[str, str, str]:
    """Return (css, html, js) for a caption layer.

    pages: [{"words": [{"word", "start", "end"}, ...]}, ...] — one entry per caption page
    (e.g. artifacts/caption_phrases.json). Each page's JS sits in a /*scene:<id>*/ region
    so render.py caches captions per page.
    """
    st = {**STYLE, **(style or {})}
    css = CSS + (f".ecap{{padding-bottom:{st['bottom_offset']}px}}"
                 f".ecap .box{{background:{st['background']}}}"
                 f".ecap .txt{{font-size:{st['font_size']}px;font-family:{st['font_family']}}}")
    html, js = [], [HELPER_JS]
    for i, page in enumerate(pages):
        words = page["words"]
        start_ms = int(words[0]["start"] * 1000)
        end_ms = int(words[-1]["end"] * 1000)
        next_ms = int(pages[i + 1]["words"][0]["start"] * 1000) if i + 1 < len(pages) else math.inf
        from_f = round(start_ms / 1000 * fps)
        dur_f = max(1, round((min(next_ms, end_ms + 700) - start_ms) / 1000 * fps))
        start, dur = from_f / fps, dur_f / fps
        cid = f"{id_prefix}{i:03d}"
        spans = " ".join(f'<span class="w" style="color:{st["color"]}99">{_esc(w["word"])}</span>' for w in words)
        html.append(f'<div id="{cid}" class="clip ecap" data-start="{start:.4f}" data-duration="{dur:.4f}" '
                    f'data-track-index="{track_index}"><div class="box"><span class="txt">{spans}</span></div></div>')
        data = json.dumps([[int(w["start"] * 1000), int(w["end"] * 1000)] for w in words])
        js.append(f"/*scene:{cid}*/ecapPage(tl,'{cid}',{start:.4f},{dur:.4f},{start_ms},{data},"
                  f"'{st['color']}','{st['highlight']}');/*/scene:{cid}*/")
    return css, "\n".join(html), "\n".join(js)
