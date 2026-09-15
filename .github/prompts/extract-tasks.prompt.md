---
mode: agent
description: Extract team tasks from the team meeting into tasks.json (not yet appended)
---
Engagement: `engagements/${input:engagement}`. Meeting file: `${input:file}`. Owner filter: `${input:owner}` (`all` or `me`; default all).
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read the normalized meeting file.
2. Write `tasks.json`: array of `{ "action", "owner", "due" (ISO date or null), "depends_on" (array of action text or []), "source" (file + timestamp), "notes" }`. If owner filter is `me`, include only the user's own actions under `tasks` and everyone else's under `candidates`. Only explicit commitments or clearly assigned actions; put maybes under a top-level `"candidates"` array instead.
3. Run `python scripts/validate.py engagements/${input:engagement}/tasks.json`.
4. Stop. Tell the user to review, then run `python scripts/append_tasks.py engagements/${input:engagement}` themselves (gate G5).
