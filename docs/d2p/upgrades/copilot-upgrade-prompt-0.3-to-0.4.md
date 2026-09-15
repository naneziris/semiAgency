# Copilot prompt — upgrade stakeholder-pipeline from 0.3 to 0.4

Paste everything below this line into GitHub Copilot Chat in VS Code, **agent mode**, with the repo open. It is long; that is deliberate — it carries the exact file contents so nothing has to be invented. If Copilot stops partway (long outputs sometimes do), say "continue from step N" and it will pick up.

---

You are upgrading this repository from scaffold version 0.3 to 0.4. Work through the steps in order. Do not paraphrase, reformat, or "improve" any file content given below — write it byte-for-byte. After each step, list the files you touched. Do not run git commands; I commit myself.

Summary of the change: each engagement gets a `kind` (`proposal` | `deck` | `meeting`) in `state.json` that selects which stages and gates apply. Two new prompts, two new instruction files, two new templates, a scenarios guide, small edits to existing prompts so they refuse to run on the wrong kind, and four script changes.

## Step 1 — create these files with EXACTLY this content (overwrite if they exist)

### `.github/copilot-instructions.md`

````markdown
# Stakeholder pipeline — repo conventions

This repo turns stakeholder discovery into a proposal, a corporate-styled .pptx, and team tasks.
Read `docs/d2p/design.md` if you need the big picture. Work one stage at a time and stop.

## Hard rules
- Python 3 standard library ONLY. Never import or suggest installing third-party packages.
  Allowed: zipfile, xml.etree.ElementTree, json, re, hashlib, csv, datetime, pathlib, argparse, sys, os, shutil, io, copy, textwrap, html.
- Never run PowerShell. Use `python scripts/<name>.py` from the integrated terminal.
- Never modify anything under `engagements/*/inputs/` or `brand/components.pptx`.
- Never hand-write PowerPoint/Excel XML from scratch in scripts. Clone existing parts and edit text nodes.
- Machine-read artifacts are JSON (`state.json`, `deck.json`, `tasks.json`, `brand/components.json`).
  Human-read artifacts are markdown.
- After writing or editing any engagement artifact, run `python scripts/validate.py <path>` and fix what it reports before finishing.
- Do exactly the stage the prompt asks for. Do not advance `state.json` yourself; `scripts/status.py` tells the user the next action.

## Engagement kinds (state.json `kind`)
- `proposal` — full flow: discovery → options → proposal + storylines → deck → tasks. Gates G1–G5.
- `deck` — a presentation from notes/documents that is not a proposal: content → storylines → deck. Gates G1, G3, G4.
- `meeting` — write-up and action points only: notes → tasks. Gate G5.
Prompts check `kind` and refuse to run on the wrong kind. See docs/d2p/scenarios.md.

## ID scheme (used everywhere; scripts check for orphans)
- Needs/pains/constraints in discovery.md: `N1`, `N2`, … (never renumber; mark superseded ones `~~N4~~`)
- Open questions: `Q1`, `Q2`, … with status `open | resolved(<evidence>) | dropped`
- Options: `O1`–`O3`
- Key messages / facts in content.md (deck kind): `K1…`, `F1…`
- Proposal sections cite needs inline: `[N1, N3]`
- Slides in deck.json carry `"refs": [...]` of N/O ids
- Tasks in tasks.json carry `"source"`: the meeting file they came from

## Citations
Every extracted fact cites its source: `[T1 00:12:34]` for transcript file T1 at that timestamp,
`[doc:<filename> p<page>]` for documents, `[notes]` for the user's own notes.
Source ids come from `normalized/manifest.json`.

## Style
- Concise, concrete, no filler. Bullets in artifacts; prose in proposal.md.
- Use the terminology in `brand/voice.md` when it exists.
- When unsure about a fact, write it under "Unverified" rather than asserting it.
````

### `.github/instructions/content.instructions.md`

````markdown
---
applyTo: "engagements/**/content.md"
---
# content.md schema (used when the engagement kind is `deck`)
The fact base for a presentation that is NOT a stakeholder proposal (status update, briefing, decision paper, training).
Sections, in this order, all present even if empty:
1. `## Subject and audience` — from state.json; one line on what the audience must take away.
2. `## Key messages` — table `| id | message | evidence |`, ids K1…; max 7; each cited.
3. `## Facts and figures` — table `| id | fact | evidence | confidence(H/M/L) |`, ids F1…; every number that could end up on a slide lives here.
4. `## Decisions and asks` — what has been decided (cited) and what the audience is being asked to decide.
5. `## Open points` — table `| id | point | owner | status |`, ids Q1….
6. `## Unverified` — heard once or inferred; never reaches a slide.
Rules: never invent evidence; a slide may only carry K and F ids; if a message has no evidence it goes to Unverified.
````

### `.github/instructions/deck.instructions.md`

````markdown
---
applyTo: "engagements/**/deck.json"
---
# deck.json rules
- Only `kind` values listed in `brand/components.md`. Only the `fields` tags that component lists.
- String fields: one line. List fields: bullets; prefix `  - ` for level-2.
- Respect each component's stated capacity (max bullets, max chars per tag) from `brand/components.md`.
- Every content slide has `"refs"` with the ids it covers: N/O ids for proposals, K/F ids for `deck`-kind engagements. Title and section slides may omit refs.
- Slide count: within the range `brand/examples/` shows for the target duration in `meta.minutes`.
- `meta.storyline` must equal `state.json` `gates.G3.chosen_storyline`, and the slide sequence must follow that storyline's `Slide outline` table in `storylines.md` (same order, same kinds; titles may be polished, refs may be extended but not dropped).
````

### `.github/instructions/notes.instructions.md`

````markdown
---
applyTo: "engagements/**/notes.md"
---
# notes.md schema (used when the engagement kind is `meeting`)
One-page write-up of a meeting for the user's own records.
1. `## Meeting` — date, participants, purpose (from inputs; do not invent).
2. `## Key takeaways` — max 7 bullets, each cited `[T1 hh:mm:ss]` or `[notes]`.
3. `## Decisions` — bullets, cited.
4. `## My actions` — table `| action | due | source |` — ONLY items the user committed to or was assigned; nothing inferred.
5. `## Others' actions` — table `| owner | action | due | source |`.
6. `## Follow-up needed` — Y/N plus a proposed agenda (3–5 bullets) if Y.
7. `## Open points` — what was raised and not settled.
Keep it under 400 words. Prefer the user's own notes over the transcript when they conflict, and say so.
````

### `.github/instructions/storylines.instructions.md`

````markdown
---
applyTo: "engagements/**/storylines.md"
---
# storylines.md schema
Exactly TWO storylines, `## S1 — <name>` and `## S2 — <name>`. They tell the SAME content (the option chosen at G2 for proposals; the key messages in content.md for decks) in different ways — e.g. problem-first vs. vision-first, decision-first vs. journey, stakeholder-pain-led vs. outcome-led. They must NOT differ in what is proposed.
Each storyline has, in order:
- `**Thesis**` — the one sentence the audience should repeat afterwards
- `**Arc**` — 3–5 beats in prose (what the audience feels/learns at each beat)
- `**Slide outline**` — table `| # | kind | title | refs |` using only kinds from `brand/components.md`, with the ask on its own slide
- `**Works well because**` (max 3 bullets, specific to THIS audience from deck meta / proposal)
- `**Risks**` (max 3 bullets: where this telling can lose them)
- `**Coverage**` — list of every H-priority N id (proposal) or every K id (deck) and the slide # that carries it (all must be present)
Then `## Comparison` — one table, S1/S2 as columns; rows: opening, where the ask lands, time to first "why should I care", strongest slide, biggest risk, fit to audience.
Then `## Recommendation` — which storyline and 3 lines why. The user decides (gate G3); do not build anything.
````

### `.github/prompts/extract-tasks.prompt.md`

````markdown
---
mode: agent
description: Extract team tasks from the team meeting into tasks.json (not yet appended)
---
Engagement: `engagements/${input:engagement}`. Meeting file: `${input:file}`. Owner filter: `${input:owner}` (`all` or `me`; default all).
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read the normalized meeting file.
2. Write `tasks.json`: array of `{ "action", "owner", "due" (ISO date or null), "depends_on" (array of action text or []), "source" (file + timestamp), "notes" }`. If owner filter is `me`, include only the user's own actions under `tasks` and everyone else's under `candidates`. Only explicit commitments or clearly assigned actions; put maybes under a top-level `"candidates"` array instead.
3. Run `python scripts/validate.py engagements/${input:engagement}/tasks.json`.
4. Stop. Tell the user to review, then run `python scripts/append_tasks.py engagements/${input:engagement}` themselves (gate G5).
````

### `.github/prompts/outline-deck.prompt.md`

````markdown
---
mode: agent
description: Turn the approved proposal + chosen storyline into deck.json using only corporate components
---
Engagement: `engagements/${input:engagement}`.
1. Read `state.json`. If `gates.G3.passed` is false or `chosen_storyline` is null, stop and tell the user to pass G3 first.
2. Read `brand/components.md` (allowed kinds, tags, capacities), the chosen storyline's section in `storylines.md`, and the content source: `proposal.md` when `kind` is `proposal`, `content.md` when `kind` is `deck`.
3. Write `deck.json` per `.github/instructions/deck.instructions.md`, following the chosen storyline's slide outline exactly in order and kinds; fill each slide's fields from the content source with citations preserved as `refs` (N/O ids for proposals, K/F ids for decks), not as visible text. Set `meta.storyline`.
4. Run `python scripts/validate.py engagements/${input:engagement}/deck.json` then `python scripts/storyboard.py engagements/${input:engagement}`.
5. Stop. Tell the user to review `storyboard.html`, then run `python scripts/build_deck.py engagements/${input:engagement}` and open the result in PowerPoint (gate G4).
````

### `.github/prompts/sketch-options.prompt.md`

````markdown
---
mode: agent
description: Sketch 2–3 candidate solution approaches from discovery.md
---
Engagement: `engagements/${input:engagement}`.
1. Read `state.json`; if `kind` is not `proposal`, stop — options only apply to proposals. Read `discovery.md`. If any blocking Q is open, stop and say so.
2. Write `options.md` per `.github/instructions/options.instructions.md`. Make the options genuinely different in shape (e.g., minimal/rules-based vs. agentic vs. process-change-only), not three flavours of one idea. At least one option must be deliberately small.
3. Run `python scripts/validate.py engagements/${input:engagement}/options.md` and fix errors.
4. Stop. Do not recommend. List which H-priority needs each option leaves uncovered.
````

### `.github/prompts/summarize-meeting.prompt.md`

````markdown
---
mode: agent
description: Write a one-page meeting write-up with my actions (kind = meeting)
---
Engagement: `engagements/${input:engagement}`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read everything in `normalized/`.
2. Write `notes.md` per `.github/instructions/notes.instructions.md`.
3. Write `tasks.json` from `## My actions` and `## Others' actions`: explicit commitments under `tasks` (owner "me" for the user's own), maybes under `candidates`.
4. Run `python scripts/validate.py` on both files and fix errors.
5. Stop. Tell the user how many actions are theirs, and that `python scripts/append_tasks.py engagements/${input:engagement}` sends them to the tracker (gate G5). If `## Follow-up needed` is Y, mention `python scripts/followup_agenda.py`.
````

### `.github/prompts/synthesize-discovery.prompt.md`

````markdown
---
mode: agent
description: Turn transcript, notes and documents into discovery.md
---
Engagement: `engagements/${input:engagement}`.
0. Read `state.json`. If `kind` is `deck`, write `content.md` per `.github/instructions/content.instructions.md` instead of `discovery.md` and apply the steps below to it. If `kind` is `meeting`, stop: use `/summarize-meeting`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read `normalized/manifest.json`.
2. Read the normalized transcript(s), notes and documents. If a transcript exceeds ~8,000 words, process it in the chunks `ingest.py` produced (`normalized/T1.part01.md`, …), keeping a running list of N and Q ids, then merge.
3. Write `discovery.md` following `.github/instructions/discovery.instructions.md`. Every row cites a source. Put anything heard once or inferred under `## Unverified`.
4. Run `python scripts/validate.py engagements/${input:engagement}/discovery.md` and fix errors.
5. Stop. Tell the user how many needs, open questions (and how many are blocking) you found, and the 3 items you are least sure about — that is what to verify at gate G1.
````

### `.github/prompts/write-proposal.prompt.md`

````markdown
---
mode: agent
description: Write proposal.md from the chosen option, then two storylines with a recommendation
---
Engagement: `engagements/${input:engagement}`.
1. Read `state.json`. If `kind` is not `proposal`, stop: decks use `/write-storylines`. Use `gates.G2.chosen_option`. If missing, stop and ask the user to choose an option first.
2. Read `discovery.md`, `options.md`, and `brand/voice.md` if present.
3. Write `proposal.md` per `.github/instructions/proposal.instructions.md`. Run `python scripts/validate.py engagements/${input:engagement}/proposal.md` and fix errors, especially traceability gaps.
4. Read `brand/components.md` and `brand/examples/*.json`. Write `storylines.md` per `.github/instructions/storylines.instructions.md`: two genuinely different tellings of THIS proposal for the audience named in `state.json` (`audience`, `minutes`). Run validate on it.
5. Stop. Summarize: the 3 proposal claims you are least sure about (gate G3 check), and your storyline recommendation in 3 lines. Tell the user to record the decision with `python scripts/status.py <dir> --pass G3 --storyline S1|S2`.
````

### `.github/prompts/write-storylines.prompt.md`

````markdown
---
mode: agent
description: Two storylines + recommendation for a non-proposal deck (kind = deck)
---
Engagement: `engagements/${input:engagement}`.
1. Read `state.json`. If `kind` is not `deck`, stop: proposals use `/write-proposal`. If `gates.G1.passed` is false, stop and ask the user to verify `content.md` first.
2. Read `content.md`, `brand/components.md`, `brand/examples/*.json`, `brand/voice.md` if present.
3. Write `storylines.md` per `.github/instructions/storylines.instructions.md`, with two tellings of the SAME key messages for the audience and duration in `state.json`; the Coverage list references K ids (all of them) and the F ids each slide carries.
4. Run `python scripts/validate.py engagements/${input:engagement}/storylines.md`.
5. Stop. Give your recommendation in 3 lines and tell the user to record it with `python scripts/status.py <dir> --pass G3 --storyline S1|S2`.
````

### `VERSION`

````
0.4
````

### `templates/content.md`

````markdown
## Subject and audience

## Key messages
| id | message | evidence |
|---|---|---|

## Facts and figures
| id | fact | evidence | confidence |
|---|---|---|---|

## Decisions and asks

## Open points
| id | point | owner | status |
|---|---|---|---|

## Unverified
````

### `templates/notes.md`

````markdown
## Meeting

## Key takeaways

## Decisions

## My actions
| action | due | source |
|---|---|---|

## Others' actions
| owner | action | due | source |
|---|---|---|---|

## Follow-up needed

## Open points
````

### `templates/state.json`

````json
{
  "engagement": "",
  "kind": "proposal",
  "subject": "",
  "stakeholders": [],
  "audience": "",
  "minutes": 20,
  "stage": 0,
  "gates": {
    "G1": {
      "passed": false
    },
    "G2": {
      "passed": false,
      "chosen_option": null
    },
    "G3": {
      "passed": false,
      "chosen_storyline": null
    },
    "G4": {
      "passed": false
    },
    "G5": {
      "passed": false
    }
  },
  "followups": 0
}
````

### `docs/d2p/scenarios.md`

````markdown
# Scenarios — which parts of the system to use when

The pipeline is a set of stages that read and write files, with gates you record. Not every situation needs every stage. Each engagement has a `kind` in `state.json` that tells the prompts and `status.py` which stages and gates apply; prompts refuse to run on the wrong kind, so you can't accidentally skip a gate that matters.

| kind | You have | You want | Stages | Gates |
|---|---|---|---|---|
| `proposal` | a stakeholder conversation (or several) | a proposal deck for an agentic solution, and team tasks | prep → discovery → options → proposal + storylines → deck → speech → team tasks | G1 G2 G3 G4 G5 |
| `deck` | notes + documents from a meeting that already happened | a corporate-styled presentation on a subject, for an audience | content → storylines → deck → speech | G1 G3 G4 |
| `meeting` | notes + documents from a meeting that already happened | a write-up and my action points in the tracker | notes → tasks | G5 |

`<dir>` below means `engagements/<name>`. Prompts run in Copilot Chat with `@analyst` (agent mode) unless `@critic` is named.

---

## Scenario A — Stakeholder proposal (the full flow)

You'll sit down with stakeholders, extract what they need, and come back with a proposal deck.

```
python scripts/new_engagement.py --kind proposal --name 2026-09-acme --stakeholders "Maria K (Ops)" --audience "Ops leadership" --minutes 20
```

Then follow `README.md` steps 1–16. Summary: `/prep-discovery` → meeting → `/synthesize-discovery` → **G1** verify facts → (`followup_agenda.py` / `/merge-followup` until no blocking questions) → `/sketch-options` → **G2** choose → `/write-proposal` → **G3** approve + choose storyline → `/outline-deck` → `build_deck.py` → **G4** → `/write-speech` → `/brief-team` → `/extract-tasks` → **G5** → `append_tasks.py`.

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
````

### `docs/d2p/upgrades/README.md`

````markdown
# Upgrades

`VERSION` at the repo root says which scaffold version you're on. Each upgrade note here is `<from>-to-<to>.md` with a matching `upgrade-<from>-to-<to>.patch` for the scaffold files (apply with `git apply`), and a Copilot prompt for any script changes. Apply them in order; never skip one.

Rule for future changes: scaffold files (docs, .github, templates) ship as a patch; scripts are never shipped — they are described in docs/d2p/bootstrap.md §2 and regenerated or edited by Copilot from that spec.
````

## Step 2 — apply these edits to the three long documents

Find the OLD text exactly and replace it with the NEW text. If an OLD block is not found verbatim, stop and tell me which one.

### `README.md`

````diff
diff --git a/README.md b/README.md
index 6996615..40d334b 100644
--- a/README.md
+++ b/README.md
@@ -7,6 +7,8 @@ From a stakeholder conversation to a corporate-styled proposal deck and team tas
               ▲ G1 facts        ▲ G2 option      ▲ G3 storyline               ▲ G4 visual        ▲ G5 tasks
 ```
 
+This README walks the full **proposal** flow. For the two lighter uses — a presentation from a meeting you already had, or just your action points from a meeting — see `docs/d2p/scenarios.md`; they reuse the same steps with fewer gates.
+
 Everything for one engagement lives in `engagements/<name>/`. Open that folder's files in VS Code as you go; Copilot's instructions attach automatically to each one.
 
 ---
@@ -32,7 +34,7 @@ Time budget in brackets is *your* time, not Copilot's.
 ### Step 0 — Start [2 min]
 
 ```
-python scripts/new_engagement.py --name 2026-09-acme-support --stakeholders "Maria K (Ops lead)","Jan D (IT)" --audience "Ops leadership" --minutes 20
+python scripts/new_engagement.py --kind proposal --name 2026-09-acme-support --stakeholders "Maria K (Ops lead)","Jan D (IT)" --audience "Ops leadership" --minutes 20
 ```
 
 Drop anything you already have (prior slides, PDFs converted to `.docx` via Word, emails saved as `.md`) into `engagements/2026-09-acme-support/inputs/`. Never edit files in `inputs/` afterwards — they are the evidence.
````

### `docs/d2p/bootstrap.md`

````diff
diff --git a/docs/d2p/bootstrap.md b/docs/d2p/bootstrap.md
index f7c5c01..69d827e 100644
--- a/docs/d2p/bootstrap.md
+++ b/docs/d2p/bootstrap.md
@@ -197,7 +197,7 @@ Be specific: quote the text you object to. Do not praise.
 
 ### 1.9 Prompt files — `.github/prompts/*.prompt.md`
 
-All prompts take `engagement` as input: `/synthesize-discovery: engagement=2026-09-acme`. In VS Code, `${input:engagement}` prompts for it.
+Two further prompts live in the repo but are not reproduced here — `write-storylines.prompt.md` (deck kind) and `summarize-meeting.prompt.md` (meeting kind); see `.github/prompts/` and `docs/d2p/scenarios.md`. All prompts take `engagement` as input: `/synthesize-discovery: engagement=2026-09-acme`. In VS Code, `${input:engagement}` prompts for it.
 
 **`prep-discovery.prompt.md`**
 ```markdown
@@ -356,11 +356,11 @@ Each script: stdlib only, `argparse`, exit code 1 on failure, `--selftest` flag
 | Script | Input | Output | Acceptance |
 |---|---|---|---|
 | `ooxml.py` | – | helpers: `read_pkg(path)->dict[name,bytes]`, `write_pkg(path, parts)` (Content_Types first, deflate), `parts_rels(name)`, `next_part_number(parts, prefix)`, `content_type_add/remove`, `replace_shape_text(sp_elem, value, is_list)`, namespace constants | selftest round-trips `tests/fixtures/mini.pptx` byte-for-byte when no edits are made |
-| `new_engagement.py` | `--name`, `--stakeholders`, `--audience`, `--minutes` | folder tree, `state.json` (stage 0, all gates false), templates copied | idempotent; refuses to overwrite |
+| `new_engagement.py` | `--kind proposal\|deck\|meeting`, `--name`, `--subject`, `--stakeholders`, `--audience`, `--minutes`, `--from <dir>` | folder tree, `state.json` (kind, stage 0, all gates false), the templates that kind needs; `--from` copies another engagement's `inputs/` and `normalized/` | idempotent; refuses to overwrite |
 | `ingest.py` | engagement dir | `normalized/<Tn|Dn|notes>.md`, `manifest.json` `{id, file, sha256, kind, words}`; transcripts >8k words also split into `.partNN.md` at speaker turns | `.md` transcript: normalizes `[hh:mm:ss] Speaker:` lines; `.docx`/`.pptx`: text via `word/document.xml` / `ppt/slides/*.xml` `<w:t>`/`<a:t>` (pptx includes notes, slide numbers as `[slide N]`); `.pdf`: best-effort (inflate `FlateDecode` streams, collect `Tj`/`TJ` strings) with a loud warning to convert via Word if the result looks wrong; unchanged files (same sha) are skipped |
-| `validate.py` | any artifact path | errors to stdout, exit 1 | checks per schema in §1: sections present, tables well-formed, ids unique and sequential, every row cited, options count 2–3, proposal traceability covers all non-superseded N, storylines: exactly 2, both cover every H-priority N, recommendation present, outline kinds exist in components.json; deck.json `meta.storyline` equals state and slide kinds/order match that storyline's outline, deck kinds/tags/capacities vs `brand/components.json`, deck refs exist, speech sections match deck slides, tasks.json shape; also prints orphan N ids for options/proposal/deck |
-| `status.py` | engagement dir | prints stage, gate status, blocking Qs, and the exact next command/prompt | reads `state.json` and artifact presence; `--pass G1`, `--pass G2 --option O2`, `--pass G3 --storyline S2`, `--pass G4`, `--pass G5` record gates; refuses G3 without `--storyline`; re-passing an earlier gate resets every later gate (e.g. `--pass G2` clears G3/G4) |
-| `followup_agenda.py` | engagement dir | `followups/agenda-N.md` + `agenda-N.ics` (VEVENT, DESCRIPTION = agenda text, no attendees) | agenda lists open Qs (blocking first) with owners; N increments; `.ics` opens in Outlook |
+| `validate.py` | any artifact path | errors to stdout, exit 1 | checks per schema in §1 (including `content.md` K/F ids and `notes.md` for the other kinds): sections present, tables well-formed, ids unique and sequential, every row cited, options count 2–3, proposal traceability covers all non-superseded N, storylines: exactly 2, both cover every H-priority N, recommendation present, outline kinds exist in components.json; deck.json `meta.storyline` equals state and slide kinds/order match that storyline's outline, deck kinds/tags/capacities vs `brand/components.json`, deck refs exist, speech sections match deck slides, tasks.json shape; also prints orphan N ids for options/proposal/deck |
+| `status.py` | engagement dir | prints stage, gate status, blocking Qs, and the exact next command/prompt | applies the gate map for the engagement's kind (proposal: G1–G5; deck: G1,G3,G4; meeting: G5) and only ever suggests prompts valid for that kind; reads `state.json` and artifact presence; `--pass G1`, `--pass G2 --option O2`, `--pass G3 --storyline S2`, `--pass G4`, `--pass G5` record gates; refuses G3 without `--storyline`; re-passing an earlier gate resets every later gate (e.g. `--pass G2` clears G3/G4) |
+| `followup_agenda.py` | engagement dir | `followups/agenda-N.md` + `agenda-N.ics` (VEVENT, DESCRIPTION = agenda text, no attendees) | reads open points from whichever exists: `discovery.md`, `content.md`, or `notes.md`; agenda lists open Qs (blocking first) with owners; N increments; `.ics` opens in Outlook |
 | `inspect_components.py` | `brand/components.pptx` | `brand/components.json` + `components.md` | per slide: kind (from `{{kind:...}}` text on the slide, else derived from the layout name), tags = explicit shape names matching `{{...}}` PLUS auto-detected placeholders (`<p:ph type="title">`→`title`, `type="subTitle"`→`subtitle`, `type="body"` or untyped `idx`→`body`, `body2`… in idx order) so ordinary slides need no manual tagging, recursive through groups, for each tag: is_list (paragraph count >1 in exemplar), capacity (chars of exemplar text, bullets count), theme fonts/colors from `ppt/theme/theme1.xml` |
 | `skeletonize_deck.py` | any `.pptx` | `brand/examples/<name>.json` | per slide: layout name, title text, shape count, bullet count, has_picture; plus totals |
 | `build_deck.py` | engagement dir | `deck.pptx` | as specified in design §5.2; refuses to overwrite a deck without the `generated-by` stamp unless `--force`; `--notes-only` rewrites speaker notes in an existing built deck without touching slides; `--only-kinds a,b` builds a subset for bisecting repair issues; selftest builds 3 slides from `tests/fixtures/mini.pptx` and re-parses every part as XML |
@@ -380,8 +380,8 @@ Paste one at a time. Use the best model available. After each, run the selftests
 **Phase 1 — skeleton + discovery loop**
 ```
 Read .github/copilot-instructions.md and docs/d2p/design.md §2–§4.
-Implement scripts/new_engagement.py, scripts/ingest.py, scripts/validate.py (schemas for brief.md, discovery.md only for now), scripts/status.py, scripts/followup_agenda.py per the specifications table in docs/d2p/bootstrap.md §2.
-Also create templates/ for brief.md, discovery.md, state.json.
+Implement scripts/new_engagement.py, scripts/ingest.py, scripts/validate.py (schemas for brief.md, discovery.md, content.md, notes.md for now), scripts/status.py (kind-aware gate map, see docs/d2p/scenarios.md), scripts/followup_agenda.py per the specifications table in docs/d2p/bootstrap.md §2.
+templates/ already exist; read them.
 Stdlib only. Every script has --selftest that creates its own temp fixtures under a temp dir and cleans up.
 Run all selftests and show me the output. Then create a sample engagement "2026-09-sample" with a fake 200-line transcript in inputs/transcript.md and run ingest + status on it.
 ```
````

### `docs/d2p/design.md`

````diff
diff --git a/docs/d2p/design.md b/docs/d2p/design.md
index e0df847..ab1a2b2 100644
--- a/docs/d2p/design.md
+++ b/docs/d2p/design.md
@@ -10,7 +10,7 @@ Target tooling: GitHub Copilot (agent mode) in VS Code, Python scripts for every
 ## 1. Design principles
 
 1. **AI only where judgment is needed.** Anything that is parsing, validating, rendering, diffing, or bookkeeping is a script. The model reads and writes markdown/YAML; it never touches OOXML, xlsx internals, or styling.
-2. **Files are the state.** One folder per engagement. Every stage produces a file with a fixed schema. `state.json` records which gates you have approved. This is the same "context externalization" you already use in SemiPilotPro — reuse the philosophy, not the code.
+2. **Files are the state.** One folder per engagement, with a `kind` (`proposal`, `deck`, `meeting`) that selects which stages and gates apply — see `docs/d2p/scenarios.md`. Every stage produces a file with a fixed schema. `state.json` records which gates you have approved. This is the same "context externalization" you already use in SemiPilotPro — reuse the philosophy, not the code.
 3. **Human gates are explicit and few.** Five gates (see §3): facts, option, storyline, visual, tasks. Copilot never advances a stage on its own; a script tells you what the next action is. The gates are the product — they are what makes the deck defensible in front of the people who gave you the facts.
 4. **Corporate styling is copied, never generated.** The reference deck's slide master is the single source of truth. No "make it look corporate" prompts.
 5. **Scripts never author OOXML from scratch.** They clone XML that PowerPoint itself wrote (slides from your own decks) and replace text. This is what makes a stdlib-only builder safe: the risky part (valid slide XML) is never our code's job.
@@ -30,6 +30,8 @@ stakeholder-pipeline/
 │   │   ├── options.instructions.md      # applyTo: engagements/**/options.md
 │   │   ├── proposal.instructions.md     # applyTo: engagements/**/proposal.md
 │   │   ├── storylines.instructions.md   # applyTo: engagements/**/storylines.md
+│   │   ├── content.instructions.md      # applyTo: engagements/**/content.md   (deck kind)
+│   │   ├── notes.instructions.md        # applyTo: engagements/**/notes.md     (meeting kind)
 │   │   ├── deck.instructions.md         # applyTo: engagements/**/deck.json
 │   │   └── speech.instructions.md       # applyTo: engagements/**/speech.md
 │   ├── prompts/                      # slash-prompts, one per AI step
@@ -38,6 +40,8 @@ stakeholder-pipeline/
 │   │   ├── merge-followup.prompt.md
 │   │   ├── sketch-options.prompt.md
 │   │   ├── write-proposal.prompt.md
+│   │   ├── write-storylines.prompt.md   # deck kind
+│   │   ├── summarize-meeting.prompt.md  # meeting kind
 │   │   ├── outline-deck.prompt.md
 │   │   ├── write-speech.prompt.md
 │   │   ├── critique-deck.prompt.md
````

## Step 3 — `.gitignore`

Append a line `.DS_Store` if not present.

## Step 4 — update the scripts (stdlib only; keep every existing `--selftest` passing)

Read `docs/d2p/scenarios.md` and the updated `docs/d2p/bootstrap.md` §2 rows for `new_engagement.py`, `status.py`, `validate.py`, `followup_agenda.py`, then:

1. `scripts/new_engagement.py`: add `--kind proposal|deck|meeting` (default `proposal`), `--subject`, and `--from <dir>` (copies that engagement's `inputs/` and `normalized/`). Write `kind` and `subject` into `state.json`. Copy only the templates the kind needs — proposal: brief, discovery, options, proposal, storylines, deck, speech, tasks; deck: content, storylines, deck, speech; meeting: notes, tasks.
2. `scripts/status.py`: read `kind` (missing → `proposal`). Gate map: proposal G1–G5; deck G1, G3, G4; meeting G5. Only list gates and suggest prompts valid for the kind. `--pass` on a gate outside the map is an error. Re-passing an earlier gate still resets later ones.
3. `scripts/validate.py`: add schemas for `content.md` (sections in order; K and F ids unique and sequential; every K/F row cited) and `notes.md` (sections in order; "My actions" table shape). `deck.json` refs may be K/F ids when kind is `deck`; `storylines.md` coverage must list every K id when kind is `deck`.
4. `scripts/followup_agenda.py`: read open points from `discovery.md`, `content.md` or `notes.md`, whichever exists.

Extend the selftests: create one temporary engagement per kind and assert `status.py` reports the right gate map and `validate.py` accepts that kind's templates. Run every `--selftest` (or `scripts/selftest_all.py` if present) and show me the output.

## Step 5 — verify

Run and show the output:

```
python scripts/new_engagement.py --kind meeting --name upgrade-check
python scripts/status.py engagements/upgrade-check
python scripts/new_engagement.py --kind deck --name upgrade-check-2 --subject x --audience y --minutes 10
python scripts/status.py engagements/upgrade-check-2
```

The first should show only G5; the second G1, G3, G4. Then delete both `upgrade-check*` folders and confirm `cat VERSION` prints `0.4`.
