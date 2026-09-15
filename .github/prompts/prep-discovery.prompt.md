---
mode: agent
description: Build the pre-discovery brief and question guide for an engagement
---
Engagement: `engagements/${input:engagement}`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read `normalized/manifest.json`.
2. Read every file in `normalized/`.
3. Write `brief.md` with: `## Context` (what we know, cited), `## Hypotheses` (3–5, each labelled HYPOTHESIS and stating what evidence would confirm/refute it), `## Question guide` (grouped by theme: current process, pain, constraints, success measures, decision makers; 12–20 questions total, open-ended, ordered easy → sensitive), `## Logistics` (who should be in the room and why).
4. Run `python scripts/validate.py engagements/${input:engagement}/brief.md`.
