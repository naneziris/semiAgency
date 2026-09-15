# Discovery2Presentation (D2P) — How to use it

From a stakeholder conversation to a corporate-styled proposal deck and team tasks, with you approving every step that matters. Nothing leaves your machine; Copilot does the thinking, scripts do the mechanics, you make five decisions. This is workflow #1 of the semiAgency workspace (see the top-level README); the `meeting` kind below is workflow #3.

```
 inputs ──▶ discovery.md ──▶ options.md ──▶ proposal.md + storylines.md ──▶ deck.json ──▶ deck.pptx ──▶ tasks
              ▲ G1 facts        ▲ G2 option      ▲ G3 storyline               ▲ G4 visual        ▲ G5 tasks
```

This README walks the full **proposal** flow. For the two lighter uses — a presentation from a meeting you already had, or just your action points from a meeting — see `docs/d2p/scenarios.md`; they reuse the same steps with fewer gates.

Everything for one engagement lives in `engagements/<name>/`. Open that folder's files in VS Code as you go; Copilot's instructions attach automatically to each one.

---

## Before the first engagement (one-time, ~2 hours)

1. **Have Copilot write the scripts.** The repo scaffold (docs, Copilot config, templates) is already here; `scripts/` is empty on purpose. Open the folder in VS Code and run the six Phase prompts in `docs/d2p/bootstrap.md` §3, in order, committing after each. Stop when all `--selftest`s pass and the Phase 3 test deck opens in PowerPoint without a repair prompt.
2. **Calibrate the corporate look.** Create `brand/components.pptx` from the corporate template: paste in one clean example of each slide kind you actually use (title, section header, bullets, two-column, option comparison, timeline, the ask, next steps — 8 to 15 slides). Plain slides need nothing else. For slides with custom-drawn boxes, open Home → Select → Selection Pane and rename each fillable text shape to `{{col1_head}}`, `{{col1_body}}`, etc. Add a small hidden text box `{{kind:option-comparison-3col}}` on any slide whose purpose isn't obvious from its layout name. Then:
   ```
   python scripts/inspect_components.py
   ```
   Open `brand/components.md` and check every slide is listed with the tags you expect. If a tag is missing, the shape is probably inside a group or was renamed back by PowerPoint — fix and re-run.
3. **Feed it structure examples.** Run `python scripts/skeletonize_deck.py <path-to-past-deck.pptx>` on 2–3 decks you were happy with. This teaches the outliner your typical slide count and density; it never copies their styling.
4. **Write `brand/voice.md`.** Your terms, banned words, the words you want to land, and `words_per_minute` (time yourself once on a past recording).
5. **Tracker.** `python scripts/tracker_init.py` creates `tracker/actions.xlsx` with the fixed columns (skip if the daily routine already created it). Open it once in Excel and save. `append_tasks.py` is shared with the email-triage and meeting-notes workflows — every action you own ends up in this one file.

---

## Per engagement

Time budget in brackets is *your* time, not Copilot's.

### Step 0 — Start [2 min]

```
python scripts/new_engagement.py --kind proposal --name 2026-09-acme-support --stakeholders "Maria K (Ops lead)","Jan D (IT)" --audience "Ops leadership" --minutes 20
```

Drop anything you already have (prior slides, PDFs converted to `.docx` via Word, emails saved as `.md`) into `engagements/2026-09-acme-support/inputs/`. Never edit files in `inputs/` afterwards — they are the evidence.

At any point: `python scripts/status.py engagements/2026-09-acme-support` prints where you are and the exact next command.

### Step 1 — Before the discovery meeting [10 min]

In Copilot Chat, agent mode, select `@analyst`, type:

```
/prep-discovery engagement=2026-09-acme-support
```

Read `brief.md`. The hypotheses are labelled as hypotheses — treat them that way in the meeting. Trim the question guide to what fits your slot; print it or keep it open.

### Step 2 — After the meeting → Gate G1: are the facts right? [20–30 min]

Save the Teams transcript as `inputs/transcript.md` and your own notes as `inputs/notes.md`. Then:

```
/synthesize-discovery engagement=2026-09-acme-support
```

Open `discovery.md`. **This is the most important 20 minutes of the whole flow.** Check:

- Every row in Needs / Pains / Constraints has a citation. Spot-check the three items Copilot flagged as least sure by jumping to the timestamp in the transcript.
- Anything you *know* was said but isn't there → add a row yourself with the citation.
- Anything in `## Unverified` that you can confirm → move it up with a citation; otherwise leave it there. Unverified items never reach a slide.
- Open questions: mark `blocking = Y` on the ones you can't propose without.

When you're satisfied:

```
python scripts/status.py engagements/2026-09-acme-support --pass G1
```

**If blocking questions remain**, don't pass G1 yet:

```
python scripts/followup_agenda.py engagements/2026-09-acme-support
```

Send `followups/agenda-1.ics` (double-click → Outlook invite with the agenda in the body). After the follow-up, save its transcript as `inputs/followup-1.md` and run:

```
/merge-followup engagement=2026-09-acme-support file=inputs/followup-1.md
```

Re-check `discovery.md` (only new rows and changed statuses — it never rewrites what you approved), then pass G1.

### Step 3 — Options → Gate G2: which approach? [15 min]

```
/sketch-options engagement=2026-09-acme-support
```

Read `options.md`. Copilot is instructed *not* to recommend; the comparison table at the end is your decision aid. Sanity-check the effort bands — they're the model's guess, your judgement wins. If an option is missing (you had one in mind), add it yourself as O3 following the same structure; the validator will hold you to the schema.

```
python scripts/status.py engagements/2026-09-acme-support --pass G2 --option O2
```

### Step 4 — Proposal and storylines → Gate G3: is it true, and how do we tell it? [20 min]

```
/write-proposal engagement=2026-09-acme-support
```

Two files appear.

`proposal.md` — read it once as the stakeholder would. Every claim about *their* situation cites an N id; the `## Traceability` table at the bottom shows every need and where it's addressed. Fix wording freely; if you change a fact, make sure the citation still holds.

`storylines.md` — two different ways to tell the same proposal to *this* audience (e.g., pain-led vs. outcome-led). Each has a thesis, an arc, a slide outline, and a coverage list proving every high-priority need lands on a slide. Copilot recommends one and says why. Decide — you know the room.

Optional but recommended for anything senior: select `@critic` and run

```
/critique-deck engagement=2026-09-acme-support
```

It works on the proposal at this stage too and writes `critique.md` with unsupported claims and the questions you'll get asked. Fix the proposal, then:

```
python scripts/status.py engagements/2026-09-acme-support --pass G3 --storyline S2
```

### Step 5 — Build the deck → Gate G4: does it look right? [15 min]

```
/outline-deck engagement=2026-09-acme-support
```

Copilot writes `deck.json` following the chosen storyline slide by slide, using only your corporate components, and renders `storyboard.html`. Open the storyboard in a browser: it's the deck's content without styling — wrong emphasis, too much text, a missing slide are all faster to see here. Edit `deck.json` directly if you want; it's plain JSON.

```
python scripts/build_deck.py engagements/2026-09-acme-support
python scripts/lint_deck.py  engagements/2026-09-acme-support
```

Open `deck.pptx` in PowerPoint. It is on the corporate master with your components; the lint tells you which slides risk overflow. **To change anything, edit `deck.json` and rebuild** — don't hand-edit the pptx yet, or you lose the ability to regenerate. When it looks right:

```
python scripts/status.py engagements/2026-09-acme-support --pass G4
```

From here on, hand-edit the pptx freely; the builder will refuse to overwrite it unless you pass `--force`.

### Step 6 — Speech and dry run [30 min]

```
/write-speech engagement=2026-09-acme-support
python scripts/timing.py engagements/2026-09-acme-support
python scripts/build_deck.py engagements/2026-09-acme-support --notes-only
```

`speech.md` has one section per slide; words marked `**like this**` become bold + underlined in the speaker notes. `timing.py` shows minutes per slide at your pace. Then `@critic /critique-deck` once more for the Q&A list — rehearse the three it marks as dangerous. The dry run itself is you, out loud, with the timer.

### Step 7 — Team meeting → Gate G5: which tasks are real? [10 min]

Before the team meeting:

```
/brief-team engagement=2026-09-acme-support
```

`team-brief.md` is one page plus a timed agenda. After the meeting, save notes/transcript as `inputs/team-meeting.md`, then:

```
/extract-tasks engagement=2026-09-acme-support file=inputs/team-meeting.md
```

Review `tasks.json`: only explicit commitments are in `tasks`; maybes are under `candidates` and will *not* be appended. Promote or delete, then:

```
python scripts/append_tasks.py engagements/2026-09-acme-support
```

Rows land in `tracker/actions.xlsx` with `source = d2p`, deduplicated — running it twice is safe. If Excel has the file open, they go to `tasks.pending.csv` and are picked up next time.

---

## When things don't go as planned

| Symptom | What to do |
|---|---|
| Copilot wants to `pip install` something | Reject the edit. Say: "Stdlib only, see copilot-instructions.md." It will redo it. |
| `validate.py` fails after a Copilot step | Paste the error back into the same chat: "fix these validation errors." Don't fix by hand unless it's one line. |
| `status.py` says a gate isn't passed but you did the work | Gates are recorded, not inferred: run the `--pass` command. |
| PowerPoint offers to repair `deck.pptx` | Run `python scripts/build_deck.py --selftest`. If it passes, the culprit is a specific component — rebuild with `--only-kinds title-slide,bullets` and add kinds back until it breaks. See `docs/d2p/bootstrap.md` §5. |
| Text lands in the wrong shape or not at all | Check `brand/components.md` for that kind; the tag isn't listed → shape is grouped or unnamed. Fix in `components.pptx`, re-run `inspect_components.py`. |
| Discovery synthesis is thin or invents things | Transcript too long for one pass. Check `normalized/` has `T1.part01.md`… — if not, lower the chunk size in `ingest.py`. Then re-run `/synthesize-discovery`. G1 exists for exactly this. |
| You changed your mind about the option after G3 | `status.py --pass G2 --option O3` resets G3 and G4 automatically; re-run `/write-proposal`. Nothing below G1 is touched. |
| Corporate template got refreshed | Rebuild `components.pptx` on the new template, re-tag custom shapes, re-run `inspect_components.py`. Old engagements still open; new builds use the new look. |

## What the five gates are for

- **G1 facts** — nothing reaches a slide that you haven't seen cited to a timestamp. This is the one you never skip.
- **G2 option** — the model sketches, you choose what to propose.
- **G3 storyline** — the model proposes how to tell it and recommends; you choose, and you approve the proposal text.
- **G4 visual** — you look at the real deck before anyone else does.
- **G5 tasks** — nothing hits the shared tracker without your review.

Everything between the gates is regenerable from the files above it. If a step goes wrong, fix the file above and re-run the step — never patch downstream by hand.
