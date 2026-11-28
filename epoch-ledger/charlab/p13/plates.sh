#!/usr/bin/env bash
# P13: the kitchen plates (wide and from above, dusk 2006 and night 2008): one still each + depth pass + painterly pass.
#   epoch-ledger/charlab/p13/plates.sh OUT_DIR [CACHE] [MEASURE_LOG]
set -euo pipefail
cd "$(dirname "$0")/../../.."
P=$1; C=${2:-.runtime/charlab/p13/cache}; LOG=${3:-/dev/null}; mkdir -p $P
M="python3 epoch-ledger/charlab/p9/measure.py"
for v in dusk night dusk_top night_top; do
  D=epoch-ledger/charlab/motion/demos/p13_kitchen_$v.json
  $M plate_$v $LOG -- node epoch-ledger/charlab/shot_render.mjs --demo $D --chars .runtime/charlab/out_p3 --three .runtime/charlab/three/r0.186.1 --quality cin_balanced --cache $C --out $P/$v.mp4 >/dev/null
  ffmpeg -loglevel error -y -i $P/$v.mp4 -frames:v 1 $P/${v}_raw.png
  $M track_$v $LOG -- node epoch-ledger/charlab/p9/cam_track.mjs $D epoch-ledger/charlab/p13/points.json $P/track_$v >/dev/null
  ffmpeg -loglevel error -y -i $P/${v}_raw.png -filter_complex "$(cat epoch-ledger/charlab/p9/paint_filter.txt)" $P/${v}_paint.png
done
