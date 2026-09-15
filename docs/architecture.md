# semiAgency — architecture

One VS Code workspace on the corporate Windows machine. GitHub Copilot (agent mode) is the reasoning layer; Python standard-library scripts do everything deterministic; files are the state; you approve at explicit gates. Microsoft 365 data reaches the workspace through *handoffs* produced by Agent Builder agents and pasted into `kb/inbox/`.

```
        M365 (Outlook, Calendar, OneNote, Teams)
                │  Agent Builder agents — reactive, you click them
                │  Daily Exporter · 1-1 Prep · (Meeting Exporter prompt)
                ▼  copy → paste
   ┌──────────── kb/inbox/ ──────────────┐
   │ python scripts/kb_ingest.py         │
   ▼                                     ▼
 kb/calendar  kb/email  kb/topics/*/links  kb/people/*        ← evidence, never edited
   │            │          │                 │
   │   @librarian /triage-inbox   @librarian /triage-topic   @librarian /prep-1-1
   │            │          │                 │
   │       kb/triage/*.todos.json     kb/topics/*/digests/     kb/people/*/*.prep.md
   │            │  (you review, T1)
   │            ▼
   │   python scripts/append_tasks.py ──────────────▶ tracker/actions.xlsx ◀── engagements/*/tasks.json (G5)
   │                                                        │
   └── python scripts/brief_collect.py ◀────────────────────┘◀── engagements/*/state.json
                 │
        @librarian /morning-brief → kb/briefs/<date>.md

 engagements/<name>/ — D2P (workflow #1) and the deck / meeting kinds (#3): docs/d2p/
```

## The workflows and where each one lives

| # | workflow | M365 side | local side | gate(s) | scheduling reality |
|---|---|---|---|---|---|
| 1 | Discovery2Presentation | none required (transcripts arrive as `.md`); Meeting Exporter prompt if not | `engagements/`, `@analyst`, `@critic`, D2P scripts | G1–G5 | session-based; you drive it |
| 2 | Email triage | Daily Exporter → `## Emails` | `/triage-inbox` → `kb/triage/` → `append_tasks.py` | T1 | daily, you click the export |
| 3 | Meeting notes | none (transcript `.md`) | `new_engagement.py --kind meeting` + `/summarize-meeting` → tracker | G5 | per meeting |
| 4 | Team 1-1s | 1-1 Prep (the prep itself); Power Automate flow for the agenda check | optional `kb/people/` history, `/prep-1-1` | — | prep on demand; the flow runs itself |
| 6 | Topic news triage | Daily Exporter → `## Topic links: ai` | `/interview-topic` once → `profile.md`; `/triage-topic` daily → digest; `/refine-topic` on feedback | T2 | daily, same export as #2 |
| 7 | Morning brief | Daily Exporter → `## Calendar` | `brief_collect.py` + `/morning-brief` | B1 | daily, last step of the routine |
| 8 | Knowledge base | — | `kb/`, `kb_ingest.py`, `kb_index.py` | — | the destination, not a workflow |

(#5 approvals queue is out of scope by decision.)

## Why it is shaped like this

**Everything the model does is one prompt, one artifact, then stop.** Same principle as D2P and SemiPilotPro: no long-running orchestration, so nothing to checkpoint. `brief_collect.py`, `kb_index.py` and `status.py` tell you what to do next; the "orchestrator" is you reading one line.

**The M365 side extracts, the local side judges.** The Daily Exporter is told not to prioritise. Prioritisation needs context M365 doesn't have — which engagement is at which gate, who you delegated what to, what you flagged last week — and that context lives in `kb/` and the tracker. It also keeps the M365 instructions short and stable: the export shape changes rarely; your criteria change often, and they live in files you own.

**One tracker, many writers, one writer script.** Email todos, meeting actions, D2P team tasks and 1-1 actions all end in `tracker/actions.xlsx`, each with a `source` column so you can filter. Only `append_tasks.py` writes it; every writer stages a JSON you review first (T1/G5). Dedup is by hash of (source, context, action), so re-running is safe.

**Handoffs are evidence.** `kb/calendar`, `kb/email`, `kb/topics/*/links`, `kb/people/*/<date>.md` and `kb/archive` are never edited, like `engagements/*/inputs/`. Everything derived from them is regenerable: delete a digest and re-run `/triage-topic`.

**Per-topic interest profiles are files, written from an interview, changed only by your feedback.** That is what makes the daily flagging explainable: every flagged item names the criterion. If the digest is wrong, the fix is one profile line, not a prompt rewrite.

## The scheduling limitation, plainly

Agent Builder cannot run itself. So #2, #6 and #7 are "daily" only because you click **Export today** once each morning. The rest of the routine is local and fast (see `agent-builder/README.md` for the 10-minute sequence). The only thing in this build that runs unattended is the Power Automate agenda check for #4, because it needs no AI.

What Copilot Studio (paid) would buy you: the Daily Exporter running at 07:00 and dropping its output into a SharePoint file you sync locally → `kb_ingest.py` picks it up → the routine starts with `/triage-inbox`. The handoff format was designed so that switch changes nothing on the local side. Decide after a month of manual runs: if you skip the export more than twice a week, the automation is worth paying for; if you don't, it isn't.

## Repo layout

```
semiAgency/
├── README.md                     start here — routines and where to look
├── VERSION
├── .github/
│   ├── copilot-instructions.md   conventions for all workflows
│   ├── agents/                   analyst, critic (D2P) · librarian, interviewer (KB)
│   ├── instructions/             one schema file per artifact type (applyTo-scoped)
│   └── prompts/                  one slash-prompt per AI step
├── agent-builder/                the M365 side: agent instructions, usage flows, the Power Automate flow
├── docs/
│   ├── architecture.md           this file
│   ├── handoff-format.md         the M365 → local contract
│   └── d2p/                      D2P design, scenarios, bootstrap kit (scripts spec + Copilot build prompts), upgrades
├── scripts/                      stdlib only; shipped KB/tracker scripts + Copilot-built D2P scripts
├── templates/                    D2P artifact skeletons
├── brand/                        corporate deck components + voice.md (never leaves the machine)
├── tracker/actions.xlsx          the one action list
├── kb/                           the knowledge base (see kb/README.md)
├── engagements/                  one folder per D2P engagement / meeting
└── tests/fixtures/               mini.pptx, tracker.xlsx — created once on the corporate machine
```
