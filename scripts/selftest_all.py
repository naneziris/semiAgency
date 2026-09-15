#!/usr/bin/env python3
"""Run every script's --selftest; exit non-zero on any failure.
Scripts that don't exist yet (built by Copilot on the corporate machine) are reported as missing, not failed."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHIPPED = ["append_tasks"]
COPILOT_BUILT = ["ooxml", "new_engagement", "ingest", "validate", "status", "followup_agenda",
                 "inspect_components", "skeletonize_deck", "build_deck", "storyboard", "lint_deck", "timing"]

failed = 0
for name in SHIPPED + COPILOT_BUILT:
    p = os.path.join(HERE, name + ".py")
    if not os.path.exists(p):
        print("MISSING  %s.py  (built by Copilot — docs/bootstrap.md §3)" % name)
        continue
    r = subprocess.run([sys.executable, p, "--selftest"], capture_output=True, text=True)
    if r.returncode == 0:
        print("OK       %s.py" % name)
    else:
        failed += 1
        print("FAILED   %s.py\n%s%s" % (name, r.stdout, r.stderr))
sys.exit(1 if failed else 0)
