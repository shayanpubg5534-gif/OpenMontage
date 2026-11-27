#!/usr/bin/env bash
# P10 investigation sheets: art coverage survey (views), jointed limbs (elbow disc, wrist under the cuff) and formal wardrobe.
#   epoch-ledger/charlab/p10/sheets.sh [OUT_DIR]
set -euo pipefail
cd "$(dirname "$0")/../../.."
H=epoch-ledger/charlab/p10; R=.runtime/charlab/p10; O=${1:-projects/charlab_p10}; FIG=.runtime/charlab/p8/src/open-peeps.fig
mkdir -p $O $R/survey $R/ward
python3 $H/survey.py $FIG $R/survey
python3 - <<'PY'
import sys; sys.path.insert(0, 'epoch-ledger/charlab/p8'); import peeps_compose as PC
C = PC.Composer('.runtime/charlab/p8/src/open-peeps.fig'); b = PC.CAST['banker']; inv = PC.CAST['investor']; ban = PC.CAST['banker']
head = {"HEAD": "head/Short 2", "FACE": "face/Calm", "FACIAL HAIR": "facial-hair/* None", "ACCESORIES": "accessories/* None"}
for p in ('robot_dance-1', 'pointing_finger-1'):
    open('.runtime/charlab/p10/survey/wide_%s.svg' % p, 'w').write(C.svg('standing', {**head, 'BODY': 'pose/standing/' + p}, b['palette'], pad=600))
W = '.runtime/charlab/p10/ward/'
open(W + 'inv_blazer-4.svg', 'w').write(C.svg('standing', inv['parts'], inv['palette']))
open(W + 'inv_shirt-3.svg', 'w').write(C.svg('standing', {**inv['parts'], 'BODY': 'pose/standing/shirt-3'}, inv['palette']))
open(W + 'ban_blazer-4.svg', 'w').write(C.svg('standing', {**ban['parts'], 'BODY': 'pose/standing/blazer-4'}, ban['palette']))
open(W + 'inv_bust_shirt.svg', 'w').write(C.svg('bust', {**inv['parts'], 'BODY': 'body/Button Shirt 1'}, inv['palette']))
open(W + 'inv_bust_coat.svg', 'w').write(C.svg('bust', {**inv['parts'], 'BODY': 'body/Shirt and Coat'}, inv['palette']))
PY
# views: every standing pose and every head (all three-quarter, facing right: the artwork has no profile or back views)
S=$R/survey; a=(); for f in $S/standing_*.svg; do b=$(basename $f .svg); a+=("${b#standing_}::$f"); done
node epoch-ledger/charlab/p9/sheet.mjs $O/sheet_views_poses.png "Open Peeps standing poses: all three-quarter views facing right (mirroring gives the other side; no profile or back views exist)" 9 190 "${a[@]}"
a=(); for f in $S/bust_*.svg; do b=$(basename $f .svg); a+=("${b#bust_}::$f"); done
node epoch-ledger/charlab/p9/sheet.mjs $O/sheet_busts.png "Open Peeps bust bodies: drawn for medium shots and close-ups (30 tops, several with gestures)" 10 170 "${a[@]}"
# joints
node $H/rig_test.mjs $S/wide_pointing_finger-1.svg $H/rigs/pointing_finger-1.json $O/joint_elbow.png "fore=0;fore=-15;fore=-8;fore=6;fore=12" 600,500,1500,1500
node $H/rig_test.mjs $S/wide_robot_dance-1.svg $H/rigs/robot_dance-1.json $O/joint_wrist.png "hand=0;hand=-12;hand=-6;hand=4" 700,900,1500,1600
# formal wardrobe v2 (the artist's fills recoloured by index; collar and tie in the artist's line weight)
W=$R/ward; T="node $H/wardrobe2.mjs"
$T $W/inv_blazer-4.svg $W/f_inv_suit.svg "2=#2e2e33,3=#e6e1d6,1=#2a1a12" "#6e2a2e@0.47,0.075,0.66,0.30"
$T $W/inv_shirt-3.svg $W/f_inv_shirt.svg "2=#e6e1d6,1=#2a1a12" "#6e2a2e@0.47,0.06,0.62,0.36"
$T $W/ban_blazer-4.svg $W/f_ban_suit.svg "1=#2a1a12"
$T $W/inv_bust_shirt.svg $W/f_bust_shirt.svg "1=#e6e1d6" "#6e2a2e@0.42,0.12,0.6,0.85"
$T $W/inv_bust_coat.svg $W/f_bust_coat.svg "0=#2e2e33,2=#e6e1d6" "#6e2a2e@0.48,0.27,0.66,0.95"
node epoch-ledger/charlab/p9/sheet.mjs $O/sheet_wardrobe_v2.png "P10 formal wardrobe: the artist's own fills recoloured, tie drawn in the artist's line weight (line work untouched)" 5 300 \
  "Dark suit, white shirt, tie (blazer-4)::$W/f_inv_suit.svg" "Shirt and tie (shirt-3)::$W/f_inv_shirt.svg" "Banker: navy blazer, blouse (blazer-4)::$W/f_ban_suit.svg" \
  "Close-up: button shirt and tie (bust)::$W/f_bust_shirt.svg" "Close-up: coat, shirt, tie (bust)::$W/f_bust_coat.svg"
