# Discovery2Presentation (D2P) — Copilot Bootstrap Kit

Companion to `docs/d2p/design.md`. This file is the only thing you need to carry onto the corporate machine: it contains, verbatim, every Copilot configuration file for the repo, plus the implementation prompts you paste into Copilot agent mode to have it write the scripts. Nothing here needs a network, a package, or a file from outside.

Constraints baked in: Python stdlib only, no PowerShell, JSON for machine-read artifacts, markdown for human-read ones, one stage per Copilot turn, five human gates that are never skipped.

---

## 0. Manual setup (10 minutes)

```
mkdir semiAgency && cd semiAgency
git init
mkdir -p .github/instructions .github/prompts .github/agents brand/examples templates scripts tracker engagements tests/fixtures
```

Copy the documents in as `docs/d2p/design.md` (the system design), `docs/d2p/bootstrap.md` (this file) and `docs/d2p/README.md` (the usage guide) — the prompts in §3 reference them by those paths, and Copilot reads them as context.

**If you received this repo as a scaffold** (README, docs/, .github/, templates/ already present): skip §0 and §1 — they're in place — and go straight to the Phase prompts in §3.

Otherwise: open the folder in VS Code and create the files in §1 with the exact contents given (Copilot can do this too: paste a section and say "create these files verbatim"). Then run the Phase prompts in §3 in order.

Check once that VS Code settings enable prompt and instruction files (`chat.promptFiles: true`, `github.copilot.chat.codeGeneration.useInstructionFiles: true`). In current VS Code both default on.

---

## 1. Copilot configuration files (historical copy — the live files are in `.github/`; `copilot-instructions.md` there is the semiAgency-wide version and supersedes §1.1)

### 1.1 `.github/copilot-instructions.md`

```markdown
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

## ID scheme (used everywhere; scripts check for orphans)
- Needs/pains/constraints in discovery.md: `N1`, `N2`, … (never renumber; mark superseded ones `~~N4~~`)
- Open questions: `Q1`, `Q2`, … with status `open | resolved(<evidence>) | dropped`
- Options: `O1`–`O3`
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
```

### 1.2 `.github/instructions/discovery.instructions.md`

```markdown
---
applyTo: "engagements/**/discovery.md"
---
# discovery.md schema
Sections, in this order, all present even if empty:
1. `## Context` — 3–6 lines: who the stakeholders are, what they own, why now.
2. `## Needs` — table: `| id | need | evidence | priority(H/M/L) | status |`. ids N1…; evidence is a citation.
3. `## Pains` — table with the same columns, ids continue the N sequence.
4. `## Constraints` — table, same columns (tech, policy, budget, timing).
5. `## Decisions taken` — bullets with citation.
6. `## Open questions` — table: `| id | question | owner | blocking(Y/N) | status |`.
7. `## Stakeholder map` — table: `| person | role | cares about | influence(H/M/L) |`.
8. `## Unverified` — things heard once or inferred; never cited as facts elsewhere.

Rules: never delete a row — mark status `superseded` and add a new row. Never invent evidence.
A merge (from a follow-up) appends rows and updates status; it does not rewrite existing text.
```

### 1.3 `.github/instructions/options.instructions.md`

```markdown
---
applyTo: "engagements/**/options.md"
---
# options.md schema
Exactly 2 or 3 options, `## O1 — <name>` … Each option has, in order:
- `**Summary**` (2–3 lines)
- `**Fit to needs**` table: `| need | how addressed | strength(full/partial/none) |` — every H-priority need must appear
- `**Effort**` band: S / M / L / XL with one line of justification
- `**Risks**` (max 4 bullets)
- `**Assumptions that must be true**` (bullets)
- `**Not a fit if**` (one line)
End with `## Comparison` — one table, options as columns, rows: coverage of H needs, effort, main risk, time to first value.
Do NOT recommend an option. The user chooses (gate G2).
```

### 1.4 `.github/instructions/proposal.instructions.md`

```markdown
---
applyTo: "engagements/**/proposal.md"
---
# proposal.md schema
Prose, not bullets, except where noted. Sections:
1. `## What we heard` — the problem in the stakeholders' words, citing needs `[N1, N3]`.
2. `## What we propose` — the chosen option (from state.json `chosen_option`), concrete.
3. `## How it works` — bullets allowed; the user journey and the moving parts.
4. `## What it does not do` — scope boundaries; reference options rejected and why (one line each).
5. `## Effort and timeline` — phases with rough duration bands.
6. `## Risks and mitigations` — table.
7. `## What we need from you` — decisions and inputs required from stakeholders.
8. `## Traceability` — table `| need | addressed in section |` covering every non-superseded N id.
Every claim about the stakeholders' situation cites an N id. Claims without one go under "Assumptions".
```

### 1.4b `.github/instructions/storylines.instructions.md`

```markdown
---
applyTo: "engagements/**/storylines.md"
---
# storylines.md schema
Exactly TWO storylines, `## S1 — <name>` and `## S2 — <name>`. They tell the SAME proposal (the option chosen at G2) in different ways — e.g. problem-first vs. vision-first, decision-first vs. journey, stakeholder-pain-led vs. outcome-led. They must NOT differ in what is proposed.
Each storyline has, in order:
- `**Thesis**` — the one sentence the audience should repeat afterwards
- `**Arc**` — 3–5 beats in prose (what the audience feels/learns at each beat)
- `**Slide outline**` — table `| # | kind | title | refs |` using only kinds from `brand/components.md`, with the ask on its own slide
- `**Works well because**` (max 3 bullets, specific to THIS audience from deck meta / proposal)
- `**Risks**` (max 3 bullets: where this telling can lose them)
- `**Coverage**` — list of every H-priority N id and the slide # that carries it (all must be present)
Then `## Comparison` — one table, S1/S2 as columns; rows: opening, where the ask lands, time to first "why should I care", strongest slide, biggest risk, fit to audience.
Then `## Recommendation` — which storyline and 3 lines why. The user decides (gate G3); do not build anything.
```

### 1.5 `.github/instructions/deck.instructions.md`

```markdown
---
applyTo: "engagements/**/deck.json"
---
# deck.json rules
- Only `kind` values listed in `brand/components.md`. Only the `fields` tags that component lists.
- String fields: one line. List fields: bullets; prefix `  - ` for level-2.
- Respect each component's stated capacity (max bullets, max chars per tag) from `brand/components.md`.
- Every content slide has `"refs"` with the N/O ids it covers. Title and section slides may omit refs.
- Slide count: within the range `brand/examples/` shows for the target duration in `meta.minutes`.
- `meta.storyline` must equal `state.json` `gates.G3.chosen_storyline`, and the slide sequence must follow that storyline's `Slide outline` table in `storylines.md` (same order, same kinds; titles may be polished, refs may be extended but not dropped).
```

### 1.6 `.github/instructions/speech.instructions.md`

```markdown
---
applyTo: "engagements/**/speech.md"
---
# speech.md rules
- One `## Slide N — <title>` section per slide in deck.json, same order, same N.
- Spoken language, first person plural, short sentences. No bullet points inside a slide's script.
- Mark words to stress as `**word**`. Use the emphasis glossary and preferred terms from `brand/voice.md`.
- Target pace from `brand/voice.md` (`words_per_minute`); total words must fit `meta.minutes` in deck.json with 15% slack for questions.
- End each slide's script with a one-line transition to the next slide.
```

### 1.7 `.github/agents/analyst.agent.md`

```markdown
---
description: Runs one stage of the D2P pipeline (synthesis, options, proposal, outline, speech, tasks) and validates its output.
tools: ['codebase', 'editFiles', 'runCommands', 'search']
---
You are the analyst for the D2P (Discovery2Presentation) pipeline. Follow `.github/copilot-instructions.md` strictly.
Before writing an artifact, read the matching `.github/instructions/*.instructions.md` for its schema.
After writing, run `python scripts/validate.py <artifact>` in the terminal and fix errors. Then stop and summarize in 5 lines what you produced and what the user should check at the gate.
Never advance stages, never edit inputs, never touch brand/components.pptx.
```

### 1.8 `.github/agents/critic.agent.md`

```markdown
---
description: Read-only reviewer. Finds unsupported claims, gaps against discovery.md, and weak slides. Cannot edit files.
tools: ['codebase', 'search']
---
You are a hostile but fair reviewer. You may read anything in the repo; you cannot edit.
Output a markdown report with three sections: `## Unsupported claims` (each with the sentence and which N id it would need), `## Gaps` (H-priority needs not addressed), `## Weakest points` (max 5, each with a concrete fix suggestion).
Be specific: quote the text you object to. Do not praise.
```

### 1.9 Prompt files — `.github/prompts/*.prompt.md`

Two further prompts live in the repo but are not reproduced here — `write-storylines.prompt.md` (deck kind) and `summarize-meeting.prompt.md` (meeting kind); see `.github/prompts/` and `docs/d2p/scenarios.md`. All prompts take `engagement` as input: `/synthesize-discovery: engagement=2026-09-acme`. In VS Code, `${input:engagement}` prompts for it.

**`prep-discovery.prompt.md`**
```markdown
---
mode: agent
description: Build the pre-discovery brief and question guide for an engagement
---
Engagement: `engagements/${input:engagement}`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read `normalized/manifest.json`.
2. Read every file in `normalized/`.
3. Write `brief.md` with: `## Context` (what we know, cited), `## Hypotheses` (3–5, each labelled HYPOTHESIS and stating what evidence would confirm/refute it), `## Question guide` (grouped by theme: current process, pain, constraints, success measures, decision makers; 12–20 questions total, open-ended, ordered easy → sensitive), `## Logistics` (who should be in the room and why).
4. Run `python scripts/validate.py engagements/${input:engagement}/brief.md`.
```

**`synthesize-discovery.prompt.md`**
```markdown
---
mode: agent
description: Turn transcript, notes and documents into discovery.md
---
Engagement: `engagements/${input:engagement}`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read `normalized/manifest.json`.
2. Read the normalized transcript(s), notes and documents. If a transcript exceeds ~8,000 words, process it in the chunks `ingest.py` produced (`normalized/T1.part01.md`, …), keeping a running list of N and Q ids, then merge.
3. Write `discovery.md` following `.github/instructions/discovery.instructions.md`. Every row cites a source. Put anything heard once or inferred under `## Unverified`.
4. Run `python scripts/validate.py engagements/${input:engagement}/discovery.md` and fix errors.
5. Stop. Tell the user how many needs, open questions (and how many are blocking) you found, and the 3 items you are least sure about — that is what to verify at gate G1.
```

**`merge-followup.prompt.md`**
```markdown
---
mode: agent
description: Merge a follow-up meeting into the existing discovery.md
---
Engagement: `engagements/${input:engagement}`. New material: `${input:file}` (a path under inputs/).
1. Run `python scripts/ingest.py engagements/${input:engagement}` so the new file is normalized and has a source id.
2. Read the new normalized file and the current `discovery.md`.
3. Merge: append new N rows; for each open question that the new material answers, set status `resolved(<citation>)`; add new Q rows; never rewrite existing rows except their status. Move items from Unverified to Needs/Pains only if now cited.
4. Run `python scripts/validate.py engagements/${input:engagement}/discovery.md`.
5. Run `python scripts/followup_agenda.py engagements/${input:engagement}` and tell the user whether a further follow-up is needed (any blocking Q still open).
```

**`sketch-options.prompt.md`**
```markdown
---
mode: agent
description: Sketch 2–3 candidate solution approaches from discovery.md
---
Engagement: `engagements/${input:engagement}`.
1. Read `discovery.md`. If any blocking Q is open, stop and say so.
2. Write `options.md` per `.github/instructions/options.instructions.md`. Make the options genuinely different in shape (e.g., minimal/rules-based vs. agentic vs. process-change-only), not three flavours of one idea. At least one option must be deliberately small.
3. Run `python scripts/validate.py engagements/${input:engagement}/options.md` and fix errors.
4. Stop. Do not recommend. List which H-priority needs each option leaves uncovered.
```

**`write-proposal.prompt.md`**
```markdown
---
mode: agent
description: Write proposal.md from the chosen option, then two storylines with a recommendation
---
Engagement: `engagements/${input:engagement}`.
1. Read `state.json`; use `gates.G2.chosen_option`. If missing, stop and ask the user to choose an option first.
2. Read `discovery.md`, `options.md`, and `brand/voice.md` if present.
3. Write `proposal.md` per `.github/instructions/proposal.instructions.md`. Run `python scripts/validate.py engagements/${input:engagement}/proposal.md` and fix errors, especially traceability gaps.
4. Read `brand/components.md` and `brand/examples/*.json`. Write `storylines.md` per `.github/instructions/storylines.instructions.md`: two genuinely different tellings of THIS proposal for the audience named in `state.json` (`audience`, `minutes`). Run validate on it.
5. Stop. Summarize: the 3 proposal claims you are least sure about (gate G3 check), and your storyline recommendation in 3 lines. Tell the user to record the decision with `python scripts/status.py <dir> --pass G3 --storyline S1|S2`.
```

**`outline-deck.prompt.md`**
```markdown
---
mode: agent
description: Turn the approved proposal + chosen storyline into deck.json using only corporate components
---
Engagement: `engagements/${input:engagement}`.
1. Read `state.json`. If `gates.G3.passed` is false or `chosen_storyline` is null, stop and tell the user to pass G3 first.
2. Read `brand/components.md` (allowed kinds, tags, capacities), `proposal.md`, and the chosen storyline's section in `storylines.md`.
3. Write `deck.json` per `.github/instructions/deck.instructions.md`, following the chosen storyline's slide outline exactly in order and kinds; fill each slide's fields from proposal.md with citations preserved as `[N#]` refs, not as visible text. Set `meta.storyline`.
4. Run `python scripts/validate.py engagements/${input:engagement}/deck.json` then `python scripts/storyboard.py engagements/${input:engagement}`.
5. Stop. Tell the user to review `storyboard.html`, then run `python scripts/build_deck.py engagements/${input:engagement}` and open the result in PowerPoint (gate G4).
```

**`write-speech.prompt.md`**
```markdown
---
mode: agent
description: Write per-slide speaker notes with emphasis markup
---
Engagement: `engagements/${input:engagement}`.
1. Read `deck.json`, `proposal.md`, `brand/voice.md`.
2. Write `speech.md` per `.github/instructions/speech.instructions.md`.
3. Run `python scripts/timing.py engagements/${input:engagement}` and adjust until total time fits with slack. Then run `python scripts/validate.py engagements/${input:engagement}/speech.md`.
4. Tell the user: total minutes, the longest slide, and which slides have no emphasis words.
```

**`critique-deck.prompt.md`** (use with `@critic`)
```markdown
---
mode: agent
description: Hostile review of deck.json + speech.md against discovery.md
---
Engagement: `engagements/${input:engagement}`.
Read `discovery.md`, `proposal.md`, `deck.json`, `speech.md`. Produce the critic report, then add `## Questions the stakeholders will ask` — 8–12 pointed questions with a one-line suggested answer each, and mark the 3 you think are most dangerous. Write the report to `critique.md`.
```

**`brief-team.prompt.md`**
```markdown
---
mode: agent
description: One-page team brief from the proposal
---
Engagement: `engagements/${input:engagement}`.
Read `proposal.md` and `discovery.md`. Write `team-brief.md`, max one page: `## What the stakeholders told us` (5 bullets, cited), `## What we proposed` (5 bullets), `## What I need from the team` (decisions, estimates, owners), `## Open risks`. End with `## Proposed agenda` for the team meeting, 30 minutes, timed.
```

**`extract-tasks.prompt.md`**
```markdown
---
mode: agent
description: Extract team tasks from the team meeting into tasks.json (not yet appended)
---
Engagement: `engagements/${input:engagement}`. Meeting file: `${input:file}`.
1. Run `python scripts/ingest.py engagements/${input:engagement}` and read the normalized meeting file.
2. Write `tasks.json`: array of `{ "action", "owner", "due" (ISO date or null), "depends_on" (array of action text or []), "source" (file + timestamp), "notes" }`. Only explicit commitments or clearly assigned actions; put maybes under a top-level `"candidates"` array instead.
3. Run `python scripts/validate.py engagements/${input:engagement}/tasks.json`.
4. Stop. Tell the user to review, then run `python scripts/append_tasks.py engagements/${input:engagement}` themselves (gate G5).
```

### 1.10 `brand/voice.md` (you write this one; template)

```markdown
# Voice
words_per_minute: 130   # measure once; used by timing.py

## Always use
- "agentic workflow" (not "AI automation")
- ...

## Never use
- "leverage", "synergy", ...

## Emphasis glossary (words I want to land)
- ownership, measurable, reversible, ...

## Tone
Direct, concrete, no hype. Numbers over adjectives.
```

---

## 2. Script specifications (what Copilot must build)

Each script: stdlib only, `argparse`, exit code 1 on failure, `--selftest` flag that runs without any engagement present. All share `scripts/ooxml.py`.

| Script | Input | Output | Acceptance |
|---|---|---|---|
| `ooxml.py` | – | helpers: `read_pkg(path)->dict[name,bytes]`, `write_pkg(path, parts)` (Content_Types first, deflate), `parts_rels(name)`, `next_part_number(parts, prefix)`, `content_type_add/remove`, `replace_shape_text(sp_elem, value, is_list)`, namespace constants | selftest round-trips `tests/fixtures/mini.pptx` byte-for-byte when no edits are made |
| `new_engagement.py` | `--kind proposal\|deck\|meeting`, `--name`, `--subject`, `--stakeholders`, `--audience`, `--minutes`, `--from <dir>` | folder tree, `state.json` (kind, stage 0, all gates false), the templates that kind needs, plus `templates/audience.md` → `inputs/audience.md` for proposal and deck kinds; `--from` copies another engagement's `inputs/` and `normalized/` | idempotent; refuses to overwrite |
| `ingest.py` | engagement dir | `normalized/<Tn|Dn|notes>.md`, `manifest.json` `{id, file, sha256, kind, words}`; transcripts >8k words also split into `.partNN.md` at speaker turns | `.md` transcript: normalizes `[hh:mm:ss] Speaker:` lines; `.docx`/`.pptx`: text via `word/document.xml` / `ppt/slides/*.xml` `<w:t>`/`<a:t>` (pptx one section per slide in presentation order, `[slide N]` headers, title vs body distinguished by placeholder type, notes included, and the manifest entry carries `"slides": N` and `"master_sha"` so a draft deck can be recognised and its master compared with `components.pptx`); `.pdf`: best-effort (inflate `FlateDecode` streams, collect `Tj`/`TJ` strings) with a loud warning to convert via Word if the result looks wrong; unchanged files (same sha) are skipped |
| `validate.py` | any artifact path | errors to stdout, exit 1 | checks per schema in §1 (including `content.md` K/F ids and `notes.md` for the other kinds): sections present, tables well-formed, ids unique and sequential, every row cited, options count 2–3, proposal traceability covers all non-superseded N, storylines: exactly 2, both cover every H-priority N, recommendation present, outline kinds exist in components.json; deck.json `meta.storyline` equals state and slide kinds/order match that storyline's outline, `clone` entries point at an existing input slide whose deck shares `components.pptx`'s master (compare `ppt/slideMasters/slideMaster1.xml` hashes) and that slide is not title-only, deck kinds/tags/capacities vs `brand/components.json`, deck refs exist, speech sections match deck slides, tasks.json shape; also prints orphan N ids for options/proposal/deck |
| `status.py` | engagement dir | prints stage, gate status, blocking Qs, and the exact next command/prompt | applies the gate map for the engagement's kind (proposal: G1–G5; deck: G1,G3,G4; meeting: G5) and only ever suggests prompts valid for that kind; reads `state.json` and artifact presence; `--pass G1`, `--pass G2 --option O2`, `--pass G3 --storyline S2`, `--pass G4`, `--pass G5` record gates; refuses G3 without `--storyline`; re-passing an earlier gate resets every later gate (e.g. `--pass G2` clears G3/G4) |
| `followup_agenda.py` | engagement dir | `followups/agenda-N.md` + `agenda-N.ics` (VEVENT, DESCRIPTION = agenda text, no attendees) | reads open points from whichever exists: `discovery.md`, `content.md`, or `notes.md`; agenda lists open Qs (blocking first) with owners; N increments; `.ics` opens in Outlook |
| `inspect_components.py` | `brand/components.pptx` | `brand/components.json` + `components.md` | per slide: kind (from `{{kind:...}}` text on the slide, else derived from the layout name), tags = explicit shape names matching `{{...}}` PLUS auto-detected placeholders (`<p:ph type="title">`→`title`, `type="subTitle"`→`subtitle`, `type="body"` or untyped `idx`→`body`, `body2`… in idx order) so ordinary slides need no manual tagging, recursive through groups, for each tag: is_list (paragraph count >1 in exemplar), capacity (chars of exemplar text, bullets count), theme fonts/colors from `ppt/theme/theme1.xml` |
| `skeletonize_deck.py` | any `.pptx` | `brand/examples/<name>.json` | per slide: layout name, title text, shape count, bullet count, has_picture; plus totals |
| `build_deck.py` | engagement dir | `deck.pptx` | as specified in design §5.2; a `{"clone": "inputs/x.pptx#n"}` slide is copied verbatim (part + rels + media) from that file instead of from `components.pptx`, allowed only when `validate.py` confirmed the same master; refuses to overwrite a deck without the `generated-by` stamp unless `--force`; `--notes-only` rewrites speaker notes in an existing built deck without touching slides; `--only-kinds a,b` builds a subset for bisecting repair issues; selftest builds 3 slides from `tests/fixtures/mini.pptx` and re-parses every part as XML |
| `storyboard.py` | engagement dir | `storyboard.html` | one card per slide: kind, title, fields, refs; unfilled tags highlighted; inline CSS only |
| `lint_deck.py` | engagement dir | report to stdout | text length > 1.3× exemplar capacity, >6 bullets, empty tags, N ids never referenced, slide count outside examples' range for `meta.minutes` |
| `timing.py` | engagement dir | per-slide and total minutes at `words_per_minute` from `brand/voice.md` | flags slides >2.5 min and total > `meta.minutes` × 0.85 |
| `append_tasks.py` | engagement dir or any tasks `.json` | rows appended to `tracker/actions.xlsx` | **ships with the workspace (built on `xlsxlite.py`)** — inline strings, dimension + table ref bump, dedup on a hash of source, context and action, lock → `tasks.pending.csv`; selftest included. Phase 5 only verifies it against your real tracker |

Fixtures you create once in PowerPoint/Excel on the corporate machine: `tests/fixtures/mini.pptx` (3 slides on the corporate template, shapes named `{{title}}`, `{{body}}`, `{{subtitle}}`), `tests/fixtures/tracker.xlsx` (header row per design §7, two sample rows, formatted as a Table named `Actions`).

---

## 3. Implementation prompts for Copilot agent mode

Paste one at a time. Use the best model available. After each, run the selftests it names, `git commit`, and only then continue. If Copilot reaches for a library, point it at the first rule in `copilot-instructions.md` and make it redo the file.

**Phase 1 — skeleton + discovery loop**
```
Read .github/copilot-instructions.md and docs/d2p/design.md §2–§4.
Implement scripts/new_engagement.py, scripts/ingest.py, scripts/validate.py (schemas for brief.md, discovery.md, content.md, notes.md for now), scripts/status.py (kind-aware gate map, see docs/d2p/scenarios.md), scripts/followup_agenda.py per the specifications table in docs/d2p/bootstrap.md §2.
templates/ already exist; read them.
Stdlib only. Every script has --selftest that creates its own temp fixtures under a temp dir and cleans up.
Run all selftests and show me the output. Then create a sample engagement "2026-09-sample" with a fake 200-line transcript in inputs/transcript.md and run ingest + status on it.
```

**Phase 2 — OOXML core + components inspector**
```
Read docs/d2p/design.md §5 fully.
Implement scripts/ooxml.py and scripts/inspect_components.py per docs/d2p/bootstrap.md §2.
ooxml.py must: read/write a package preserving unknown parts byte-for-byte; add/remove content-type overrides; find shapes by name recursively including <p:grpSp>; replace text in a shape keeping the first run's <a:rPr>; skip runs inside <a:fld>; clone a paragraph as a template for list values with lvl set.
Selftest for ooxml.py: round-trip tests/fixtures/mini.pptx with no edits and assert identical part bytes; then replace {{title}} text and assert the XML still parses and the text changed.
Run inspect_components.py on brand/components.pptx and show me components.md.
```

**Phase 3 — deck builder**
```
Implement scripts/build_deck.py, scripts/storyboard.py, scripts/lint_deck.py per docs/d2p/design.md §5.2 and docs/d2p/bootstrap.md §2, using ooxml.py.
Extend validate.py to cover deck.json against brand/components.json.
Selftest builds a 3-slide deck from tests/fixtures/mini.pptx using a temporary deck.json and asserts: every part parses as XML, [Content_Types].xml has one override per slide, presentation.xml sldIdLst has 3 entries with unique ids >= 256, each slide's rels resolve to existing parts, notes slides exist and contain the speech text with b="1" runs where marked.
Then build engagements/2026-09-sample/deck.pptx from a deck.json you write using only kinds from brand/components.md. I will open it in PowerPoint and report whether it opens without repair.
```

**Phase 4 — options, proposal, speech, timing**
```
Extend scripts/validate.py to cover options.md, proposal.md (including the traceability check), storylines.md (two storylines, H-need coverage, recommendation), deck.json vs chosen storyline, speech.md (sections match deck.json slides). Extend status.py with --pass G3 --storyline.
Implement scripts/timing.py per docs/d2p/bootstrap.md §2.
Create templates/options.md, templates/proposal.md, templates/storylines.md, templates/speech.md matching the instruction files.
Run selftests. Then, using the sample engagement, run the prompts /sketch-options, /write-proposal, /write-speech in that order with me approving between them, and show that validate passes each time.
```

**Phase 5 — team follow-through (verify, don't build)**
```
scripts/append_tasks.py and scripts/xlsxlite.py already exist and are tested; do not rewrite them. Extend validate.py for tasks.json (shape per .github/instructions/todos.instructions.md: `tasks` and `candidates` arrays, `action` required).
Run python scripts/append_tasks.py --selftest. Then copy tracker/actions.xlsx to a temp dir and append the sample engagement's tasks.json to the copy twice; confirm exactly the expected number of new rows (dedup) and show me the output of python scripts/xlsxlite.py --dump <copy>.
I will open the copy in Excel and confirm it opens clean and the Table extends over the new rows. If Excel reports a repair, do not patch append_tasks.py blindly: show me the sheet XML diff between the original and the copy first.
```

**Phase 6 — hardening (only after two real engagements)**
```
Review every script for: error messages that name the file and line/id that failed; --help text; handling of engagement dirs with spaces; Windows path separators; UTF-8 with BOM in inputs. scripts/selftest_all.py already exists and lists the Copilot-built scripts; make sure every one of them passes there. Do not add features.
```

---

## 4. Running an engagement (cheat sheet)

Full step-by-step with what to check at each gate: `docs/d2p/README.md`.

```
python scripts/new_engagement.py --name 2026-09-acme --stakeholders "Maria K (Ops)","Jan D (IT)" --audience "Ops leadership" --minutes 20
  drop prior docs into inputs/                    → /prep-discovery
  after the meeting: drop transcript.md, notes.md → /synthesize-discovery
  verify facts                                    → python scripts/status.py <dir> --pass G1
  blocking Qs open? python scripts/followup_agenda.py <dir> → send agenda-1.ics → /merge-followup file=inputs/followup-1.md → back to G1
/sketch-options → choose                          → python scripts/status.py <dir> --pass G2 --option O2
/write-proposal (writes proposal.md + storylines.md) → approve facts, choose arc → status.py <dir> --pass G3 --storyline S2
/outline-deck → review storyboard.html → python scripts/build_deck.py <dir> → open deck.pptx → status.py <dir> --pass G4
/write-speech → python scripts/build_deck.py <dir> (re-embeds notes) → @critic /critique-deck
/brief-team → team meeting → drop team-meeting.md → /extract-tasks file=inputs/team-meeting.md
  review tasks.json                               → python scripts/append_tasks.py <dir>   (G5)
```

---

## 5. Things that will go wrong, in order of likelihood

1. **Copilot imports something.** `python-pptx`, `openpyxl`, `pyyaml`, `lxml`. The instruction file forbids it, but agent mode will still try when stuck. Reject the edit, restate the rule, continue.
2. **PowerPoint repair prompt on the first built deck.** Almost always one of: content-type override missing for a cloned slide; `sldId` reused; a `notesSlide` rel pointing at the old slide number; a media relationship id colliding. `build_deck.py --selftest` catches the first three; the fourth appears only with images — clone a component with a picture in Phase 3's manual test on purpose.
3. **Text doesn't land in a shape.** The shape is inside a group or is a placeholder whose name PowerPoint reset. Check `components.md` — if the tag isn't listed, the inspector didn't see it either.
4. **Excel says the tracker is corrupt.** Table `ref` not bumped, or a row `r` number out of order. Fall back to `.csv` for a week rather than debugging under time pressure; fix later.
5. **Discovery synthesis is too long or hallucinates.** Chunking is in the prompt; if it still happens, lower the chunk size in `ingest.py` to 5k words. Hallucination is what gate G1 is for — verify the 3 items the prompt asks it to flag.
