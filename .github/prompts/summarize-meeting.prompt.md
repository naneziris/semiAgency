---
mode: agent
description: Write a one-page meeting write-up with my actions (kind = meeting)
---
Engagement: `engagements/${input:engagement}`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read everything in `normalized/`.
2. Write `notes.md` per `.github/instructions/notes.instructions.md`.
3. Write `tasks.json` from `## My actions` and `## Others' actions`: explicit commitments under `tasks` (owner "me" for the user's own), maybes under `candidates`.
4. Run `python scripts/validate.py` on both files and fix errors.
5. Stop. Tell the user how many actions are theirs, and that `python scripts/append_tasks.py engagements/${input:engagement}` sends them to the tracker (gate G5). If `## Follow-up needed` is Y, mention `python scripts/followup_agenda.py`.
