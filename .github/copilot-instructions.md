# semiAgency — repo conventions

This workspace runs Nikos's recurring work as file-based, human-gated workflows with GitHub Copilot as the reasoning layer and Python scripts for everything deterministic. Read `docs/architecture.md` for the big picture. Work one stage at a time and stop.

Areas:
- `engagements/` + `docs/d2p/` — Discovery2Presentation (D2P): stakeholder discovery → options → proposal → corporate deck → team tasks; also the `deck` and `meeting` kinds (`docs/d2p/scenarios.md`). Agent: `@analyst`, reviewer `@critic`.
- `kb/` — the local knowledge base: calendar/email exports handed off from M365, email triage, topic interest profiles and digests, 1-1 history, morning briefs. Agent: `@librarian`; topic interviews `@interviewer`.
- `tracker/actions.xlsx` — the single list of actions across all workflows. Only `scripts/append_tasks.py` writes to it.

## Hard rules
- Python 3 standard library ONLY. Never import or suggest installing third-party packages.
  Allowed: zipfile, xml.etree.ElementTree, json, re, hashlib, csv, datetime, pathlib, argparse, sys, os, shutil, io, copy, textwrap, html.
- Never run PowerShell. Use `python scripts/<name>.py` from the integrated terminal.
- Never modify anything under `engagements/*/inputs/`, `brand/components.pptx`, `kb/archive/`, `kb/calendar/`, `kb/email/`, `kb/topics/*/links/`. These are evidence.
- Never write to `tracker/actions.xlsx` directly. Tasks go into a `tasks.json` / `*.todos.json` for review; the user runs `append_tasks.py` (gate G5 / T2).
- Never hand-write PowerPoint/Excel XML from scratch in scripts. Clone existing parts and edit text nodes.
- Machine-read artifacts are JSON (`state.json`, `deck.json`, `tasks.json`, `*.todos.json`, `brand/components.json`). Human-read artifacts are markdown.
- After writing or editing any engagement artifact, run `python scripts/validate.py <path>` and fix what it reports before finishing.
- Do exactly the stage the prompt asks for. Do not advance `state.json` yourself; `scripts/status.py` tells the user the next action.
- When unsure about a fact, write it under "Unverified" (or mark it `?`) rather than asserting it. Never invent evidence, deadlines, or commitments.

## Engagement kinds (state.json `kind`)
- `proposal` — full flow: discovery → options → proposal + storylines → deck → tasks. Gates G1–G5.
- `deck` — a presentation from notes/documents that is not a proposal: content → storylines → deck. Gates G1, G3, G4.
- `meeting` — write-up and action points only: notes → tasks. Gate G5.
Prompts check `kind` and refuse to run on the wrong kind. See `docs/d2p/scenarios.md`.

## Knowledge-base gates (the KB workflows have their own, lighter, gates)
- **T1 triage** — `/triage-inbox` writes `kb/triage/<date>.md` + `.todos.json`; the user edits the JSON, then runs `append_tasks.py`. Nothing reaches the tracker unreviewed.
- **T2 digest** — `/triage-topic` flags items; the user's 👍/👎 feedback via `/refine-topic` is the only way the interest profile changes after the interview.
- **B1 brief** — `/morning-brief` only restates what `brief_collect.py` collected plus judgement about priorities; it never invents events or actions.

## ID scheme (used everywhere; scripts check for orphans)
- Needs/pains/constraints in discovery.md: `N1`, `N2`, … (never renumber; mark superseded ones `~~N4~~`)
- Open questions: `Q1`, `Q2`, … with status `open | resolved(<evidence>) | dropped`
- Options: `O1`–`O3`; storylines `S1`/`S2`
- Key messages / facts in content.md (deck kind): `K1…`, `F1…`
- Emails in a daily export: `E1`, `E2`, … (per day); links: their URL
- Proposal sections cite needs inline: `[N1, N3]`; slides in deck.json carry `"refs": [...]`
- Tasks carry `"source"`: the meeting file / email id / person they came from, and `"context"`: the engagement name or the date

## Citations
Every extracted fact cites its source: `[T1 00:12:34]` for transcript file T1 at that timestamp, `[doc:<filename> p<page>]` for documents, `[notes]` for the user's own notes, `[E3]` for an email in the day's export, `[kb/people/maria-k/2026-09-01.md]` for a KB file. Source ids for engagements come from `normalized/manifest.json`.

## People, topics, dates
- People slugs: the name the user uses, lower-cased, hyphens (`maria-k`). Topic slugs: short lower-case (`ai`). Dates: `YYYY-MM-DD`.
- Owner values in tasks: `me`, or `delegate:<person-slug>`.
- Urgency: `high | normal | low`. Effort: `S` (<30 min) | `M` (half a day) | `L` (more).

## Style
- Concise, concrete, no filler. Bullets in artifacts; prose in proposal.md and the morning brief.
- Use the terminology in `brand/voice.md` when it exists.
- Address the user as "you"; write actions in the imperative ("Confirm renewal with Sabine").
