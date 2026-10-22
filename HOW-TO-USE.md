# How to use SemiAgency — plain version

Start here. This page answers three questions: **which tool runs where**, **what each one is for**, and **exactly what to do**. The map (`index.html`) shows the same thing visually: pick *Microsoft 365 Copilot* or *GitHub Copilot in VS Code* first, then a flow; the **All steps** tab lists every flow with copy buttons.

---

## 0. The one split that matters

| | **Microsoft 365 Copilot** | **GitHub Copilot (VS Code)** |
|---|---|---|
| Where you type | Copilot Chat in Teams / Outlook / m365.cloud.microsoft, or Copilot inside a Teams meeting | Copilot Chat in VS Code, **agent mode**, with this folder open |
| What you paste | Plain-English prompts, or you pick an agent and send a starter | Slash commands like `/meeting-notes` (they live in `.github/prompts/`) + a few `python scripts/…` in the terminal |
| Needs this repo? | **No.** The repo only stores the build sheets (`m365/`). Once built, you never open it again. | **Yes.** Everything runs inside this folder. |
| Files | SharePoint (`Meetings` library) | `engagements/<name>/` on your machine |

Rule of thumb: daily life (brief, meetings, 1-1s, emails) → **M365**. Proposals, decks and the topic record → **VS Code**. The topic record is the one flow that uses both: it starts in M365 and finishes in VS Code.

---

## 1. Use cases at a glance

| I want to… | Runs in | Daily effort | Section |
|---|---|---|---|
| Know what matters today | M365 | 0 (arrives at 07:00) | 2.1 |
| Summarise a meeting + get my actions (Teams only) | M365 | 1 message | 2.2 |
| Be prepared for tomorrow's meetings | M365 | 0 (arrives at 18:00) | 2.3 |
| Prepare a 1-1 | M365 | 1 message | 2.4 |
| Write an email in my voice | M365 | 1 message | 2.5 |
| Judge an AI idea for a team | M365 (or VS Code) | 1 conversation | 2.6 / 3.5 |
| **Keep one record per topic across its meetings** | **M365 → VS Code** | ~10 min per meeting | **3.3** |
| Turn a stakeholder meeting into options + proposal + deck | VS Code | an afternoon | 3.1 |
| Turn material I already have into a corporate deck | VS Code | 1–2 h | 3.2 |
| Find the best Copilot model for my work | VS Code (`bench/`) | an afternoon | 3.6 |

---

## 2. Microsoft 365 Copilot

Each piece has a **set up once** (from the sheet in `m365/`) and a **daily use**. On the map, a piece's page shows both, with the exact text to paste.

How to read the build sheets:
- **Scheduled prompt** (sheets 1, 3): copy the **single grey code block** → paste into Copilot Chat → click the clock icon (**Schedule**) → days and time.
- **Agent** (sheets 4, 5, 7): Copilot Chat → **Agents → Create agent** → *Configure*. Name and Description from the sheet. **Instructions: only the text between `=== INSTRUCTIONS ===` and `=== END ===`** (not those two lines). Knowledge and starter prompts as listed.
- **Power Automate flow** (sheets 2, 6): nothing to paste; you click it together in Power Automate following the numbered steps.
- **Plain prompt** (sheet 8): nothing to build; you paste it when you need it.

Before building sheets 2, 3, 4, 6: create a SharePoint library **Meetings** with a folder **1-1** inside.

### 2.1 Morning brief
- **Set up once (10 min):** `m365/01-daily-brief.md` → scheduled prompt, weekdays 07:00.
- **Use:** nothing. Copilot Chat → *Chats* → the scheduled one: Top 3, timeline with clashes, waiting on me, waiting on others.

### 2.2 Summarise a meeting in Teams (Auto-file meetings + Meeting Summariser)
- **Set up once:** flow `m365/02-meeting-filing-flow.md` (45 min) + agent `m365/04-meeting-summariser-agent.md` (10 min).
- **Use:**
  1. Meeting ends → Teams pings you: *"Filed: 2026-10-22 Data Platform sync — <link>"* (a folder in SharePoint `Meetings` with the transcript).
  2. *(optional)* drag your notes into that folder.
  3. Copilot Chat → Agents → **Meeting Summariser** → send:
     ```
     Summarise the meeting "2026-10-22 Data Platform sync".
     ```
  4. Copy your actions into Microsoft To Do.
- Same agent, other questions:
  ```
  Summarise every meeting folder dated today.
  List every open action on me from meetings in the last 14 days.
  Prepare me for my next meeting "<subject>".
  ```
- Tracking the topic over many meetings? Use 3.3 — it starts with the end-of-meeting summary (2.7) instead.

### 2.3 Evening prep
- **Set up once (10 min):** `m365/03-evening-prep-prompt.md` → replace `<site name>` / `<notebook name>` → schedule weekdays 18:00. Needs 2.2's flow running for a while.
- **Use:** nothing. At 18:00: per meeting tomorrow — last time, open actions, proposed agenda — plus a list for To Do.

### 2.4 1-1 prep (1-1 agenda reminder + Meeting Summariser)
- **Set up once:** name every recurring 1-1 **`1-1 <name>`**; flow `m365/06-agenda-check-flow.md` (15 min).
- **Use:** 16:00 the day before, Teams pings you if the agenda is empty → Meeting Summariser:
  ```
  Prepare my next 1-1 with Maria.
  ```
  → paste the proposed agenda into the invite under a line `Agenda`.

### 2.5 Email Drafter
- **Set up once (20 min + collecting mails):** `m365/05-email-drafter-agent.md`; `voice-profile.docx` + 15–20 sent mails in SharePoint `Voice/exemplars/`.
- **Use:** Agents → **Email Drafter**:
  ```
  Draft an email to Thomas: can't do Thursday, need cost numbers first, propose Tuesday, friendly, he's senior.
  ```
  then `Same, half the length.` / `Same, but firmer.` → copy into Outlook.

### 2.6 AI idea check (Fit Finder, shared with colleagues)
- **Set up once (20 min + ~45 min context file):** `m365/07-fit-finder-agent.md`. The context file (allowed tools, data rules, past ideas, who to send good ideas to) is yours to write. Share the agent.
- **Use (anyone):** Agents → **Fit Finder**:
  ```
  I saw this idea: <describe it>. My team does <what>. Where would this fit?
  ```
  → one-page brief with a two-day test. If it says "continue", the brief becomes the first input of 3.1.

### 2.7 End-of-meeting summary (feeds the Topic record)
- **Set up once:** nothing.
- **Use:** at the end of the meeting, paste the grey block from `m365/08-end-of-meeting-summary.md` into **Copilot in the Teams meeting**. Copy the answer → it goes into the topic's folder (3.3, step 2).

---

## 3. GitHub Copilot in VS Code (this repo)

### ⚠ Before any of this works
The VS Code flows call scripts that **are not in this copy yet**: `ingest.py`, `validate.py`, `status.py`, `build_deck.py`, `followup_agenda.py`, … They are generated once on the corporate machine with the prompts in `docs/bootstrap.md` §3 (≈2 h, needs your corporate PowerPoint template). Until then `/meeting-notes`, `/discovery-synthesize`, `/content` etc. stop at their first step. Working today: `new_engagement.py`, `where.py`, `append_tasks.py`, `/start`, `/fit-finder` (once its context file exists), `bench/`.

### The vocabulary
| Term | Means |
|---|---|
| **engagement** ("job") | one folder `engagements/<name>/`. Your files go in its `inputs/`. For the topic record: one folder per topic. |
| **kind** | which job: `proposal` (they expect options), `deck` (message already decided), `meeting` (topic record) |
| **gate G1–G5** | a checkpoint where *you* review before the next step. G1 facts right · G2 option chosen · G3 storyline chosen · G4 you opened the real deck · G5 you reviewed the actions before they reach the tracker |
| **cited** | every line ends with where it came from: `[T1 00:12:30]` transcript 1 at 12m30s, `[S2]` M365 summary 2, `[notes]` your notes |
| **tracker** | `tracker/actions.csv` — your action list; open it in Excel |
| `/start` | lost? Type it in Copilot Chat; it tells you the one next step. `python scripts/where.py` does the same in the terminal. |

Every job starts with `python scripts/new_engagement.py` — it asks the kind and subject, creates the folder, waits while you drop files into `inputs/`, then **prints the exact slash command to paste**.

### 3.1 Proposal — stakeholder problem → options → deck
1. `python scripts/new_engagement.py` → **proposal**. Drop transcript, notes, their docs. Spend 10 min on `inputs/audience.md`.
2. `/discovery-synthesize` → check the 3 flagged items → `python scripts/status.py --pass` (**G1**).
3. `/options` → pick one → `status.py --pass` (**G2**).
4. `/proposal` → pick a storyline → `status.py --pass` (**G3**).
5. `/deck-outline` → `python scripts/build_deck.py` → open `deck.pptx` → `status.py --pass` (**G4**).
6. Optional: `/speech`, `@critic /critique`.
7. After presenting: `/team-brief`, then `/team-tasks file=inputs/team-meeting.md` → `python scripts/append_tasks.py` (**G5**).

### 3.2 Deck from material I already have
`new_engagement.py` → **deck** → `/content` (G1) → `/storylines` (G3) → `/deck-outline` + `build_deck.py` (G4).

### 3.3 Topic record — one living document per topic
**When:** a topic runs over several meetings (a migration, a vendor, a project) and you want one up-to-date document — where things stand, decisions with dates, open points, a meeting log — and your actions in the tracker. Works for a single meeting too.

**After every meeting on the topic:**
1. **Microsoft 365, end of the meeting:** paste the prompt from `m365/08-end-of-meeting-summary.md` into Copilot in the Teams meeting. Copy the answer.
2. **VS Code terminal:**
   - first meeting on the topic: `python scripts/new_engagement.py` → **meeting** → topic name (e.g. "Data platform migration")
   - later meetings: `python scripts/new_engagement.py --use <topic folder>`

   Save into the folder's `inputs/`, **date first**:
   - `2026-10-22-summary.md` — the M365 answer
   - `2026-10-22-transcript.docx` — Teams → meeting → Recap → Transcript → Download (recommended: it is what the record is checked against; without it, facts are marked *(summary only)*)
   - `2026-10-22-notes.md` — your own notes (they count most)
   - `notes.md` — optional standing notes on the whole topic
3. **Copilot Chat:** `/meeting-notes` → rewrites `notes.md` (the topic record) and puts only the **new** actions in `tasks.json`.
4. **Review** `tasks.json` (delete what isn't yours, promote a maybe you own) → terminal: `python scripts/append_tasks.py` → appends to the tracker, passes G5.
5. If the record says *Follow-up needed: Y*: `python scripts/followup_agenda.py` → agenda + Outlook `.ics`.

Mark actions done in `tracker/actions.csv`; the next update shows them as done. The topic turns into a proposal? `python scripts/new_engagement.py --kind proposal --name <new> --from engagements/<topic>`. Detail: `docs/runbooks/meeting.md`.

### 3.4 Something missing
`/new-flow <what you want>` designs and adds a new flow.

### 3.5 AI idea check locally
`/fit-finder` — same as 2.6, no Agent Builder needed. Needs `brand/fit-finder-context.md`.

### 3.6 Model benchmark
Copy `bench/` into an empty folder, open it in VS Code, follow `bench/README.md`.

---

## 4. Map

`python scripts/build_city.py` rebuilds `index.html`. Open it, choose where you work, pick a flow; every step has a badge (Microsoft 365 / VS Code), ⧉ copies the exact text to paste, ⚙ opens what to set up once. Share `index.html#for=m365` with colleagues who only use Microsoft 365, `#for=vscode` with those who use VS Code. The M365 prompts and agent instructions on the map are pulled from the build sheets at build time, so the sheets stay the single source.

## 5. Old names → new names

| Old | New |
|---|---|
| Town Hall | Start a job |
| Front Desk | Help: what do I run? |
| Herald's House | Prepare the discovery meeting |
| Scribe's House | Facts from the meeting |
| Messenger's Stoa | Follow-up meeting |
| Temple of Options | Choose an option |
| Design Studio | Write the proposal |
| Print House / Little Print House | Build the proposal deck / Build the deck |
| The Theatre / Open-air Theatre | Speaker notes / Speaker notes & critic |
| High Court | Critic review |
| Task Depot | Team brief & tasks |
| Little Archive | Key messages & facts |
| Story Studio | Pick a storyline |
| The Notary | Topic record |
| The Embassy | AI idea check (Fit Finder) |
| Observatory | Model benchmark |
| Radio Tower | Morning brief |
| Harbour Office | Auto-file meetings |
| Lighthouse | Evening prep |
| The Library | Meeting Summariser |
| Post Office | Email Drafter |
| Clock Tower | 1-1 agenda reminder |
| *(new)* | End-of-meeting summary |
| The Workshop / Harbour Works | Local setup / M365 setup |
| Cartographer / Architect's Office | Map maintenance / Add a new flow |
