#!/usr/bin/env bash
# P9 2.5D bank animation test, end to end (experimental, opt-in; nothing here is used by production).
#   epoch-ledger/charlab/p9/run_p9.sh [OUT.mp4]
# Needs: .runtime/charlab/p8/src/open-peeps.fig (CC0, not committed), .runtime/charlab/three/r0.186.1, ffmpeg, node+playwright.
# Every step is timed (wall clock, peak RSS of the process tree) into .runtime/charlab/p9/perf.jsonl.
set -euo pipefail
cd "$(dirname "$0")/../../.."
R=epoch-ledger/charlab/p9; P=.runtime/charlab/p9; OUT=${1:-projects/charlab_p9/p9_bank_25d.mp4}
M="python3 $R/measure.py"; mkdir -p "$P" "$(dirname "$OUT")"
python3 $R/prepare.py .runtime/charlab/p8/src/open-peeps.fig $P
for k in 1 2; do
  D=epoch-ledger/charlab/motion/demos/p9_shot$k.json
  # 1 the set plate, no characters (P5 continuous-session renderer, P4 cinematic look, Balanced profile)
  $M plate_shot$k $P/perf.jsonl -- node epoch-ledger/charlab/shot_render.mjs --demo $D --chars .runtime/charlab/out_p3 \
     --three .runtime/charlab/three/r0.186.1 --quality cin_balanced --out $P/plate$k.mp4
  # 2 slightly painterly treatment (edge-preserving smoothing, warm grade, soft ink edges)
  rm -rf $P/paint$k; mkdir -p $P/paint$k
  $M paint_shot$k $P/perf.jsonl -- ffmpeg -loglevel error -y -i $P/plate$k.mp4 -filter_complex "$(cat $R/paint_filter.txt)" -q:v 2 -start_number 0 $P/paint$k/%05d.jpg
  # 3 camera track + depth pass (same camera as the plate)
  $M track_depth_shot$k $P/perf.jsonl -- node $R/cam_track.mjs $D $R/points_shot$k.json $P/track$k
  # 4 characters, lighting, shadows, occlusion, grain; composited per frame
  $M animate_shot$k $P/perf.jsonl -- node $R/animate.mjs $P/shot$k.json $P/paint$k $P/track$k $P/anim$k.mp4
done
$M assemble $P/perf.jsonl -- ffmpeg -loglevel error -y -i $P/anim1.mp4 -i $P/anim2.mp4 -filter_complex \
  "[0][1]concat=n=2:v=1:a=0,fade=t=in:st=0:d=0.5,fade=t=out:st=16.4:d=0.6,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 18 \
  -preset medium -colorspace bt709 -color_primaries bt709 -color_trc bt709 -movflags +faststart "$OUT"
node epoch-ledger/scripts/qc.mjs --video "$OUT"
# wardrobe feasibility (fills recoloured, collar/tie added; line work untouched)
W=$P/wardrobe; mkdir -p $W
node $R/wardrobe.mjs .runtime/charlab/p8/cast/investor.svg $W/investor "#2c3444" "#6e2a2e" "#2a1a12"
node $R/wardrobe.mjs .runtime/charlab/p8/cast/banker.svg $W/banker "#2f3b52" "#7a5a2a" "#2a1a12" 0.46,0.03,0.68,0.28
