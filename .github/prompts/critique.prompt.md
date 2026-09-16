---
mode: agent
description: "[proposal, deck] Hostile review of proposal/deck/speech against the fact base, plus the questions you will get"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Agent: `@critic` (read-only).
Read the fact base (`discovery.md` or `content.md`) and whatever exists of `proposal.md`, `deck.json`, `speech.md`. Produce the critic report, then add `## Questions the audience will ask` — 8–12 pointed questions with a one-line suggested answer each, marking the 3 most dangerous. Write the report to `critique.md`. Works at any stage after G1; the earlier you run it, the cheaper the fix.
