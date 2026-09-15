# Power Automate flow: 1-1 agenda check, the day before

Workflow **#4**, the two requirements that need something to run *by itself*: "agenda adjusted a day before, editable by both" and "if the agenda is empty, tell me to cancel". Agent Builder cannot run unattended, and Power Automate's Copilot Studio action does not reach Agent Builder agents — but the check itself needs no AI at all. A scheduled Power Automate cloud flow with the standard Office 365 Outlook connector (included in your M365 licence, no premium connector) does it.

## What it does

Every working day at 16:00, for each recurring 1-1 that occurs tomorrow: read the meeting body; if the `Agenda` section is empty, send you a Teams chat message (or email) "Agenda for tomorrow's 1-1 with <name> is empty — run 1-1 Prep and paste an agenda, or cancel." If it is not empty, do nothing.

## Where the agenda lives

Pick one and stick to it, because the flow reads only one place:

- **Meeting body (recommended for the flow).** The invite body has a heading line `Agenda` and the items below it. Both attendees can edit the body of a meeting they organise; the attendee can't edit the organiser's invite — so this is only "editable by both" if you are fine being the one who pastes what they send you. Simplest, and it is what the flow below reads.
- **Collaborative notes (Loop).** Truly co-editable, but the content is a Loop component and not readable through the Outlook connector's event body. If you choose this, the flow degrades to "remind me to check the notes" — still useful, no emptiness detection.

## Build it (Power Automate → Create → Scheduled cloud flow, ~15 minutes)

1. **Trigger — Recurrence:** every 1 day, at 16:00, time zone W. Europe Standard Time, on Monday–Friday (Advanced options → "On these days").
2. **Get calendar view of events (V3)** (Office 365 Outlook): Calendar = Calendar; Start = `formatDateTime(addDays(utcNow(), 1), 'yyyy-MM-dd')`; End = `formatDateTime(addDays(utcNow(), 2), 'yyyy-MM-dd')`. Advanced: Order by `start/dateTime`. On a Friday change the offsets to 3 / 4 with a Condition on `dayOfWeek(utcNow())` — or accept that Friday runs check Saturday (empty) and add a second flow for Monday; the second flow is simpler.
3. **Filter array** on the events: `Is recurring` equals `true` **and** the attendee count is 1 other than you. There is no "attendee count" field; use `length(split(item()?['requiredAttendees'], ';'))` equals `2` (you and one other; the string is semicolon-separated and ends with one). Alternatively name your 1-1s consistently ("1-1 <name>") and filter on `contains(item()?['subject'], '1-1')` — the naming rule is more robust than the attendee count and costs nothing.
4. **Apply to each** filtered event:
   - **Compose — agenda text:** `trim(last(split(item()?['body'], 'Agenda')))` — everything after the word Agenda in the (HTML) body. Then a second Compose stripping tags: `replace(replace(replace(outputs('agenda_text'), '<br>', ''), '<p>', ''), '</p>', '')` — extend for `&nbsp;` and `<div>`. Good enough: you are only testing for "is there anything at all".
   - **Condition:** `length(trim(outputs('agenda_stripped')))` is less than `15`  **or**  the body does not contain `Agenda` at all.
     - **If yes → Post message in a chat or channel** (Microsoft Teams connector), post as Flow bot, to you: `Agenda for tomorrow's 1-1 with @{item()?['requiredAttendees']} at @{formatDateTime(item()?['start'], 'HH:mm')} is empty. Cancel it, or run "1-1 Prep" in Copilot and paste an agenda. Open: @{item()?['webLink']}`
     - **If no →** nothing.
5. Save; **Test → Manually** once with a real empty-agenda 1-1 tomorrow.

## What it deliberately does not do

- It does not write the agenda. That would be an autonomous agent step (Copilot Studio, paid). You run 1-1 Prep (one click) and paste (one paste). If you later pay for Copilot Studio, the same flow gets one extra action ("Execute agent → 1-1 Prep → Update event body") and becomes fully automatic.
- It does not cancel the meeting. It tells you; you decide. Cancelling someone's 1-1 automatically is the wrong default for a wellbeing-adjacent meeting.

## Candid note

If the naming rule ("1-1 <name>" in every recurring 1-1 subject) is acceptable to you, the whole flow is trigger → get events → filter on subject → condition on body length → Teams message: five steps, standard connectors, and nothing to maintain. The attendee-count expression is the part most likely to break; avoid it if you can.
