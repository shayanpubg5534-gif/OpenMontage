#!/usr/bin/env bash
# P10 narrated 2.5D test, end to end and cold (experimental, opt-in; production defaults and P9 are untouched).
#   epoch-ledger/charlab/p10/run_p10.sh [OUT.mp4] [WORKERS]
# Needs: .runtime/charlab/p8/src/open-peeps.fig (CC0, not committed), .runtime/charlab/three/r0.186.1, the Kokoro/Whisper
# narration stack (.venv), ffmpeg, node + playwright. Every step is timed (wall clock, peak RSS of the process tree) into
# .runtime/charlab/p10/perf.jsonl; caches are cleared first so the numbers are a cold run.
set -euo pipefail
cd "$(dirname "$0")/../../.."
H=epoch-ledger/charlab/p10; R=.runtime/charlab/p10; P=$R/plates; S=$R/shots; EP=projects/charlab_p10/story
OUT=${1:-projects/charlab_p10/p10_narrated_test.mp4}; W=${2:-4}
M="python3 epoch-ledger/charlab/p9/measure.py"; LOG=$R/perf.jsonl
rm -rf $P $S $R/cache_cold projects/charlab_p10/assets projects/charlab_p10/hf_final; rm -f $LOG; mkdir -p $P $S "$(dirname "$OUT")"
# 1 narration: Kokoro voice-over, Whisper word times, gold caption pages (series settings in config/production.json)
$M narrate $LOG -- .venv/bin/python epoch-ledger/scripts/narrate.py $EP --workspace projects/charlab_p10/hf
for k in A B C; do
  D=epoch-ledger/charlab/motion/demos/p10_cam$k.json
  # 2 one still of the set per camera (P5 renderer, P4 cinematic look, Balanced), and its depth pass + anchor points
  $M plate_$k $LOG -- node epoch-ledger/charlab/shot_render.mjs --demo $D --chars .runtime/charlab/out_p3 \
     --three .runtime/charlab/three/r0.186.1 --quality cin_balanced --cache $R/cache_cold --out $P/cam$k.mp4
  ffmpeg -loglevel error -y -i $P/cam$k.mp4 -frames:v 1 $P/cam${k}_raw.png
  $M track_$k $LOG -- node epoch-ledger/charlab/p9/cam_track.mjs $D $H/points.json $P/track$k
  # 3 slightly painterly treatment (P9 filter)
  $M paint_$k $LOG -- ffmpeg -loglevel error -y -i $P/cam${k}_raw.png -filter_complex "$(cat epoch-ledger/charlab/p9/paint_filter.txt)" $P/cam${k}_paint.png
done
# 4 cast, rigs and per-shot performance keyed to the narration's word times
$M prepare $LOG -- python3 $H/prepare.py .runtime/charlab/p8/src/open-peeps.fig $P $EP $S
# 5 the 2.5D shots: bitmap-layer compositing, W workers per shot
for k in A B C; do $M compose_$k $LOG -- node $H/render_shot.mjs $S/shot$k.json $R/shot$k.mp4 --workers $W; done
# 6 HyperFrames: shots as video clips + the financial motion graphic + gold captions + narration (render.py, unmodified)
$M hf_build $LOG -- python3 epoch-ledger/charlab/hf_sequence.py epoch-ledger/charlab/sequences/p10_test.py .runtime/charlab/out_p3 projects/charlab_p10/hf_final
EPOCH_RENDER_TIMEOUT_PER_FRAME=3 $M hf_render $LOG -- python3 epoch-ledger/scripts/render.py render projects/charlab_p10/hf_final --isolate --jobs $W -o "$OUT"
node epoch-ledger/scripts/qc.mjs --video "$OUT"
python3 - "$LOG" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
print(json.dumps({"total_wall_s": round(sum(r["wall_s"] for r in rows), 1), "peak_rss_mb": max(r["peak_rss_mb"] for r in rows),
                  "steps": {r["label"]: r["wall_s"] for r in rows}}, indent=1))
PY
