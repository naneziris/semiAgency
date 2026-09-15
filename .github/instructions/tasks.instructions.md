---
applyTo: "engagements/**/tasks.json"
---
# tasks.json schema — staged before append_tasks.py (gate G5)
```json
{"tasks": [
  {"action": "Send Jan the integration estimate", "owner": "me", "due": "2026-09-18",
   "depends_on": [], "source": "T1 00:41:10", "notes": ""}
 ],
 "candidates": [ {"action": "…", "why_candidate": "implied, not committed", "source": "T1 00:52:00"} ]}
```
- `action`: imperative, one line, names the person and the thing. Required.
- `owner`: `me` or `delegate:<person-slug>`. A delegated task's `notes` starts with the one-line ask you would send.
- `due`: only a date stated or clearly implied by the source (`"by Thursday"` → the date); else `null`. Never invent.
- `source`: the meeting file + timestamp (`T1 00:41:10`) or `[notes]`.
- `tasks` holds only explicit commitments or clearly assigned actions. Anything inferred goes under `candidates` with `why_candidate`; candidates are never appended.
- Keep ids stable: the tracker dedups on (source, engagement, action), so do not rephrase an action that already exists in `tracker/actions.csv`.
