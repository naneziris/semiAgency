---
mode: agent
description: "[proposal] Before the discovery meeting: brief + question guide from whatever is in inputs/"
---
Engagement: `engagements/${input:engagement}`. Agent: `@analyst`.
0. Read `state.json`. Works for kind `proposal` (and `deck` if you want a question guide before a briefing meeting). For an existing engagement with open questions in `discovery.md`, build the guide from those instead of from scratch.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read `normalized/manifest.json`, then every file in `normalized/`.
2. Write `brief.md`: `## Context` (what we know, cited), `## Hypotheses` (3–5, each labelled HYPOTHESIS with what would confirm/refute it), `## Question guide` (themes: current process, pain, constraints, success measures, decision makers; 12–20 open questions, easy → sensitive), `## Logistics` (who should be in the room and why).
3. Run `python scripts/validate.py engagements/${input:engagement}/brief.md`.
4. Stop. Tell the user the 3 hypotheses you are least sure about.
