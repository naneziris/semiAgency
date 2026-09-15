# 6 · 1-1 agenda check — Power Automate flow (standard connectors only)

Every working day at 16:00: for each recurring 1-1 tomorrow, read the invite body; if there is no `Agenda` section with content, post you a Teams message "Agenda for tomorrow's 1-1 with <name> is empty — run Meeting Summariser → Prep 1-1 and paste an agenda, or cancel." Nothing else. It doesn't write the agenda (no model step without premium) and it doesn't cancel anything (that's your call for a wellbeing-adjacent meeting).

Prerequisite that makes this trivial: name every recurring 1-1 **"1-1 <name>"**. The attendee-count alternative is the fragile part; avoid it.

## Build (Scheduled cloud flow, ~15 minutes)

1. **Recurrence** — every 1 day at 16:00, time zone W. Europe Standard Time, Monday–Friday. (Friday runs check Saturday and find nothing; add a second flow "Sunday 16:00" checking Monday if you want Monday 1-1s covered.)
2. **Office 365 Outlook: Get calendar view of events (V3)** — Start `formatDateTime(addDays(utcNow(), 1), 'yyyy-MM-dd')`, End `formatDateTime(addDays(utcNow(), 2), 'yyyy-MM-dd')`.
3. **Filter array** — `startsWith(item()?['subject'], '1-1')` and `item()?['isCancelled']` is false.
4. **Apply to each** filtered event:
   - **Compose — bodyText**: strip tags well enough to test for emptiness: `replace(replace(replace(replace(item()?['body'], '<br>', ' '), '&nbsp;', ' '), '<p>', ' '), '</p>', ' ')`.
   - **Compose — agenda**: `if(contains(outputs('bodyText'), 'Agenda'), trim(last(split(outputs('bodyText'), 'Agenda'))), '')`.
   - **Condition**: `length(outputs('agenda'))` is less than 15 (the HTML wrapper after "Agenda" is a few characters; 15 means "nothing typed").
     - Yes → **Teams: Post message in a chat or channel**, Flow bot, chat with you: `Agenda for tomorrow's "@{item()?['subject']}" at @{formatDateTime(item()?['start'], 'HH:mm')} is empty. Prep it (Meeting Summariser → Prep 1-1) and paste an agenda into the invite, or cancel. @{item()?['webLink']}`
     - No → nothing.
5. Save. Test with a real empty-agenda 1-1 tomorrow.

## Where the agenda lives

Type it under a line `Agenda` in the meeting body of that occurrence (Outlook/Teams → open occurrence → edit body). Both of you can read it; only the organiser can edit the body, so if the colleague sends items, you paste them. Collaborative notes (the Loop component in Teams meetings) are co-editable but not readable by this flow — if you prefer Loop, keep the flow as a plain reminder by removing the Condition.
