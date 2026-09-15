---
applyTo: "engagements/**/content.md"
---
# content.md schema (used when the engagement kind is `deck`)
The fact base for a presentation that is NOT a stakeholder proposal (status update, briefing, decision paper, training).
Sections, in this order, all present even if empty:
1. `## Subject and audience` — from state.json; one line on what the audience must take away.
2. `## Key messages` — table `| id | message | evidence |`, ids K1…; max 7; each cited.
3. `## Facts and figures` — table `| id | fact | evidence | confidence(H/M/L) |`, ids F1…; every number that could end up on a slide lives here.
4. `## Decisions and asks` — what has been decided (cited) and what the audience is being asked to decide.
5. `## Open points` — table `| id | point | owner | status |`, ids Q1….
6. `## Unverified` — heard once or inferred; never reaches a slide.
Rules: never invent evidence; a slide may only carry K and F ids; if a message has no evidence it goes to Unverified.
