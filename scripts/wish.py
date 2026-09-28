#!/usr/bin/env python3
"""Append-only wishlist: things you asked the agency for that it can't do yet.

The /start guide runs this when nothing on the menu matches, so the wish isn't lost.
/new-flow reads wishlist.md to design the next flow. This script never changes or deletes existing lines.

Usage:
  python scripts/wish.py "help me write a book about my life"
  python scripts/wish.py --list
  python scripts/wish.py --selftest
"""
import argparse
import datetime
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = ("# Wishlist\n\nThings asked of this agency that it can't do yet. Added by `/start` (via `scripts/wish.py`); "
          "`/new-flow` turns one into a flow and marks it `[built → /name]`.\n\n")


def add(root, text, today=None):
    text = " ".join(text.split())
    if not text:
        raise ValueError("empty wish")
    path = os.path.join(root, "wishlist.md")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(HEADER)
    existing = open(path, encoding="utf-8").read()
    line = "- %s: %s\n" % (today or datetime.date.today().isoformat(), text)
    if (": " + text + "\n") in existing:
        return path, False  # same wish already listed
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        if not existing.endswith("\n"):
            fh.write("\n")
        fh.write(line)
    return path, True


def open_wishes(root):
    path = os.path.join(root, "wishlist.md")
    if not os.path.exists(path):
        return []
    return [l.rstrip("\n") for l in open(path, encoding="utf-8") if l.startswith("- ") and "[built" not in l]


def _selftest():
    tmp = tempfile.mkdtemp()
    try:
        p, added = add(tmp, "write a  book\nabout my life", today="2026-09-25")
        assert added and open(p).read().endswith("- 2026-09-25: write a book about my life\n")
        _, added = add(tmp, "write a book about my life", today="2026-09-26")
        assert not added
        add(tmp, "plan my runs", today="2026-09-26")
        with open(p, "a") as fh:
            fh.write("- 2026-09-20: done thing [built → /done]\n")
        assert open_wishes(tmp) == ["- 2026-09-25: write a book about my life", "- 2026-09-26: plan my runs"]
        try:
            add(tmp, "   ")
            raise AssertionError("empty wish accepted")
        except ValueError:
            pass
    finally:
        shutil.rmtree(tmp)
    print("wish selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wish", nargs="*")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return
    if a.list or not a.wish:
        w = open_wishes(ROOT)
        print("\n".join(w) if w else "wishlist is empty")
        return
    path, added = add(ROOT, " ".join(a.wish))
    print(("added to " if added else "already on ") + os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
