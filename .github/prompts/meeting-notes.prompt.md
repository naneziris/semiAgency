---
mode: agent
description: "[meeting] Topic record: all meetings on a topic + your notes → one living document + your actions as tasks.json (gate G5 follows)"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Agent: `@analyst`.

0. Read `state.json`. If `kind` is not `meeting`, stop: proposals use `/discovery-synthesize`, decks `/content`.
1. Run `python scripts/ingest.py <dir>` (it skips files it already ingested) and read `normalized/manifest.json`. Files in `inputs/` are named `<yyyy-mm-dd>-transcript.*`, `<yyyy-mm-dd>-summary.md` (the end-of-meeting summary from Microsoft 365 Copilot), `<yyyy-mm-dd>-notes.md`, or `notes.md` (standing notes on the whole topic). The date in the file name is the meeting the file belongs to. Summaries get source ids `S1…` in date order; transcripts `T1…`.
2. **First run** (no `notes.md` yet): read everything in `normalized/`. **Update** (`notes.md` exists): read `notes.md`, then only the inputs that are new since it was last written (the manifest entries not yet listed in its `## Topic` table) plus `notes.md`-type files that changed. Do not re-read old transcripts unless a new source contradicts the record and you need to check the citation.
3. If `tracker/actions.csv` exists, read its rows whose `engagement` is this engagement's name (read only; never write to it). Reuse their `action` text **exactly** for the same action, and take `status` from there.
4. Write (or rewrite) `notes.md` per `.github/instructions/notes.instructions.md`.
5. Write `tasks.json` per `.github/instructions/tasks.instructions.md`, containing only actions **not already in the tracker** for this engagement: the user's explicit commitments under `tasks` (owner `me`), others' and maybes under `candidates`.
6. Run `python scripts/validate.py` on both files and fix errors.
7. Stop. Say: which meetings the record now covers; how many new actions are yours; that in the terminal `python scripts/append_tasks.py` shows them, adds them to the tracker and passes gate G5; and — if `## Follow-up needed` is Y — that `python scripts/followup_agenda.py` writes the agenda and the .ics. End with: "After the next meeting on this topic: save its summary/transcript/notes into `<dir>/inputs/` with the date in the file name, then run `/meeting-notes` again."
