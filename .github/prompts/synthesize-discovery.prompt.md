---
mode: agent
description: Turn transcript, notes and documents into discovery.md
---
Engagement: `engagements/${input:engagement}`.
0. Read `state.json`. If `kind` is `deck`, write `content.md` per `.github/instructions/content.instructions.md` instead of `discovery.md` and apply the steps below to it. If `kind` is `meeting`, stop: use `/summarize-meeting`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read `normalized/manifest.json`.
2. Read the normalized transcript(s), notes and documents. Read `inputs/audience.md` if it exists and treat it as the definition of the audience, overriding the one-line `audience` in state.json. If a transcript exceeds ~8,000 words, process it in the chunks `ingest.py` produced (`normalized/T1.part01.md`, …), keeping a running list of N and Q ids, then merge.
3. Write `discovery.md` following `.github/instructions/discovery.instructions.md`. Every row cites a source. Put anything heard once or inferred under `## Unverified`.
4. Run `python scripts/validate.py engagements/${input:engagement}/discovery.md` and fix errors.
5. Stop. Tell the user how many needs, open questions (and how many are blocking) you found, and the 3 items you are least sure about — that is what to verify at gate G1.
