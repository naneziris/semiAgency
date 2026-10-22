# Runbook — meeting (the Topic record)

One engagement per **topic**, not per meeting: every meeting on the topic, your notes, and the end-of-meeting summaries from Microsoft 365 Copilot become one living document (`notes.md`) and your actions land in the tracker. One gate (G5), repeated after every meeting. 5–10 minutes per meeting.

Prompts run in Copilot Chat, agent mode, `@analyst`. Scripts and prompts default to the engagement you started or switched to last (`engagements/CURRENT`).

## Step 0 — at the end of the meeting, in Microsoft 365 [1 min]

Paste the prompt from `m365/08-end-of-meeting-summary.md` into Copilot in the Teams meeting. Copy the answer.

## Step 1 — put the meeting into the topic folder [2 min]

**First meeting on the topic:**

```
python scripts/new_engagement.py
```

Answer **meeting** and the topic (e.g. "Data platform migration"); the folder is `engagements/<yyyy-mm>-<topic>/`.

**A later meeting on the same topic:**

```
python scripts/new_engagement.py --use <topic folder name>
```

Then save into `inputs/`, with the meeting's date at the start of every file name:

| file | what |
|---|---|
| `<date>-summary.md` | the M365 answer from step 0 |
| `<date>-transcript.docx` (or `.md`) | Teams → meeting → Recap → Transcript → Download. Strongly recommended: it is what the record is checked against. |
| `<date>-notes.md` | your own notes from that meeting — they win over everything else |
| `notes.md` | optional, standing notes on the whole topic (context, background) |
| documents | anything shared in the meeting |

`python scripts/new_engagement.py --check` lists what it found. Never edit or delete files in `inputs/` afterwards — the record cites them.

## Step 2 — update the topic record → G5 [5 min]

`/meeting-notes` → rewrites `notes.md` (where we stand, decisions with dates, my actions with status, others' actions, open points, meeting log) and writes `tasks.json` with only the **new** actions.

- [ ] `## My actions` holds only what you committed to or were assigned — nothing inferred
- [ ] anything marked *(summary only)* is something you remember being said
- [ ] `tasks.json`: promote from `candidates` if you own something; delete what you don't

```
python scripts/append_tasks.py
```

shows the new rows, appends them to `tracker/actions.csv`, and asks whether to pass G5. Mark actions done in the CSV (Excel, `status` column); the next update shows them as done in the record.

## Step 3 — follow-up needed? [2 min]

If `notes.md` says `## Follow-up needed: Y`: `python scripts/followup_agenda.py` → `followups/agenda-N.md` + `.ics`.

## Variants

- **The topic turns into a proposal.** `python scripts/new_engagement.py --kind proposal --name <new> --from engagements/<topic>` copies every meeting's inputs; continue with the proposal runbook.
- **No transcript and no M365 summary.** In Microsoft 365 Copilot Chat (Work mode): *"Reproduce the transcript of my meeting '<title>' on <date> as `[hh:mm:ss] Speaker: text` lines, in order, without summarising."* Save it as `inputs/<date>-transcript.md`.
- **Keep the record next to the meetings in SharePoint.** Copy `notes.md` into the meeting's SharePoint folder after each update; the Meeting Summariser and the evening prep then see it too.
