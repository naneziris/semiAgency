---
applyTo: "engagements/**/discovery.md"
---
# discovery.md schema
Sections, in this order, all present even if empty:
1. `## Context` — 3–6 lines: who the stakeholders are, what they own, why now.
2. `## Needs` — table: `| id | need | evidence | priority(H/M/L) | status |`. ids N1…; evidence is a citation.
3. `## Pains` — table with the same columns, ids continue the N sequence.
4. `## Constraints` — table, same columns (tech, policy, budget, timing).
5. `## Decisions taken` — bullets with citation.
6. `## Open questions` — table: `| id | question | owner | blocking(Y/N) | status |`.
7. `## Stakeholder map` — table: `| person | role | cares about | influence(H/M/L) |`.
8. `## Unverified` — things heard once or inferred; never cited as facts elsewhere.

Rules: never delete a row — mark status `superseded` and add a new row. Never invent evidence.
A merge (from a follow-up) appends rows and updates status; it does not rewrite existing text.
