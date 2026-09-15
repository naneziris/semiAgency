#!/usr/bin/env python3
"""Create the shared action tracker (tracker/actions.xlsx) with the fixed column set.

Columns (docs/d2p/design.md §7, extended for email triage):
  id | created | source | context | owner | action | due | urgency | effort | status | depends_on | notes

Run once. Refuses to overwrite. If you already keep a tracker, don't run this — make sure its first
sheet has this header row (same names, same order) and is formatted as a Table; append_tasks.py
only ever appends rows.
"""
import argparse
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xlsxlite  # noqa: E402

HEADER = ["id", "created", "source", "context", "owner", "action", "due",
          "urgency", "effort", "status", "depends_on", "notes"]
SOURCES = ["d2p", "meeting-notes", "email-triage", "one-on-one", "manual"]
DEFAULT = os.path.join("tracker", "actions.xlsx")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", default=DEFAULT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "actions.xlsx")
            xlsxlite.create(p, HEADER)
            h, rows = xlsxlite.read_rows(p)
            assert h == HEADER and rows == []
        print("tracker_init selftest OK")
        return
    if os.path.exists(a.path):
        print("refusing to overwrite existing %s" % a.path)
        sys.exit(1)
    os.makedirs(os.path.dirname(os.path.abspath(a.path)), exist_ok=True)
    xlsxlite.create(a.path, HEADER)
    print("created %s with columns: %s" % (a.path, " | ".join(HEADER)))
    print("open it once in Excel and save, so Excel adds its own metadata; then never edit the header row.")


if __name__ == "__main__":
    main()
