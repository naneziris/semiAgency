# M365 side — Agent Builder agents

Rule that shapes this folder: **information about your emails, calendar and 1-1 notes stays inside Microsoft 365.** GitHub Copilot in VS Code never sees it. The M365 agents therefore *do* the daily work in chat rather than exporting it; the only thing that crosses to the local workspace is a sanitized list of topic links (URLs and titles), and meeting transcripts you already receive as files.

| file | agent | workflow | how often |
|---|---|---|---|
| `daily-brief.md` | **Daily Brief** | #7 morning brief, #2 email triage, #6 topic links (sanitized handoff) | once each morning, ~2 minutes |
| `one-on-one-prep.md` | **1-1 Prep** | #4 team 1-1s — its own flow, fully in M365 | before a 1-1, on demand |
| `power-automate-1-1-agenda.md` | *(a Power Automate flow, not an agent)* | #4 — agenda check the day before, cancel suggestion | runs itself daily |
| `meeting-exporter.md` | *(no agent — a prompt for the standard Copilot Chat)* | #3 meeting notes, only when a transcript `.md` was not delivered | occasionally |

Two agents. If more than one were needed for a single workflow it would say so here; none is.

## What Agent Builder can and cannot do — read this once

- **It only runs when you type into it.** No schedule, no trigger. The morning brief is you clicking a starter prompt. Scheduled runs need Copilot Studio (paid, credit-metered); nothing here would change except that the brief would arrive instead of being fetched.
- **It cannot write.** It can't create To Do tasks, edit calendar events or save files. Every "keep this action" is you adding it to To Do; every agenda is you pasting it into the invite. The Power Automate flow is the one thing that acts on its own, and it only sends you a message.
- **Instructions are capped (~8,000 characters);** both instruction blocks are well under that.
- **Knowledge sources.** Mail, calendar and (tenant-dependent) To Do come from the Microsoft 365 work-data grounding the agent inherits. OneNote is reached as files in OneDrive/SharePoint — add the notebook's location as a knowledge source on 1-1 Prep. If your tenant's builder does not expose mail/calendar to custom agents, paste the same instruction block as a message into the ordinary Copilot Chat (**Work** mode); same result, no agent.
- **Copilot Chat's "Copy" button copies markdown.** For the topic-links handoff that means the `---` header survives; `kb_ingest.py` tolerates a lost header as long as the `handoff:` and `date:` lines are there.

## Setting up an agent (once, ~5 minutes each)

1. Microsoft 365 Copilot (app or web) → **Agents** → **Create agent** → **Configure** tab.
2. Name, Description: copy from the file. **Instructions**: paste the block between `=== INSTRUCTIONS ===` and `=== END ===` verbatim.
3. Knowledge: as the file says. Capabilities: code interpreter and image generator off. Web search off.
4. Starter prompts: add the ones listed — they are what you click every day.
5. Create. Test with the first starter; compare with the output shape in the file. Correct it in chat once; if it keeps drifting, fix the instruction text.
6. Keep it private.

## The daily routine

```
M365 Copilot Chat → Daily Brief → "Morning brief"      read; add accepted actions to To Do; move clashing meetings
                               → "Topic links"        copy → kb/inbox/ → python scripts/kb_ingest.py
VS Code Copilot Chat → @librarian /triage-topic topic=ai    read the digest; 👍/👎 via /refine-topic
```

Before a 1-1: **1-1 Prep** → read → paste the agenda into the invite. That's the separate flow; it never touches the other two.
