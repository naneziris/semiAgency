---
mode: agent
description: Prepare for a 1-1 from local history (when the M365 1-1 Prep agent was not run) — workflow #4
---
Person: `${input:person}` (the name you use, e.g. `Maria K`). Use `@librarian`.
1. Slug the name (`maria-k`). Read `kb/people/<slug>/profile.md` if present and the 3 newest dated files in `kb/people/<slug>/`. If there are none, stop: tell the user to run the **1-1 Prep** agent in M365 Copilot Chat (it reads OneNote) and paste the result into `kb/inbox/`.
2. Read `tracker/actions.xlsx` via `python scripts/xlsxlite.py --dump tracker/actions.xlsx` and keep the open rows whose owner is `delegate:<slug>` or whose notes mention the person.
3. Write `kb/people/<slug>/<today>.prep.md` per `.github/instructions/people.instructions.md`. Follow-ups still open from two or more meetings ago go first in the agenda. Cite the file each item came from.
4. Stop. Print the suggested agenda and, if it is empty, the one-line "consider cancelling" note (the user decides).
