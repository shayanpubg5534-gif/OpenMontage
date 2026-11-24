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


def _line_key(spoken: str, cfg: dict) -> str:
    """Content address for one voiced line: same text + voice settings → same audio file."""
    import hashlib
    sig = f"{cfg['tool']}|{cfg['voice']}|{cfg['speed']}|{spoken}"
    return hashlib.sha1(sig.encode()).hexdigest()[:12]


def spoken_text(line: dict) -> str:
    """What the narrator says. `tts` overrides pronunciation only; captions always use `text`."""
    return line.get("tts", line["text"])


def synthesize(lines: list[dict], work: Path, cfg: dict, reuse: bool = True) -> list[dict]:
    """Voice each line once and cache it by content, so edits re-voice only the changed lines."""
    tts = None
    segs, t = [], cfg["lead_seconds"]
    work.mkdir(parents=True, exist_ok=True)
    for line in lines:
        spoken = spoken_text(line)
        key = _line_key(spoken, cfg)
        raw, trimmed = work / f"v_{key}.wav", work / f"vt_{key}.wav"
        if not trimmed.exists():
            if tts is None:
                from tools.tool_registry import registry
                registry.discover()
                tts = registry._tools["tts_selector"]
            r = tts.execute({"text": spoken, "preferred_tool": cfg["tool"], "voice": cfg["voice"],
                             "speed": cfg["speed"], "output_path": str(raw)})
            if not r.success:
                raise RuntimeError(f"TTS failed on line {line['id']}: {r.error}")
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(raw), "-af",
                            "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                            "silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                            "-ar", "24000", "-ac", "1", str(trimmed)], check=True)
            print(f"voiced {line['id']}")
        d = _dur(trimmed)
        segs.append({"id": line["id"], "text": line["text"], "spoken": spoken, "key": key, "file": str(trimmed),
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


_WHISPER = {}


def _merge_numbers(raw: list[dict]) -> list[dict]:
    merged = []
    for x in raw:
        w = x["word"].strip()
        if not w:
            continue
        # Whisper splits numbers: "$10" ",000" · "86" "%" · "$5" ".5"
        if merged and (w.startswith(",") or w == "%" or (w[:1] in ".%" and merged[-1]["word"][-1:].isdigit())):
            merged[-1]["word"] += w
            merged[-1]["end"] = x["end"]
        else:
            merged.append({"word": w, "start": x["start"], "end": x["end"]})
    return merged


def transcribe_lines(segs: list[dict], model: str) -> list[dict]:
    """Whisper each voiced line on its own (cached next to the audio) and offset to film time.

    Per-line transcription never skips a short line the way one long pass can, keeps word
    times inside their line, and lets an edit re-transcribe only the lines that changed. No
    prompt is given, so a mispronounced word still shows up as a mismatch for review.
    """
    words = []
    for s in segs:
        cache = Path(s["file"]).with_suffix(f".{model}.words.json")
        if cache.exists():
            rel = json.loads(cache.read_text())
        else:
            if model not in _WHISPER:
                from faster_whisper import WhisperModel
                _WHISPER[model] = WhisperModel(model, device="cpu", compute_type="int8")
            parts, _ = _WHISPER[model].transcribe(s["file"], language="en", word_timestamps=True,
                                                   condition_on_previous_text=False)
            rel = [{"word": w.word, "start": w.start, "end": w.end} for p in parts for w in (p.words or [])]
            cache.write_text(json.dumps(rel))
        for w in _merge_numbers(rel):
            words.append({"word": w["word"], "start": round(s["start"] + w["start"], 3),
                          "end": round(s["start"] + w["end"], 3)})
    return words


def transcribe(audio: Path, model: str, outdir: Path, reuse: bool = False) -> list[dict]:
    """Single-pass transcription of a full mix (legacy path; per-line is the default)."""
    cached = outdir / f"{audio.stem}_transcript.json"
    if reuse and cached.exists() and cached.stat().st_mtime >= audio.stat().st_mtime:
        raw = json.loads(cached.read_text())["word_timestamps"]
    else:
        from tools.tool_registry import registry
        registry.discover()
        r = registry._tools["transcriber"].execute({"input_path": str(audio), "model_size": model,
                                                     "output_dir": str(outdir)})
        if not r.success:
            raise RuntimeError(f"transcription failed: {r.error}")
        raw = r.data["word_timestamps"]
    return _merge_numbers(raw)


def _uk_us(text: str) -> str:
    t = _norm(text.replace("-", "").replace(".", "dot"))
    for a, b in (("tre", "ter"), ("bre", "ber"), ("ise", "ize"), ("our", "or"), ("yse", "yze")):
        t = t.replace(a, b)
    return t


def audio_check(words: list[dict], segs: list[dict]) -> list[dict]:
    """Per line: script words Whisper heard differently (pronunciation review list)."""
    import difflib
    out = []
    for s in segs:
        heard = [w["word"] for w in words if s["start"] - 0.01 <= w["start"] <= s["end"] + 0.01]
        a = [_norm(x) for x in s["text"].split()]
        b = [_norm(x) for x in heard]
        for op, a1, a2, b1, b2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if op == "equal":
                continue
            said, got = " ".join(s["text"].split()[a1:a2]), " ".join(heard[b1:b2])
            if _is_number_words(s["text"].split()[a1:a2]) and any(c.isdigit() for c in got):
                continue  # numerals for spelled-out numbers are fine
            if _norm(said.replace("-", "")) == _norm(got.replace(" ", "")):
                continue  # hyphenation / spacing only
            if _uk_us(said) == _uk_us(got):
                continue  # British vs American spelling (centre/center, recognise/recognize, fibre/fiber)
            if not got and all(_norm(t) in ("dollars", "dollar", "percent") for t in said.split()):
                continue  # folded into "$…" / "…%"
            out.append({"id": s["id"], "script": said, "heard": got})
    return out


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9$]", "", s.lower())


def align_lines(words: list[dict], segs: list[dict]) -> list[dict]:
    """Assign Whisper words to script lines with a global sequence alignment.

    Script and transcript tokens are aligned with difflib (robust to Whisper spelling numbers
    differently, merging or splitting words); each line starts at the transcript position of
    its first aligned token, shifted back by any unaligned tokens before it. Line onsets are
    pinned to the real audio start of that line.
    """
    import difflib
    toks, owner = [], []
    for k, s in enumerate(segs):
        for w in s["text"].split():
            toks.append(_norm(w))
            owner.append(k)
    heard = [_norm(w["word"]) for w in words]
    mapping = {}
    for a, b, n in difflib.SequenceMatcher(None, toks, heard, autojunk=False).get_matching_blocks():
        for j in range(n):
            mapping[a + j] = b + j
    if not mapping:
        raise RuntimeError("transcript does not match the script at all")
    # estimated transcript index for every script token: exact where aligned, otherwise offset
    # from the nearest aligned token before it (or after it, at the very start)
    est, last = [], None
    first_mapped = min(mapping)
    for t in range(len(toks)):
        if t in mapping:
            last = t
            est.append(mapping[t])
        elif last is None:
            est.append(max(0, mapping[first_mapped] - (first_mapped - t)))
        else:
            est.append(mapping[last] + (t - last))
    starts, prev, first_tok = [], 0, 0
    for k, s in enumerate(segs):
        start = min(max(prev, est[first_tok]), len(words) - 1)
        starts.append(start)
        prev, first_tok = start + 1, first_tok + len(s["text"].split())
    starts.append(len(words))
    lines = []
    for k, s in enumerate(segs):
        ws = [dict(w) for w in words[starts[k]:starts[k + 1]]]
        if not ws:
            raise RuntimeError(f"line {s['id']!r} received no transcript words")
        ws[0]["start"] = max(ws[0]["start"], s["start"])
        lines.append({"id": s["id"], "start": ws[0]["start"], "end": ws[-1]["end"], "words": ws})
    return lines


NUMBER_WORDS = set("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
                   "sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety "
                   "hundred thousand million billion trillion point percent dollars dollar".split())


def _is_number_words(tokens: list[str]) -> bool:
    parts = [p for t in tokens for p in re.split(r"[-\s]", re.sub(r"[^a-z\- ]", "", t.lower())) if p]
    return bool(parts) and all(p in NUMBER_WORDS for p in parts)


def reconcile(words: list[dict], segs: list[dict]) -> list[dict]:
    """Caption words per line: the approved script's text on Whisper's timing.

    * matching words → script spelling and punctuation, Whisper times;
    * Whisper heard a different spelling (centers/centres, fiber/fibre, a mumbled word) → script words
      spread over the heard span;
    * the script spells a number in words and Whisper wrote numerals ("86%", "$5.5") → keep the
      numerals (more readable); years and figures written as digits in the script stay as written;
    * script words Whisper missed → placed in the gap they occupy, inside their line's audio window;
      a bare "dollars"/"percent" already folded into "$…"/"…%" is dropped.
    Each word stays inside its own line's audio window, so captions never straddle lines.
    """
    import difflib
    toks, owner = [], []
    for k, s in enumerate(segs):
        for w in s["text"].split():
            toks.append(w)
            owner.append(k)
    nt = [_norm(t) for t in toks]
    nh = [_norm(w["word"]) for w in words]
    out = [[] for _ in segs]

    def put(k, text, a, b):
        lo, hi = segs[k]["start"], segs[k]["end"]
        a = min(max(a, lo), hi)
        b = min(max(b, a), hi)
        out[k].append({"word": text, "start": round(a, 3), "end": round(b, 3)})

    def spread(idx, a, b):
        weights = [max(1, len(toks[i])) for i in idx]
        tot, t = sum(weights), a
        for i, wgt in zip(idx, weights):
            d = (b - a) * wgt / tot
            put(owner[i], toks[i], t, t + d)
            t += d

    ops = difflib.SequenceMatcher(None, nt, nh, autojunk=False).get_opcodes()
    for n, (op, a1, a2, b1, b2) in enumerate(ops):
        if op == "equal":
            for i, j in zip(range(a1, a2), range(b1, b2)):
                put(owner[i], toks[i], words[j]["start"], words[j]["end"])
        elif op == "replace":
            heard = words[b1:b2]
            span = (heard[0]["start"], heard[-1]["end"])
            if _is_number_words(toks[a1:a2]) and any(c.isdigit() for w in heard for c in w["word"]):
                k = owner[a1]
                for w in heard:
                    put(k, w["word"], w["start"], w["end"])
                if toks[a2 - 1][-1] in ".,;:?!" and not out[k][-1]["word"].endswith(toks[a2 - 1][-1]):
                    out[k][-1]["word"] += toks[a2 - 1][-1]
            else:
                spread(list(range(a1, a2)), *span)
        elif op == "delete":
            if all(_norm(t) in ("dollars", "dollar", "percent") for t in toks[a1:a2]):
                k = owner[a1 - 1] if a1 else owner[a1]
                if out[k] and toks[a2 - 1][-1] in ".,;:?!" and not out[k][-1]["word"].endswith(toks[a2 - 1][-1]):
                    out[k][-1]["word"] += toks[a2 - 1][-1]
                continue
            prev_end = words[b1 - 1]["end"] if b1 > 0 else 0.0
            next_start = words[b1]["start"] if b1 < len(words) else segs[-1]["end"]
            k0, k1 = owner[a1], owner[a2 - 1]
            a = max(prev_end, segs[k0]["start"])
            b = min(next_start, segs[k1]["end"])
            if b - a < 0.1 * (a2 - a1):  # no usable gap: fall back to the line window
                a, b = segs[k0]["start"], segs[k1]["end"]
            spread(list(range(a1, a2)), a, b)
        # "insert": words Whisper heard that are not in the script (rare) are dropped
    lines = []
    for k, s in enumerate(segs):
        ws = sorted(out[k], key=lambda w: w["start"])
        if not ws:
            raise RuntimeError(f"line {s['id']!r} has no caption words")
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
            unit_next = i + 1 < len(ws) and _norm(ws[i + 1]["word"]) in ("million", "billion", "trillion", "percent")
            if w["word"][-1] in ",.:;?!" or (len(cur) >= max_words and not tail_next and not unit_next):
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
    ap.add_argument("--reuse", action="store_true", help=argparse.SUPPRESS)  # always on: content-cached
    a = ap.parse_args(argv)
    ep = a.episode.resolve()
    ws = (a.workspace or REPO / "projects" / ep.name / "hyperframes").resolve()
    art = ep / "artifacts"
    art.mkdir(exist_ok=True)
    lines = json.loads((ep / "script.json").read_text())["lines"]
    ncfg, ccfg = CONFIG["narration"], CONFIG["captions"]
    segs = synthesize(lines, ws.parent / "assets" / "audio", ncfg)
    wav = ws / "narration.wav"
    total = mix(segs, wav, ncfg)
    words = transcribe_lines(segs, ccfg["whisper_model"])
    aligned = reconcile(words, segs)
    pages = caption_pages(aligned, ccfg["max_words_per_page"])
    (art / "narration_timing.json").write_text(json.dumps({"total": total, "segments": segs}, indent=1))
    (art / "words.json").write_text(json.dumps(words, indent=0))
    (art / "caption_phrases.json").write_text(json.dumps(pages, indent=1))
    (art / "captions.srt").write_text(srt(pages))
    check = audio_check(words, segs)
    (art / "audio_check.json").write_text(json.dumps(check, indent=1))
    for s in segs:
        print(f"{s['start']:7.2f}–{s['end']:7.2f}  {s['id']}")
    print(f"total {total}s → {ws / 'narration.wav'}; {len(pages)} caption pages; "
          f"{len(check)} pronunciation mismatches to review (artifacts/audio_check.json)")


if __name__ == "__main__":
    main()
