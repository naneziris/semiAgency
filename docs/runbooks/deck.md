# Runbook — deck

A presentation on a subject you already have material for: a status update, a briefing, a decision paper, a training slot, or a draft deck that needs a proper storyline for a new audience. No options, no proposal document. Three gates. About 45 minutes of your attention for a 15-slide deck, most of it at G1.

Short version: `docs/after-meeting.md`. Prompts run in Copilot Chat, agent mode, `@analyst` unless `@critic` is named. Scripts and prompts default to the engagement you started last (`engagements/CURRENT`); `<dir>` and `engagement=<name>` below are only needed to point at another one.

## Step 0 — start [5 min]

```
python scripts/new_engagement.py
```

Answer the questions (2 = deck, subject, folder name, audience, minutes); the script waits while you fill `inputs/`, then lists what it found and prints the next prompt. Scripted: `python scripts/new_engagement.py --kind deck --name 2026-09-q3-update --subject "Q3 platform status" --audience "Steering committee" --minutes 15`.

Into `inputs/`: transcript (`transcript.md`), your notes (`notes.md`), documents (PDF → open in Word → save as `.docx` first), and — if you have one — the draft deck as `inputs/draft.pptx`. Titles alone give structure, not facts: add the material the titles were meant to summarise. Fill `inputs/audience.md` (10 min): who is in the room, what they decide, what they push back on, the language they use. The storylines and the speech are only as good as this.

## Step 1 — facts → G1 [15–20 min]

`/content engagement=<name>` → `content.md`: key messages (K ids), facts and figures (F ids), decisions and asks, open points, unverified. With a draft deck, each slide is cited `[doc:draft.pptx slide 4]`; title-only slides land under Unverified unless something else backs them.

- [ ] Every number in *Facts and figures* checked against its source
- [ ] Anything you can't confirm → Unverified (it will never reach a slide)
- [ ] Gaps: add sources to `inputs/` and re-run, or accept that some titles get cut

`python scripts/status.py --pass`

New material later? `/merge-followup engagement=<name> file=inputs/<new>.md` appends and updates statuses; re-pass G1.

## Step 2 — storylines → G3 [10 min]

`/storylines engagement=<name>` → `storylines.md`. Two tellings of the same key messages for this audience, compared, one recommended. With a draft deck in the inputs the two are always **S1 evolve the draft** (your order kept, re-framed, slides to drop/merge called out) and **S2 re-sequence** (the order this audience needs). Add your intent in plain words after the command if you have one, e.g. *keep every subject, change the narrative for a business audience, explain the technical parts in business terms*.

- [ ] Coverage list has every K id on a slide
- [ ] The ask lands on its own slide

`python scripts/status.py --pass` — it asks which storyline (or `--pass G3 --storyline S1`)

## Step 3 — deck → G4 [15 min]

`/deck-outline engagement=<name>` → `deck.json` + `storyboard.html`. Slides of the draft that were already finished are kept as `{"clone": "inputs/draft.pptx#7"}` (same corporate master only; validate checks). Review the storyboard, edit `deck.json` if needed, then:

```
python scripts/build_deck.py
```

builds and lints. Open `deck.pptx`. Fix by editing `deck.json` and rebuilding.

- [ ] Corporate master everywhere, no overflow, slide count fits the minutes

`python scripts/status.py --pass` — hand-edit the pptx freely after this.

## Step 4 — speech and Q&A (optional) [20 min]

`/speech engagement=<name>` → `python scripts/build_deck.py --notes-only` (runs the timing check, then embeds the notes). `@critic /critique engagement=<name>` for the questions this audience will ask.

## Variants

- **Only documents, no meeting.** Same flow; `content.md` cites `[doc:… p…]`. "Turn this 30-page report into 10 slides" works fine.
- **Started as a meeting write-up, now need a deck.** `python scripts/new_engagement.py --kind deck --name <new> --from engagements/<old>` copies `inputs/` and `normalized/` so you don't re-ingest.
