---
mode: agent
description: "[proposal] Team meeting notes/transcript → tasks.json for review (gate G5 follows)"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Meeting file: `${input:file}` (a path under inputs/). Owner filter: `${input:owner}` (`all` or `me`; default all). Agent: `@analyst`.
1. Run `python scripts/ingest.py <dir>` and read the normalized meeting file.
2. Write `tasks.json` per `.github/instructions/tasks.instructions.md`. Only explicit commitments or clearly assigned actions under `tasks`; maybes under `candidates`. With owner filter `me`, only the user's own actions go under `tasks`, everyone else's under `candidates`.
3. Run `python scripts/validate.py <dir>/tasks.json`.
4. Stop. Tell the user to review `tasks.json`, then run `python scripts/append_tasks.py` (appends and passes gate G5).
