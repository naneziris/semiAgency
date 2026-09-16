# Runbook — meeting

The everyday write-up: a meeting happened, you want a one-page record and your action points in the tracker. One gate. 5–10 minutes. One engagement per meeting — the folder name is the date and subject, and `notes.md` becomes your searchable record.

Short version: `docs/after-meeting.md`. Prompts run in Copilot Chat, agent mode, `@analyst`. Scripts and prompts default to the engagement you started last (`engagements/CURRENT`); `<dir>` and `engagement=<name>` below are only needed to point at another one.

## Step 0 — start [1 min]

```
python scripts/new_engagement.py
```

Answer 3 (meeting) and the subject; the folder name defaults to `<date>-<subject>`. Drop the transcript (`inputs/transcript.md`), your notes (`inputs/notes.md`) and any attachments into `inputs/`, press Enter, and paste the prompt it prints. Scripted: `python scripts/new_engagement.py --kind meeting --name 2026-09-08-vendor-sync`.

## Step 1 — write-up + actions → G5 [5 min]

`/meeting-notes engagement=<name>` → `notes.md` (takeaways, decisions, *my actions*, others' actions, follow-up needed, open points; under 400 words, your notes win over the transcript when they conflict) and `tasks.json` (your commitments under `tasks`, everyone else's under `candidates`).

- [ ] `## My actions` is only what you committed to or were assigned — nothing inferred
- [ ] `tasks.json`: promote from `candidates` if you actually own something; delete what you don't

```
python scripts/append_tasks.py
```

shows the rows, appends them, and asks whether to pass G5. Rows land in `tracker/actions.csv` with `source = meeting-notes`; re-running appends nothing twice. Open the CSV in Excel to work the list (status, notes); the script never rewrites existing rows.

## Step 2 — follow-up needed? [2 min]

If `notes.md` says `## Follow-up needed: Y`:

```
python scripts/followup_agenda.py
```

→ `followups/agenda-1.md` and `agenda-1.ics` (double-click → Outlook invite with the agenda in the body). After the follow-up meeting, start a new `meeting` engagement for it, or — if it is part of a proposal — `/merge-followup` in that engagement.

## Variants

- **Everyone's actions, not just yours.** `/team-tasks engagement=<name> file=inputs/transcript.md owner=all` puts every explicit commitment under `tasks`.
- **This meeting turns out to need a deck.** `python scripts/new_engagement.py --kind deck --name <new> --from <dir>` and continue with the deck runbook.
- **No transcript file arrived.** In Microsoft 365 Copilot Chat (Work mode) ask: *"Reproduce the transcript of my meeting '<title>' on <date> as `[hh:mm:ss] Speaker: text` lines, in order, without summarising."* Save it as `inputs/transcript.md`. A recap alone gives you nothing to verify against.
