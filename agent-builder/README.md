# M365 side — Agent Builder agents and how they hand off to the local workspace

GitHub Copilot in VS Code cannot see Outlook, Teams, OneNote or the calendar. The agents in this folder run inside **Microsoft 365 Copilot Chat → Agent Builder** (free with the M365 Copilot licence), read what lives there, and print a *handoff* in the fixed shape described in `docs/handoff-format.md`. You copy that handoff into `kb/inbox/` and run `python scripts/kb_ingest.py`. From there everything is local.

Two agents cover all five workflows; a third file is a plain prompt for an occasional need.

| file | agent | used by workflow | how often |
|---|---|---|---|
| `daily-exporter.md` | **Daily Exporter** | #2 email triage, #6 topic links, #7 morning brief (calendar), #3/#4 indirectly (calendar) | once each morning, ~1 minute |
| `one-on-one-prep.md` | **1-1 Prep** | #4 team 1-1s | before a 1-1, on demand |
| `meeting-exporter.md` | *(no agent — a prompt for the standard Copilot Chat)* | #3 meeting notes, when a transcript `.md` was not delivered | occasionally |
| `power-automate-1-1-agenda.md` | *(a Power Automate flow, not an agent)* | #4 — agenda check the day before, cancel suggestion | runs itself daily |

## What Agent Builder can and cannot do — read this once

- **It only runs when you type into it.** No schedule, no trigger, no background run. Every export is you: open the agent, click the starter prompt, copy the answer. Scheduled/unattended runs need Copilot Studio (paid, credit-metered); the handoff format is the same, so if you later pay for it nothing on the local side changes.
- **It answers in chat.** It cannot write a file to OneDrive or the KB. Copy → paste into a new file in `kb/inbox/` (any name; the header inside the text tells `kb_ingest.py` what it is). In VS Code: `Ctrl+N`, paste, `Ctrl+S` into `kb/inbox/`.
- **Instructions are capped (~8,000 characters)** and the model is the one Microsoft provides. The instruction texts below fit and were written for that limit; don't pad them.
- **Knowledge sources.** Mail and calendar come from the Microsoft 365 grounding the agent inherits when you leave "Microsoft 365 Copilot" / work data enabled in the builder; OneNote is reached as files in OneDrive/SharePoint — add the notebook's location as a SharePoint/OneDrive knowledge source on the 1-1 Prep agent. If your tenant's builder does not expose mail or calendar to custom agents, the fallback is one step shorter, not blocked: paste the same instruction block as a message into the ordinary Copilot Chat (**Work** mode), which does have your mail and calendar.
- **Output can be truncated** on a heavy mail day. The Daily Exporter is told to stop at 40 emails and to say `[truncated — ask: continue from E41]`. Reply `continue` and paste both parts into one file, or run the section-only starters ("Calendar only", "Emails only", "Topic links only") and paste each as its own handoff — `kb_ingest.py` accepts both.
- **Copilot Chat's "Copy" button copies markdown.** The tables and the `---` header survive. If you select-and-copy from the rendered view instead, the `---` fences may be lost; the ingest script tolerates that as long as the `handoff:` and `date:` lines are still there.

## Setting up an agent (once, ~5 minutes each)

1. In Microsoft 365 Copilot (app or web) → **Agents** → **Create agent** → switch to the **Configure** tab (skip the Describe chat).
2. Name, Description: copy from the file. **Instructions**: paste the block between the `=== INSTRUCTIONS ===` markers verbatim.
3. Knowledge: as the file says. Capabilities: leave code interpreter/image generator off. Web search off (we only want your data).
4. Starter prompts: add the ones listed in the file — they are what you actually click every day.
5. Create. Test with the first starter prompt; check the output against `docs/handoff-format.md`. If a table column is missing, tell the agent in chat ("the calendar table must have exactly these 7 columns …") — then fix the instruction text if it keeps happening.
6. Sharing: keep it private (your data only).

## The daily routine, end to end (~10 minutes of your time)

```
M365 Copilot Chat → Daily Exporter → "Export today"          (copy)
VS Code           → new file in kb/inbox/ → paste → save
terminal          → python scripts/kb_ingest.py
Copilot Chat      → @librarian /triage-inbox                  → edit kb/triage/<date>.todos.json
terminal          → python scripts/append_tasks.py kb/triage/<date>.todos.json
Copilot Chat      → @librarian /triage-topic topic=ai         → read the digest
Copilot Chat      → @librarian /morning-brief                 → read the brief
```

The brief is last on purpose: it reads the triage and the digest, so run it after them. If you are short on time, run only the export + `/morning-brief`; the brief will list what you skipped.
