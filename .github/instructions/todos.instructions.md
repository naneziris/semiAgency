---
applyTo: "kb/**/*.todos.json"
---
# *.todos.json schema (email triage, 1-1 actions) — staged before append_tasks.py
```json
{"tasks": [
  {"action": "Confirm renewal terms with Sabine", "owner": "me", "due": "2026-09-18",
   "urgency": "high", "effort": "S", "depends_on": [], "source": "E1", "context": "2026-09-15",
   "notes": "price +8%, legal approved"}
 ],
 "candidates": [ {"action": "…", "why_candidate": "implied, not asked", "source": "E7"} ]}
```
- `action`: imperative, one line, names the person and the thing. Required.
- `owner`: `me` or `delegate:<person-slug>`. A delegated task's `notes` starts with the one-line ask you would send.
- `due`: only a date stated or clearly implied by the source (`"by Thursday"` → the date); else `null`. Never invent.
- `urgency`: `high` (today/tomorrow or a person is blocked), `normal`, `low`. `effort`: `S` <30 min, `M` half a day, `L` more.
- `source`: the email id (`E3`), the KB file, or the meeting file + timestamp. `context`: the export date or engagement name.
- `tasks` holds only explicit asks or commitments. Anything inferred goes under `candidates` with `why_candidate`; candidates are never appended.
- Keep ids stable: the tracker dedups on (source, context, action), so do not rephrase an action that already exists in `tracker/actions.xlsx` — check `kb/index.md` → tracker summary or ask the user.
