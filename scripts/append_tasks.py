#!/usr/bin/env python3
"""Append reviewed tasks to the shared tracker (tracker/actions.xlsx). Append-only, deduplicated.

Usage:
  python scripts/append_tasks.py engagements/<name>              # reads <name>/tasks.json, source from state.json kind
  python scripts/append_tasks.py path/to/tasks.json               # any tasks file; --source overrides
  python scripts/append_tasks.py --drain                           # only push tasks.pending.csv left over from a lock

Tasks file shape (see .github/instructions/tasks.instructions.md):
  {"tasks": [{"action": "...", "owner": "me", "due": "2026-09-18" | null, "urgency": "high|normal|low",
              "effort": "S|M|L", "depends_on": [], "source": "E3", "context": "2026-09-15", "notes": ""}],
   "candidates": [...]}                                              # candidates are never appended
Only `action` is required. `id` = sha1(source + "|" + action)[:10] is the dedup key across the tracker and the pending CSV.
If Excel has the tracker open, rows go to tracker/tasks.pending.csv and are drained on the next run.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xlsxlite  # noqa: E402
from tracker_init import HEADER  # noqa: E402

KIND_SOURCE = {"proposal": "d2p", "deck": "d2p", "meeting": "meeting-notes"}


def task_id(source, action):
    return hashlib.sha1(("%s|%s" % (source, action.strip())).encode("utf-8")).hexdigest()[:10]


def load_tasks(path):
    """path: engagement dir or a .json file. Returns (tasks, default_source, default_context)."""
    if os.path.isdir(path):
        tfile = os.path.join(path, "tasks.json")
        state = os.path.join(path, "state.json")
        kind = "proposal"
        if os.path.exists(state):
            with open(state, encoding="utf-8") as f:
                kind = json.load(f).get("kind", "proposal")
        source = KIND_SOURCE.get(kind, "d2p")
        context = os.path.basename(os.path.normpath(path))
    else:
        tfile = path
        source = "manual"
        base = os.path.basename(path)
        context = base.split(".")[0]
    if not os.path.exists(tfile):
        raise FileNotFoundError(tfile)
    with open(tfile, encoding="utf-8") as f:
        data = json.load(f)
    tasks = data.get("tasks", []) if isinstance(data, dict) else data
    return tasks, source, context


def to_row(t, source, context, today):
    action = (t.get("action") or "").strip()
    if not action:
        return None
    src_ref = t.get("source") or ""
    ctx = t.get("context") or context
    dedup_source = "%s:%s" % (source, ctx)
    dep = t.get("depends_on") or []
    if isinstance(dep, list):
        dep = "; ".join(str(x) for x in dep)
    notes = t.get("notes") or ""
    if src_ref:
        notes = ("[%s] " % src_ref) + notes
    return [
        task_id(dedup_source, action), today, source, ctx,
        t.get("owner") or "me", action, t.get("due") or "",
        t.get("urgency") or "", t.get("effort") or "", t.get("status") or "open",
        dep, notes.strip(),
    ]


def existing_ids(tracker, pending):
    ids = set()
    if os.path.exists(tracker):
        _, rows = xlsxlite.read_rows(tracker)
        ids.update(r.get("id", "") for r in rows)
    if os.path.exists(pending):
        with open(pending, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                ids.add(r.get("id", ""))
    return ids


def read_pending(pending):
    if not os.path.exists(pending):
        return []
    with open(pending, encoding="utf-8", newline="") as f:
        return [[r.get(k, "") for k in HEADER] for r in csv.DictReader(f)]


def write_pending(pending, rows, append=True):
    exists = os.path.exists(pending)
    with open(pending, "a" if append else "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if not exists or not append:
            w.writerow(HEADER)
        w.writerows(rows)


def push(tracker, rows, pending):
    """Try the xlsx; on lock, park in the pending CSV. Returns (written_to_xlsx, parked)."""
    if not rows:
        return 0, 0
    try:
        n = xlsxlite.append_rows(tracker, rows)
        return n, 0
    except PermissionError as e:
        write_pending(pending, rows)
        print("tracker locked (%s) — %d row(s) parked in %s; run again later" % (e, len(rows), pending))
        return 0, len(rows)


def run(path, tracker, source_override=None, drain_only=False):
    pending = os.path.join(os.path.dirname(os.path.abspath(tracker)), "tasks.pending.csv")
    if not os.path.exists(tracker):
        print("no tracker at %s — run python scripts/tracker_init.py first" % tracker)
        return 1
    today = dt.date.today().isoformat()
    ids = existing_ids(tracker, pending)
    # 1. drain
    parked = read_pending(pending)
    if parked:
        try:
            n = xlsxlite.append_rows(tracker, parked)
            os.remove(pending)
            print("drained %d parked row(s) into %s" % (n, tracker))
        except PermissionError:
            print("tracker still locked; %d row(s) remain parked in %s" % (len(parked), pending))
            if drain_only:
                return 1
    if drain_only:
        return 0
    # 2. new tasks
    tasks, source, context = load_tasks(path)
    source = source_override or source
    rows, skipped = [], 0
    for t in tasks:
        r = to_row(t, source, context, today)
        if r is None:
            continue
        if r[0] in ids:
            skipped += 1
            continue
        ids.add(r[0])
        rows.append(r)
    n, p = push(tracker, rows, pending)
    print("source=%s context=%s: %d appended, %d parked, %d already present (skipped)" % (source, context, n, p, skipped))
    kb = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(tracker))), "kb")
    if os.path.isdir(kb):
        try:
            import kb_index
            kb_index.build(kb, tracker)
        except Exception:
            pass
    return 0


def _selftest():
    with tempfile.TemporaryDirectory() as d:
        tracker = os.path.join(d, "actions.xlsx")
        xlsxlite.create(tracker, HEADER)
        tfile = os.path.join(d, "2026-09-15.tasks.json")
        with open(tfile, "w", encoding="utf-8") as f:
            json.dump({"tasks": [
                {"action": "Confirm renewal", "owner": "me", "due": "2026-09-18", "urgency": "high", "effort": "S", "source": "E1"},
                {"action": "Ask Jan for estimate", "owner": "delegate:jan-d", "source": "E4", "depends_on": ["Confirm renewal"]},
                {"action": "", "owner": "me"},
            ], "candidates": [{"action": "maybe"}]}, f)
        assert run(tfile, tracker, "manual") == 0
        assert run(tfile, tracker, "manual") == 0  # idempotent
        h, rows = xlsxlite.read_rows(tracker)
        assert len(rows) == 2, rows
        assert rows[0]["source"] == "manual" and rows[0]["notes"].startswith("[E1]"), rows[0]
        assert rows[1]["depends_on"] == "Confirm renewal"
        # lock → pending → drain
        lock = os.path.join(d, "~$actions.xlsx")
        open(lock, "w").close()
        with open(tfile, "w", encoding="utf-8") as f:
            json.dump({"tasks": [{"action": "Third one", "source": "E9"}]}, f)
        run(tfile, tracker, "manual")
        pending = os.path.join(d, "tasks.pending.csv")
        assert os.path.exists(pending)
        assert run(tfile, tracker, "manual") == 0  # still locked: nothing new, nothing lost
        os.remove(lock)
        assert run(None, tracker, drain_only=True) == 0
        h, rows = xlsxlite.read_rows(tracker)
        assert [r["action"] for r in rows] == ["Confirm renewal", "Ask Jan for estimate", "Third one"], rows
        assert not os.path.exists(pending)
        # engagement dir form
        eng = os.path.join(d, "2026-09-x")
        os.makedirs(eng)
        with open(os.path.join(eng, "state.json"), "w") as f:
            json.dump({"kind": "meeting"}, f)
        with open(os.path.join(eng, "tasks.json"), "w") as f:
            json.dump({"tasks": [{"action": "From a meeting", "owner": "me", "source": "T1 00:10:00"}]}, f)
        run(eng, tracker)
        h, rows = xlsxlite.read_rows(tracker)
        assert rows[-1]["source"] == "meeting-notes" and rows[-1]["context"] == "2026-09-x"
    print("append_tasks selftest OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", help="engagement dir or tasks .json file")
    ap.add_argument("--tracker", default=os.path.join("tracker", "actions.xlsx"))
    ap.add_argument("--source", help="override source column (d2p|meeting-notes|manual)")
    ap.add_argument("--drain", action="store_true", help="only push parked rows from tasks.pending.csv")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        sys.exit(0)
    if not a.drain and not a.path:
        ap.print_help()
        sys.exit(1)
    sys.exit(run(a.path, a.tracker, a.source, a.drain))
