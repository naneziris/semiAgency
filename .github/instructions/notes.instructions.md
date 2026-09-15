---
applyTo: "engagements/**/notes.md"
---
# notes.md schema (used when the engagement kind is `meeting`)
One-page write-up of a meeting for the user's own records.
1. `## Meeting` — date, participants, purpose (from inputs; do not invent).
2. `## Key takeaways` — max 7 bullets, each cited `[T1 hh:mm:ss]` or `[notes]`.
3. `## Decisions` — bullets, cited.
4. `## My actions` — table `| action | due | source |` — ONLY items the user committed to or was assigned; nothing inferred.
5. `## Others' actions` — table `| owner | action | due | source |`.
6. `## Follow-up needed` — Y/N plus a proposed agenda (3–5 bullets) if Y.
7. `## Open points` — what was raised and not settled.
Keep it under 400 words. Prefer the user's own notes over the transcript when they conflict, and say so.
