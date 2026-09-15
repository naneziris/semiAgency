---
mode: agent
description: "[any kind] Merge a follow-up meeting or new document into discovery.md / content.md (back to G1)"
---
Engagement: `engagements/${input:engagement}`. New material: `${input:file}` (a path under inputs/). Agent: `@analyst`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` so the new file is normalized and has a source id.
2. Read the new normalized file and the current fact base: `discovery.md` (proposal) or `content.md` (deck).
3. Merge: append new N (or K/F) rows; set open questions the new material answers to `resolved(<citation>)`; add new Q rows; never rewrite existing rows except their status. Move items from Unverified up only if now cited.
4. Run `python scripts/validate.py` on the file.
5. Run `python scripts/followup_agenda.py engagements/${input:engagement}` and tell the user whether another follow-up is needed (any blocking Q still open), then to re-pass G1.
