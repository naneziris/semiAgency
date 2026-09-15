# Scenarios — which parts of the system to use when

The pipeline is a set of stages that read and write files, with gates you record. Not every situation needs every stage. Each engagement has a `kind` in `state.json` that tells the prompts and `status.py` which stages and gates apply; prompts refuse to run on the wrong kind, so you can't accidentally skip a gate that matters.

| kind | You have | You want | Stages | Gates |
|---|---|---|---|---|
| `proposal` | a stakeholder conversation (or several) | a proposal deck for an agentic solution, and team tasks | prep → discovery → options → proposal + storylines → deck → speech → team tasks | G1 G2 G3 G4 G5 |
| `deck` | notes + documents from a meeting that already happened, and/or a draft deck | a corporate-styled presentation on a subject, for an audience | content → storylines → deck → speech | G1 G3 G4 |
| `meeting` | notes + documents from a meeting that already happened | a write-up and my action points in the tracker | notes → tasks | G5 |

`<dir>` below means `engagements/<name>`. Prompts run in Copilot Chat with `@analyst` (agent mode) unless `@critic` is named.

---

## Scenario A — Stakeholder proposal (the full flow)

You'll sit down with stakeholders, extract what they need, and come back with a proposal deck.

```
python scripts/new_engagement.py --kind proposal --name 2026-09-acme --stakeholders "Maria K (Ops)" --audience "Ops leadership" --minutes 20
```

Then follow `docs/d2p/README.md` steps 0–7. Summary: `/prep-discovery` → meeting → `/synthesize-discovery` → **G1** verify facts → (`followup_agenda.py` / `/merge-followup` until no blocking questions) → `/sketch-options` → **G2** choose → `/write-proposal` → **G3** approve + choose storyline → `/outline-deck` → `build_deck.py` → **G4** → `/write-speech` → `/brief-team` → `/extract-tasks` → **G5** → `append_tasks.py`.

---

## Scenario B — I already had the meeting; I need a presentation

A status update, a briefing, a decision paper, a training slot. No solution options, no proposal document — but the facts on the slides still get verified, and you still choose how the story is told.

```
python scripts/new_engagement.py --kind deck --name 2026-09-q3-update --subject "Q3 platform status" --audience "Steering committee" --minutes 15
```

1. Drop the transcript (`inputs/transcript.md`), your notes (`inputs/notes.md`) and any documents into `inputs/`. PDFs: open in Word, save as `.docx` first.
2. `/synthesize-discovery engagement=2026-09-q3-update` — because the kind is `deck`, this writes `content.md` instead of `discovery.md`: key messages (K ids), facts and figures (F ids), decisions and asks, open points, unverified. Every K and F is cited.
3. **G1** — read `content.md`. Check every number in *Facts and figures* against its source; anything you can't confirm goes to *Unverified* and will never reach a slide. `python scripts/status.py <dir> --pass G1`.
4. `/write-storylines engagement=2026-09-q3-update` — two ways to tell these key messages to this audience (e.g. results-first vs. journey; risk-led vs. ask-led), compared, one recommended.
5. **G3** — choose: `python scripts/status.py <dir> --pass G3 --storyline S1`.
6. `/outline-deck` → check `storyboard.html` → `python scripts/build_deck.py <dir>` → `python scripts/lint_deck.py <dir>`.
7. **G4** — open `deck.pptx` in PowerPoint; fix by editing `deck.json` and rebuilding. `status.py <dir> --pass G4`.
8. Optional: `/write-speech` → `timing.py` → `build_deck.py <dir> --notes-only`; `@critic /critique-deck` for the questions you'll get.

Time: about 45 minutes of your attention for a 15-slide deck, most of it at G1.

**Variant — no meeting, only documents.** Same flow; `inputs/` holds only documents. `content.md` will cite `[doc:… p…]` instead of timestamps. Works fine for "turn this 30-page report into 10 slides".

**Variant — update an existing deck with new input.** Drop the new material into `inputs/`, run `/merge-followup file=inputs/<new>.md` (it works on `content.md` too — appends and updates statuses, never rewrites approved rows), re-pass G1, re-run `/outline-deck` and rebuild. Your earlier `deck.json` edits are lost, so if you hand-tuned it, diff the old and new `deck.json` in git first.

---

## Scenario C — I already had the meeting; I need my action points

This is the everyday meeting write-up. It shares the tracker with everything else so your actions end up in one place.

```
python scripts/new_engagement.py --kind meeting --name 2026-09-08-vendor-sync
```

1. Drop transcript / notes / attachments into `inputs/`.
2. `/summarize-meeting engagement=2026-09-08-vendor-sync` — writes `notes.md` (one page: takeaways, decisions, *my actions*, others' actions, follow-up needed, open points) and `tasks.json` with your commitments under `tasks` and everyone else's under `candidates`.
3. **G5** — read `tasks.json`; promote from `candidates` if you actually own something; delete what you don't. `python scripts/append_tasks.py <dir>` → rows appended to `tracker/actions.xlsx` with `source = meeting`.
4. If `notes.md` says a follow-up is needed: `python scripts/followup_agenda.py <dir>` gives you the agenda and an `.ics`.

Time: 5–10 minutes. If you find you're doing this several times a day, keep one engagement per meeting — the folder name is the date and subject, and `notes.md` is your searchable record.

**Variant — everyone's actions, not just mine.** `/extract-tasks engagement=… file=inputs/transcript.md owner=all` puts every explicit commitment under `tasks`.

---

## Scenario D — Prepare for a follow-up meeting

Applies to any kind. The open points in `discovery.md` / `content.md` / `notes.md` are the agenda.

```
python scripts/followup_agenda.py <dir>
```

Gives `followups/agenda-N.md` and `agenda-N.ics`. For a stakeholder follow-up, `/prep-discovery` also works on an existing engagement and will build a question guide from the open questions rather than from scratch.

---

## Scenario E — Same stakeholders, new topic

Start a new engagement; don't reuse the old one. Copy the old `discovery.md` into the new `inputs/` as a document — it becomes a cited source (`[doc:discovery-acme-v1.md]`), and the stakeholder map carries over without you re-typing it.

---

## Scenario F — I have a draft deck (mostly titles) and a new audience

You already sketched the structure; what you need is the right storyline for *this* audience and a finished deck. Use the `deck` kind with the draft as an input.

```
python scripts/new_engagement.py --kind deck --name 2026-09-arch-review-cto --subject "Platform architecture review" --audience "CTO and staff" --minutes 20
```

1. Put the draft in `inputs/draft.pptx`, plus everything the titles were meant to summarise — your notes, the documents, the earlier versions of the talk for other audiences. Titles alone give structure, not facts.
   Optional: `inputs/audience.md` if you want to describe the audience in more than one line.
2. `/synthesize-discovery` → `content.md`. `ingest.py` extracts the draft slide by slide (`[doc:draft.pptx slide 4]`), so titles become candidate key messages and any slides that already have real content become cited facts. Everything that exists only as a title lands under *Unverified* unless another input backs it up.
3. **G1** — this is where you find out what you actually have. Fill gaps by adding sources to `inputs/` and re-running, or by accepting that some titles will be cut. `status.py <dir> --pass G1`.
4. `/write-storylines`, adding your intent in plain words after the command, e.g. *keep every subject in draft.pptx, change the narrative for a business audience, explain the technical parts in business terms*. Each slide in the outlines is marked `clone` / `rewrite` / `new`. Because a draft deck is in the inputs, the two storylines are always: **S1 — evolve the draft** (your slide order kept, re-framed for the audience, with the slides to drop or merge called out) and **S2 — re-sequence** (the order this audience needs, which may put your slide 9 first). Compared, one recommended.
5. **G3** — choose: `status.py <dir> --pass G3 --storyline S2`.
6. `/outline-deck` → `deck.json`. Slides of the draft that were already finished can be kept as-is: the outliner uses `{"clone": "inputs/draft.pptx#7"}` for those and corporate components for the rest. Then `build_deck.py`, `lint_deck.py`, PowerPoint, **G4**.
7. `/write-speech` → `timing.py` → `build_deck.py <dir> --notes-only` for the speaker notes. `@critic /critique-deck` for the questions this audience will ask.

The `clone` entry only works if the draft is on the same corporate master as `components.pptx`; `validate.py` checks that and tells you otherwise, in which case the slide is rebuilt from a component instead.

---

## Picking the kind: three questions

1. Will there be a *choice between solution approaches*? → `proposal`.
2. Is the output a *deck* but the content is already decided? → `deck`.
3. Is the output *actions and a record*, no deck? → `meeting`.

If you start as `meeting` and later need a deck from the same material, run `new_engagement.py --kind deck --from <old-dir>`: it copies `inputs/` and `normalized/` so you don't re-ingest.

## What stays constant across scenarios

- Facts are verified by you before they reach a slide (G1), always.
- Styling always comes from `brand/components.pptx`; the model never touches it.
- Tasks always go through `tasks.json` review (G5) before the tracker.
- Every stage is regenerable from the file above it: fix upstream, re-run — never patch downstream by hand.
