# SemiAgency — flows, agent use cases, and how the map should guide a newcomer

Written 2026-09-23 as input for the map (`index.html`, formerly `city.html`) UX rework. Source of truth: `README.md`, `city/city.json`, `.github/prompts`, `.github/agents`, `m365/*.md`, `bench/`.

Two terms, used strictly:

- **Flow** — an end-to-end route a person takes to get from a situation to a result. It chains several steps (prompts, scripts, agents, gates). This is what a newcomer is looking for.
- **Use case** — one thing a single prompt, agent or automation does. It is a building block; several flows reuse the same one.

---

## Part 1 — Flows

### Overview

| # | Flow | Environment | Starts from | Ends with | Effort |
|---|---|---|---|---|---|
| F1 | Stakeholder proposal | VS Code + Copilot | a discovery meeting | options, proposal, corporate deck, speaker notes, team tasks | an afternoon (first time), 5 gates |
| F2 | Deck from known content | VS Code + Copilot | notes / docs / a draft deck | corporate deck (+ notes) | 1–2 h, 3 gates |
| F3 | Meeting record (local) | VS Code + Copilot | a transcript + notes | one-page write-up + your actions in the tracker | ~10 min, 1 gate |
| F4 | Morning brief | M365 | nothing — runs at 07:00 | one-page brief of the day in Copilot Chat | 10 min setup, then automatic |
| F5 | Meeting lifecycle (M365) | M365 | a Teams meeting ends | filed folder → summary + your actions → prepared next meeting | 45+10+10 min setup, then ~2 clicks per meeting |
| F6 | 1-1 preparation | M365 | a recurring 1-1 tomorrow | an agenda in the invite | 15 min setup, then one click |
| F7 | Email drafting | M365 | rough text + a recipient | ready-to-send email in your voice | 20 min setup + exemplars |
| F8 | AI idea → fit check → proposal | M365 (anyone) → VS Code | an AI idea someone saw | one-page brief; promising ones enter F1 | one conversation |
| F9 | Model benchmark | VS Code + Copilot (separate workspace) | tasks where AI failed you | a pass/fail matrix per model | an afternoon, then 10 min per new model |
| F10 | Setup & maintenance | VS Code / M365 | a fresh machine or tenant | working pipeline, built M365 pieces, an up-to-date map | ~2 h local, ~2 h M365 |

F1–F3 are one engine (Discovery2Presentation, "D2P") with three `kind`s. F4–F7 are the M365 side and never touch the local workspace. F8 bridges the two. F9 is independent.

---

### F1 — Stakeholder proposal (`kind = proposal`)

**Use it when** someone described a problem to you and expects you to come back with options, a recommendation and a deck they can decide on.

**Example.** The head of Customer Service spends 45 minutes telling you their agents copy data between three systems and misses SLAs. They ask: "What could AI do here? Show us something at the steering committee in two weeks — 20 minutes slot."

**Input**
- `inputs/transcript.md` (Teams transcript), `inputs/notes.md` (your notes), any documents they sent (`.docx`, `.pptx`, `.md`)
- `inputs/audience.md` — who decides, what they push back on (strongly recommended)
- Once, beforehand: corporate template calibrated (`brand/`), `brand/voice.md`

**Steps**
1. *(optional, before the meeting)* `/discovery-prep` → `brief.md` with hypotheses and a question guide
2. `new_engagement.py` → kind `proposal`
3. `/discovery-synthesize` → `discovery.md` (needs N, open questions Q, each cited) → **G1 facts**
   - blocking questions open → `followup_agenda.py` → follow-up meeting → `/merge-followup` → back to G1
4. `/options` → 2–3 genuinely different approaches → **G2 you choose one**
5. `/proposal` → `proposal.md` + two storylines → **G3 you pick the storyline**
6. `/deck-outline` → `deck.json` + `storyboard.html` → `build_deck.py` → **G4 you open the deck**
7. `/speech` → timed speaker notes; `@critic /critique` → unsupported claims + likely audience questions
8. After presenting: `/team-brief` → one-page brief + agenda for your team; `/team-tasks` on their meeting → `tasks.json` → **G5** → `append_tasks.py` → `tracker/actions.csv`

**Output**
- `deck.pptx` in the corporate template, with speaker notes
- `proposal.md`, `critique.md` (8–12 hostile questions, 3 marked dangerous)
- `team-brief.md`, tasks appended to the tracker

---

### F2 — Deck from known content (`kind = deck`)

**Use it when** the message is already decided — no options to compare — and you need corporate slides plus something to say.

**Example.** You must present the Q3 status of the AI adoption programme to the management team (15 minutes). You have a Word report and a messy 25-slide draft from a colleague.

**Input** — your notes, documents, and/or a draft `.pptx` in `inputs/`; `audience.md`.

**Steps**
1. `new_engagement.py` → kind `deck`
2. `/content` → `content.md` (key messages K, facts F, cited) → **G1**
3. `/storylines` → two tellings (with a draft deck: "evolve the draft" vs "re-sequence") → **G3**
4. `/deck-outline` → `build_deck.py` → **G4** (complete slides from the draft are cloned, not retyped)
5. *(optional)* `/speech`, `@critic /critique`

**Output** — `deck.pptx` in the corporate template, `speech.md` and notes embedded if you ran step 5.

---

### F3 — Meeting record, local (`kind = meeting`)

**Use it when** a meeting happened, you owe nobody a deck, but you want a clean write-up and your actions in the tracker before you forget.

**Example.** A 40-minute architecture sync where you agreed to "check licence cost for the Copilot Studio pilot" and two colleagues took other actions.

**Input** — `inputs/transcript.md` + `inputs/notes.md`.

**Steps**
1. `new_engagement.py` → kind `meeting`
2. `/meeting-notes` → `notes.md` + `tasks.json`
3. Review `tasks.json` → `append_tasks.py` → **G5**
4. *(if "Follow-up needed: Y")* `followup_agenda.py` → agenda + `.ics`

**Output** — one-page `notes.md` cited to the transcript; your actions (and others' as candidates) in `tracker/actions.csv`; optionally a follow-up invite.

> ⚠ Overlaps with F5's *Summarise* (Meeting Summariser). Same need, two routes. See Part 3.

---

### F4 — Morning brief (M365)

**Use it when** you want to start the day knowing what is on, what clashes, what is waiting on you — without opening five apps.

**Example.** Tuesday 07:00: the brief says you have 6 meetings, two clash at 14:00 (suggests moving the vendor call), Anna is blocked on your review since Friday, and the 11:00 steering meeting has no agenda.

**Input** — nothing at run time. Setup: one scheduled prompt in Copilot Chat (weekdays 07:00; optional Monday variant).

**Output** — in Copilot Chat → Chats: `Top 3`, `Today` (timeline, clashes, focus slots), `Waiting on me`, `Waiting on others`, `Prepare`, `Everything else`. ≤ 350 words.

---

### F5 — Meeting lifecycle in M365

**Use it when** you want every meeting filed, summarised and prepared for next time without a local machine.

**Example.** The weekly "Data Platform sync" ends at 10:30. At 10:35 Teams pings you with a link to a new folder `Meetings/2026-09-23 Data Platform sync/`. You drop your notes in, click *Summarise*, add your two actions to To Do. The evening before next week's sync, the 18:00 prep lists what's still open and proposes the agenda.

**Input** — a Teams meeting with transcription on; your notes/attachments dropped into the folder.

**Steps**
1. Automatic — **Harbour Office** flow: transcript lands → SharePoint folder (or `1-1/<person>/<date>`) + OneNote page + Teams ping
2. Manual — drop notes/attachments into the folder
3. One click — **Meeting Summariser → Summarise** → takeaways, decisions, my actions, others' actions, follow-up Y/N
4. Manual — add accepted actions to To Do
5. Automatic — **Evening prep** at 18:00 for tomorrow's meetings: last time, where we left it, open actions, proposed agenda
6. On demand — **Meeting Summariser → Open actions** (last 14 days)

**Output** — a filed folder per meeting, a cited summary in chat, actions you copy into To Do, a daily prep for tomorrow.

---

### F6 — 1-1 preparation (M365)

**Use it when** you have recurring 1-1s and want each one to have an agenda built from what's still open.

**Example.** Wednesday 16:00: Teams pings "Agenda for tomorrow's 1-1 Maria is empty". You click *Prep 1-1* → last three 1-1s, open actions on both sides, 4 proposed items → paste under `Agenda` in the invite.

**Input** — 1-1s named `1-1 <name>`; past 1-1 material in `Meetings/1-1/<person>/` (via F5).

**Steps** — Clock Tower flow pings (automatic) → Meeting Summariser *Prep 1-1* (one click) → paste agenda into invite (manual).

**Output** — an agenda in tomorrow's invite; no 1-1 goes in unprepared.

---

### F7 — Email drafting (M365)

**Use it when** you know what you want to say but not how to phrase it for this recipient.

**Example.** "Draft an email to Thomas: can't do Thursday, need the cost numbers first, propose next Tuesday, keep it friendly he's senior." → subject + body in your voice, and one line saying what was softened.

**Input** — rough text + recipient (optionally "reply to the last email from X"); once: `voice-profile.docx` + 15–20 sent mails.

**Output** — `Subject`, `To`, ready-to-send body; unresolved ambiguities marked `[?]`. Then *Shorter* / *Softer / firmer*.

*(Strictly a single-agent use case; kept in the flow list because a newcomer looks for it as a task.)*

---

### F8 — AI idea → fit check → proposal

**Use it when** a demo, newsletter or vendor pitch makes someone think "what would that be for my team?".

**Example.** A colleague in HR saw a demo of an agent that answers policy questions from a handbook. They tell Fit Finder: "HR team of 6, we answer ~200 policy questions a month, one person knows Power Platform, data must stay in the tenant."

**Input** — the idea, what the team does and for whom, what the team can build, known hard limits (the agent asks for what's missing).

**Setup (once, by whoever runs SemiAgency for the team)** — write the context file (`brand/fit-finder-context.md`, and the same text as `fit-finder-context.docx` on SharePoint): the tools it may recommend, data rules, past ideas. The agent does not create it. Then build the agent from `m365/07-fit-finder-agent.md` and share it.

**Steps** — Fit Finder conversation (Embassy): the shared M365 agent, or `/fit-finder` in VS Code with the same instructions → brief → if "continue": you start an F1 engagement (Town Hall) with the brief as an input.

**Output** — a ≤ 450-word brief: what it is here, new value vs saved effort (blunt if efficiency-only), build-with inside the tenant, a two-day test with stop/continue criteria, next step.

> The handoff crosses environments: the colleague has M365, and F1 runs in *your* VS Code. So the brief's **Next step** names a real person and says in plain words what happens next: an hour's conversation, then a short proposal with options and a recommendation. It never says "discovery session" or "engagement". The name and timing come from the context file.

---

### F9 — Model benchmark (`bench/`)

**Use it when** you wonder whether the expensive model is worth it, or which model is best at *your* kind of task.

**Example.** Last month Copilot twice produced a proposal outline that ignored the audience file. You file that and 6 other failures as cases, run them on 4 models × 3 repeats, and see that model B passes 11/14 checks vs model A's 6/14.

**Input** — 5–10 tasks where AI recently failed you, with context files; the model ids in the picker.

**Steps** — `/bench-setup` (interview → cases) → `/bench-run` per model or `bench_cli.py` → `/bench-feedback` (your reactions → pass/fail checks) → `/bench-judge` (one fixed judge model) → `bench_report.py` → `index.html`.

**Output** — `index.html` matrix of case × model pass/fail + side-by-side outputs.

---

### F10 — Setup & maintenance

**Use it when** you (or a colleague) are setting SemiAgency up, or you've added a feature.

| sub-flow | input | output |
|---|---|---|
| Local setup (Workshop) | VS Code, Python 3, 2–3 past decks, the corporate template | built scripts passing `selftest_all.py`, `brand/components.md`, `brand/voice.md`, `tracker/actions.csv` |
| M365 setup | tenant with Copilot Chat scheduling, Power Automate standard connectors, Agent Builder | built sheets 1–7 in the order 1 → 2 → 3 → 4 → 5 → 6 (7 is independent) |
| Map maintenance (Cartographer) | a new prompt / agent / sheet | rebuilt `index.html`; `--check` fails on anything unplaced |

---

## Part 2 — Individual use cases, per agent / prompt / automation

### Local — Discovery2Presentation (VS Code, Copilot agent mode)

Every prompt below runs as the **@analyst** agent (writes one artifact, validates it, stops at a gate) unless noted.

| Prompt | Kind | Use case | Input | Output |
|---|---|---|---|---|
| `/discovery-prep` | proposal (deck) | Prepare for a discovery meeting | whatever is in `inputs/` (email, org chart, prior docs) or open Qs from an existing `discovery.md` | `brief.md`: context, 3–5 hypotheses, 12–20 questions, who should be in the room |
| `/discovery-synthesize` | proposal | Turn a discovery meeting into a fact base | transcript, notes, docs, `audience.md` | `discovery.md`: needs (N), open questions (Q, blocking flagged), Unverified; 3 items to check |
| `/content` | deck | Extract key messages and facts from existing material | notes, docs, draft `.pptx` | `content.md`: K + F ids, cited |
| `/merge-followup file=…` | any | Fold a follow-up meeting or new document into the fact base | one new file in `inputs/` | updated `discovery.md` / `content.md`, resolved Qs; says if another follow-up is needed |
| `/options` | proposal | Sketch genuinely different solution approaches | `discovery.md` (G1 passed, no blocking Q) | `options.md`: 2–3 options, one deliberately small, honest value line; no recommendation |
| `/proposal` | proposal | Write the proposal and two ways to tell it | chosen option, `discovery.md`, `voice.md`, brand examples | `proposal.md` + `storylines.md` with a 3-line recommendation |
| `/storylines` | deck | Two storylines for a non-proposal deck | `content.md`, brand components | `storylines.md` (evolve vs re-sequence if a draft exists) |
| `/deck-outline` | proposal, deck | Storyline → slide spec | chosen storyline, content source, `components.md` | `deck.json` + `storyboard.html` |
| `/speech` | proposal, deck | Timed speaker notes with emphasis | `deck.json`, content source, `voice.md`, `audience.md` | `speech.md`, fits the slot |
| `@critic /critique` | proposal, deck | Hostile review before anyone else sees it (**@critic**, read-only) | fact base + whatever exists of proposal / deck / speech | `critique.md`: unsupported claims, gaps, weakest points, inflated value claims, 8–12 audience questions |
| `/team-brief` | proposal | Brief your team after the stakeholder presentation | `proposal.md`, `discovery.md` | `team-brief.md`: one page + 30-min agenda |
| `/team-tasks file=… owner=all\|me` | proposal | Team meeting → tasks for review | team meeting notes/transcript | `tasks.json` (tasks vs candidates) |
| `/meeting-notes` | meeting | One-page record + my actions | transcript, notes | `notes.md` + `tasks.json` |

Scripts you touch directly (the terminal half):

| Script | Use case |
|---|---|
| `new_engagement.py` | Start: asks kind / subject / audience, opens `inputs/`, prints the next prompt (`--use`, `--check`) |
| `status.py` | Where am I, what's the checklist, what's next; `--pass` records a gate (asks option / storyline) |
| `followup_agenda.py` | Agenda + `.ics` for a follow-up from open questions |
| `build_deck.py` | Render + lint `deck.pptx`; `--notes-only` embeds speaker notes after the timing check |
| `append_tasks.py` | Show reviewed tasks, append to `tracker/actions.csv`, pass G5 |

### Local — bench (separate workspace)

| Prompt / agent | Use case | Input | Output |
|---|---|---|---|
| `/bench-setup` | Interview me for tasks where AI failed me | a conversation | `cases/<case>/task/…` |
| `/bench-run case= model=` | Run one case on the selected model | case + exact model id | `runs/<case>/<model>__<date>__r<n>.md` |
| `/bench-feedback case=` | Turn my reactions to two outputs into checks | runs side by side + your reactions | `grading/checks.md` (3–10 pass/fail) |
| `/bench-judge judge_model=` (**@judge**) | Grade all ungraded runs with one fixed judge | runs + checks | `results/…json` |
| `bench_cli.py`, `bench_report.py` | Batch runs via Copilot CLI; build the matrix | models list | `index.html` |

### M365 — scheduled prompts, flows, agents

| Piece | Type | Use case | Input | Output |
|---|---|---|---|---|
| Daily brief (Radio Tower) | scheduled prompt, 07:00 | What matters today | calendar, inbox since 17:00, To Do | brief in Chats |
| Meeting filing (Harbour Office) | Power Automate | File every transcript | transcript file created in OneDrive | SharePoint folder, OneNote page, Teams ping |
| Evening prep (Lighthouse) | scheduled prompt, 18:00 | Prepare tomorrow's meetings | tomorrow's calendar + Meetings library (+ OneNote) | per meeting: last time, open actions, proposed agenda; list for To Do |
| Meeting Summariser (Library) → *Summarise* | Agent Builder | Summary of one meeting | folder name | takeaways, decisions, my / others' actions, follow-up, open points |
| → *Summarise today* | | All of today's meetings | — | one summary per folder dated today |
| → *Prep* | | Prepare for next occurrence | meeting subject | last time(s), where we left it, open actions, agenda |
| → *Prep 1-1* | | Prepare a 1-1 | person's name | same, from `1-1/<person>/` only, personal topics masked |
| → *Open actions* | | What do I still owe | window (default 14 days) | table of my open actions across meetings |
| Email Drafter (Post Office) → *Draft* / *Draft reply* | Agent Builder | Rough text → email in my voice | rough text + recipient | subject + body + change note |
| → *Shorter* / *Softer / firmer* | | Adjust the last draft | — | revised draft |
| 1-1 agenda check (Clock Tower) | Power Automate, 16:00 | Catch unprepared 1-1s | tomorrow's `1-1 …` invites | Teams ping if agenda empty |
| Fit Finder (Embassy) → *I saw this* | shared Agent Builder | Translate an idea to my team | idea + team + skills + limits | one-page brief |
| `/fit-finder` (Embassy, VS Code) | prompt, runs the same instructions locally | Same as the shared agent, without building it | idea + team (+ `brand/fit-finder-context.md`) | one-page brief in chat |
| → *Is it worth it?* | | Blunt value judgement | idea | new value vs efficiency verdict |
| → *Just the test* | | Smallest experiment | idea + team | two-day test, stop/continue criteria |
| → *Compare two* | | Pick between ideas | idea A, idea B, team | which fits better and why |

Count: **10 flows**, built from **13 D2P prompts + 2 agents, 4 bench prompts + 1 agent, 7 M365 pieces with 13 starter prompts**, plus 5 terminal scripts that drive D2P.

---

## Part 3 — Brainstorm: making the map work for someone who knows nothing

### What the map does today

A painted city; 16 buildings in 4 districts; an audience filter (Everything / VS Code / M365) that dims buildings; 7 "I want to…" journeys that number stops and open a side guide; a modal per building with copy buttons and the full prompt; deep links via `#id`.

### Honest diagnosis

1. **The metaphor is a second vocabulary.** "Archive", "Notary", "Design Studio", "Radio Tower" mean nothing until you've clicked them. A newcomer has to learn the city *and* the system. The city is a good hook for sharing and a poor lookup tool. Keep it, but it should never be the thing you must decode to find your answer.
2. **The first real decision is hidden.** Whether you have VS Code + Copilot or only M365 decides which half of the system exists for you. Today that's a small filter chip that *dims* buildings. It should be the first question.
3. **Buildings are organised by pipeline stage, but people arrive with a situation.** The Archive holds 4 prompts that belong to 3 different flows. Following the "deck" journey, you open the Archive and see `/discovery-synthesize` first — the wrong prompt for you.
4. **The M365 journey is a build order, not a usage journey.** "Radio Tower → Harbour Office → Lighthouse → …" tells you what to set up, not what to do after a meeting on Tuesday. A newcomer mixes up "set it up once" with "use it daily".
5. **Two routes for the same need, with no guidance on which.** Meeting record: Notary (F3, local) vs Library → *Summarise* (F5, M365). 1-1 prep: Lighthouse vs Library → *Prep 1-1*. Nothing on the map tells you which to pick.
6. **Cost of entry is invisible.** F1–F3 need ~2 hours of setup on a corporate machine; F4 needs 10 minutes. A newcomer can walk the whole proposal journey before discovering it doesn't work on their machine yet.
7. **No "what will I get" preview.** Pitches describe; they don't show. A real example of the output (a brief, a critique, a Fit Finder page) sells and explains faster than any sentence.
8. **The owner's voice leaks.** "you open the real deck before anyone else does", gate jargon (G1–G5), "kind" — clear to you, opaque to a colleague.

### Ideas, from highest value to lowest

**A. A "What do you need?" front door (task-first layer over the city)** — *strongest idea*
A 2–3 question picker before or beside the map:
1. *Where do you work?* VS Code + Copilot / only Outlook & Teams / both
2. *What do you have in hand?* a meeting just happened / material for a presentation / an AI idea / nothing, I want my day organised / an email to write / tasks where AI failed me
3. *(if needed)* *What do you owe?* a proposal with options / a deck / just a record

→ lands on exactly one flow, highlighted on the map, with its first step's copy button. Every answer maps directly to a flow in Part 1, so this is a small table in `city.json`, not new logic.

**B. Input → output cards for every flow.** Each flow gets a card: *when* (one sentence), *you bring*, *you get*, *time*, *setup needed?*, and a real, redacted **example output** thumbnail. Part 1 above is the content. This is also the list view (see D).

**C. Journey-aware building modals.** When a journey is active, the modal shows only the steps for that flow (Archive in the deck journey shows `/content`, not `/discovery-synthesize`) and a "Step 2 of 4" header with Next. Everything else collapses under "Other things this building does". Tag each `steps[]` entry in `city.json` with the journeys it belongs to.

**D. A list view toggle ("Map | List").** Same data, scannable: flows first, then a use-case catalogue grouped by environment (Part 2). The city stays the default for sharing; the list is where people go the second time. Add a search box with synonyms ("summarise meeting", "slides", "email", "1-1", "which model").

**E. Plain-language subtitles on every building.** "The Archive — *get the facts from your meeting*", "The Notary — *meeting notes + my actions*", "Post Office — *write an email in my voice*". The name stays for charm, the subtitle does the work. Same for gates: "G1 · check the facts".

**F. Split setup from use.** Two badges per building: **Ready to use** vs **Set up first (~N min)**. Split the M365 journey into "Set up M365 once" (build order) and three usage journeys: "After a meeting (M365)", "Before a 1-1", "Write an email". Move Workshop + Cartographer + M365 setup into a visually separate "Construction yard".

**G. Resolve the overlaps explicitly.** A "which one?" note on both Notary and Library: *"Use the Notary if you have VS Code and want tasks in the tracker. Use the Library if you live in Teams."* Same for Lighthouse vs Prep.

**H. Show the gates as a visible line under the journey.** A progress strip (Facts → Option → Storyline → Deck → Tasks) under the guide panel, with the current stop highlighted. Explains the D2P model without a paragraph of text.

**I. Audience-specific shareable links.** `index.html#for=m365` opens with the M365 answer preselected and the VS Code half hidden (not dimmed). You send colleagues the link that fits them; the Fit Finder post in the team channel links to `#embassy`.

**J. Small polish.** Keyboard navigation between buildings; "copy link to this journey"; a 20-second first-visit coach mark ("Start with *What do you need?*, or click any building"); make the guide panel usable on phones (colleagues will open a shared link on mobile).

### What I would not do

- **Don't redesign the city itself.** The problem is the entry path and the modal content, not the illustration. A new scene costs a re-trace and adds nothing a newcomer needs.
- **Don't add more journeys before the front door exists.** Seven chips in a row is already the limit of what people read; ten will be ignored. The picker (A) scales, the chip bar doesn't.
- **Don't make the static page stateful** (progress tracking, "where am I in my engagement"). `status.py` owns that; duplicating it in a shared HTML page creates two truths.

### Suggested order

1. E (subtitles) + G (overlap notes) — content-only edits in `city.json`, an hour.
2. B + D (flow cards and list view) — uses Part 1/2 of this doc as data.
3. C (journey-aware modals) — needs a `journeys` tag per step.
4. A (front door) — once flows and cards exist, the picker is just routing.
5. F, H, I, J as polish.
