#!/usr/bin/env python3
"""Route handoff files from kb/inbox/ into the knowledge base (docs/handoff-format.md).

  python scripts/kb_ingest.py            # process every file in kb/inbox/
  python scripts/kb_ingest.py <file>     # process one file (anywhere)
  python scripts/kb_ingest.py --selftest

Handoff types: topic-links (-> kb/topics/<topic>/links/<date>.md; a file with several topic sections is split),
meeting (-> kb/meetings/), note (-> kb/notes/). Anything else is refused: email, calendar and 1-1 content
stay in Microsoft 365 by design. The raw handoff is kept in kb/archive/. Existing targets are never
overwritten (a second file gets `.2`, `.3`...). Content is never edited — only a header is prepended.
Ends by rebuilding kb/index.md.
"""
import argparse
import datetime as dt
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TYPES = {"topic-links", "meeting", "note"}
REFUSED = {"daily-export", "calendar", "email", "one-on-one"}
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
            if m and m.group(1).lower() in ("handoff", "date", "source", "topic", "subject"):
                meta[m.group(1).lower()] = m.group(2).strip("`* ")
                body_start = i + 1
        if "handoff" not in meta:
            body_start = 0
    if "handoff" not in meta or "date" not in meta:
        base = os.path.basename(filename)
        m = re.match(r"^%s-(topic-links|meeting|note)(?:-(.+?))?\.md$" % DATE_RE, base)
        if m:
            meta.setdefault("date", m.group(1))
            meta.setdefault("handoff", m.group(2))
            if m.group(3):
                meta.setdefault("topic" if m.group(2) == "topic-links" else "subject", m.group(3))
    if "handoff" in meta:
        meta["handoff"] = meta["handoff"].strip("`* ").lower()
    if "date" in meta:
        m = re.search(DATE_RE, meta["date"])
        meta["date"] = m.group(1) if m else ""
    body = "\n".join(lines[body_start:]).lstrip("\n")
    return meta, body


def split_sections(body):
    """Split a body by H2. Returns list of (heading, text)."""
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
    if t in REFUSED:
        log.append("  !! refused %s: handoff type %r is not allowed locally — email, calendar and 1-1 content stay in M365 (docs/handoff-format.md)" % (
            os.path.basename(path), t))
        return False
    if t not in TYPES or not re.match(r"^\d{4}-\d{2}-\d{2}$", date or ""):
        log.append("  !! cannot route %s: handoff=%r date=%r — add a header (docs/handoff-format.md) or rename the file" % (
            os.path.basename(path), t, date))
        return False
    src = meta.get("source")
    if t == "topic-links":
        # one file may carry several "## Topic links: <topic>" sections (several topics in one run)
        sections = [(h, sec) for h, sec in split_sections(body) if re.match(r"^topic links\s*:", h.lower())]
        if not sections:
            topic = slug(meta.get("topic", "") or "unsorted")
            write_part(kb, "topics/%s/links/%s.md" % (topic, date), header(t, date, {"topic": topic}, src) + body, log)
        for head, sec in sections:
            topic = slug(re.match(r"^topic links\s*:\s*(.+)$", head.lower()).group(1))
            write_part(kb, "topics/%s/links/%s.md" % (topic, date),
                       header(t, date, {"topic": topic}, src) + "## Topic links: %s\n\n%s" % (topic, sec), log)
        if re.search(r"^\s*\|\s*from\s*\|", body, flags=re.M | re.I) or re.search(r"^- from:", body, flags=re.M):
            log.append("  !! WARNING: this links file carries a sender/from column — the agent drifted; re-paste JOB 3 of agent-builder/daily-brief.md")
    elif t == "meeting":
        subject = meta.get("subject", "") or "meeting"
        target = write_part(kb, "meetings/%s-%s.md" % (date, slug(subject)), header(t, date, {"subject": subject}, src) + body, log)
        log.append("     to work on it: python scripts/new_engagement.py --kind meeting --name %s-%s  then copy %s into its inputs/" % (
            date, slug(subject), os.path.relpath(target)))
    elif t == "note":
        subject = meta.get("subject", "") or "note"
        write_part(kb, "notes/%s-%s.md" % (date, slug(subject)), header(t, date, {"subject": subject}, src) + body, log)
    # archive raw
    arch = free_path(os.path.join(kb, "archive", "%s-%s.md" % (date, t)))
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
handoff: topic-links
date: 2026-09-15
topic: ai
source: agent-builder/daily-brief
---
## Topic links: ai
| url | title | one-line |
|---|---|---|
| https://example.org/a | A | Something |
| https://example.org/b | B | |

## Topic links: platform
| url | title | one-line |
|---|---|---|
| https://example.org/c | C | Other |
"""


def _selftest():
    with tempfile.TemporaryDirectory() as d:
        kb = os.path.join(d, "kb")
        os.makedirs(os.path.join(kb, "inbox"))
        with open(os.path.join(kb, "inbox", "paste.md"), "w", encoding="utf-8") as f:
            f.write(SAMPLE)
        with open(os.path.join(kb, "inbox", "2026-09-13-note-vendor-call.md"), "w", encoding="utf-8") as f:
            f.write("Just text.\n")
        with open(os.path.join(kb, "inbox", "m.md"), "w", encoding="utf-8") as f:
            f.write("handoff: meeting\ndate: 2026-09-12\nsubject: Vendor sync\n\n## Transcript\n[00:00:01] A: hi\n")
        with open(os.path.join(kb, "inbox", "refused.md"), "w", encoding="utf-8") as f:
            f.write("---\nhandoff: email\ndate: 2026-09-15\n---\n### E1 — secret\n")
        with open(os.path.join(kb, "inbox", "bad.md"), "w", encoding="utf-8") as f:
            f.write("no header at all\n")
        rc = run(kb)
        assert rc == 1  # refused.md and bad.md stay
        for rel in ["topics/ai/links/2026-09-15.md", "topics/platform/links/2026-09-15.md",
                    "notes/2026-09-13-vendor-call.md", "meetings/2026-09-12-vendor-sync.md",
                    "archive/2026-09-15-topic-links.md", "inbox/bad.md", "inbox/refused.md"]:
            assert os.path.exists(os.path.join(kb, rel)), rel
        assert not os.path.exists(os.path.join(kb, "email"))
        with open(os.path.join(kb, "topics/ai/links/2026-09-15.md"), encoding="utf-8") as f:
            t = f.read()
        assert "topic: ai" in t and "https://example.org/b" in t and "example.org/c" not in t, t
        # second paste same day -> .2 ; and a drifted file with a from column warns
        with open(os.path.join(kb, "inbox", "again.md"), "w", encoding="utf-8") as f:
            f.write(SAMPLE.replace("| url | title | one-line |", "| url | title | from | one-line |"))
        os.remove(os.path.join(kb, "inbox", "bad.md"))
        os.remove(os.path.join(kb, "inbox", "refused.md"))
        assert run(kb) == 0
        assert os.path.exists(os.path.join(kb, "topics/ai/links/2026-09-15.2.md"))
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
