#!/usr/bin/env python3
"""Route handoff files from kb/inbox/ into the knowledge base (docs/handoff-format.md).

  python scripts/kb_ingest.py            # process every file in kb/inbox/
  python scripts/kb_ingest.py <file>     # process one file (anywhere)
  python scripts/kb_ingest.py --selftest

A daily-export is split by its H2 sections into kb/calendar/<date>.md, kb/email/<date>.md and
kb/topics/<topic>/links/<date>.md. Other types land in their folder as one file. The raw handoff
is kept in kb/archive/. Existing targets are never overwritten (a second file gets `.2`, `.3`...).
Content is never edited — only a header is prepended to each part. Ends by rebuilding kb/index.md.
"""
import argparse
import datetime as dt
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TYPES = {"daily-export", "calendar", "email", "topic-links", "one-on-one", "meeting", "note"}
SECTION_TYPE = {"calendar": "calendar", "emails": "email", "email": "email"}
DATE_RE = r"(\d{4}-\d{2}-\d{2})"


def slug(s):
    s = re.sub(r"[^\w\s-]", "", s.strip().lower(), flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-") or "unnamed"


def parse_header(text, filename):
    """Return (meta dict, body). Tolerant of lost --- fences; falls back to the file name."""
    lines = text.splitlines()
    meta = {}
    body_start = 0
    # fenced form
    if lines and lines[0].strip() == "---":
        for i in range(1, min(len(lines), 20)):
            if lines[i].strip() == "---":
                body_start = i + 1
                break
            m = re.match(r"^\s*([a-zA-Z_-]+)\s*:\s*(.*?)\s*$", lines[i])
            if m:
                meta[m.group(1).lower()] = m.group(2)
    if "handoff" not in meta:
        meta = {}
        for i, ln in enumerate(lines[:15]):
            m = re.match(r"^\s*[-*]?\s*([a-zA-Z_-]+)\s*:\s*(.*?)\s*$", ln)
            if m and m.group(1).lower() in ("handoff", "date", "source", "topic", "person", "subject"):
                meta[m.group(1).lower()] = m.group(2).strip("`* ")
                body_start = i + 1
        if "handoff" not in meta:
            body_start = 0
    if "handoff" not in meta or "date" not in meta:
        base = os.path.basename(filename)
        m = re.match(r"^%s-(daily-export|calendar|email|topic-links|one-on-one|meeting|note)(?:-(.+?))?\.md$" % DATE_RE, base)
        if m:
            meta.setdefault("date", m.group(1))
            meta.setdefault("handoff", m.group(2))
            if m.group(3):
                key = {"one-on-one": "person", "topic-links": "topic"}.get(m.group(2), "subject")
                meta.setdefault(key, m.group(3))
    if "handoff" in meta:
        meta["handoff"] = meta["handoff"].strip("`* ").lower()
    if "date" in meta:
        m = re.search(DATE_RE, meta["date"])
        meta["date"] = m.group(1) if m else ""
    body = "\n".join(lines[body_start:]).lstrip("\n")
    return meta, body


def split_sections(body):
    """Split a daily-export body by H2. Returns list of (heading, text)."""
    parts = []
    cur_head, cur = None, []
    for ln in body.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", ln)
        if m:
            if cur_head is not None:
                parts.append((cur_head, "\n".join(cur).strip("\n")))
            cur_head, cur = m.group(1), []
        else:
            cur.append(ln)
    if cur_head is not None:
        parts.append((cur_head, "\n".join(cur).strip("\n")))
    return parts


def header(meta_type, date, extra=None, source=None):
    out = ["---", "handoff: %s" % meta_type, "date: %s" % date]
    for k, v in (extra or {}).items():
        out.append("%s: %s" % (k, v))
    if source:
        out.append("source: %s" % source)
    out += ["ingested: %s" % dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "---", ""]
    return "\n".join(out)


def free_path(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    n = 2
    while os.path.exists("%s.%d%s" % (base, n, ext)):
        n += 1
    return "%s.%d%s" % (base, n, ext)


def write_part(kb, rel, text, log):
    target = free_path(os.path.join(kb, rel))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    note = "" if target == os.path.join(kb, rel) else "   (target existed — kept both; delete the one you don't want)"
    log.append("  -> %s%s" % (os.path.relpath(target, kb), note))
    return target


def route(kb, path, log):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    meta, body = parse_header(text, path)
    t, date = meta.get("handoff", ""), meta.get("date", "")
    if t not in TYPES or not re.match(r"^\d{4}-\d{2}-\d{2}$", date or ""):
        log.append("  !! cannot route %s: handoff=%r date=%r — add a header (docs/handoff-format.md) or rename the file" % (
            os.path.basename(path), t, date))
        return False
    src = meta.get("source")
    if t == "daily-export":
        sections = split_sections(body)
        if not sections:
            log.append("  !! daily-export has no '## ' sections; nothing routed")
            return False
        for head, sec in sections:
            hl = head.lower().strip()
            m = re.match(r"^topic links\s*:\s*(.+)$", hl)
            if m:
                topic = slug(m.group(1))
                write_part(kb, "topics/%s/links/%s.md" % (topic, date),
                           header("topic-links", date, {"topic": topic}, src) + "## Topic links: %s\n\n%s" % (topic, sec), log)
            elif hl in SECTION_TYPE:
                kind = SECTION_TYPE[hl]
                write_part(kb, "%s/%s.md" % (kind, date), header(kind, date, None, src) + "## %s\n\n%s" % (head, sec), log)
            else:
                write_part(kb, "notes/%s-%s.md" % (date, slug(head)), header("note", date, {"subject": head}, src) + "## %s\n\n%s" % (head, sec), log)
    elif t in ("calendar", "email"):
        write_part(kb, "%s/%s.md" % (t, date), header(t, date, None, src) + body, log)
    elif t == "topic-links":
        topic = slug(meta.get("topic", "") or "unsorted")
        write_part(kb, "topics/%s/links/%s.md" % (topic, date), header(t, date, {"topic": topic}, src) + body, log)
    elif t == "one-on-one":
        person = meta.get("person", "").strip()
        if not person:
            log.append("  !! one-on-one handoff without person: — add `person: <name>` to the header")
            return False
        write_part(kb, "people/%s/%s.md" % (slug(person), date), header(t, date, {"person": person}, src) + body, log)
    elif t == "meeting":
        subject = meta.get("subject", "") or "meeting"
        target = write_part(kb, "meetings/%s-%s.md" % (date, slug(subject)), header(t, date, {"subject": subject}, src) + body, log)
        log.append("     to work on it: python scripts/new_engagement.py --kind meeting --name %s-%s  then copy %s into its inputs/" % (
            date, slug(subject), os.path.relpath(target)))
    elif t == "note":
        subject = meta.get("subject", "") or "note"
        write_part(kb, "notes/%s-%s.md" % (date, slug(subject)), header(t, date, {"subject": subject}, src) + body, log)
    # archive raw
    arch = free_path(os.path.join(kb, "archive", "%s-%s.md" % (date, t if t != "one-on-one" else "one-on-one-" + slug(meta.get("person", "")))))
    os.makedirs(os.path.dirname(arch), exist_ok=True)
    shutil.move(path, arch)
    log.append("  raw kept as %s" % os.path.relpath(arch, kb))
    return True


def run(kb, single=None):
    log = []
    files = [single] if single else sorted(
        os.path.join(kb, "inbox", f) for f in os.listdir(os.path.join(kb, "inbox"))
        if f.lower().endswith((".md", ".txt")) and not f.startswith("."))
    if not files:
        print("kb/inbox is empty — nothing to do")
        return 0
    ok = 0
    for p in files:
        log.append(os.path.basename(p))
        if route(kb, p, log):
            ok += 1
    print("\n".join(log))
    try:
        import kb_index
        kb_index.build(kb)
        print("kb/index.md rebuilt")
    except Exception as e:  # index is a convenience; never fail ingest because of it
        print("index not rebuilt: %s" % e)
    print("%d of %d file(s) routed" % (ok, len(files)))
    return 0 if ok == len(files) else 1


SAMPLE = """---
handoff: daily-export
date: 2026-09-15
source: agent-builder/daily-exporter
---
## Calendar
### 2026-09-15
| start | end | title | with | kind | link | notes |
|---|---|---|---|---|---|---|
| 09:00 | 09:30 | Weekly 1-1 Maria K | Maria K | 1-1 | | recurring |
| 09:15 | 10:00 | Platform sync | Jan D, Ali R | meeting | | overlaps 1-1 |

## Emails
### E1 — Re: vendor contract renewal
- from: Sabine L
- gist: needs sign-off.
- asks: confirm by Thu.
- deadline: 2026-09-18

## Topic links: AI
| url | title | from | one-line |
|---|---|---|---|
| https://example.org/a | A | newsletter | Something |
"""


def _selftest():
    with tempfile.TemporaryDirectory() as d:
        kb = os.path.join(d, "kb")
        os.makedirs(os.path.join(kb, "inbox"))
        with open(os.path.join(kb, "inbox", "paste.md"), "w", encoding="utf-8") as f:
            f.write(SAMPLE)
        # fence-less variant, 1-1, and a file-name-only variant
        with open(os.path.join(kb, "inbox", "x.md"), "w", encoding="utf-8") as f:
            f.write("handoff: one-on-one\ndate: 2026-09-14\nperson: Maria K\n\n## Meetings covered\n- a\n")
        with open(os.path.join(kb, "inbox", "2026-09-13-note-vendor-call.md"), "w", encoding="utf-8") as f:
            f.write("Just text.\n")
        with open(os.path.join(kb, "inbox", "bad.md"), "w", encoding="utf-8") as f:
            f.write("no header at all\n")
        rc = run(kb)
        assert rc == 1  # bad.md stays
        for rel in ["calendar/2026-09-15.md", "email/2026-09-15.md", "topics/ai/links/2026-09-15.md",
                    "people/maria-k/2026-09-14.md", "notes/2026-09-13-vendor-call.md",
                    "archive/2026-09-15-daily-export.md", "archive/2026-09-14-one-on-one-maria-k.md", "inbox/bad.md"]:
            assert os.path.exists(os.path.join(kb, rel)), rel
        with open(os.path.join(kb, "calendar/2026-09-15.md"), encoding="utf-8") as f:
            cal = f.read()
        assert cal.startswith("---\nhandoff: calendar\ndate: 2026-09-15") and "| 09:00 | 09:30 |" in cal, cal
        with open(os.path.join(kb, "topics/ai/links/2026-09-15.md"), encoding="utf-8") as f:
            assert "topic: ai" in f.read()
        # second export same day → .2
        with open(os.path.join(kb, "inbox", "again.md"), "w", encoding="utf-8") as f:
            f.write(SAMPLE)
        os.remove(os.path.join(kb, "inbox", "bad.md"))
        assert run(kb) == 0
        assert os.path.exists(os.path.join(kb, "calendar/2026-09-15.2.md"))
    print("kb_ingest selftest OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--kb", default="kb")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
    else:
        sys.exit(run(a.kb, a.file))
