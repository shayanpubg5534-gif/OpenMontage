"""P10: survey the Open Peeps file for what the artwork can support (views, arms, wardrobe): every standing pose, every
bust body and every head, rendered with one neutral head/face in the muted palette.

    python3 epoch-ledger/charlab/p10/survey.py FIG OUT_DIR
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "p8"))
import peeps_compose as PC  # noqa: E402

fig, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
C = PC.Composer(fig); base = PC.CAST["banker"]
names = sorted(C.sym)
def write(kind, parts, fn):
    open(os.path.join(out, fn), "w").write(C.svg(kind, parts, base["palette"]))
head = {"HEAD": "head/Short 2", "FACE": "face/Calm", "FACIAL HAIR": "facial-hair/* None", "ACCESORIES": "accessories/* None"}
for n in names:
    k, leaf = n.rsplit("/", 1)
    if k == "pose/standing": write("standing", {**head, "BODY": n}, "standing_%s.svg" % leaf)
    elif k == "pose/sitting": write("sitting", {**head, "BODY": n}, "sitting_%s.svg" % leaf)
    elif k == "body": write("bust", {**head, "BODY": n}, "bust_%s.svg" % leaf.replace(" ", "_"))
    elif k == "head": write("bust", {**head, "BODY": "body/Button Shirt 1", "HEAD": n}, "head_%s.svg" % leaf.replace(" ", "_"))
print("survey", out)
