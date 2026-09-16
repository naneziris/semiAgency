# Runbook — proposal

You will sit down with stakeholders, extract what they need, and come back with a proposal deck and team tasks. Five gates; you approve each. `python scripts/status.py` always prints the next step from this page.

Short version: `docs/after-meeting.md`. Prompts run in Copilot Chat, agent mode, `@analyst` unless `@critic` is named. Scripts and prompts default to the engagement you started last (`engagements/CURRENT`); `<dir>` and `engagement=<name>` below are only needed to point at another one.

## Step 0 — start [2 min]

```
python scripts/new_engagement.py
```

Answer the questions (1 = proposal, subject, folder name, stakeholders, audience, minutes). Drop what you already have into `inputs/` (transcript.md, notes.md, prior slides, PDFs saved as `.docx` via Word, emails saved as `.md`), press Enter; the script lists what it found and prints the next prompt. Never edit `inputs/` afterwards. Fill `inputs/audience.md` (10 min, optional but it makes G3 better). Scripted alternative: `python scripts/new_engagement.py --kind proposal --name 2026-09-acme --stakeholders "Maria K (Ops lead), Jan D (IT)" --audience "Ops leadership" --minutes 20`.

## Step 1 — before the discovery meeting [10 min]

`/discovery-prep engagement=<name>` → `brief.md`. Hypotheses are hypotheses; trim the question guide to your slot.

## Step 2 — after the meeting → G1 facts [20–30 min, the one you never skip]

Save the transcript as `inputs/transcript.md`, your notes as `inputs/notes.md`.

`/discovery-synthesize engagement=<name>` → `discovery.md`.

- [ ] Every Needs / Pains / Constraints row has a citation; spot-check the 3 the prompt flagged by jumping to the timestamp
- [ ] Anything you know was said but isn't there → add a row with its citation
- [ ] `## Unverified`: promote only what you can cite; the rest never reaches a slide
- [ ] Open questions you can't propose without → `blocking = Y`

`python scripts/status.py --pass` (shows this checklist, asks you to confirm, records G1)

**Blocking questions still open?** Don't pass G1. `python scripts/followup_agenda.py` → send `followups/agenda-1.ics`. After the follow-up: save it as `inputs/followup-1.md`, `/merge-followup engagement=<name> file=inputs/followup-1.md`, re-check only the new rows, then pass G1.

## Step 3 — options → G2 [15 min]

`/options engagement=<name>` → `options.md`. The prompt does not recommend; the comparison table is your decision aid. Missing an option you had in mind? Add it as O3 in the same structure.

- [ ] Effort bands are believable
- [ ] Each option's "not a fit if" is true

`python scripts/status.py --pass` — it asks which option (or `--pass G2 --option O2` in one go)

## Step 4 — proposal + storylines → G3 [20 min]

`/proposal engagement=<name>` → `proposal.md` and `storylines.md`.

- [ ] Read `proposal.md` as the stakeholder would; every claim about *their* situation cites an N id; the Traceability table covers every need
- [ ] `storylines.md`: two tellings of the same proposal; pick one — you know the room
- [ ] Senior audience? `@critic /critique engagement=<name>` first and fix what it finds

`python scripts/status.py --pass` — it asks which storyline, defaulting to the recommended one (or `--pass G3 --storyline S2`)

## Step 5 — deck → G4 [15 min]

`/deck-outline engagement=<name>` → `deck.json` + `storyboard.html`. Open the storyboard: wrong emphasis, too much text, missing slide — faster to see here than in PowerPoint. Edit `deck.json` directly if you like.

```
python scripts/build_deck.py
```

builds `deck.pptx` and runs the lint. Open `deck.pptx`. **To change anything, edit `deck.json` and rebuild** — don't hand-edit the pptx yet.

- [ ] Every slide is on the corporate master, nothing overflows (lint says which slides risk it)
- [ ] Slide count fits the minutes

`python scripts/status.py --pass` — from here on hand-edit the pptx freely; the builder refuses to overwrite it without `--force`.

## Step 6 — speech + dry run [30 min]

`/speech engagement=<name>` → `speech.md` (words marked `**like this**` become bold-underlined in the notes). Then:

```
python scripts/build_deck.py --notes-only
```

runs the timing check (which slides are over, total vs. your slot) and embeds the notes.

`@critic /critique engagement=<name>` for the Q&A list; rehearse the 3 marked dangerous. The dry run itself is you, out loud, with a timer.

## Step 7 — team meeting → G5 [10 min]

Before: `/team-brief engagement=<name>` → `team-brief.md`.
After: save notes/transcript as `inputs/team-meeting.md`, then `/team-tasks engagement=<name> file=inputs/team-meeting.md` → `tasks.json`.

- [ ] Only explicit commitments under `tasks`; promote from `candidates` or delete

`python scripts/append_tasks.py` → shows the rows, appends them to `tracker/actions.csv` (safe to re-run), and asks whether to pass G5.

## If you change your mind

Re-passing an earlier gate resets the later ones (`--pass G2 --option O3` clears G3/G4); re-run from that step. Everything between gates is regenerable from the file above it: fix upstream, re-run — never patch downstream by hand.
