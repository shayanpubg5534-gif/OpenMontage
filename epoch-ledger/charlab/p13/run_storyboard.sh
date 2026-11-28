#!/usr/bin/env bash
# P13 storyboard for the P12 mortgage passage (experimental, opt-in; P12 and earlier untouched): the new kitchen world
# (two lights), the 2.5D key frames, the 3D tranche building, the HyperFrames board with captions, the treatment check
# and the sheets. Cold (caches cleared) and timed into .runtime/charlab/p13/perf.jsonl.
#   epoch-ledger/charlab/p13/run_storyboard.sh
set -euo pipefail
cd "$(dirname "$0")/../../.."
H=epoch-ledger/charlab/p13; R=.runtime/charlab/p13; EV=epoch-ledger/charlab/evidence/p13; FIG=.runtime/charlab/p8/src/open-peeps.fig
M="python3 epoch-ledger/charlab/p9/measure.py"; LOG=$R/perf.jsonl
rm -rf $R/cache $R/plates $R/shots $R/kf $R/board $R/board_ws; rm -f $LOG; mkdir -p $R/plates $R/shots $R/kf $EV
$M backdrop $LOG -- node $H/backdrop.mjs $R/backdrop
$M sets $LOG -- python3 $H/sets.py
for v in dusk night; do
  D=epoch-ledger/charlab/motion/demos/p13_kitchen_$v.json
  $M plate_$v $LOG -- node epoch-ledger/charlab/shot_render.mjs --demo $D --chars .runtime/charlab/out_p3 --three .runtime/charlab/three/r0.186.1 --quality cin_balanced --cache $R/cache --out $R/plates/$v.mp4
  ffmpeg -loglevel error -y -i $R/plates/$v.mp4 -frames:v 1 $R/plates/${v}_raw.png
  $M track_$v $LOG -- node epoch-ledger/charlab/p9/cam_track.mjs $D $H/points.json $R/plates/track_$v
  ffmpeg -loglevel error -y -i $R/plates/${v}_raw.png -filter_complex "$(cat epoch-ledger/charlab/p9/paint_filter.txt)" $R/plates/${v}_paint.png
done
$M cast $LOG -- python3 $H/keyframes.py $FIG $R/plates $R/shots
for k in kf1_signing kf6_bookend; do
  $M compose_$k $LOG -- node epoch-ledger/charlab/p10/compose.mjs $R/shots/$k.json $R/shots/$k.mp4 --from 35 --to 35
  ffmpeg -loglevel error -y -i $R/shots/$k.mp4 -frames:v 1 $R/kf/$k.png
done
K='[[0,[2.55,1.05,3.05],[-0.05,0.95,0],38]]'
$M building_pay $LOG -- node epoch-ledger/charlab/p12/three_shot.mjs $H/scenes/tranches.js $R/shots/kf3.mp4 0.034 "$K" '{"mode":0}'
$M building_loss $LOG -- node epoch-ledger/charlab/p12/three_shot.mjs $H/scenes/tranches.js $R/shots/kf5.mp4 0.034 "$K" '{"mode":1,"flood":0.62,"defaults":0.14}'
for k in kf3 kf5; do ffmpeg -loglevel error -y -i $R/shots/$k.mp4 -frames:v 1 $R/shots/${k}_raw.png; done
$M board $LOG -- python3 $H/board.py $R $R/board_ws $R/board
for k in 1 2 3 4 5 6; do convert $R/board/KF$k.png -quality 86 $EV/KF$k.jpg; done
(cd epoch-ledger && ../.venv/bin/python -m kit.treatment charlab/p13/treatment.json)
python3 $H/sheets.py $R/board projects/charlab_p12/p12_passage.mp4 $EV
python3 - "$LOG" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
print(json.dumps({"total_wall_s": round(sum(r["wall_s"] for r in rows), 1), "peak_rss_mb": max(r["peak_rss_mb"] for r in rows),
                  "steps": {r["label"]: r["wall_s"] for r in rows}}, indent=1))
PY
