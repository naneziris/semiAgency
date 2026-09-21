"""Shared helpers for the bench scripts. Python 3 standard library only."""
import json
import re
import sys
import threading
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "cases"
RUNS = ROOT / "runs"
RESULTS = ROOT / "results"

HEADER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
CHECK_RE = re.compile(r"^-\s*(~~)?(C\d+)(~~)?\s*:\s*(.+?)\s*$")


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def slug(s):
    s = re.sub(r"[^a-z0-9.-]+", "-", s.lower()).strip("-")
    return s or "unnamed"


def list_cases():
    if not CASES.is_dir():
        return []
    return sorted(p.name for p in CASES.iterdir()
                  if p.is_dir() and (p / "task" / "prompt.md").is_file())


def case_dir(name):
    d = CASES / name
    if not (d / "task" / "prompt.md").is_file():
        die(f"no case '{name}' (expected {d / 'task' / 'prompt.md'})")
    return d


def read_checks(case):
    """Return list of (id, text) for live checks; [] when checks.md is missing."""
    f = CASES / case / "grading" / "checks.md"
    if not f.is_file():
        return []
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        m = CHECK_RE.match(line.strip())
        if m and not (m.group(1) or m.group(3)):
            out.append((m.group(2), m.group(4)))
    return out


def parse_header(text):
    m = HEADER_RE.match(text)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    body = text[m.end():] if m else text
    return meta, body


_alloc_lock = threading.Lock()


def make_header(case, model, run_no, mode):
    return (f"---\ncase: {case}\nmodel: {slug(model)}\n"
            f"date: {datetime.now().isoformat(timespec='minutes')}\n"
            f"run: {run_no}\nmode: {mode}\n---\n\n")


def new_run_path(case, model, mode):
    """Create runs/<case>/<model>__<YYYYMMDD-HHMM>__r<n>.md with its header (n = 1 + existing runs of that model).
    Thread-safe: the file exists when this returns, so parallel callers never get the same path."""
    d = RUNS / case
    d.mkdir(parents=True, exist_ok=True)
    m = slug(model)
    with _alloc_lock:
        n = 1 + len([p for p in d.glob("*.md") if p.name.split("__")[0] == m])
        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        p = d / f"{m}__{stamp}__r{n}.md"
        while p.exists():
            n += 1
            p = d / f"{m}__{stamp}__r{n}.md"
        p.write_text(make_header(case, model, n, mode), encoding="utf-8")
    return p, n


def list_runs(case=None):
    out = []
    if not RUNS.is_dir():
        return out
    for cd in sorted(RUNS.iterdir()):
        if not cd.is_dir() or (case and cd.name != case):
            continue
        for f in sorted(cd.glob("*.md")):
            out.append(f)
    return out


def result_path(run_file):
    return RESULTS / run_file.parent.name / (run_file.stem + ".json")


def load_result(run_file):
    p = result_path(run_file)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def pending_runs(case=None):
    return [f for f in list_runs(case) if load_result(f) is None]


def write_result(run_file, data):
    p = result_path(run_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return p
