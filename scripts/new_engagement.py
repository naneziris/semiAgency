#!/usr/bin/env python3
"""Start an engagement. Stdlib only. Run it right after a meeting, with no arguments.

  python scripts/new_engagement.py                  # asks kind, subject, name, stakeholders, audience, minutes;
                                                    # then waits until you have put your files into inputs/ and
                                                    # prints the exact Copilot prompt to paste next
  python scripts/new_engagement.py --check [dir]    # re-run the inputs/ check + next step (default: current engagement)
  python scripts/new_engagement.py --use <name>     # make an existing engagement the current one
  python scripts/new_engagement.py --kind meeting --name 2026-09-16-vendor-sync --no-wait   # scripted; missing answers are asked
  python scripts/new_engagement.py --selftest

Writes engagements/<name>/ (inputs/, normalized/, followups/, state.json, inputs/audience.md for proposal and deck)
and engagements/CURRENT, which every other script and every Copilot prompt uses when no engagement is given.
Artifact templates are NOT copied into the engagement: Copilot reads templates/ directly, and status.py infers
progress from which artifacts exist, so empty copies would mislead it.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

KINDS = {
    "proposal": {
        "menu": "stakeholders told me what they need; I will sketch 2-3 approaches, propose one,\n"
                "                present it, and give my team tasks",
        "asks": ["subject", "stakeholders", "audience", "minutes"],
        "minutes": 20,
        "name_date": "%Y-%m",
        "first_prompt": "/discovery-synthesize",
        "runbook": "docs/runbooks/proposal.md",
    },
    "deck": {
        "menu": "the content is already decided; I need a presentation for an audience",
        "asks": ["subject", "audience", "minutes"],
        "minutes": 15,
        "name_date": "%Y-%m",
        "first_prompt": "/content",
        "runbook": "docs/runbooks/deck.md",
    },
    "meeting": {
        "menu": "I just want a one-page record and my action points in the tracker, no deck",
        "asks": ["subject"],
        "minutes": 0,
        "name_date": "%Y-%m-%d",
        "first_prompt": "/meeting-notes",
        "runbook": "docs/runbooks/meeting.md",
    },
}
KIND_ORDER = ["proposal", "deck", "meeting"]

DEFAULT_STATE = {
    "engagement": "", "kind": "proposal", "subject": "", "stakeholders": [], "audience": "", "minutes": 20,
    "stage": 0,
    "gates": {"G1": {"passed": False}, "G2": {"passed": False, "chosen_option": None},
              "G3": {"passed": False, "chosen_storyline": None}, "G4": {"passed": False}, "G5": {"passed": False}},
    "followups": 0,
}

READABLE = {".md", ".txt", ".docx", ".pptx", ".pdf"}
IGNORED = {"audience.md", ".gitkeep", ".DS_Store", "Thumbs.db"}
TIMESTAMP = re.compile(r"^\s*\[?\d{1,2}:\d{2}(:\d{2})?\]?\s+\S", re.M)

# --------------------------------------------------------------------------- helpers

ask = input  # replaced by the selftest


def say(msg=""):
    print(msg)


def eng_root(root):
    return os.path.join(root, "engagements")


def current_path(root):
    return os.path.join(eng_root(root), "CURRENT")


def read_current(root):
    p = current_path(root)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        name = f.read().strip()
    return name or None


def write_current(root, name):
    os.makedirs(eng_root(root), exist_ok=True)
    with open(current_path(root), "w", encoding="utf-8") as f:
        f.write(name + "\n")


def resolve_dir(root, arg):
    """`arg` may be None (current engagement), a name, or a path."""
    if arg:
        d = arg if os.path.isdir(arg) else os.path.join(eng_root(root), arg)
        if not os.path.isfile(os.path.join(d, "state.json")):
            raise SystemExit("no engagement at %s (no state.json)" % d)
        return os.path.abspath(d)
    name = read_current(root)
    if not name:
        raise SystemExit("no current engagement: run python scripts/new_engagement.py, or --use <name>")
    return os.path.join(eng_root(root), name)


def slugify(text, limit=40):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].rstrip("-") or "engagement"


def load_state_template(root):
    p = os.path.join(root, "templates", "state.json")
    state = json.loads(json.dumps(DEFAULT_STATE))
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            state.update(json.load(f))
    return state


# --------------------------------------------------------------------------- questions

def ask_kind():
    say("What do you need from this meeting?")
    for i, k in enumerate(KIND_ORDER, 1):
        say("  %d  %-9s %s" % (i, k, KINDS[k]["menu"]))
    while True:
        a = ask("Choose 1, 2 or 3: ").strip().lower()
        if a in ("1", "2", "3"):
            return KIND_ORDER[int(a) - 1]
        if a in KINDS:
            return a
        say("  please answer 1, 2 or 3")


def ask_text(prompt, default=None, required=False):
    while True:
        a = ask("%s%s: " % (prompt, (" [%s]" % default) if default else "")).strip()
        if a:
            return a
        if default is not None:
            return default
        if not required:
            return ""
        say("  this one is needed")


def ask_int(prompt, default):
    while True:
        a = ask("%s [%d]: " % (prompt, default)).strip()
        if not a:
            return default
        if a.isdigit():
            return int(a)
        say("  a number, please")


def ask_name(root, kind, subject, today):
    default = "%s-%s" % (today.strftime(KINDS[kind]["name_date"]), slugify(subject))
    while True:
        name = ask_text("Folder name under engagements/", default)
        name = slugify(name, 60) if name != default else name
        if os.path.exists(os.path.join(eng_root(root), name)):
            say("  engagements/%s already exists; pick another name (or --use %s to continue it)" % (name, name))
            continue
        return name


def collect(root, args, today, interactive):
    """Return the answers for create(); asks for whatever the flags did not provide."""
    kind = args.kind
    if not kind:
        if not interactive:
            raise SystemExit("--kind is required when not running interactively")
        kind = ask_kind()
    spec = KINDS[kind]
    a = {"kind": kind, "subject": args.subject or "", "stakeholders": args.stakeholders or "",
         "audience": args.audience or "", "minutes": args.minutes, "name": args.name}
    if interactive:
        if "subject" in spec["asks"] and not a["subject"]:
            a["subject"] = ask_text("Subject, in a few words (e.g. 'Acme ops automation', 'vendor sync')", required=True)
        if not a["name"]:
            a["name"] = ask_name(root, kind, a["subject"], today)
        if "stakeholders" in spec["asks"] and not a["stakeholders"]:
            a["stakeholders"] = ask_text("Stakeholders, comma-separated with role (e.g. 'Maria K (Ops lead), Jan D (IT)')")
        if "audience" in spec["asks"] and not a["audience"]:
            a["audience"] = ask_text("Audience of the presentation, one line (e.g. 'Ops leadership')")
        if "minutes" in spec["asks"] and a["minutes"] is None:
            a["minutes"] = ask_int("Presentation slot in minutes", spec["minutes"])
    if not a["name"]:
        if not a["subject"]:
            raise SystemExit("--name (or --subject) is required when not running interactively")
        a["name"] = "%s-%s" % (today.strftime(spec["name_date"]), slugify(a["subject"]))
    if a["minutes"] is None:
        a["minutes"] = spec["minutes"]
    return a


# --------------------------------------------------------------------------- create

def create(root, kind, name, subject="", stakeholders="", audience="", minutes=None, from_dir=None):
    d = os.path.join(eng_root(root), name)
    if os.path.exists(d):
        raise SystemExit("refusing to overwrite existing %s" % d)
    if from_dir and not os.path.isdir(os.path.join(from_dir, "inputs")):
        raise SystemExit("--from %s has no inputs/ folder" % from_dir)
    for sub in ("inputs", "normalized", "followups"):
        os.makedirs(os.path.join(d, sub))
    state = load_state_template(root)
    state.update({
        "engagement": name, "kind": kind, "subject": subject,
        "stakeholders": [s.strip() for s in stakeholders.split(",") if s.strip()] if isinstance(stakeholders, str) else list(stakeholders),
        "audience": audience, "minutes": minutes if minutes is not None else KINDS[kind]["minutes"],
        "stage": 0, "followups": 0, "created": dt.date.today().isoformat(),
    })
    for g in state["gates"].values():
        g["passed"] = False
        for k in list(g):
            if k.startswith("chosen_"):
                g[k] = None
    with open(os.path.join(d, "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    if from_dir:
        for sub in ("inputs", "normalized"):
            src = os.path.join(from_dir, sub)
            if os.path.isdir(src):
                shutil.rmtree(os.path.join(d, sub))
                shutil.copytree(src, os.path.join(d, sub))
    if kind in ("proposal", "deck") and not os.path.exists(os.path.join(d, "inputs", "audience.md")):
        tpl = os.path.join(root, "templates", "audience.md")
        if os.path.exists(tpl):
            shutil.copy(tpl, os.path.join(d, "inputs", "audience.md"))
    write_current(root, name)
    return d


# --------------------------------------------------------------------------- inputs check

def classify(path):
    base = os.path.basename(path)
    ext = os.path.splitext(base)[1].lower()
    low = base.lower()
    if ext not in READABLE:
        return "unreadable"
    if ext == ".pdf":
        return "pdf"
    if ext == ".pptx":
        return "draft deck"
    if ext == ".docx":
        return "document"
    if "transcript" in low:
        return "transcript"
    if "notes" in low:
        return "notes"
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            head = f.read(4000)
    except OSError:
        return "document"
    if len(TIMESTAMP.findall(head)) >= 3:
        return "transcript"
    return "document"


def check_inputs(d):
    """Print what is in inputs/ and return {category: [files]}."""
    inp = os.path.join(d, "inputs")
    found = {}
    for base in sorted(os.listdir(inp)) if os.path.isdir(inp) else []:
        p = os.path.join(inp, base)
        if base in IGNORED or not os.path.isfile(p):
            continue
        found.setdefault(classify(p), []).append(base)
    say()
    if not any(found.values()):
        say("inputs/ is empty.")
        return found
    say("Found in inputs/:")
    for cat in ("transcript", "notes", "document", "draft deck", "pdf", "unreadable"):
        for base in found.get(cat, []):
            say("  %-10s %s" % (cat, base))
    warnings = []
    if "transcript" not in found and "notes" not in found:
        warnings.append("no transcript and no notes: add at least one, or the synthesis has nothing to cite")
    if "transcript" not in found:
        warnings.append("no transcript: if Teams did not send one, ask M365 Copilot Chat to reproduce it as "
                        "'[hh:mm:ss] Speaker: text' lines and save it as inputs/transcript.md")
    for base in found.get("pdf", []):
        warnings.append("%s: PDF text extraction is best-effort; open it in Word and save as .docx if the result looks wrong" % base)
    for base in found.get("unreadable", []):
        warnings.append("%s: not a type ingest.py reads (.md .txt .docx .pptx .pdf); save it as .docx or .md" % base)
    for w in warnings:
        say("  ! " + w)
    return found


def next_step(root, d):
    with open(os.path.join(d, "state.json"), encoding="utf-8") as f:
        state = json.load(f)
    kind = state.get("kind", "proposal")
    name = state.get("engagement") or os.path.basename(os.path.normpath(d))
    say()
    if kind in ("proposal", "deck"):
        say("Optional but worth 10 minutes: fill inputs/audience.md (who is in the room, what they decide, what they push back on).")
    say("Next, in Copilot Chat (agent mode), paste:")
    say("    %s engagement=%s" % (KINDS[kind]["first_prompt"], name))
    say("When it stops, in the terminal:")
    say("    python scripts/status.py")
    say("It prints the checklist for the gate and the exact command to pass it. Guide: docs/after-meeting.md")


def open_folder(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa
        elif sys.platform == "darwin":
            import subprocess
            subprocess.Popen(["open", path])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


def wait_for_inputs(root, d):
    inp = os.path.join(d, "inputs")
    say()
    say("Created engagements/%s (now the current engagement)." % os.path.basename(d))
    say("Put your material into %s:" % os.path.relpath(inp, root))
    say("  transcript.md   the Teams transcript (.md)")
    say("  notes.md        your own notes")
    say("  documents       .docx / .pptx / .md (PDF: open in Word, save as .docx first)")
    say("Never edit these files afterwards; every fact will cite them.")
    if ask("Open the inputs folder now? [Y/n]: ").strip().lower() not in ("n", "no"):
        if not open_folder(inp):
            say("  (could not open a file browser; the path is above)")
    while True:
        a = ask("Press Enter when the files are in place, or type 'later': ").strip().lower()
        found = check_inputs(d)
        if a == "later":
            say("When they are: python scripts/new_engagement.py --check")
            return
        if not any(found.values()):
            say("Nothing there yet.")
            continue
        next_step(root, d)
        return


# --------------------------------------------------------------------------- selftest

def _selftest():
    global ask
    answers = []
    ask = lambda prompt="": answers.pop(0)  # noqa: E731
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "templates"))
        with open(os.path.join(root, "templates", "state.json"), "w") as f:
            json.dump(DEFAULT_STATE, f)
        with open(os.path.join(root, "templates", "audience.md"), "w") as f:
            f.write("# Audience brief\n")
        today = dt.date(2026, 9, 16)
        ns = argparse.Namespace(kind=None, name=None, subject=None, stakeholders=None, audience=None, minutes=None)

        # interactive proposal
        answers[:] = ["1", "Acme ops automation", "", "Maria K (Ops lead), Jan D (IT)", "Ops leadership", ""]
        a = collect(root, ns, today, interactive=True)
        assert a["kind"] == "proposal" and a["name"] == "2026-09-acme-ops-automation" and a["minutes"] == 20, a
        d = create(root, **a)
        st = json.load(open(os.path.join(d, "state.json")))
        assert st["kind"] == "proposal" and st["stakeholders"] == ["Maria K (Ops lead)", "Jan D (IT)"]
        assert st["audience"] == "Ops leadership" and not st["gates"]["G1"]["passed"] and st["engagement"] == a["name"]
        assert os.path.exists(os.path.join(d, "inputs", "audience.md"))
        assert read_current(root) == a["name"]
        try:
            create(root, **a)
            raise AssertionError("should refuse to overwrite")
        except SystemExit:
            pass

        # name collision is caught while asking
        answers[:] = ["3", "Acme ops automation", "2026-09-acme-ops-automation", "vendor-sync"]
        a2 = collect(root, ns, today, interactive=True)
        assert a2["kind"] == "meeting" and a2["name"] == "vendor-sync", a2

        # non-interactive meeting with --from
        with open(os.path.join(d, "inputs", "transcript.md"), "w") as f:
            f.write("[00:00:01] Maria: hello\n[00:00:05] Jan: hi\n[00:00:09] Maria: ok\n")
        ns2 = argparse.Namespace(kind="meeting", name="2026-09-16-vendor-sync", subject=None, stakeholders=None, audience=None, minutes=None)
        a3 = collect(root, ns2, today, interactive=False)
        d3 = create(root, **a3)
        assert not os.path.exists(os.path.join(d3, "inputs", "audience.md"))
        assert json.load(open(os.path.join(d3, "state.json")))["minutes"] == 0
        assert read_current(root) == "2026-09-16-vendor-sync"
        d4 = create(root, kind="deck", name="2026-09-acme-deck", from_dir=d)
        assert os.path.exists(os.path.join(d4, "inputs", "transcript.md")) and os.path.exists(os.path.join(d4, "inputs", "audience.md"))
        with open(os.path.join(d3, "inputs", "transcript.md"), "w") as f:
            f.write("[00:00:01] Maria: hello\n[00:00:05] Jan: hi\n[00:00:09] Maria: ok\n")

        # inputs classification
        inp = os.path.join(d3, "inputs")
        with open(os.path.join(inp, "call.md"), "w") as f:
            f.write("[00:01:00] A: x\n[00:02:00] B: y\n[00:03:00] A: z\n")
        with open(os.path.join(inp, "my-notes.md"), "w") as f:
            f.write("- point\n")
        for n in ("spec.docx", "draft.pptx", "report.pdf", "data.xlsx"):
            open(os.path.join(inp, n), "wb").close()
        found = check_inputs(d3)
        assert set(found["transcript"]) == {"transcript.md", "call.md"}, found
        assert found["notes"] == ["my-notes.md"] and found["document"] == ["spec.docx"]
        assert found["draft deck"] == ["draft.pptx"] and found["pdf"] == ["report.pdf"] and found["unreadable"] == ["data.xlsx"]

        # wait loop: 'later' path, then Enter path
        answers[:] = ["n", "later"]
        wait_for_inputs(root, d3)
        answers[:] = ["n", ""]
        wait_for_inputs(root, d3)

        # --use and resolve
        write_current(root, a["name"])
        assert resolve_dir(root, None) == d
        assert resolve_dir(root, "2026-09-16-vendor-sync") == os.path.abspath(d3)
        assert slugify("  Q3 -- Platform Status!! ") == "q3-platform-status"
    print("new_engagement selftest OK")


# --------------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kind", choices=KIND_ORDER)
    ap.add_argument("--name")
    ap.add_argument("--subject")
    ap.add_argument("--stakeholders", help="comma-separated, e.g. \"Maria K (Ops lead), Jan D (IT)\"")
    ap.add_argument("--audience")
    ap.add_argument("--minutes", type=int)
    ap.add_argument("--from", dest="from_dir", help="copy inputs/ and normalized/ from another engagement")
    ap.add_argument("--no-wait", action="store_true", help="do not wait for inputs/ after creating")
    ap.add_argument("--check", nargs="?", const="", metavar="DIR", help="re-run the inputs/ check and print the next step")
    ap.add_argument("--use", metavar="NAME", help="make an existing engagement the current one")
    ap.add_argument("--root", default=ROOT, help=argparse.SUPPRESS)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    root = args.root
    if args.use:
        d = resolve_dir(root, args.use)
        write_current(root, os.path.basename(d))
        say("current engagement: %s" % os.path.basename(d))
        next_step(root, d)
        return 0
    if args.check is not None:
        d = resolve_dir(root, args.check or None)
        check_inputs(d)
        next_step(root, d)
        return 0
    interactive = sys.stdin.isatty() or not args.kind
    a = collect(root, args, dt.date.today(), interactive)
    d = create(root, from_dir=args.from_dir, **a)
    if args.no_wait or not sys.stdin.isatty():
        say("created engagements/%s (current). Put transcript.md, notes.md and documents into inputs/, then:" % a["name"])
        say("    python scripts/new_engagement.py --check")
        return 0
    wait_for_inputs(root, d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
