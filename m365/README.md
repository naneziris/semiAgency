# M365 automations — build sheets

Three cases, entirely inside Microsoft 365, with no premium Power Automate, no Copilot Studio, and nothing on the local machine. The rule that shapes them: **Power Automate (standard connectors) does the filing; the free unattended model step is a scheduled prompt in Copilot Chat; on-demand thinking is an Agent Builder agent reading SharePoint.** Nothing here writes a summary into OneNote by itself — that needs a model step inside a flow, which is premium. Instead the raw material is filed automatically and the summary is generated the evening before you need it.

| # | sheet | what it is | automatic? | build time |
|---|---|---|---|---|
| 1 | `01-daily-brief.md` | scheduled prompt, 07:00 weekdays | yes — appears in Copilot Chat | 10 min |
| 2 | `02-meeting-filing-flow.md` | Power Automate: transcript lands → folder per meeting in SharePoint + OneNote page + Teams ping | yes | 45 min |
| 3 | `03-evening-prep-prompt.md` | scheduled prompt, 18:00 weekdays: for each meeting tomorrow, summarise the last ones from the library, open actions, proposed agenda | yes | 10 min |
| 4 | `04-meeting-summariser-agent.md` | Agent Builder agent over the Meetings library: same-day summary, 1-1 prep, open actions | on demand (one click) | 10 min |
| 5 | `05-email-drafter-agent.md` | Agent Builder agent with your voice profile + exemplar mails: rough text in, subject + body out | one paste | 20 min + collecting exemplars |
| 6 | `06-agenda-check-flow.md` | Power Automate: the day before a recurring 1-1, ping you if the invite's agenda is empty | yes | 15 min |

Build in this order: 1 (validates scheduled prompts in your tenant) → 2 (validates the trigger on your transcript folder) → 3 → 4 → 5 → 6.

## Prerequisites to check once (5 minutes, before building anything)

- Copilot Chat → is there a **Schedule** option on a prompt (clock icon / "Schedule prompt")? If not, scheduled prompts aren't enabled for you yet; ask the admin. Sheets 1 and 3 depend on it.
- Where do your Teams transcripts land? Open OneDrive and find the last meeting's transcript (typically a *Recordings* folder, or wherever your `.md` transcripts arrive). Note the exact folder path — sheet 2's trigger points at it.
- Power Automate → can you create a cloud flow with the SharePoint, OneDrive, Outlook, OneNote and Teams connectors (all standard)? A DLP policy sometimes blocks OneNote or Teams; you'll see it when adding the action.
- Create the SharePoint document library **Meetings** (on a site you own, or your OneDrive if you prefer — the flows and the agent point at one place). Inside it, one folder `1-1`.
- Agent Builder → create a test agent and check the **Knowledge** step offers *SharePoint*. Sheets 4 and 5 point their knowledge at the library.

## What stays manual, and why

- Adding accepted actions to Microsoft To Do (a flow can't extract them without a model step; the evening prompt lists them).
- Dropping your manual notes and attachments into the meeting's folder after the meeting (one drag; the flow has already created and named it).
- Pasting an email draft into a new mail (no draft-creation action in the standard Outlook connector).
- Pasting an agenda into a 1-1 invite (no calendar-write from Agent Builder).

## If premium ever arrives

Add an AI Builder *Run a prompt* step to flow 2 (summary written into the OneNote page and `summary.md` at filing time, actions into To Do), and a flow for case 5 that reads a "DRAFT:" mail to yourself and creates the draft via Graph. Everything else stays as is.
