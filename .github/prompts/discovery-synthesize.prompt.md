---
mode: agent
description: "[proposal] After the discovery meeting: transcript + notes + docs → discovery.md (gate G1 follows)"
---
Engagement: `engagements/${input:engagement}`. Agent: `@analyst`.
0. Read `state.json`. If `kind` is `deck`, stop: use `/content`. If `meeting`, stop: use `/meeting-notes`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read `normalized/manifest.json`.
2. Read the normalized transcript(s), notes and documents. Read `inputs/audience.md` if it exists; it overrides the one-line `audience` in state.json. If a transcript exceeds ~8,000 words, work chunk by chunk (`normalized/T1.part01.md`, …) keeping a running list of N and Q ids, then merge.
3. Write `discovery.md` per `.github/instructions/discovery.instructions.md`. Every row cites a source. Anything heard once or inferred goes under `## Unverified`.
4. Run `python scripts/validate.py engagements/${input:engagement}/discovery.md` and fix errors.
5. Stop. Tell the user: number of needs, open questions (how many blocking), and the 3 items you are least sure about — that is what to verify at gate G1. Next command: `python scripts/status.py engagements/${input:engagement}`.
