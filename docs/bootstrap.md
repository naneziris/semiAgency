# Discovery2Presentation (D2P) — Copilot Bootstrap Kit

Companion to `docs/design.md`: the script specifications (§2) and the implementation prompts you paste into Copilot agent mode to have it write them (§3). Nothing here needs a network, a package, or a file from outside.

Constraints baked in: Python stdlib only, no PowerShell, JSON for machine-read artifacts, markdown for human-read ones, one stage per Copilot turn, five human gates that are never skipped.

---

## 0. Manual setup (5 minutes)

The repo ships as a scaffold (README, docs/, .github/, templates/, `scripts/new_engagement.py`, `scripts/append_tasks.py`). On the corporate machine: copy it in, open in VS Code, `git init`, check once that prompt and instruction files are enabled (`chat.promptFiles: true`, `github.copilot.chat.codeGeneration.useInstructionFiles: true` — both default on). Then run the Phase prompts in §3 in order.

---

## 1. Copilot configuration files

They live in `.github/` (copilot-instructions.md, agents/, instructions/, prompts/) and ship with the repo; nothing to create by hand. `brand/voice.md` is the one file you write yourself (template in place).

---

## 2. Script specifications (what Copilot must build)

Each script: stdlib only, `argparse`, exit code 1 on failure, `--selftest` flag that runs without any engagement present. All share `scripts/ooxml.py`. **Every script that takes an engagement dir accepts it as an optional positional argument and falls back to the name in `engagements/CURRENT`** (written by `new_engagement.py`; a name or a path both work; a clear error when neither is given). Console output is ASCII only (Windows terminals).

| Script | Input | Output | Acceptance |
|---|---|---|---|
| `ooxml.py` | – | helpers: `read_pkg(path)->dict[name,bytes]`, `write_pkg(path, parts)` (Content_Types first, deflate), `parts_rels(name)`, `next_part_number(parts, prefix)`, `content_type_add/remove`, `replace_shape_text(sp_elem, value, is_list)`, namespace constants | selftest round-trips `tests/fixtures/mini.pptx` byte-for-byte when no edits are made |
| `new_engagement.py` | **ships** — no arguments: asks kind (menu of three), subject, folder name (default `YYYY-MM-<slug>`, meetings `YYYY-MM-DD-<slug>`), and for proposal/deck stakeholders, audience, minutes; flags `--kind`, `--name`, `--subject`, `--stakeholders`, `--audience`, `--minutes`, `--from <dir>`, `--no-wait`, `--check [dir]`, `--use <name>` | folder tree, `state.json`, `templates/audience.md` → `inputs/audience.md` for proposal and deck, **`engagements/CURRENT`** (the name every script and prompt defaults to); then waits until the user has filled `inputs/`, lists what it found (transcript / notes / document / draft deck / pdf / unreadable, with warnings), and prints the first Copilot prompt to paste | selftest covers the interactive path; refuses to overwrite; no artifact templates are copied into the engagement (status.py infers progress from artifact presence) |
| `ingest.py` | engagement dir (optional, defaults to CURRENT) | `normalized/<Tn|Dn|notes>.md`, `manifest.json` `{id, file, sha256, kind, words}`; transcripts >8k words also split into `.partNN.md` at speaker turns | `.md` transcript: normalizes `[hh:mm:ss] Speaker:` lines; `.docx`/`.pptx`: text via `word/document.xml` / `ppt/slides/*.xml` `<w:t>`/`<a:t>` (pptx one section per slide in presentation order, `[slide N]` headers, title vs body distinguished by placeholder type, notes included, and the manifest entry carries `"slides": N` and `"master_sha"` so a draft deck can be recognised and its master compared with `components.pptx`); `.pdf`: best-effort (inflate `FlateDecode` streams, collect `Tj`/`TJ` strings) with a loud warning to convert via Word if the result looks wrong; unchanged files (same sha) are skipped |
| `validate.py` | any artifact path | errors to stdout, exit 1 | checks per schema in §1 (including `content.md` K/F ids and `notes.md` for the other kinds): sections present, tables well-formed, ids unique and sequential, every row cited, options count 2–3, proposal traceability covers all non-superseded N, storylines: exactly 2, both cover every H-priority N, recommendation present, outline kinds exist in components.json; deck.json `meta.storyline` equals state and slide kinds/order match that storyline's outline, `clone` entries point at an existing input slide whose deck shares `components.pptx`'s master (compare `ppt/slideMasters/slideMaster1.xml` hashes) and that slide is not title-only, deck kinds/tags/capacities vs `brand/components.json`, deck refs exist, speech sections match deck slides, tasks.json shape; also prints orphan N ids for options/proposal/deck |
| `status.py` | engagement dir, **optional — defaults to `engagements/CURRENT`** | prints stage, gate status, blocking Qs, **the current step of `docs/runbooks/<kind>.md` verbatim** (the `## Step N` section whose gate is the next unpassed one, or the step after the last passed gate), and at the end two lines the user can copy: the next Copilot prompt with `engagement=<name>` filled in, and the next terminal command | applies the gate map for the engagement's kind (proposal: G1–G5; deck: G1,G3,G4; meeting: G5) and only ever suggests prompts valid for that kind; reads `state.json` and artifact presence; **`--pass` with no gate name = the next unpassed gate**: prints that step's `- [ ]` checklist, asks `Confirm? [y/N]`, asks `Which option? (O1/O2/O3)` for G2 and `Which storyline? (S1/S2)` for G3 when `--option`/`--storyline` were not given (offers the storyline the model recommended as default), then records it; `--pass G1`, `--pass G2 --option O2`, `--pass G3 --storyline S2`, `--pass G4`, `--pass G5` still work unattended; refuses G3 without a storyline; re-passing an earlier gate resets every later gate (e.g. `--pass G2` clears G3/G4) and says so; when every gate is passed prints `done` and what is left manual (dry run); `--use <name>` switches `CURRENT` (same as new_engagement.py --use) |
| `followup_agenda.py` | engagement dir (optional, defaults to CURRENT) | `followups/agenda-N.md` + `agenda-N.ics` (VEVENT, DESCRIPTION = agenda text, no attendees) | reads open points from whichever exists: `discovery.md`, `content.md`, or `notes.md`; agenda lists open Qs (blocking first) with owners; N increments; `.ics` opens in Outlook |
| `inspect_components.py` | `brand/components.pptx` | `brand/components.json` + `components.md` | per slide: kind (from `{{kind:...}}` text on the slide, else derived from the layout name), tags = explicit shape names matching `{{...}}` PLUS auto-detected placeholders (`<p:ph type="title">`→`title`, `type="subTitle"`→`subtitle`, `type="body"` or untyped `idx`→`body`, `body2`… in idx order) so ordinary slides need no manual tagging, recursive through groups, for each tag: is_list (paragraph count >1 in exemplar), capacity (chars of exemplar text, bullets count), theme fonts/colors from `ppt/theme/theme1.xml` |
| `skeletonize_deck.py` | any `.pptx` | `brand/examples/<name>.json` | per slide: layout name, title text, shape count, bullet count, has_picture; plus totals |
| `build_deck.py` | engagement dir (optional, defaults to CURRENT) | `deck.pptx`; **runs `lint_deck.py` automatically after a build** (`--no-lint` to skip) and ends with "open deck.pptx; to change anything edit deck.json and rebuild; then `python scripts/status.py --pass`" | as specified in design §5.2; a `{"clone": "inputs/x.pptx#n"}` slide is copied verbatim (part + rels + media) from that file instead of from `components.pptx`, allowed only when `validate.py` confirmed the same master; refuses to overwrite a deck without the `generated-by` stamp unless `--force`; `--notes-only` **runs `timing.py` first, prints its report,** then rewrites speaker notes in an existing built deck without touching slides; `--only-kinds a,b` builds a subset for bisecting repair issues; selftest builds 3 slides from `tests/fixtures/mini.pptx` and re-parses every part as XML |
| `storyboard.py` | engagement dir (optional, defaults to CURRENT) | `storyboard.html` | one card per slide: kind, title, fields, refs; unfilled tags highlighted; inline CSS only |
| `lint_deck.py` | engagement dir (optional, defaults to CURRENT) | report to stdout | text length > 1.3× exemplar capacity, >6 bullets, empty tags, N ids never referenced, slide count outside examples' range for `meta.minutes` |
| `timing.py` | engagement dir (optional, defaults to CURRENT) | per-slide and total minutes at `words_per_minute` from `brand/voice.md` | flags slides >2.5 min and total > `meta.minutes` × 0.85 |
| `append_tasks.py` | engagement dir (optional, defaults to CURRENT) | rows appended to `tracker/actions.csv`; lists the rows it will add; then asks `Pass gate G5 now? [y/N]` (or `--pass-g5`) and records G5 in `state.json` | **ships** — stdlib csv, dedup on sha1(source, engagement, action); Phase 5 only extends validate.py for tasks.json |

Fixture you create once in PowerPoint on the corporate machine: `tests/fixtures/mini.pptx` (3 slides on the corporate template, shapes named `{{title}}`, `{{body}}`, `{{subtitle}}`).

---

## 3. Implementation prompts for Copilot agent mode

Paste one at a time. Use the best model available. After each, run the selftests it names, `git commit`, and only then continue. If Copilot reaches for a library, point it at the first rule in `copilot-instructions.md` and make it redo the file.

**Phase 1 — skeleton + discovery loop**
```
Read .github/copilot-instructions.md and docs/design.md §2–§4.
scripts/new_engagement.py and scripts/append_tasks.py already exist and are tested; do not rewrite them. Read new_engagement.py first: it defines engagements/CURRENT, which every script you write must fall back to when no engagement dir is given (reuse its resolve_dir logic).
Implement scripts/ingest.py, scripts/validate.py (schemas for brief.md, discovery.md, content.md, notes.md for now), scripts/status.py (kind-aware gate map; prints the current `## Step N` section of docs/runbooks/<kind>.md; `--pass` with no gate name passes the next gate interactively as specified), scripts/followup_agenda.py per the specifications table in docs/bootstrap.md §2.
templates/ already exist; read them.
Stdlib only. Every script has --selftest that creates its own temp fixtures under a temp dir and cleans up.
Run all selftests and show me the output. Then run `python scripts/new_engagement.py --kind proposal --name 2026-09-sample --subject "sample" --no-wait`, put a fake 200-line transcript in its inputs/transcript.md, and run `python scripts/new_engagement.py --check`, `python scripts/ingest.py` and `python scripts/status.py` with no engagement argument on it.
```

**Phase 2 — OOXML core + components inspector**
```
Read docs/design.md §5 fully.
Implement scripts/ooxml.py and scripts/inspect_components.py per docs/bootstrap.md §2.
ooxml.py must: read/write a package preserving unknown parts byte-for-byte; add/remove content-type overrides; find shapes by name recursively including <p:grpSp>; replace text in a shape keeping the first run's <a:rPr>; skip runs inside <a:fld>; clone a paragraph as a template for list values with lvl set.
Selftest for ooxml.py: round-trip tests/fixtures/mini.pptx with no edits and assert identical part bytes; then replace {{title}} text and assert the XML still parses and the text changed.
Run inspect_components.py on brand/components.pptx and show me components.md.
```

**Phase 3 — deck builder**
```
Implement scripts/build_deck.py, scripts/storyboard.py, scripts/lint_deck.py per docs/design.md §5.2 and docs/bootstrap.md §2, using ooxml.py. build_deck.py runs lint_deck.py after every build unless --no-lint, and --notes-only runs timing.py first (timing.py arrives in Phase 4; until then print that it is missing).
Extend validate.py to cover deck.json against brand/components.json.
Selftest builds a 3-slide deck from tests/fixtures/mini.pptx using a temporary deck.json and asserts: every part parses as XML, [Content_Types].xml has one override per slide, presentation.xml sldIdLst has 3 entries with unique ids >= 256, each slide's rels resolve to existing parts, notes slides exist and contain the speech text with b="1" runs where marked.
Then build engagements/2026-09-sample/deck.pptx from a deck.json you write using only kinds from brand/components.md. I will open it in PowerPoint and report whether it opens without repair.
```

**Phase 4 — options, proposal, speech, timing**
```
Extend scripts/validate.py to cover options.md, proposal.md (including the traceability check), storylines.md (two storylines, H-need coverage, recommendation), deck.json vs chosen storyline, speech.md (sections match deck.json slides). Extend status.py with --pass G3 --storyline.
Implement scripts/timing.py per docs/bootstrap.md §2.
Create templates/options.md, templates/proposal.md, templates/storylines.md, templates/speech.md matching the instruction files.
Run selftests. Then, using the sample engagement, run the prompts /options, /proposal, /speech in that order with me approving between them, and show that validate passes each time.
```

**Phase 5 — team follow-through**
```
scripts/append_tasks.py already exists (CSV tracker) and is tested; do not rewrite it. Extend validate.py for tasks.json (shape per .github/instructions/tasks.instructions.md: `tasks` and `candidates` arrays, `action` required, owner `me` or `delegate:<slug>`).
Run python scripts/append_tasks.py --selftest and python scripts/validate.py on the sample engagement's tasks.json.
```

**Phase 6 — hardening (only after two real engagements)**
```
Review every script for: error messages that name the file and line/id that failed; --help text; handling of engagement dirs with spaces; Windows path separators; UTF-8 with BOM in inputs. scripts/selftest_all.py already exists and lists the Copilot-built scripts; make sure every one of them passes there. Do not add features.
```

---

## 4. Running an engagement

`docs/after-meeting.md` is the one page the user follows: `python scripts/new_engagement.py` → paste the prompt it prints → `python scripts/status.py` → checklist → `python scripts/status.py --pass` → repeat. `docs/runbooks/proposal.md`, `deck.md`, `meeting.md` hold the per-kind detail that `status.py` prints step by step.

---

## 5. Things that will go wrong, in order of likelihood

1. **Copilot imports something.** `python-pptx`, `openpyxl`, `pyyaml`, `lxml`. The instruction file forbids it, but agent mode will still try when stuck. Reject the edit, restate the rule, continue.
2. **PowerPoint repair prompt on the first built deck.** Almost always one of: content-type override missing for a cloned slide; `sldId` reused; a `notesSlide` rel pointing at the old slide number; a media relationship id colliding. `build_deck.py --selftest` catches the first three; the fourth appears only with images — clone a component with a picture in Phase 3's manual test on purpose.
3. **Text doesn't land in a shape.** The shape is inside a group or is a placeholder whose name PowerPoint reset. Check `components.md` — if the tag isn't listed, the inspector didn't see it either.
4. **Excel changed the tracker CSV encoding or delimiter on save.** `append_tasks.py` reads with utf-8-sig and commas; if Excel saved with `;` (regional setting), open with the Text Import wizard instead of double-click, or keep the file in a text editor.
5. **Discovery synthesis is too long or hallucinates.** Chunking is in the prompt; if it still happens, lower the chunk size in `ingest.py` to 5k words. Hallucination is what gate G1 is for — verify the 3 items the prompt asks it to flag.
