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

## After a meeting

```
python scripts/new_engagement.py      # asks what you need, waits while you fill inputs/, prints the prompt to paste
<paste that prompt in Copilot Chat>   # /discovery-synthesize, /content or /meeting-notes
python scripts/status.py              # where you are, the checklist, the next prompt
python scripts/status.py --pass       # records the gate (asks for the option / storyline when needed)
```

Repeat the last three until `status.py` says done. That is the whole flow; **`docs/after-meeting.md`** is the one page to read. Scripts and prompts default to the engagement you started last (`engagements/CURRENT`), so you never type its name unless you run two in parallel (`new_engagement.py --use <name>` switches).

Three kinds, chosen in the first question: **proposal** (there will be a choice between solution approaches — `docs/runbooks/proposal.md`), **deck** (content already decided, you need slides — `docs/runbooks/deck.md`), **meeting** (a record and your actions, no deck — `docs/runbooks/meeting.md`). The runbooks are the per-kind detail that `status.py` prints step by step.

## One-time setup (~2 hours, on the corporate machine)

1. Open this folder in VS Code; `git init`; Python 3 on PATH; prompt and instruction files enabled (default).
2. `python scripts/append_tasks.py --init` → `tracker/actions.csv`.
3. **Have Copilot write the scripts.** `scripts/` ships `new_engagement.py` and `append_tasks.py`; the rest are built here because they need your corporate deck. Run the Phase prompts in `docs/bootstrap.md` §3 in order, committing after each, until `python scripts/selftest_all.py` is all OK and the Phase 3 test deck opens in PowerPoint without a repair prompt.
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

`engagement=<name>` is optional everywhere: without it a prompt works on `engagements/CURRENT`. `status.py` prints the next prompt with the name filled in; paste that.

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

## Also in this repo: `bench/` — a personal model benchmark for Copilot users

Independent of D2P. Copy `bench/` into an empty workspace and it walks you through building your own benchmark of the models in the Copilot picker: collect 5–10 tasks where AI recently failed you (`/bench-setup`), run them per model (`/bench-run`, or the Copilot CLI runner), turn your reactions into pass/fail checks (`/bench-feedback`), let one judge model grade everything (`/bench-judge`), open `index.html`. Ten minutes per new model after the first afternoon. Read `bench/README.md`; it is meant to be shared with colleagues as is.

## The map: `city.html`

`python scripts/build_city.py` generates `city.html` — a single shareable page that shows everything in this repo as a city: one building per feature, a modal with copy-paste instructions and the full prompt or build sheet behind it, "I want to…" journeys that number their stops on the map, and free lots for what comes next. It embeds no corporate data (`city/city.json` lists what is embedded, what is redacted and what is never embedded). Any prompt, agent or M365 sheet that no building claims is placed in "New Arrivals" automatically; `--check` fails if that happens, so run it before you share. To give a new feature a proper building, add an entry to `city/city.json` and rebuild. With an illustration in `city/scene.jpg` and traced hotspots the same script renders the painted city instead of the drawn one — `city/README.md`.

## When things don't go as planned

| symptom | do |
|---|---|
| Copilot wants to `pip install` | reject; "stdlib only, see copilot-instructions.md" |
| `validate.py` fails after a Copilot step | paste the error back: "fix these validation errors" |
| `status.py` says a gate isn't passed but you did the work | gates are recorded, not inferred: run `python scripts/status.py --pass` |
| a script or prompt works on the wrong engagement | `engagements/CURRENT` points elsewhere: `python scripts/new_engagement.py --use <name>` |
| you closed the terminal before adding inputs | `python scripts/new_engagement.py --check` re-runs the inputs check and prints the next prompt |
| PowerPoint offers to repair `deck.pptx` | `python scripts/build_deck.py --selftest`; if it passes, bisect with `--only-kinds title-slide,bullets` (`docs/bootstrap.md` §5) |
| text lands in the wrong shape | the tag isn't in `brand/components.md` → shape is grouped or unnamed; fix in `components.pptx`, re-run `inspect_components.py` |
| synthesis is thin or invents things | transcript too long for one pass; check `normalized/T1.part01.md` exists; G1 exists for exactly this |
| tracker CSV locked | close Excel, run `append_tasks.py` again |

Reference: `docs/design.md` (why it is built this way), `docs/bootstrap.md` (script specs and build prompts).

**Everything that lives in Microsoft 365** — daily brief, meeting filing and prep, email drafts, 1-1 agenda check — is in `m365/` (build sheets: scheduled prompts, Power Automate flows with standard connectors, Agent Builder agents). It never touches this workspace. `docs/parked.md` records the earlier attempts and why they were dropped.

Sheets 7+ in `m365/` are Agent Builder agents built to **share with colleagues** (first one: Fit Finder, which turns an AI idea someone saw into a brief for their own team and feeds the good ones into Discovery2Presentation). Entry bar: someone other than Nikos uses it.
