---
applyTo: "engagements/**/tasks.json"
---
# tasks.json schema — staged before append_tasks.py (gate G5)
```json
{"tasks": [
  {"action": "Send Jan the integration estimate", "owner": "me", "due": "2026-09-18",
   "urgency": "normal", "effort": "S", "depends_on": [], "source": "T1 00:41:10", "context": "2026-09-acme",
   "notes": ""}
 ],
 "candidates": [ {"action": "…", "why_candidate": "implied, not committed", "source": "T1 00:52:00"} ]}
```
- `action`: imperative, one line, names the person and the thing. Required.
- `owner`: `me` or `delegate:<person-slug>`. A delegated task's `notes` starts with the one-line ask you would send.
- `due`: only a date stated or clearly implied by the source (`"by Thursday"` → the date); else `null`. Never invent.
- `urgency`: `high` (today/tomorrow or a person is blocked), `normal`, `low`. `effort`: `S` <30 min, `M` half a day, `L` more. Both optional.
- `source`: the meeting file + timestamp (`T1 00:41:10`) or `[notes]`. `context`: the engagement name (filled by append_tasks.py if omitted).
- `tasks` holds only explicit commitments or clearly assigned actions. Anything inferred goes under `candidates` with `why_candidate`; candidates are never appended.
- Keep ids stable: the tracker dedups on (source, context, action), so do not rephrase an action that already exists in `tracker/actions.xlsx`.
