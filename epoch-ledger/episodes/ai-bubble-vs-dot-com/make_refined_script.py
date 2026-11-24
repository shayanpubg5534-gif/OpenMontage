"""Write refined_script.md: the lightly refined script with chapter timings and every change marked."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:04.1f}"


def main():
    script = json.loads((HERE / "script.json").read_text())
    timing = json.loads((HERE / "artifacts" / "narration_timing.json").read_text())
    changes = json.loads((HERE / "artifacts" / "script_changes.json").read_text())
    check = json.loads((HERE / "artifacts" / "audio_check.json").read_text())
    seg = {s["id"]: s for s in timing["segments"]}
    changed = {c["id"] for c in changes}
    words = sum(len(l["text"].split()) for l in script["lines"])
    md = [f"# {script['title']} — refined script (for approval)\n",
          f"**Narration duration: {fmt(timing['total'])} ({timing['total']:.1f} s)** · {words} words · "
          f"{len(script['lines'])} lines · Kokoro bm_george 0.95 · {len(changes)} changes, all listed below.\n",
          "Lines marked ✎ were edited (light refinement, factual correction or precision); 🔊 marks a "
          "spoken-only pronunciation fix (captions keep the written form). Chapter headings appear on "
          "screen as chapter cards and are not narrated.\n",
          "## Chapter timings\n", "| Chapter | Start | Duration |", "|---|---|---|"]
    for c in script["chapters"]:
        ids = [l["id"] for l in script["lines"] if l["chapter"] == c["n"]]
        a, b = seg[ids[0]]["start"], seg[ids[-1]]["end"]
        md.append(f"| {c['n']}. {c['title']} | {fmt(a)} | {(b - a) / 60:.2f} min |")
    md += ["\n## Changes from the approved script\n", "| Line | Before | After | Reason |", "|---|---|---|---|"]
    for c in changes:
        md.append(f"| {c['id']} | {c['before']} | {c['after']} | {c['reason']} |")
    md.append("\n## Refined script\n")
    for c in script["chapters"]:
        md.append(f"\n### Chapter {c['n']} — {c['title']}\n")
        for l in script["lines"]:
            if l["chapter"] != c["n"]:
                continue
            mark = (" ✎" if l["id"] in changed and not all(
                x["reason"] == "PRONUNCIATION" for x in changes if x["id"] == l["id"]) else "")
            mark += " 🔊" if "tts" in l else ""
            md.append(f"`{fmt(seg[l['id']]['start'])}` {l['text']}{mark}\n")
    md += ["\n## Remaining transcription mismatches (reviewed)\n",
           "Whisper vs script after the fixes. These are transcription artefacts, not narration errors, "
           "unless stated otherwise; captions always show the script wording.\n",
           "| Line | Script | Whisper heard |", "|---|---|---|"]
    for x in check:
        md.append(f"| {x['id']} | {x['script']} | {x['heard']} |")
    (HERE / "refined_script.md").write_text("\n".join(md) + "\n")
    print("wrote refined_script.md", fmt(timing["total"]), words, "words", len(check), "mismatches")


if __name__ == "__main__":
    main()
