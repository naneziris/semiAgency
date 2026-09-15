# Handoff format — the contract between the M365 side and the local knowledge base

A *handoff* is a markdown file produced by an agent in Microsoft 365 Copilot Chat (Agent Builder), copied by you into `kb/inbox/`, and routed into the knowledge base by `python scripts/kb_ingest.py`. The Agent Builder prompts in `agent-builder/` are written to emit exactly this shape; `kb_ingest.py` is written to tolerate the ways copy-paste from Copilot Chat mangles it.

## 1. Header

The first lines of every handoff are a header block:

```
---
handoff: daily-export
date: 2026-09-15
source: agent-builder/daily-exporter
---
```

Keys:

| key | required | values |
|---|---|---|
| `handoff` | yes | `daily-export`, `calendar`, `email`, `topic-links`, `one-on-one`, `meeting`, `note` |
| `date` | yes | `YYYY-MM-DD` — the day the content is *about* (for a morning export: today) |
| `source` | no | free text, which agent produced it |
| `topic` | for `topic-links` | topic slug, e.g. `ai` |
| `person` | for `one-on-one` | the colleague's name as you use it, e.g. `Maria K` |
| `subject` | for `meeting`, `note` | short title, used in the file name |

Tolerance: if the `---` fences got lost in copy-paste, `kb_ingest.py` still looks for `handoff:` and `date:` in the first 15 lines. If the header is missing entirely, it falls back to the file name (`2026-09-15-daily-export.md`, `2026-09-15-one-on-one-maria-k.md`). If it still can't tell, it leaves the file in `kb/inbox/` and says why.

## 2. `daily-export` — one file, three sections

Produced once per morning by the **Daily Exporter** agent (`agent-builder/daily-exporter.md`). `kb_ingest.py` splits it into three files (`kb/calendar/<date>.md`, `kb/email/<date>.md`, `kb/topics/<topic>/links/<date>.md`) so each downstream prompt reads only what it needs. The section headings are H2 and must be spelled exactly:

### `## Calendar`

One H3 per day (`### 2026-09-15`, `### 2026-09-16`), each with a table:

```
| start | end | title | with | kind | link | notes |
|---|---|---|---|---|---|---|
| 09:00 | 09:30 | Weekly 1-1 Maria K | Maria K | 1-1 | https://teams.microsoft.com/... | recurring |
| 09:30 | 10:30 | Platform sync | Jan D, Ali R (+4) | meeting | ... | I am organizer |
| 13:00 | 14:00 | Focus: proposal draft | — | focus | | |
| all-day | all-day | Public holiday (ZH) | — | all-day | | |
```

- `start`/`end` are `HH:MM` in your local time, or `all-day`.
- `kind` ∈ `1-1` | `meeting` | `focus` | `all-day` | `tentative`. `1-1` is used for any recurring meeting with exactly one other attendee — that is what `brief_collect.py` uses to find whose 1-1 history to surface.
- `with` lists attendees by the names you use; more than five → first three `(+N)`.
- `notes`: anything the agent noticed — you are organizer, no agenda in the body, declined by the other side, overlaps another event.

### `## Emails`

One H3 per email that needs a decision from you, most recent first, capped at 40. FYI-only mails are summarised in one line each under `#### FYI` at the end. Every email gets a stable id `E<n>` for the day so the local triage can cite it.

```
### E1 — Re: vendor contract renewal
- from: Sabine L (Procurement)
- received: 2026-09-15 07:12
- to-me: direct        (direct | cc | list)
- thread: 4 messages, last from Sabine
- gist: Procurement needs our sign-off on the renewed terms; the price rose 8%; legal already approved.
- asks: Confirm by Thu 18 Sep whether to proceed.
- deadline: 2026-09-18
- links: https://... (contract PDF on SharePoint)
- attachments: renewal-terms.pdf
```

Rules for the agent: never paste full bodies; `gist` is at most three sentences; `asks` is only what is explicitly requested of *you*; `deadline` is only a date actually stated in the mail (else `none`). Newsletters and notifications go to FYI; automated system mails are dropped.

### `## Topic links: <topic>`

Every hyperlink found in the day's emails that is about the topic, deduplicated by URL:

```
| url | title | from | one-line |
|---|---|---|---|
| https://example.org/post | Example post | newsletter@x (AI weekly) | Agent eval harness released |
```

The heading carries the topic slug (`## Topic links: ai`). A daily export may have several such sections, one per topic you track. The agent does not judge importance — that is the local `/triage-topic` prompt's job, against your interest profile.

## 3. `one-on-one`

Produced on demand by the **1-1 Prep** agent (`agent-builder/one-on-one-prep.md`). It already *is* the preparation summary — you can use it straight from Copilot Chat. Paste it into `kb/inbox/` only when you want the history kept locally (recommended: it is what lets the morning brief show "1-1 with Maria today — open follow-ups: 2").

```
---
handoff: one-on-one
date: 2026-09-15
person: Maria K
source: agent-builder/one-on-one-prep
---
## Meetings covered
- 2026-09-01 — regular 1-1
- 2026-08-18 — regular 1-1
- 2026-08-04 — career conversation

## Recurring threads
...

## Open follow-ups (to raise next time)
| raised on | follow-up | status |
|---|---|---|

## My open actions
| raised on | action | due | status |
|---|---|---|---|

## Suggested agenda for the next 1-1
1. ...
```

Routed to `kb/people/<slug>/<date>.md` where slug is the person's name lower-cased with hyphens (`maria-k`).

## 4. `calendar`, `email`, `topic-links`

The three sections of a daily export, as standalone files, for the case where you ran only part of the export (e.g. "calendar only, for tomorrow"). Same section body as above; the header carries `handoff: calendar` etc. and, for `topic-links`, `topic:`.

## 5. `meeting` and `note`

Escape hatches. `meeting` (with `subject`) is a transcript or write-up you obtained M365-side and want to feed into a D2P `meeting`-kind engagement: `kb_ingest.py` puts it in `kb/meetings/<date>-<subject-slug>.md` and tells you the `new_engagement.py` command to move it into `engagements/`. `note` is anything else worth keeping; it lands in `kb/notes/<date>-<subject-slug>.md`.

## 6. What `kb_ingest.py` guarantees

- Never edits the content of a handoff; it only splits by H2 and adds a header to each part.
- Keeps the raw file in `kb/archive/<date>-<type>.md` (so a bad split can be redone).
- Refuses to overwrite an existing target; a second export for the same day lands as `<date>.2.md` and the script says so — decide which one you want and delete the other.
- Regenerates `kb/index.md` at the end (same as `python scripts/kb_index.py`).
