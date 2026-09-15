# Handoff format — the contract between the M365 side and the local knowledge base

A *handoff* is a markdown block produced in Microsoft 365 Copilot Chat, copied by you into `kb/inbox/`, and routed into the knowledge base by `python scripts/kb_ingest.py`.

**The boundary.** Information about your emails, calendar, To Do and 1-1 notes stays inside Microsoft 365. Only three handoff types exist, and none of them carries email content:

| type | carries | produced by | lands in |
|---|---|---|---|
| `topic-links` | URLs, titles and a one-line description of links about a topic — no senders, no subject lines, no mail text | Daily Brief agent, **Topic links** starter | `kb/topics/<topic>/links/<date>.md` |
| `meeting` | a meeting transcript / recap (meeting content, not mail) | the Meeting Exporter prompt in Copilot Chat, only when the transcript `.md` was not delivered | `kb/meetings/<date>-<subject>.md` |
| `note` | anything else you decide to keep | you | `kb/notes/<date>-<subject>.md` |

`kb_ingest.py` **refuses** files whose header says `email`, `calendar`, `daily-export` or `one-on-one`, and warns when a topic-links table carries a `from` column. That is deliberate: if the M365 agent drifts and starts adding senders, the local side rejects it rather than storing it.

## Header

```
---
handoff: topic-links
date: 2026-09-15
topic: ai
source: agent-builder/daily-brief
---
```

| key | required | values |
|---|---|---|
| `handoff` | yes | `topic-links`, `meeting`, `note` |
| `date` | yes | `YYYY-MM-DD` — the day the content is about |
| `topic` | for `topic-links` when the body has no `## Topic links: <topic>` heading | topic slug, e.g. `ai` |
| `subject` | for `meeting`, `note` | short title, used in the file name |
| `source` | no | free text |

Tolerance: if the `---` fences are lost in copy-paste, the script still looks for `handoff:` and `date:` in the first 15 lines; failing that, it reads the file name (`2026-09-15-topic-links-ai.md`, `2026-09-12-meeting-vendor-sync.md`). Otherwise the file stays in `kb/inbox/` and the script says why.

## `topic-links` body

```
## Topic links: ai
| url | title | one-line |
|---|---|---|
| https://example.org/post | Example post | Agent eval harness released |
```

Exactly three columns. One H2 per topic; a single paste may carry several topics (`## Topic links: ai`, `## Topic links: platform`) and is split into one file per topic. The agent does not judge importance — that is `/triage-topic`'s job, against your interest profile.

## `meeting` body

```
## Participants
- name (role)
## Transcript
[00:00:12] Speaker: text
...
## Recap
```

After ingest the script prints the `new_engagement.py --kind meeting` command; copy the file into that engagement's `inputs/transcript.md` and continue as in `docs/d2p/scenarios.md` Scenario C.

## What `kb_ingest.py` guarantees

- Never edits content; it prepends a header and, for multi-topic pastes, splits by H2.
- Keeps the raw paste in `kb/archive/<date>-<type>.md`.
- Never overwrites: a second paste for the same day lands as `<date>.2.md` and the script says so — pick one and delete the other.
- Rebuilds `kb/index.md` at the end (same as `python scripts/kb_index.py`).
