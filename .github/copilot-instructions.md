# Discovery2Presentation — repo conventions

This repo turns stakeholder discovery into a proposal, a corporate-styled .pptx, and team tasks; it also does plain decks and meeting write-ups. Read `docs/design.md` if you need the big picture; `docs/runbooks/<kind>.md` is what the user follows. Work one stage at a time and stop.

## Hard rules
- Python 3 standard library ONLY. Never import or suggest installing third-party packages.
  Allowed: zipfile, xml.etree.ElementTree, json, re, hashlib, csv, datetime, pathlib, argparse, sys, os, shutil, io, copy, textwrap, html.
- Never run PowerShell. Use `python scripts/<name>.py` from the integrated terminal.
- Never modify anything under `engagements/*/inputs/` or `brand/components.pptx`.
- Never write to `tracker/actions.csv` directly. Tasks go into `tasks.json` for review; the user runs `append_tasks.py` (gate G5).
- Never hand-write PowerPoint XML from scratch in scripts. Clone existing parts and edit text nodes.
- Machine-read artifacts are JSON (`state.json`, `deck.json`, `tasks.json`, `brand/components.json`). Human-read artifacts are markdown.
- After writing or editing any engagement artifact, run `python scripts/validate.py <path>` and fix what it reports before finishing.
- Do exactly the stage the prompt asks for. Do not advance `state.json` yourself; `scripts/status.py` tells the user the next action.
- The engagement to work on is `engagements/<name>` where `<name>` is the prompt's `engagement` input, or - when it was not given - the single line in `engagements/CURRENT`. Never guess from folder listings; if neither exists, stop and say so. Scripts accept the engagement dir as an optional argument and fall back to the same file.
- When unsure about a fact, write it under "Unverified" rather than asserting it. Never invent evidence, deadlines, or commitments.

## Engagement kinds (state.json `kind`) and their prompts
- `proposal` — `/discovery-prep` → `/discovery-synthesize` → G1 → (`/merge-followup`) → `/options` → G2 → `/proposal` → G3 → `/deck-outline` → G4 → `/speech` → `/team-brief` → `/team-tasks` → G5.
- `deck` — `/content` → G1 → `/storylines` → G3 → `/deck-outline` → G4 → `/speech`.
- `meeting` — `/meeting-notes` → G5.
- `@critic /critique` works for proposal and deck at any point after G1.
Every prompt checks `kind` first and, on a mismatch, names the right prompt instead of running.

## ID scheme (used everywhere; scripts check for orphans)
- Needs/pains/constraints in discovery.md: `N1`, `N2`, … (never renumber; mark superseded ones `~~N4~~`)
- Open questions: `Q1`, `Q2`, … with status `open | resolved(<evidence>) | dropped`
- Options: `O1`–`O3`; storylines `S1`/`S2`
- Key messages / facts in content.md (deck kind): `K1…`, `F1…`
- Proposal sections cite needs inline: `[N1, N3]`; slides in deck.json carry `"refs": [...]` of N/O or K/F ids
- Tasks in tasks.json carry `"source"`: the meeting file + timestamp they came from

## Citations
Every extracted fact cites its source: `[T1 00:12:34]` for transcript file T1 at that timestamp, `[doc:<filename> p<page>]` for documents (`[doc:draft.pptx slide 4]` for a draft deck), `[notes]` for the user's own notes. Source ids come from `normalized/manifest.json`.

## Style
- Concise, concrete, no filler. Bullets in artifacts; prose in proposal.md.
- Use the terminology in `brand/voice.md` when it exists.
- Owner values in tasks: `me`, or `delegate:<person-slug>` (name lower-cased, hyphens). Actions are imperative and name the person and the thing.
