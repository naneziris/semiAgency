#!/usr/bin/env python3
"""Add a prompt to the agency in one go: the .prompt.md file, its building on the map, its stop on a route,
then rebuild the map and the menu.

    python scripts/new_prompt.py              # asks everything, one question at a time
    python scripts/new_prompt.py --name weekly-report --description "[any] One-page weekly report" \\
        --district record --building "Weekly Desk" --pitch "…" --journey new --q "Write my weekly report" …

Without this script, a new prompt file is still found by build_city.py — it lands in "New Arrivals" — but
the /start guide cannot send anyone to it until it is a stop on a route (build_menu.py --check fails). This
script does the three things together so a prompt is never half-added. Python 3 standard library only.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHAPES = ["house", "small", "columns", "studio", "factory", "dome", "warehouse", "tower", "office",
          "lighthouse", "clock", "embassy", "observatory", "workshop", "construction"]
MODES = ["prompt", "run", "paste", "read", "setup", "click", "auto"]
BODY = """<Write here what Copilot must do when the user types /{name}. Keep the style of the other prompts in this
folder: numbered steps, say which files to read and what to write where, and when to stop and ask.>

1. Read …
2. Write … per `.github/instructions/….instructions.md`.
3. Stop. Tell the user what you wrote and what the next step is.
"""


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def ask(label, default=None, required=True, validate=None):
    while True:
        hint = f" [{default}]" if default else ""
        v = input(f"{label}{hint}: ").strip()
        if not v and default is not None:
            v = default
        if not v and required:
            print("  (needed)")
            continue
        if v and validate:
            err = validate(v)
            if err:
                print("  " + err)
                continue
        return v


def pick(label, options, default=None):
    """options: list of (key, text). Returns the key."""
    print(label)
    for i, (k, t) in enumerate(options, 1):
        print(f"  {i}) {t}")
    while True:
        v = input(f"number{f' [{default}]' if default else ''}: ").strip() or (default or "")
        if v.isdigit() and 1 <= int(v) <= len(options):
            return options[int(v) - 1][0]
        for k, _ in options:
            if v == k:
                return k
        print("  pick a number from the list")


def load_city(root):
    p = os.path.join(root, "city", "city.json")
    with open(p, encoding="utf-8") as fh:
        return json.load(fh), p


def add(root, a, interactive):
    city, cpath = load_city(root)
    prompts_dir = os.path.join(root, ".github", "prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    existing = {f[:-len(".prompt.md")] for f in os.listdir(prompts_dir) if f.endswith(".prompt.md")}
    bids = {b["id"] for b in city["buildings"]}
    districts = [d for d in city["districts"] if not d.get("auto")]
    journeys = city["journeys"]

    def ok_name(v):
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", v):
            return "lowercase letters, digits and dashes only"
        if v in existing:
            return f"/{v} exists already"
        return None

    name = a.name if a.name else ask("Command name (users will type /name)", validate=ok_name)
    if err := ok_name(name):
        sys.exit("error: " + err)
    description = a.description or ask("One-line description, shown in Copilot's prompt picker (start with [kind])",
                                       default="[any] " + name.replace("-", " ").capitalize())
    district = a.district or pick("Which area of the map does it belong to?", [(d["id"], f"{d['name']} — {d['subtitle'][:70]}") for d in districts])
    if district not in {d["id"] for d in districts}:
        sys.exit(f"error: unknown district {district}; one of " + ", ".join(d["id"] for d in districts))
    building = a.building or ask("Building name on the map", default=name.replace("-", " ").title())
    bid = slug(building)
    if bid in bids:
        bid = slug(building + "-" + name)
    sub = a.sub if a.sub is not None else ask("Subtitle under the name (a few words, what it gives you)", required=False)
    pitch = a.pitch or ask("Pitch: one or two sentences, what it does and when")
    shape = a.shape or pick("Building shape", [(s, s) for s in SHAPES], default="1")
    mode = a.mode or "prompt"
    say = a.say or "In VS Code, Copilot Chat (agent mode):"
    copy = a.copy or f"/{name}"
    jid = a.journey
    if not jid:
        jid = pick("Which route ('I want to…') does it belong to?",
                   [("new", "a new route of its own")] + [(j["id"], j["q"]) for j in journeys], default="1")
    stop_say = a.stop_say or (ask("One line for its stop on the route (what happens here)", default=sub or pitch.split(". ")[0])
                              if interactive else (sub or pitch.split(". ")[0]))
    new_j = None
    if jid == "new":
        q = a.q or ask("The route's wish, as the user would say it ('I want to…')", default=building)
        when = a.when or ask("When does this route apply? (one sentence)", default=pitch.split(". ")[0])
        bring = a.bring or ask("You bring", default="your notes", required=False)
        get = a.get or ask("You get", default=sub or "the result", required=False)
        time = a.time or ask("Takes", default="10 minutes", required=False)
        jid = slug(q)[:40] if slug(q) not in {j["id"] for j in journeys} else slug(q)[:40] + "-" + name
        new_j = {"id": jid, "area": district, "audience": "vscode", "q": q, "when": when, "bring": bring,
                 "get": get, "time": time, "stops": [{"building": bid, "say": stop_say}]}
    elif jid not in {j["id"] for j in journeys}:
        sys.exit(f"error: unknown route {jid}")

    # 1. the prompt file
    ppath = os.path.join(prompts_dir, name + ".prompt.md")
    with open(ppath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"---\nmode: agent\ndescription: \"{description}\"\n---\n" + BODY.format(name=name))
    # 2. the building and its stop
    city["buildings"].append({"id": bid, "district": district, "name": building, "sub": sub, "shape": shape,
                              "mode": mode, "audience": "vscode", "pitch": pitch,
                              "steps": [{"say": say, "copy": copy}], "prompts": [name]})
    if new_j:
        journeys.append(new_j)
    else:
        next(j for j in journeys if j["id"] == jid)["stops"].append({"building": bid, "say": stop_say})
    with open(cpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(city, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return name, bid, jid, ppath


def rebuild(root):
    for s in ("build_city.py", "build_menu.py", "sync_opencode.py"):
        p = os.path.join(root, "scripts", s)
        if os.path.exists(p):
            print(f"\n$ python scripts/{s}")
            subprocess.run([sys.executable, p], cwd=root)


def _selftest():
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "city"))
        os.makedirs(os.path.join(tmp, ".github", "prompts"))
        city = {"districts": [{"id": "record", "name": "Notary Corner", "subtitle": "records"},
                              {"id": "arrivals", "name": "New", "subtitle": "", "auto": True}],
                "buildings": [{"id": "notary", "district": "record", "name": "The Notary", "steps": [], "prompts": ["meeting-notes"]}],
                "journeys": [{"id": "meeting", "area": "record", "audience": "vscode", "q": "Record a meeting",
                              "stops": [{"building": "notary", "say": "x"}]}]}
        json.dump(city, open(os.path.join(tmp, "city", "city.json"), "w"))
        ns = argparse.Namespace(name="weekly-report", description="[any] Weekly report", district="record", building="The Notary",
                                sub="your week on one page", pitch="Writes the weekly report. Ten minutes.", shape="house", mode=None,
                                say=None, copy=None, journey="meeting", stop_say=None, q=None, when=None, bring=None, get=None, time=None)
        name, bid, jid, ppath = add(tmp, ns, interactive=False)
        assert name == "weekly-report" and bid == "the-notary" and jid == "meeting", (bid, jid)
        c = json.load(open(os.path.join(tmp, "city", "city.json")))
        assert c["buildings"][-1]["prompts"] == ["weekly-report"] and c["buildings"][-1]["steps"][0]["copy"] == "/weekly-report"
        assert c["journeys"][0]["stops"][-1] == {"building": bid, "say": "your week on one page"}
        assert open(ppath).read().startswith('---\nmode: agent\ndescription: "[any] Weekly report"\n---\n')
        ns2 = argparse.Namespace(name="daily-log", description="[any] Daily log", district="record", building="Log House", sub="",
                                 pitch="Keeps a log.", shape="small", mode=None, say=None, copy=None, journey="new", stop_say="Write the log.",
                                 q="Keep a daily log", when="Every evening.", bring="nothing", get="a log entry", time="2 minutes")
        name, bid, jid, _ = add(tmp, ns2, interactive=False)
        c = json.load(open(os.path.join(tmp, "city", "city.json")))
        assert jid == "keep-a-daily-log" and c["journeys"][-1]["stops"] == [{"building": "log-house", "say": "Write the log."}]
        try:
            add(tmp, ns, interactive=False)
            assert False, "duplicate name must fail"
        except SystemExit:
            pass
    finally:
        shutil.rmtree(tmp)
    print("new_prompt selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for f in ("name", "description", "district", "building", "sub", "pitch", "shape", "mode", "say", "copy",
              "journey", "stop_say", "q", "when", "bring", "get", "time"):
        ap.add_argument("--" + f.replace("_", "-"), dest=f)
    ap.add_argument("--no-build", action="store_true", help="do not run build_city / build_menu afterwards")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return
    if a.shape and a.shape not in SHAPES:
        sys.exit("error: shape must be one of " + ", ".join(SHAPES))
    if a.mode and a.mode not in MODES:
        sys.exit("error: mode must be one of " + ", ".join(MODES))
    interactive = not a.name
    name, bid, jid, ppath = add(ROOT, a, interactive)
    print(f"\nAdded /{name}: {os.path.relpath(ppath, ROOT)}, building '{bid}' on route '{jid}' in city/city.json.")
    if not a.no_build:
        rebuild(ROOT)
    print(f"\nNext: open {os.path.relpath(ppath, ROOT)} and write the instructions (the body is a skeleton), "
          f"then in Copilot Chat: /{name}. Commit when it works: git add -A && git commit -m \"new prompt: /{name}\"")


if __name__ == "__main__":
    main()
