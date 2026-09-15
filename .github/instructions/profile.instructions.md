---
applyTo: "kb/topics/*/profile.md"
---
# kb/topics/<topic>/profile.md schema — the interest profile that drives /triage-topic
Header: `# Interest profile — <topic>` then `last updated: <date>` and `interviewed: <date>`.
Sections, in this order:
1. `## Why I follow this` — 2–4 lines in the user's words: what they do with what they read.
2. `## Flag it when` — numbered criteria `C1…`, each one line, concrete and testable against a title + one-line summary. Optional weight `(high|normal)`. Example: `C1 (high) — a new capability I could use in our SDLC agents within a month, with code or a spec, not a demo`.
3. `## Skip it when` — numbered `X1…`: things that look relevant but are not (hype, funding news, vendor marketing, repeats of a known story).
4. `## Sub-areas` — table `| sub-area | interest (high/normal/low) | note |`.
5. `## Sources` — table `| source | trust (high/normal/low) | note |` for newsletters/sites/people the user named.
6. `## Examples` — table `| item | verdict (flag/skip) | matches |` — the calibration examples from the interview and from feedback.
7. `## Feedback log` — `| date | item | user said | profile change |` — appended by /refine-topic only.
Rules: every line comes from something the user said; lines the user did not confirm end with `?`. Never delete a criterion — mark it `(retired <date>)`. Keep under 60 lines; condense rather than append.
