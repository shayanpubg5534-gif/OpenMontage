"""P9: run a command and report wall time and peak resident memory of its whole process tree (sampled every 0.25 s).

    python3 epoch-ledger/charlab/p9/measure.py LABEL LOG.jsonl -- CMD ARGS...
Appends {"label", "wall_s", "peak_rss_mb", "rc"} to LOG.jsonl and prints it.
"""
import json
import os
import subprocess
import sys
import time

label, log = sys.argv[1], sys.argv[2]; cmd = sys.argv[sys.argv.index("--") + 1:]


def tree_rss(pid):
    kids = {}
    for p in os.listdir("/proc"):
        if not p.isdigit(): continue
        try:
            st = open(f"/proc/{p}/stat").read().rsplit(")", 1)[1].split(); kids.setdefault(int(st[1]), []).append(int(p))
        except OSError: pass
    tot, stack = 0, [pid]
    while stack:
        q = stack.pop(); stack += kids.get(q, [])
        try:
            for line in open(f"/proc/{q}/status"):
                if line.startswith("VmRSS:"): tot += int(line.split()[1])
        except OSError: pass
    return tot / 1024


t0 = time.time(); pr = subprocess.Popen(cmd); peak = 0.0
while pr.poll() is None:
    peak = max(peak, tree_rss(pr.pid)); time.sleep(0.25)
r = {"label": label, "wall_s": round(time.time() - t0, 1), "peak_rss_mb": round(peak), "rc": pr.returncode}
open(log, "a").write(json.dumps(r) + "\n"); print("MEASURE", json.dumps(r))
sys.exit(pr.returncode)
