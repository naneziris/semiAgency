---
applyTo: "engagements/**/notes.md"
---
# notes.md schema — the topic record (engagement kind `meeting`)
One living document per topic: every meeting on the topic, the user's own notes, and the end-of-meeting summaries from Microsoft 365 Copilot, merged into the current state of things. Rewritten (not appended to) each time a meeting is added. A topic with a single meeting is valid.

Sections, in this order:
1. `## Topic` — one line on what the topic is; participants seen so far; a table `| # | date | meeting | sources |` with one row per meeting, oldest first (sources = the `T`/`S` ids and `[notes]` files for that meeting).
2. `## Where we stand` — 3–7 bullets: the current state, as of the latest meeting. Cited.
3. `## Decisions` — table `| date | decision | source |`, newest first. A decision overturned later stays in the table, struck through (`~~…~~`), with the later row citing why.
4. `## My actions` — table `| action | due | status | source |` — ONLY items the user committed to or was assigned; nothing inferred. `status` = `open`, or `done` when the tracker row for this engagement says so.
5. `## Others' actions` — table `| owner | action | due | status | source |`.
6. `## Open points` — raised and not settled, each with the date it was first raised. Remove a point only when a later source settles it (then it moves to Decisions or Where we stand).
7. `## Follow-up needed` — Y/N plus a proposed agenda (3–5 bullets) if Y.
8. `## Meeting log` — one block per meeting, newest first: `### <date> — <meeting>` then 2–4 bullets, cited.

Sources and authority (highest first): the user's notes `[notes]` > transcripts `[T<n> hh:mm:ss]` > end-of-meeting summaries `[S<n>]` > other documents. When sources disagree, the higher one wins and the record says so in one line. A fact that appears only in a summary (no transcript or note supports it) carries `(summary only)`.

Size: `## Where we stand` to `## Follow-up needed` fit on one page (≈450 words); the meeting log may grow.
