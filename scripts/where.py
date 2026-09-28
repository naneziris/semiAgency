#!/usr/bin/env python3
"""Where am I? Read-only: prints the current engagement, what is done, and the one next step.

The /start guide runs this instead of working it out itself, so small models get it right.
It never writes anything. (status.py, built on the corporate machine, also shows checklists and passes gates.)

Usage:
  python scripts/where.py                 current engagement (engagements/CURRENT)
  python scripts/where.py engagements/<name>
  python scripts/where.py --selftest
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT = "Copilot Chat (agent mode)"
TERM = "the terminal"

# Per kind, in order: (kind of check, file or gate, what to do, where, command). The first row that applies wins.
# ("file", "x.md") applies when x.md does not exist; ("gate", "G1") applies when G1 is not passed.
RULES = {
    "meeting": [
        ("file", "notes.md", "write the notes and your actions", CHAT, "/meeting-notes"),
        ("gate", "G5", "review tasks.json, then send your actions to the tracker (this passes G5)", TERM,
         "python scripts/append_tasks.py"),
    ],
    "deck": [
        ("file", "content.md", "write the key messages and facts", CHAT, "/content"),
        ("gate", "G1", "check the facts Copilot flagged in content.md, then pass G1", None, None),
        ("file", "storylines.md", "write two storylines", CHAT, "/storylines"),
        ("gate", "G3", "pick S1 or S2 in storylines.md, then pass G3", None, None),
        ("file", "deck.json", "outline the deck, then build it with `python scripts/build_deck.py`", CHAT, "/deck-outline"),
        ("gate", "G4", "open deck.pptx before anyone else, then pass G4", None, None),
        ("file", "speech.md", "write the speaker notes", CHAT, "/speech"),
    ],
    "proposal": [
        ("file", "discovery.md", "turn the meeting into the fact base", CHAT, "/discovery-synthesize"),
        ("gate", "G1", "check the three items Copilot flagged in discovery.md, then pass G1", None, None),
        ("file", "options.md", "sketch 2-3 options", CHAT, "/options"),
        ("gate", "G2", "read options.md and choose an option, then pass G2", None, None),
        ("file", "proposal.md", "write the proposal and two storylines", CHAT, "/proposal"),
        ("gate", "G3", "pick S1 or S2 in storylines.md, then pass G3", None, None),
        ("file", "deck.json", "outline the deck, then build it with `python scripts/build_deck.py`", CHAT, "/deck-outline"),
        ("gate", "G4", "open deck.pptx before anyone else, then pass G4", None, None),
        ("file", "speech.md", "write the speaker notes", CHAT, "/speech"),
        ("file", "critique.md", "have the critic review it (recommended before presenting)", CHAT, "@critic /critique"),
        ("file", "team-brief.md", "after presenting: brief the team", CHAT, "/team-brief"),
        ("file", "tasks.json", "after the team meeting: turn it into tasks", CHAT,
         "/team-tasks file=inputs/<team meeting file>"),
        ("gate", "G5", "review tasks.json, then send the tasks to the tracker (this passes G5)", TERM,
         "python scripts/append_tasks.py"),
    ],
}
GATE_EXTRA = {"G2": ' and "chosen_option": "O1" (or O2/O3)', "G3": ' and "chosen_storyline": "S1" (or S2)'}


def current_dir(root):
    p = os.path.join(root, "engagements", "CURRENT")
    if not os.path.exists(p):
        return None
    name = open(p, encoding="utf-8").read().strip()
    return os.path.join(root, "engagements", name) if name else None


def where(root, eng_dir=None):
    """Return a dict: engagement, kind, done (list), next (what, where, command) or None, notes (list)."""
    eng_dir = eng_dir or current_dir(root)
    if not eng_dir:
        return {"engagement": None}
    name = os.path.basename(os.path.normpath(eng_dir))
    sp = os.path.join(eng_dir, "state.json")
    if not os.path.exists(sp):
        return {"engagement": name, "error": "engagements/%s/state.json does not exist" % name}
    state = json.load(open(sp, encoding="utf-8"))
    kind = state.get("kind", "")
    gates = state.get("gates", {})
    has_status = os.path.exists(os.path.join(root, "scripts", "status.py"))
    done, nxt, notes = [], None, []
    for check, key, what, loc, cmd in RULES.get(kind, []):
        if check == "file":
            ok = os.path.exists(os.path.join(eng_dir, key))
        else:
            ok = bool(gates.get(key, {}).get("passed"))
        if ok:
            done.append(key if check == "file" else key + " passed")
            continue
        if check == "gate" and cmd is None:
            if has_status:
                loc, cmd = TERM, "python scripts/status.py --pass"
            else:
                loc = "by hand (status.py is not on this machine)"
                cmd = 'in engagements/%s/state.json set "passed": true under "%s"%s' % (name, key, GATE_EXTRA.get(key, ""))
        nxt = {"what": what, "where": loc, "command": cmd}
        break
    if kind == "proposal" and nxt and nxt["command"] == "/discovery-synthesize":
        inputs = os.path.join(eng_dir, "inputs")
        material = [f for f in (os.listdir(inputs) if os.path.isdir(inputs) else []) if f != "audience.md"]
        if not material and not os.path.exists(os.path.join(eng_dir, "brief.md")):
            notes.append("inputs/ has no transcript or notes yet. Meeting not held? Prepare it first: /discovery-prep")
    if kind == "meeting" and nxt is None:
        notes_md = os.path.join(eng_dir, "notes.md")
        if os.path.exists(notes_md) and "follow-up needed" in open(notes_md, encoding="utf-8").read().lower():
            notes.append("If notes.md says Follow-up needed: Y -> in the terminal: python scripts/followup_agenda.py")
    if kind not in RULES:
        notes.append("unknown kind %r in state.json" % kind)
    return {"engagement": name, "kind": kind, "done": done, "next": nxt, "notes": notes}


def render(w):
    if not w.get("engagement"):
        return "engagement: none in progress (engagements/CURRENT is missing or empty)\n"
    if w.get("error"):
        return "engagement: %s\nerror: %s\n" % (w["engagement"], w["error"])
    lines = ["engagement: %s (%s)" % (w["engagement"], w["kind"]),
             "done: " + (", ".join(w["done"]) if w["done"] else "nothing yet")]
    if w["next"]:
        lines += ["next: " + w["next"]["what"], "where: " + w["next"]["where"], "command: " + w["next"]["command"]]
    else:
        lines.append("next: nothing, this engagement is done")
    lines += ["note: " + n for n in w["notes"]]
    return "\n".join(lines) + "\n"


def _selftest():
    tmp = tempfile.mkdtemp()
    try:
        e = os.path.join(tmp, "engagements", "acme")
        os.makedirs(os.path.join(e, "inputs"))
        os.makedirs(os.path.join(tmp, "scripts"))
        assert where(tmp) == {"engagement": None}
        open(os.path.join(tmp, "engagements", "CURRENT"), "w").write("acme\n")
        st = {"kind": "proposal", "gates": {"G1": {"passed": True}, "G2": {"passed": False, "chosen_option": None}}}
        json.dump(st, open(os.path.join(e, "state.json"), "w"))
        w = where(tmp)
        assert w["next"]["command"] == "/discovery-synthesize" and any("discovery-prep" in n for n in w["notes"]), w
        for f in ("discovery.md", "options.md", "inputs/transcript.md"):
            open(os.path.join(e, f), "w").write("x")
        w = where(tmp)
        assert w["done"] == ["discovery.md", "G1 passed", "options.md"], w
        assert "choose an option" in w["next"]["what"] and '"chosen_option"' in w["next"]["command"], w
        assert "status.py" not in w["next"]["command"]
        open(os.path.join(tmp, "scripts", "status.py"), "w").write("")
        w = where(tmp)
        assert w["next"]["command"] == "python scripts/status.py --pass", w
        assert "next: read options.md" in render(w)
        json.dump({"kind": "meeting", "gates": {"G5": {"passed": True}}}, open(os.path.join(e, "state.json"), "w"))
        open(os.path.join(e, "notes.md"), "w").write("## Follow-up needed\nY")
        w = where(tmp)
        assert w["next"] is None and w["notes"] and "done" in render(w), w
        assert "state.json does not exist" in render(where(tmp, os.path.join(tmp, "engagements", "nope")))
    finally:
        shutil.rmtree(tmp)
    print("where selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("engagement", nargs="?", help="engagements/<name> (default: engagements/CURRENT)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return
    d = a.engagement
    if d and not os.path.isabs(d):
        d = os.path.join(ROOT, d) if not os.path.isdir(d) else os.path.abspath(d)
    sys.stdout.write(render(where(ROOT, d)))


if __name__ == "__main__":
    main()
