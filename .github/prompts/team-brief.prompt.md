---
mode: agent
description: "[proposal] One-page team brief + timed agenda for the team meeting after the stakeholder presentation"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Agent: `@analyst`.
Read `proposal.md` and `discovery.md`. Write `team-brief.md`, max one page: `## What the stakeholders told us` (5 bullets, cited), `## What we proposed` (5 bullets), `## What I need from the team` (decisions, estimates, owners), `## Open risks`, `## Proposed agenda` (30 minutes, timed). Then stop and tell the user the next step: "Hold the team meeting with this agenda. Afterwards save its notes or transcript as `inputs/team-meeting.md` and run `/team-tasks file=inputs/team-meeting.md` in Copilot Chat."
