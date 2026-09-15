# Prompt: Meeting Exporter (no agent needed)

Workflow **#3 meeting notes** normally needs nothing from the M365 side: Teams transcripts arrive as `.md`, you drop them into `engagements/<meeting>/inputs/` and run `/summarize-meeting`. This prompt is for the exception — a meeting with a Teams recap/transcript that was *not* delivered to you as a file. Paste it into the ordinary Microsoft 365 Copilot Chat (Work mode), which can read meeting transcripts and recaps.

```
Using only the transcript and recap of my meeting "<title>" on <date>, produce a markdown handoff and nothing else:

---
handoff: meeting
date: <YYYY-MM-DD>
subject: <title>
source: copilot-chat/meeting-exporter
---
## Participants
- name (role if known)
## Transcript
Reproduce the transcript as `[hh:mm:ss] Speaker: text` lines, in order, without summarising or omitting turns. If the transcript is longer than you can output, stop at a speaker turn and add `[truncated — ask: continue from hh:mm:ss]`.
## Recap (Teams-generated, verbatim if available)
```

Then: copy → `kb/inbox/` → `python scripts/kb_ingest.py` → it lands in `kb/meetings/<date>-<subject>.md` and the script prints the `new_engagement.py --kind meeting` command; copy the file into that engagement's `inputs/transcript.md` and continue with `/summarize-meeting` as in `docs/d2p/scenarios.md` Scenario C.

Why the transcript and not just the recap: the local write-up cites timestamps (`[T1 00:12:34]`) so you can verify at the gate. A recap alone gives you nothing to check against.
