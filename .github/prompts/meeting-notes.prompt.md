---
mode: agent
description: "[meeting] One-page write-up + my actions as tasks.json (gate G5 follows)"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Agent: `@analyst`.
0. Read `state.json`. If `kind` is not `meeting`, stop: proposals use `/discovery-synthesize`, decks `/content`.
1. Run `python scripts/ingest.py <dir>` and read everything in `normalized/`.
2. Write `notes.md` per `.github/instructions/notes.instructions.md`.
3. Write `tasks.json` per `.github/instructions/tasks.instructions.md` from `## My actions` (owner `me`) and `## Others' actions`: explicit commitments under `tasks`, maybes under `candidates`.
4. Run `python scripts/validate.py` on both files and fix errors.
5. Stop. Tell the user how many actions are theirs, that `python scripts/append_tasks.py` sends them to the tracker and passes gate G5, and — if `## Follow-up needed` is Y — that `python scripts/followup_agenda.py` writes the agenda and the .ics.
