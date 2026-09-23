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
- `/fit-finder` needs no engagement and writes no files: it is a conversation that ends in a brief, using the instructions in `m365/07-fit-finder-agent.md` and the context in `brand/fit-finder-context.md`.
Every prompt checks `kind` first. On a mismatch, don't just name another prompt. Say: "This engagement was started as a <kind>, so its step here is `<prompt>`. If you meant a <kind this prompt is for>, start a new engagement in the terminal: `python scripts/new_engagement.py`."

## Handoffs (whenever you send the user to another step, prompt, script or tool)
- Say **where** it runs, every time: "in the terminal: `python scripts/…`" or "in Copilot Chat (agent mode): `/…`". Never just "run X" or "use X".
- When a step is blocked by a gate, give the command that gets past it, not only the gate name: "Gate G2 isn't passed yet. In the terminal: `python scripts/status.py` shows the checklist and the command that passes it."
- End every stage with the exact next step. If nothing follows inside this tool, say what happens outside it (e.g. "hold the team meeting, then …").
- Name other tools the way the user sees them: an M365 agent by its name and where to find it ("Microsoft 365 Copilot Chat → Agents → Meeting Summariser"), a person by name (never a role or an internal term).

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
