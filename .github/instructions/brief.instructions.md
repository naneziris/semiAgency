---
applyTo: "kb/briefs/*.md"
---
# kb/briefs/<date>.md schema — the morning brief (one page)
Applies to `<date>.md`, not to the generated `<date>.inputs.md`.
Header: `# <Weekday> <date>` and one line: what kind of day this is (meeting-heavy / focus / travel …) with the count of meetings and hours of free time.
1. `## Top 3` — the three things that matter most today, numbered, each one line with *why now* (a deadline, a person waiting, a gate). This is judgement; state it plainly.
2. `## Today` — the calendar as a timeline, one line per event: `09:00 1-1 Maria K — open follow-ups: 2 (kb/people/maria-k/…)`; clashes marked `⟂ CLASH` with a suggested resolution (which one to move or shorten); gaps ≥ 60 min marked as focus slots with what to use them for.
3. `## Waiting on you` — overdue and due-today actions (mine) from the inputs, one line each with the source; then engagements waiting at a gate.
4. `## Waiting on others` — delegated actions, and anything blocked; suggest who to nudge if it is older than 5 working days.
5. `## Inputs missing` — what the brief could not see (no calendar export, email not triaged, digest not run) with the exact command/prompt to fix it. Omit the section if nothing is missing.
Rules: every line traces to `kb/briefs/<date>.inputs.md`; the only additions are prioritisation and phrasing. Never add events or actions that are not in the inputs. Under 350 words. No headings beyond these.
