#!/usr/bin/env python3
"""Run every script's --selftest; exit non-zero on the first failure.
Scripts that don't exist yet (the D2P ones Copilot builds on the corporate machine) are reported as missing, not failed."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHIPPED = ["xlsxlite", "tracker_init", "append_tasks", "kb_ingest", "kb_index"]
COPILOT_BUILT = ["ooxml", "new_engagement", "ingest", "validate", "status", "followup_agenda",
                 "inspect_components", "skeletonize_deck", "build_deck", "storyboard", "lint_deck", "timing"]

failed = 0
for name in SHIPPED + COPILOT_BUILT:
    p = os.path.join(HERE, name + ".py")
    if not os.path.exists(p):
        print("MISSING  %s.py%s" % (name, "  (built by Copilot — see docs/d2p/bootstrap.md §3)" if name in COPILOT_BUILT else ""))
        continue
    r = subprocess.run([sys.executable, p, "--selftest"], capture_output=True, text=True)
    if r.returncode == 0:
        print("OK       %s.py" % name)
    else:
        failed += 1
        print("FAILED   %s.py\n%s%s" % (name, r.stdout, r.stderr))
sys.exit(1 if failed else 0)
