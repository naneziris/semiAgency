# Discovery2Presentation

From a stakeholder conversation to a corporate-styled proposal deck and team tasks — or a deck from material you already have, or a one-page meeting write-up with your actions. GitHub Copilot does the thinking, stdlib Python scripts do the mechanics, you approve at the gates. Nothing leaves your machine.

```
proposal   inputs ─▶ discovery.md ─▶ options.md ─▶ proposal.md + storylines.md ─▶ deck.json ─▶ deck.pptx ─▶ tasks
                       ▲ G1 facts      ▲ G2 option    ▲ G3 storyline                ▲ G4 visual       ▲ G5 tasks
deck       inputs ─▶ content.md ──────────────────▶ storylines.md ─▶ deck.json ─▶ deck.pptx
                       ▲ G1                             ▲ G3               ▲ G4
meeting    inputs ─▶ notes.md + tasks.json ─▶ tracker
                                  ▲ G5
```

## Which runbook?

1. Will there be a *choice between solution approaches*? → **`docs/runbooks/proposal.md`**
2. Is the output a *deck* but the content is already decided (notes, docs, a draft deck)? → **`docs/runbooks/deck.md`**
3. Is the output *a record and my actions*, no deck? → **`docs/runbooks/meeting.md`**

`python scripts/new_engagement.py` with no `--kind` asks you these three questions. `python scripts/status.py engagements/<name>` prints the current step of the right runbook, so once started you don't need the docs open.

## One-time setup (~2 hours, on the corporate machine)

1. Open this folder in VS Code; `git init`; Python 3 on PATH; prompt and instruction files enabled (default).
2. `python scripts/append_tasks.py --init` → `tracker/actions.csv`.
3. **Have Copilot write the scripts.** `scripts/` holds only `append_tasks.py`; the rest are built here because they need your corporate deck. Run the Phase prompts in `docs/bootstrap.md` §3 in order, committing after each, until `python scripts/selftest_all.py` is all OK and the Phase 3 test deck opens in PowerPoint without a repair prompt.
4. **Calibrate the corporate look.** `brand/components.pptx`: one clean example of each slide kind you use (8–15 slides) from your own past decks; tag custom text shapes `{{col1_head}}` etc. via the Selection Pane; then `python scripts/inspect_components.py` and check `brand/components.md`. Details: `docs/design.md` §5.1.
5. `python scripts/skeletonize_deck.py <past-deck.pptx>` on 2–3 decks you were happy with (structure and density, never styling).
6. Write `brand/voice.md`: your terms, banned words, emphasis glossary, `words_per_minute`.

## The five gates

| gate | you check | never skip |
|---|---|---|
| G1 facts | every row cites a timestamp/page you can jump to; Unverified stays Unverified | **this one** |
| G2 option | the model sketched 2–3, you choose | |
| G3 storyline | the proposal text is true; you pick how it's told | |
| G4 visual | you open the real deck before anyone else does | |
| G5 tasks | nothing hits the tracker without your review | |

Everything between gates is regenerable from the file above it. Fix upstream, re-run — never patch downstream by hand.

## Prompts (Copilot Chat, agent mode)

| kind | prompt | writes |
|---|---|---|
| proposal | `/discovery-prep` | `brief.md` |
| proposal | `/discovery-synthesize` | `discovery.md` → G1 |
| deck | `/content` | `content.md` → G1 |
| any | `/merge-followup file=…` | merges into the fact base → back to G1 |
| proposal | `/options` | `options.md` → G2 |
| proposal | `/proposal` | `proposal.md` + `storylines.md` → G3 |
| deck | `/storylines` | `storylines.md` → G3 |
| proposal, deck | `/deck-outline` | `deck.json` + `storyboard.html` → build → G4 |
| proposal, deck | `/speech` | `speech.md` |
| proposal, deck | `@critic /critique` | `critique.md` |
| proposal | `/team-brief`, `/team-tasks file=…` | `team-brief.md`, `tasks.json` → G5 |
| meeting | `/meeting-notes` | `notes.md` + `tasks.json` → G5 |

Each prompt checks the engagement `kind` and tells you the right one if you picked wrong.

## When things don't go as planned

| symptom | do |
|---|---|
| Copilot wants to `pip install` | reject; "stdlib only, see copilot-instructions.md" |
| `validate.py` fails after a Copilot step | paste the error back: "fix these validation errors" |
| `status.py` says a gate isn't passed but you did the work | gates are recorded, not inferred: run `--pass` |
| PowerPoint offers to repair `deck.pptx` | `python scripts/build_deck.py --selftest`; if it passes, bisect with `--only-kinds title-slide,bullets` (`docs/bootstrap.md` §5) |
| text lands in the wrong shape | the tag isn't in `brand/components.md` → shape is grouped or unnamed; fix in `components.pptx`, re-run `inspect_components.py` |
| synthesis is thin or invents things | transcript too long for one pass; check `normalized/T1.part01.md` exists; G1 exists for exactly this |
| tracker CSV locked | close Excel, run `append_tasks.py` again |

Reference: `docs/design.md` (why it is built this way), `docs/bootstrap.md` (script specs and build prompts).

**Everything that lives in Microsoft 365** — daily brief, meeting filing and prep, email drafts, 1-1 agenda check — is in `m365/` (build sheets: scheduled prompts, Power Automate flows with standard connectors, two Agent Builder agents). It never touches this workspace. `docs/parked.md` records the earlier attempts and why they were dropped.
