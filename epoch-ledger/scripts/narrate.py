#!/usr/bin/env python3
"""Epoch Ledger narration: script lines → timed narration, Whisper words, caption pages, SRT.

  python epoch-ledger/scripts/narrate.py EPISODE_DIR [--workspace WS]

Reads EPISODE_DIR/script.json:  {"lines": [{"id": "hook", "text": "..."}, ...]}
Writes EPISODE_DIR/artifacts/{narration_timing,words,caption_phrases}.json + captions.srt,
and the mixed narration to WS/narration.wav (default projects/<episode>/hyperframes).

Settings come from epoch-ledger/config/production.json → "narration" / "captions".
TTS goes through OpenMontage's tts_selector (Kokoro, free and local); timing through the
local faster-whisper transcriber. Each line is synthesised separately so every scene can be
keyed to the real audio, trimmed of edge silence, then laid out with fixed breaths.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
REPO = KIT.parent
sys.path.insert(0, str(REPO))
CONFIG = json.loads((KIT / "config" / "production.json").read_text())


def _dur(path: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(path)]))


def synthesize(lines: list[dict], work: Path, cfg: dict) -> list[dict]:
    from tools.tool_registry import registry
    registry.discover()
    tts = registry._tools["tts_selector"]
    segs, t = [], cfg["lead_seconds"]
    work.mkdir(parents=True, exist_ok=True)
    for i, line in enumerate(lines):
        raw, trimmed = work / f"line_{i:03d}_{line['id']}.wav", work / f"t_line_{i:03d}_{line['id']}.wav"
        r = tts.execute({"text": line["text"], "preferred_tool": cfg["tool"], "voice": cfg["voice"],
                         "speed": cfg["speed"], "output_path": str(raw)})
        if not r.success:
            raise RuntimeError(f"TTS failed on line {line['id']}: {r.error}")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(raw), "-af",
                        "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                        "-ar", "24000", "-ac", "1", str(trimmed)], check=True)
        d = _dur(trimmed)
        segs.append({"id": line["id"], "text": line["text"], "file": str(trimmed),
                     "start": round(t, 3), "end": round(t + d, 3)})
        t += d + line.get("pause_after", cfg["gap_seconds"])
    return segs


def mix(segs: list[dict], out: Path, cfg: dict) -> float:
    total = round(segs[-1]["end"] + cfg["tail_seconds"], 2)
    inputs = sum([["-i", s["file"]] for s in segs], [])
    fl = "".join(f"[{i}]adelay={int(s['start'] * 1000)}:all=1[a{i}];" for i, s in enumerate(segs))
    fl += "".join(f"[a{i}]" for i in range(len(segs)))
    fl += (f"amix=inputs={len(segs)}:normalize=0,apad,atrim=0:{total},"
           f"loudnorm=I={cfg['loudness_lufs']}:TP=-1.5:LRA=11[o]")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex", fl,
                    "-map", "[o]", "-ar", "48000", "-ac", "2", str(out)], check=True)
    return total


def transcribe(audio: Path, model: str, outdir: Path) -> list[dict]:
    from tools.tool_registry import registry
    registry.discover()
    r = registry._tools["transcriber"].execute({"input_path": str(audio), "model_size": model,
                                                 "output_dir": str(outdir)})
    if not r.success:
        raise RuntimeError(f"transcription failed: {r.error}")
    merged = []
    for x in r.data["word_timestamps"]:
        w = x["word"].strip()
        if merged and w.startswith(","):  # Whisper splits "$10" ",000"
            merged[-1]["word"] += w
            merged[-1]["end"] = x["end"]
        else:
            merged.append({"word": w, "start": x["start"], "end": x["end"]})
    return merged


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9$]", "", s.lower())


def align_lines(words: list[dict], segs: list[dict]) -> list[dict]:
    """Assign words to script lines by first word; pin each line's onset to the real audio start."""
    idx, i = [], 0
    for s in segs:
        first = _norm(s["text"].split()[0])
        while i < len(words) and _norm(words[i]["word"]) != first:
            i += 1
        if i == len(words):
            raise RuntimeError(f"could not align line {s['id']!r} — check the transcript")
        idx.append(i)
        i += 1
    idx.append(len(words))
    lines = []
    for k, s in enumerate(segs):
        ws = [dict(w) for w in words[idx[k]:idx[k + 1]]]
        ws[0]["start"] = max(ws[0]["start"], s["start"])
        lines.append({"id": s["id"], "start": ws[0]["start"], "end": ws[-1]["end"], "words": ws})
    return lines


def caption_pages(lines: list[dict], max_words: int) -> list[dict]:
    """Clause-level pages: break at , . : ; ? ! or max_words, never orphan a 1-word sentence tail."""
    pages = []
    for line in lines:
        cur, ws = [], line["words"]
        for i, w in enumerate(ws):
            cur.append(w)
            tail_next = i == len(ws) - 2 and ws[-1]["word"][-1] in ".?!"
            if w["word"][-1] in ",.:;?!" or (len(cur) >= max_words and not tail_next):
                pages.append(cur)
                cur = []
        if cur:
            pages.append(cur)
    return [{"start": p[0]["start"], "end": p[-1]["end"], "text": " ".join(w["word"] for w in p), "words": p}
            for p in pages]


def srt(pages: list[dict]) -> str:
    def ts(x):
        h, rem = divmod(x, 3600)
        m, s = divmod(rem, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02},{int(round((s - int(s)) * 1000)):03}"
    return "".join(f"{n}\n{ts(p['start'])} --> {ts(p['end'])}\n{p['text']}\n\n" for n, p in enumerate(pages, 1))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode", type=Path)
    ap.add_argument("--workspace", type=Path)
    a = ap.parse_args(argv)
    ep = a.episode.resolve()
    ws = (a.workspace or REPO / "projects" / ep.name / "hyperframes").resolve()
    art = ep / "artifacts"
    art.mkdir(exist_ok=True)
    lines = json.loads((ep / "script.json").read_text())["lines"]
    ncfg, ccfg = CONFIG["narration"], CONFIG["captions"]
    segs = synthesize(lines, ws.parent / "assets" / "audio", ncfg)
    total = mix(segs, ws / "narration.wav", ncfg)
    words = transcribe(ws / "narration.wav", ccfg["whisper_model"], ws.parent / "artifacts" / "transcript")
    aligned = align_lines(words, segs)
    pages = caption_pages(aligned, ccfg["max_words_per_page"])
    (art / "narration_timing.json").write_text(json.dumps({"total": total, "segments": segs}, indent=1))
    (art / "words.json").write_text(json.dumps(words, indent=0))
    (art / "caption_phrases.json").write_text(json.dumps(pages, indent=1))
    (art / "captions.srt").write_text(srt(pages))
    for s in segs:
        print(f"{s['start']:7.2f}–{s['end']:7.2f}  {s['id']}")
    print(f"total {total}s → {ws / 'narration.wav'}; {len(pages)} caption pages")


if __name__ == "__main__":
    main()
