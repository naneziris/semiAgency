#!/usr/bin/env python3
"""Append reviewed tasks to the shared tracker (tracker/actions.csv). Append-only, deduplicated. Stdlib only.

  python scripts/append_tasks.py                            # current engagement (engagements/CURRENT); shows the rows, appends, offers to pass G5
  python scripts/append_tasks.py engagements/<name>        # a specific engagement; source = d2p or meeting-notes from state.json kind
  python scripts/append_tasks.py --pass-g5                  # also record gate G5 in state.json without asking
  python scripts/append_tasks.py --init                     # create tracker/actions.csv with the header row (once)
  python scripts/append_tasks.py --selftest

Columns: id | created | source | engagement | owner | action | due | status | depends_on | notes
`id` = sha1(source, engagement, action)[:10] — running the same engagement twice appends nothing.
`candidates` in tasks.json are never appended. Open the CSV in Excel to edit status/notes; the script never rewrites existing rows.
If Excel has the file locked on Windows, the script says so and writes nothing — close it and run again.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = ["id", "created", "source", "engagement", "owner", "action", "due", "status", "depends_on", "notes"]
KIND_SOURCE = {"proposal": "d2p", "deck": "d2p", "meeting": "meeting-notes"}
DEFAULT = os.path.join("tracker", "actions.csv")


def task_id(source, engagement, action):
    return hashlib.sha1(("%s|%s|%s" % (source, engagement, action.strip())).encode("utf-8")).hexdigest()[:10]


def init(tracker):
    if os.path.exists(tracker):
        print("%s already exists" % tracker)
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(tracker)), exist_ok=True)
    with open(tracker, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerow(HEADER)
    print("created %s" % tracker)
    return 0


def existing_ids(tracker):
    with open(tracker, encoding="utf-8-sig", newline="") as f:
        return {r.get("id", "") for r in csv.DictReader(f)}


def rows_from(engagement_dir, today):
    with open(os.path.join(engagement_dir, "state.json"), encoding="utf-8") as f:
        kind = json.load(f).get("kind", "proposal")
    source = KIND_SOURCE.get(kind, "d2p")
    name = os.path.basename(os.path.normpath(engagement_dir))
    with open(os.path.join(engagement_dir, "tasks.json"), encoding="utf-8") as f:
        data = json.load(f)
    out = []
    for t in data.get("tasks", []):
        action = (t.get("action") or "").strip()
        if not action:
            continue
        dep = t.get("depends_on") or []
        notes = t.get("notes") or ""
        if t.get("source"):
            notes = ("[%s] " % t["source"]) + notes
        out.append([task_id(source, name, action), today, source, name, t.get("owner") or "me", action,
                    t.get("due") or "", t.get("status") or "open",
                    "; ".join(dep) if isinstance(dep, list) else str(dep), notes.strip()])
    return out


def current_engagement():
    p = os.path.join(ROOT, "engagements", "CURRENT")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        name = f.read().strip()
    return os.path.join(ROOT, "engagements", name) if name else None


def pass_g5(engagement_dir):
    p = os.path.join(engagement_dir, "state.json")
    with open(p, encoding="utf-8") as f:
        state = json.load(f)
    state.setdefault("gates", {}).setdefault("G5", {})["passed"] = True
    state["gates"]["G5"]["passed_on"] = dt.date.today().isoformat()
    with open(p, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    print("gate G5 passed; run python scripts/status.py to see where you are")


def run(engagement_dir, tracker, show=True):
    if not os.path.exists(tracker):
        print("no tracker at %s — run: python scripts/append_tasks.py --init" % tracker)
        return 1
    for req in ("state.json", "tasks.json"):
        if not os.path.exists(os.path.join(engagement_dir, req)):
            print("missing %s in %s" % (req, engagement_dir))
            return 1
    ids = existing_ids(tracker)
    rows = [r for r in rows_from(engagement_dir, dt.date.today().isoformat()) if r[0] not in ids]
    skipped = len(rows_from(engagement_dir, "")) - len(rows)
    if show:
        for r in rows:
            print("  + %-18s %s%s" % (r[4], r[5], (" (due %s)" % r[6]) if r[6] else ""))
    try:
        with open(tracker, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(rows)
    except PermissionError:
        print("%s is locked (open in Excel?) — nothing written; close it and run again" % tracker)
        return 1
    print("%s: %d appended, %d already present" % (os.path.basename(os.path.normpath(engagement_dir)), len(rows), skipped))
    return 0


def _selftest():
    with tempfile.TemporaryDirectory() as d:
        tracker = os.path.join(d, "actions.csv")
        assert init(tracker) == 0
        eng = os.path.join(d, "2026-09-acme")
        os.makedirs(eng)
        json.dump({"kind": "meeting"}, open(os.path.join(eng, "state.json"), "w"))
        json.dump({"tasks": [
            {"action": "Send Jan the estimate", "owner": "me", "due": "2026-09-18", "source": "T1 00:41:10"},
            {"action": "Ask Ali for the numbers, \"all of them\"", "owner": "delegate:ali-r", "depends_on": ["Send Jan the estimate"]},
            {"action": ""}], "candidates": [{"action": "maybe"}]}, open(os.path.join(eng, "tasks.json"), "w"))
        assert run(eng, tracker, show=False) == 0
        assert run(eng, tracker) == 0
        pass_g5(eng)
        assert json.load(open(os.path.join(eng, "state.json")))["gates"]["G5"]["passed"] is True
        with open(tracker, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2 and rows[0]["source"] == "meeting-notes" and rows[0]["notes"] == "[T1 00:41:10]", rows
        assert rows[1]["depends_on"] == "Send Jan the estimate" and rows[1]["owner"] == "delegate:ali-r"
        assert list(rows[0].keys()) == HEADER
    print("append_tasks selftest OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("engagement", nargs="?", help="engagement dir containing state.json and tasks.json")
    ap.add_argument("--tracker", default=DEFAULT)
    ap.add_argument("--init", action="store_true", help="create the tracker with its header row")
    ap.add_argument("--pass-g5", action="store_true", help="record gate G5 in state.json after appending")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
    elif a.init:
        sys.exit(init(a.tracker))
    else:
        eng = a.engagement or current_engagement()
        if not eng:
            print("no engagement given and no current engagement (engagements/CURRENT)")
            ap.print_help()
            sys.exit(1)
        rc = run(eng, a.tracker)
        if rc != 0:
            sys.exit(rc)
        if a.pass_g5:
            pass_g5(eng)
        elif sys.stdin.isatty():
            if input("Tasks reviewed and in the tracker. Pass gate G5 now? [y/N]: ").strip().lower() in ("y", "yes"):
                pass_g5(eng)
            else:
                print("later: python scripts/status.py --pass")
        sys.exit(0)
