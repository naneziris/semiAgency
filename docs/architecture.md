# semiAgency — architecture

Two sides, one rule. **Microsoft 365 side:** everything that touches your emails, calendar, To Do or 1-1 notes runs as an Agent Builder agent inside M365 Copilot Chat and stays there. **Local side:** one VS Code workspace on the corporate Windows machine where GitHub Copilot (agent mode) reasons over files you own — engagements, meeting transcripts, topic interest profiles — with stdlib Python scripts for everything deterministic and explicit human gates. The only thing that crosses from M365 to local is a sanitized list of topic links (URLs and titles).

```
 MICROSOFT 365 (nothing leaves)                     LOCAL WORKSPACE (nothing about mail enters)
 ─────────────────────────────                      ────────────────────────────────────────────
 Daily Brief agent ── "Morning brief" ─▶ read        engagements/<name>/   D2P #1, meeting notes #3
                   ── "Triage inbox"  ─▶ To Do           @analyst · @critic · G1–G5 · D2P scripts
                   ── "Topic links"  ──┐                       │ tasks.json ─▶ append_tasks.py ─▶ tracker/actions.xlsx
 1-1 Prep agent    ── "Prep 1-1"      ─▶ read, paste  │
                                        agenda        │  kb/topics/<t>/links/<date>.md ◀── kb_ingest.py ◀── kb/inbox/ ◀─┘
 Power Automate    ── agenda empty?   ─▶ Teams ping   │        │  profile.md (@interviewer /interview-topic, /refine-topic)
                                                      │        ▼
                                                      │  @librarian /triage-topic ─▶ kb/topics/<t>/digests/<date>.md   (gate T2)
```

## The workflows and where each one lives

| # | workflow | runs where | how | gate | scheduling reality |
|---|---|---|---|---|---|
| 1 | Discovery2Presentation | local | `engagements/`, `@analyst`, `@critic`, D2P scripts (`docs/d2p/`) | G1–G5 | session-based; you drive it |
| 2 | Email triage | M365 | Daily Brief → **Triage inbox**; keep = add to To Do; delegate = paste the one-line ask | you read it | daily, one click |
| 3 | Meeting notes | local | transcript `.md` → `new_engagement.py --kind meeting` → `/summarize-meeting` → tracker | G5 | per meeting |
| 4 | Team 1-1s | M365 — its own flow | 1-1 Prep → read → paste agenda into the invite; Power Automate checks the agenda the day before | you read it | prep on demand; the flow runs itself |
| 6 | Topic news triage | M365 → local | Daily Brief → **Topic links** → `kb_ingest.py` → `/triage-topic` against `profile.md`; `/interview-topic` once, `/refine-topic` on feedback | T2 | daily, same click |
| 7 | Morning brief | M365 | Daily Brief → **Morning brief** (calendar + triaged mail + To Do) | you read it | daily, one click |
| 8 | Knowledge base | local | `kb/` — profiles, links, digests, meetings; `kb_ingest.py`, `kb_index.py` | — | the destination, not a workflow |

(#5 approvals queue is out of scope by decision.)

## Why it is shaped like this

**The data boundary decides the split, not convenience.** Email, calendar and 1-1 content are sensitive; the local Copilot never sees them. So the daily loop (#2, #7) and the 1-1 flow (#4) run entirely in M365 Copilot Chat and their outputs are read, not stored — the only durable trace is what you choose to put in To Do or an invite. Local Copilot gets what is yours to keep: engagement material, transcripts you already receive as files, and your own interest criteria.

**Two agents, not five.** The Daily Brief agent does triage, brief and link extraction because they read the same window of the same mailbox; one agent, three starter prompts. 1-1 Prep is separate because its knowledge source (the OneNote notebook) and its cadence are different, and because you asked for it to be its own flow. No workflow needs more than one agent.

**The M365 side judges what only it can see; the local side judges what only it can see.** Urgency of a mail, clashes in the calendar, what to bring to a meeting — the agent has the thread, the attendees, the To Do list. What counts as an interesting AI link — that criterion is yours, changes with your feedback, and lives in a file you own, so it runs locally with an explicit gate (T2).

**Everything the model does is one prompt, one artifact, then stop.** Same principle as D2P and SemiPilotPro; no long executions, nothing to checkpoint.

**One tracker, one writer script — for local work.** Meeting actions and D2P team tasks end in `tracker/actions.xlsx` via `append_tasks.py`, deduplicated. Email actions live in Microsoft To Do. Two lists is a real cost; the boundary makes it unavoidable, and the morning brief covers To Do while `engagements/*/state.json` + `status.py` cover the local side.

**Handoffs are evidence, and the ingest refuses the wrong kind.** `kb/topics/*/links/` and `kb/meetings/` are never edited; `kb_ingest.py` rejects `email`, `calendar` and `one-on-one` handoffs outright and warns if a links table carries a sender column.

## The scheduling limitation, plainly

Agent Builder cannot run itself. #2, #6 and #7 are "daily" because you click a starter once each morning (~2 minutes for the brief, ~1 for the links). Agent Builder also cannot write: To Do entries and invite agendas are your paste. The Power Automate agenda check is the only unattended piece, because it needs no AI. Copilot Studio (paid) would let the brief arrive on its own and could write the To Do items; nothing in the instruction texts would change.

## Repo layout

```
semiAgency/
├── README.md                     start here — setup, routines, gates
├── VERSION
├── .github/
│   ├── copilot-instructions.md   conventions and the data boundary
│   ├── agents/                   analyst, critic (D2P) · librarian, interviewer (topics)
│   ├── instructions/             one schema file per artifact type (applyTo-scoped)
│   └── prompts/                  one slash-prompt per AI step
├── agent-builder/                the M365 side: agent instructions, starters, usage flows, the Power Automate flow
├── docs/
│   ├── architecture.md           this file
│   ├── handoff-format.md         the M365 → local contract (topic-links, meeting, note)
│   └── d2p/                      D2P design, scenarios, bootstrap kit, upgrades
├── scripts/                      stdlib only; shipped KB/tracker scripts + Copilot-built D2P scripts
├── templates/                    D2P artifact skeletons
├── brand/                        corporate deck components + voice.md (never leaves the machine)
├── tracker/actions.xlsx          local action list (D2P + meetings)
├── kb/                           topics, meetings, notes (see kb/README.md)
├── engagements/                  one folder per D2P engagement / meeting
└── tests/fixtures/               mini.pptx, tracker.xlsx — created once on the corporate machine
```
