# Knowledge base (workflow #8)

The local memory the local workflows read from and write to. Plain markdown and JSON, dated file names. GitHub Copilot reads it through the workspace; scripts keep it tidy.

What is **not** here, by design: anything about your emails, calendar, To Do or 1-1 notes. Those workflows run inside Microsoft 365 (`agent-builder/`). The only M365-derived content here is the sanitized topic link list (URLs and titles).

```
kb/
├── inbox/            drop handoffs here (docs/handoff-format.md) → python scripts/kb_ingest.py
├── archive/          raw handoffs after ingest, never edited
├── topics/<topic>/   profile.md         your interest profile for the topic (/interview-topic, /refine-topic)
│                     links/<date>.md    links about the topic seen that day — url, title, one-line only
│                     links.md           GENERATED — all links ever, one table, newest first (kb_index.py)
│                     digests/<date>.md  the day's flagged items + the rest (/triage-topic)
├── meetings/         transcripts handed off from Copilot Chat, waiting to become an engagement
├── notes/            anything else worth keeping
└── index.md          GENERATED — what's in here, newest first
```

Conventions:

- Dates are `YYYY-MM-DD` in file names and `date:` headers.
- Topic slugs are short and lower-case (`ai`, `platform-security`).
- Generated files say so in their first line and are safe to delete — `python scripts/kb_index.py` rebuilds them.
- Copilot may write under `topics/*/profile.md` and `topics/*/digests/`. It never writes under `archive/`, `topics/*/links/`, `meetings/` — those are evidence, like `engagements/*/inputs/`.
- Actions from meetings go through an engagement's `tasks.json` and `append_tasks.py` into `tracker/actions.xlsx`. Actions from email live in Microsoft To Do and never come here.
