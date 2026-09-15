# semiAgency — repo conventions

This workspace runs Nikos's recurring work as file-based, human-gated workflows with GitHub Copilot as the reasoning layer and Python scripts for everything deterministic. Read `docs/architecture.md` for the big picture. Work one stage at a time and stop.

Areas:
- `engagements/` + `docs/d2p/` — Discovery2Presentation (D2P): stakeholder discovery → options → proposal → corporate deck → team tasks; also the `deck` and `meeting` kinds (`docs/d2p/scenarios.md`). Agent: `@analyst`, reviewer `@critic`.
- `kb/` — the local knowledge base: topic interest profiles, daily topic link lists (URLs and titles only) and digests, plus meeting transcripts/notes waiting to become engagements. Agent: `@librarian`; topic interviews `@interviewer`.
- **Boundary:** email, calendar, To Do and 1-1 (OneNote) content stay in Microsoft 365 — the Daily Brief and 1-1 Prep agents there do that work in chat (`agent-builder/`). Never ask the user to paste emails, calendar entries or 1-1 notes here; if some appear, do not store them.
- `tracker/actions.xlsx` — the single list of actions across all workflows. Only `scripts/append_tasks.py` writes to it.

## Hard rules
- Python 3 standard library ONLY. Never import or suggest installing third-party packages.
  Allowed: zipfile, xml.etree.ElementTree, json, re, hashlib, csv, datetime, pathlib, argparse, sys, os, shutil, io, copy, textwrap, html.
- Never run PowerShell. Use `python scripts/<name>.py` from the integrated terminal.
- Never modify anything under `engagements/*/inputs/`, `brand/components.pptx`, `kb/archive/`, `kb/topics/*/links/`, `kb/meetings/`. These are evidence.
- Never write to `tracker/actions.xlsx` directly. Tasks go into `tasks.json` for review; the user runs `append_tasks.py` (gate G5).
- Never hand-write PowerPoint/Excel XML from scratch in scripts. Clone existing parts and edit text nodes.
- Machine-read artifacts are JSON (`state.json`, `deck.json`, `tasks.json`, `brand/components.json`). Human-read artifacts are markdown.
- After writing or editing any engagement artifact, run `python scripts/validate.py <path>` and fix what it reports before finishing.
- Do exactly the stage the prompt asks for. Do not advance `state.json` yourself; `scripts/status.py` tells the user the next action.
- When unsure about a fact, write it under "Unverified" (or mark it `?`) rather than asserting it. Never invent evidence, deadlines, or commitments.

## Engagement kinds (state.json `kind`)
- `proposal` — full flow: discovery → options → proposal + storylines → deck → tasks. Gates G1–G5.
- `deck` — a presentation from notes/documents that is not a proposal: content → storylines → deck. Gates G1, G3, G4.
- `meeting` — write-up and action points only: notes → tasks. Gate G5.
Prompts check `kind` and refuse to run on the wrong kind. See `docs/d2p/scenarios.md`.

## Knowledge-base gate
- **T2 digest** — `/triage-topic` flags items; the user's 👍/👎 feedback via `/refine-topic` is the only way the interest profile changes after the interview.

## ID scheme (used everywhere; scripts check for orphans)
- Needs/pains/constraints in discovery.md: `N1`, `N2`, … (never renumber; mark superseded ones `~~N4~~`)
- Open questions: `Q1`, `Q2`, … with status `open | resolved(<evidence>) | dropped`
- Options: `O1`–`O3`; storylines `S1`/`S2`
- Key messages / facts in content.md (deck kind): `K1…`, `F1…`
- Proposal sections cite needs inline: `[N1, N3]`; slides in deck.json carry `"refs": [...]`
- Tasks carry `"source"`: the meeting file + timestamp they came from, and `"context"`: the engagement name

## Citations
Every extracted fact cites its source: `[T1 00:12:34]` for transcript file T1 at that timestamp, `[doc:<filename> p<page>]` for documents, `[notes]` for the user's own notes, `[kb/topics/ai/links/2026-09-15.md]` for a KB file. Source ids for engagements come from `normalized/manifest.json`.

## Topics, dates, tasks
- Topic slugs: short lower-case (`ai`). Dates: `YYYY-MM-DD`.
- Owner values in tasks: `me`, or `delegate:<person-slug>` (name lower-cased, hyphens).
- Urgency: `high | normal | low`. Effort: `S` (<30 min) | `M` (half a day) | `L` (more).

## Style
- Concise, concrete, no filler. Bullets in artifacts; prose in proposal.md.
- Use the terminology in `brand/voice.md` when it exists.
- Address the user as "you"; write actions in the imperative ("Confirm renewal with Sabine").
