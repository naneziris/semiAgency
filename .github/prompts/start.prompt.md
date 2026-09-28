---
mode: agent
description: "[start here] Not sure what to run? Tells you where you are and the one next step"
---
What the user wants: `${input:want}` (empty, or still a placeholder, means they said nothing). Agent: `@guide` (read-only: you point, the user runs).

## 1. Where am I
Run `python scripts/where.py` in the terminal and read its output. Do not work out the state yourself: its `next`, `where` and `command` lines are the next step, copied exactly. If it says no engagement is in progress, nothing is in progress.

## 2. Answer
- **The user said what they want** (above, or in the chat): match it to one numbered item in `docs/menu.md` and go to step 3. If it continues the current engagement, give its next step from section 1.
- **An engagement is in progress and they said nothing:** reply in this shape and stop:
  "You're on **<engagement>** (<kind>). Done: <its done line>. Next: <its next line>." + "In <its where>:" + its command in a code block (or, when `where` says by hand, the instruction as plain text) + any `note` lines + "Do that, or something else?"
- **Nothing in progress and they said nothing:** read `docs/menu.md` and show its `##` items as a numbered list, one line each (the title only), grouped under "Here in VS Code" and "In Microsoft 365" by their `where`, plus a last line "Explain how this works". Ask "Which one?" and stop.

## 3. For a chosen item
One message, then stop:
1. **You get:** … · **Time:** … · **Bring:** … (from the menu, one line each).
2. **First step:** the item's first step from the menu. If it has a command, say where it runs and put the exact command in a code block. For the VS Code flows this is starting an engagement (`python scripts/new_engagement.py`) unless one of the same kind is already in progress. If it has no command (most Microsoft 365 items), say in plain words what to do, name the file to follow from its `read:` line, and put no code block.
3. "When that's done, run `/start` again and I'll give you the next step." Offer "all the steps" only as a closing half-sentence; show them only if asked.

"Explain how this works" → five lines at most from the menu, then name the one file to read (`docs/after-meeting.md` for the VS Code flows, the `read:` file of the item otherwise). Something not on the menu → run `python scripts/wish.py "<what they want, in their words>"`, then say in three lines: this workspace doesn't do that yet; it's noted in `wishlist.md`; "Want to design it now? In Copilot Chat: `/new-flow <the wish>`". Name a closest item only if it really covers part of the wish. Stop.
