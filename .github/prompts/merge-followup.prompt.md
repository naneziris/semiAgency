---
mode: agent
description: Merge a follow-up meeting into the existing discovery.md
---
Engagement: `engagements/${input:engagement}`. New material: `${input:file}` (a path under inputs/).
1. Run `python scripts/ingest.py engagements/${input:engagement}` so the new file is normalized and has a source id.
2. Read the new normalized file and the current `discovery.md`.
3. Merge: append new N rows; for each open question that the new material answers, set status `resolved(<citation>)`; add new Q rows; never rewrite existing rows except their status. Move items from Unverified to Needs/Pains only if now cited.
4. Run `python scripts/validate.py engagements/${input:engagement}/discovery.md`.
5. Run `python scripts/followup_agenda.py engagements/${input:engagement}` and tell the user whether a further follow-up is needed (any blocking Q still open).
