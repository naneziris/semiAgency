---
applyTo: "kb/triage/*.md"
---
# kb/triage/<date>.md schema — the human-read email triage for one day
Sections, in this order, all present even if empty:
1. `## Do today` — table `| # | action | from email | urgency | effort | due |`, ids match the `tasks` entries in the companion `.todos.json` (same order).
2. `## Delegate` — table `| # | action | to | ask (one line you can paste) | from email |`.
3. `## Schedule / later` — table `| # | action | effort | due | from email |` (normal/low urgency).
4. `## Reply drafts` — for each email that needs a written reply and can be answered from what you know: `### E<n> — <subject>` then a 3–6 line draft in the user's voice (`brand/voice.md`), plain text, no greeting fluff. Mark anything you are guessing with `[?]`.
5. `## Candidates (implied, not asked)` — bullets, each with the email id and why it is only a candidate.
6. `## FYI, no action` — one line per email that needs nothing; include the newsletters the exporter listed under FYI.
7. `## Needs your judgement` — emails where you could not tell whether an action is expected; one line each, with the question to answer.
Rules: every row cites an `E<n>`. Never merge two emails into one action unless they are the same thread. Never mark `due` without a stated date. Under 400 words excluding drafts.
