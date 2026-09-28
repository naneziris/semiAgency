---
mode: agent
description: "[any] Turn a wish into a new flow: short interview, a one-screen design, then the files, the map entry and the menu"
---
The wish: `${input:wish}` (empty, or still a placeholder, means none given). Agent: `@builder`.

1. **Pick the wish.** If none was given, run `python scripts/wish.py --list`, show the open wishes numbered, and ask which one (or a new one). Stop until answered.
2. **Check it isn't here already.** Read `docs/menu.md`. If an item covers most of it, say which and what is missing, and ask: extend that item, or a new flow? If it needs what `docs/parked.md` says this setup can't do (schedules, reading mail, writing to M365), say so plainly and stop unless the user still wants a manual version.
3. **Interview, one question per message, five at most**, skipping what the wish already answers:
   - What do you hold in your hands at the end (a file, a message, a decision)?
   - What do you bring each time (files, a conversation, nothing)?
   - How often, and how long may it take?
   - Where should it run: VS Code, Microsoft 365, or both?
   - What must never happen (data that must not leave, things it must not decide for you)?
4. **Design, on one screen, then stop:** name and the command(s) the user will type; each step with its gate (where the user checks before moving on); the files it adds (prompts, agent only if needed, an instructions file per artifact, templates, scripts only for mechanics); where its data lives (gitignored if personal or confidential); the map entry (district, building name, one-line pitch). Ask: "Build it?"
5. **Build, only after a yes.** Write the files by the rules in `@builder`. Add the building to `city/city.json` (with `steps` whose `copy` is each command, and `prompts`/`agents` naming the new files) and a journey (`id`, `audience`, `q` phrased as the user's wish, `when`, `bring`, `get`, `time`, `stops`). Then run, in the terminal: `python scripts/build_menu.py`, `python scripts/build_city.py`, `python scripts/sync_opencode.py` (if it exists), `python scripts/selftest_all.py`, and fix what they report. In `wishlist.md`, append ` [built → /<command>]` to the wish's line.
6. **Hand over:** list the files you added, then: "In Copilot Chat: `/start <the wish in your words>`. It now knows the new flow. Then commit: `git add -A && git commit -m \"new flow: <name>\"`."
