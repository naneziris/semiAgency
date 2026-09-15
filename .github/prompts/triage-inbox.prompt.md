---
mode: agent
description: Turn the day's email export into reviewed todos (urgency/effort/delegate) and reply drafts — workflow #2
---
Date: `${input:date}` (YYYY-MM-DD; default today). Use `@librarian`.
1. Read `kb/email/${input:date}.md`. If it does not exist, stop: tell the user to run the Daily Exporter in M365 Copilot Chat, paste the result into `kb/inbox/`, and run `python scripts/kb_ingest.py`.
2. Read `kb/index.md` (tracker summary) and, for context on names and running threads, the latest `kb/triage/*.md`, `kb/people/*/profile.md`, and `engagements/*/state.json` subjects. Read `brand/voice.md` for the reply drafts.
3. For every `E<n>`: decide none / do / delegate / later. Classify urgency and effort per `.github/copilot-instructions.md`. Delegate when someone else owns the topic or is named in the thread as responsible; write the one-line ask. Only explicit asks or commitments become tasks; implied ones are candidates.
4. Write `kb/triage/${input:date}.md` per `.github/instructions/triage.instructions.md` and `kb/triage/${input:date}.todos.json` per `.github/instructions/todos.instructions.md` (same items, same order; `context` = the date).
5. Stop. Tell the user: how many do/delegate/later, the 3 emails you were least sure about, and that after editing the JSON they run `python scripts/append_tasks.py kb/triage/${input:date}.todos.json` (gate T1).
