#!/usr/bin/env bash
# P12 validation passage ("Sold on", 2006–2008 mortgage crisis), end to end and cold (experimental, opt-in; P11 and
# earlier untouched). Every step is timed into .runtime/charlab/p12/perf.jsonl; caches are cleared first.
#   epoch-ledger/charlab/p12/run_p12.sh [OUT.mp4] [WORKERS]
set -euo pipefail
cd "$(dirname "$0")/../../.."
H=epoch-ledger/charlab/p12; R=.runtime/charlab/p12; P=$R/plates; S=$R/shots; EP=projects/charlab_p12/story
OUT=${1:-projects/charlab_p12/p12_passage.mp4}; W=${2:-4}
M="python3 epoch-ledger/charlab/p9/measure.py"; LOG=$R/perf.jsonl
rm -rf $P $S $R/cache_cold $R/cast projects/charlab_p12/assets projects/charlab_p12/hf_final; rm -f $LOG; mkdir -p $P $S "$(dirname "$OUT")"
# 1 narration (Kokoro voice-over, Whisper words, gold caption pages) and the timeline the sequence reads
$M narrate $LOG -- .venv/bin/python epoch-ledger/scripts/narrate.py $EP --workspace projects/charlab_p12/hf
python3 -c "import json; a='$EP/artifacts/'; t=json.load(open(a+'narration_timing.json')); w=json.load(open(a+'words.json')); t['words']=w if isinstance(w,list) else w['words']; json.dump(t,open(a+'timeline.json','w'),indent=1)"
# 2 plan: narration-to-visual map checked and resolved to the real word times (P11 method)
$M plan $LOG -- python3 epoch-ledger/charlab/p11/visual_map.py check $H/map_p12.json --resolved $R/map_resolved.json --table $R/map_table.md
# 3 cast: identities and wardrobe, checked on the definitions AND on the rendered pixels
$M cast $LOG -- python3 $H/cast.py .runtime/charlab/p8/src/open-peeps.fig $R/cast
$M continuity $LOG -- node $H/continuity.mjs $R/cast
# 4 set stills (lender's office close, home window, desk from above) + depth + paint
for k in B C D; do
  D=epoch-ledger/charlab/motion/demos/p10_cam$k.json; [ $k = D ] && D=epoch-ledger/charlab/motion/demos/p11_camD.json
  $M plate_$k $LOG -- node epoch-ledger/charlab/shot_render.mjs --demo $D --chars .runtime/charlab/out_p3 \
     --three .runtime/charlab/three/r0.186.1 --quality cin_balanced --cache $R/cache_cold --out $P/cam$k.mp4
  ffmpeg -loglevel error -y -i $P/cam$k.mp4 -frames:v 1 $P/cam${k}_raw.png
  $M track_$k $LOG -- node epoch-ledger/charlab/p9/cam_track.mjs $D epoch-ledger/charlab/p10/points.json $P/track$k
  ffmpeg -loglevel error -y -i $P/cam${k}_raw.png -filter_complex "$(cat epoch-ledger/charlab/p9/paint_filter.txt)" $P/cam${k}_paint.png
done
# 5 2.5D shots (P10 compositor, plate-matched lighting) and the selective 3D shot
$M prepare $LOG -- python3 $H/prepare.py .runtime/charlab/p8/src/open-peeps.fig $R/map_resolved.json $P $S
for k in S1 S2 S6 S8; do $M compose_$k $LOG -- node epoch-ledger/charlab/p10/render_shot.mjs $S/shot$k.json $R/shot$k.mp4 --workers $W; done
$M stack_3d $LOG -- $H/render_3d.sh $R/map_resolved.json $R/stack.mp4 2
# 6 HyperFrames: video shots + the format library's scenes (map, chart, document, newspaper, timeline) + captions + narration
$M hf_build $LOG -- python3 epoch-ledger/charlab/hf_sequence.py epoch-ledger/charlab/sequences/p12_test.py .runtime/charlab/out_p3 projects/charlab_p12/hf_final
EPOCH_RENDER_TIMEOUT_PER_FRAME=3 $M hf_render $LOG -- python3 epoch-ledger/scripts/render.py render projects/charlab_p12/hf_final --isolate --jobs $W -o "$OUT"
# 7 checks: technical QC and semantic sync on the rendered film
node epoch-ledger/scripts/qc.mjs --video "$OUT"
python3 epoch-ledger/charlab/p11/visual_map.py inspect $H/map_p12.json "$OUT" --out $R/sync_report.json | tail -1
python3 - "$LOG" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
print(json.dumps({"total_wall_s": round(sum(r["wall_s"] for r in rows), 1), "peak_rss_mb": max(r["peak_rss_mb"] for r in rows),
                  "steps": {r["label"]: r["wall_s"] for r in rows}}, indent=1))
PY
