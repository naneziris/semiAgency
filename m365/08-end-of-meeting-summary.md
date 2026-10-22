# 8 · End-of-meeting summary — a prompt you paste (feeds the Topic record)

Nothing to build. At the end of a meeting (or right after it), paste the prompt below into **Copilot in the Teams meeting** (the Copilot button in the meeting window, or the meeting's *Recap* tab afterwards) — it already knows the meeting. From Microsoft 365 Copilot Chat instead, add one line at the top: `Meeting: "<title>" on <date>.`

The answer is written to be saved as a file in the topic's folder in VS Code, where the **Topic record** (`/meeting-notes`) merges it with the transcript, your notes and every earlier meeting on the topic.

Needs transcription (or Copilot "during the meeting only") turned on for the meeting. Copy from the line below to the end of the block, as one message.

```
Summarise this meeting for my records. Use only the transcript and the chat of this meeting. Never invent: if something is unclear, write [unclear]. Give a timestamp [hh:mm:ss] for every bullet, taken from the transcript. Output Markdown only, no text before or after, exactly in this shape:

# <yyyy-mm-dd> — <meeting title>
Participants: <names>

## Key points
- max 7 bullets [hh:mm:ss]

## Decisions
- <decision> [hh:mm:ss]   (write "none" if there were none)

## My actions
| action | due | timestamp |
Only what I explicitly committed to or was explicitly assigned. Nothing implied.

## Others' actions
| owner | action | due | timestamp |

## Open points
- raised and not settled [hh:mm:ss]

## Follow-up needed
Y or N, and if Y: 3–5 agenda bullets.
```

## Then

1. Copy the answer. In VS Code, save it as `engagements/<topic>/inputs/<yyyy-mm-dd>-summary.md` (the date of the meeting).
2. Also save the transcript there if you can: Teams → the meeting → *Recap* → *Transcript* → *Download* (.docx) → `inputs/<yyyy-mm-dd>-transcript.docx`. The summary alone works, but then every fact in the record is marked *(summary only)* — the transcript is what the record is checked against.
3. Your own notes from the meeting, if any: `inputs/<yyyy-mm-dd>-notes.md`. They count more than anything else.
4. Copilot Chat (agent mode) in VS Code: `/meeting-notes` — see the *Topic record* in `HOW-TO-USE.md`.

## Check the first three runs

- Every bullet has a timestamp. If Copilot drops them, add "A bullet without a timestamp is an error." after the never-invent sentence.
- *My actions* holds only explicit commitments. If it infers, add "If in doubt, put it under Others' actions with owner 'unclear'."
