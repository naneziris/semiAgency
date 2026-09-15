# 2 · Meeting filing — Power Automate flow (standard connectors only)

What it does, by itself, every time a transcript lands: finds the meeting in your calendar, creates a folder `Meetings/<yyyy-MM-dd> <subject>/` (or `Meetings/1-1/<person>/<yyyy-MM-dd>/` for a recurring meeting with one other attendee), copies the transcript in, creates a OneNote page with the meeting facts and a link to the folder, and posts you a Teams message with the link. That folder is where you then drop your manual notes and attachments — no naming, the flow named it. The summary is generated later by the evening prompt (sheet 3) or on demand by the agent (sheet 4).

Connectors used: OneDrive for Business, Office 365 Outlook, SharePoint, OneNote (Business), Microsoft Teams. All standard.

## Before you build

- Library **Meetings** exists (site or OneDrive — pick one; the sheets assume a SharePoint site). Folder `1-1` inside it.
- OneNote notebook with a section **Meetings** and a section **1-1**.
- The transcript folder path in OneDrive (see README prerequisites).

## Build (Power Automate → Create → Automated cloud flow, ~45 minutes)

**1. Trigger — OneDrive for Business: When a file is created**
Folder: your transcript folder. Infer content type: yes. (If the transcript trigger arrives late or twice, add a *Delay* of 2 minutes as the first action; duplicates are handled by the "folder exists" check below.)

**2. Compose — `createdAt`**
`triggerOutputs()?['headers']['Last-Modified']` — or, simpler and reliable, `utcNow()` (the transcript is created within minutes of the meeting ending).

**3. Office 365 Outlook: Get calendar view of events (V3)**
Calendar: Calendar. Start: `addHours(outputs('createdAt'), -4)`. End: `addMinutes(outputs('createdAt'), 15)`. Order by: `end/dateTime desc`. Top: 5.

**4. Filter array** on the events: keep those with `isCancelled` false and `showAs` not `free`. Then **Compose — `event`**: `first(body('Filter_array'))` — the event that ended most recently. If the array is empty, the flow uses a fallback folder name (step 6) and continues; do not fail.

**5. Compose — facts** (one Compose each; names are used below)
- `subject`: `coalesce(outputs('event')?['subject'], 'Unfiled meeting')`
- `dateLocal`: `formatDateTime(convertTimeZone(outputs('createdAt'), 'UTC', 'W. Europe Standard Time'), 'yyyy-MM-dd')`
- `attendees`: `coalesce(outputs('event')?['requiredAttendees'], '')` — a `;`-separated string of addresses
- `attendeeCount`: `length(split(outputs('attendees'), ';'))` — note this string ends with `;`, so you and one other = 3
- `isOneOnOne`: `and(equals(outputs('event')?['isRecurring'], true), equals(outputs('attendeeCount'), 3))`
- `otherPerson`: for a 1-1, the address that is not yours: `first(filter(split(outputs('attendees'), ';'), item() != '' and item() != '<your address>'))` — Power Automate has no `filter()` on strings; do it with a *Filter array* action on `split(outputs('attendees'), ';')` with condition `item()` is not equal to your address and not equal to `''`, then `first(body('Filter_array_2'))`. Turn it into a display name with a *Get user profile (V2)* (Office 365 Users, standard) → `DisplayName`.
- `safeSubject`: `replace(replace(replace(replace(outputs('subject'), '/', '-'), '\', '-'), ':', '-'), '?', '')` — SharePoint rejects a few characters; extend as needed.
- `folderPath`: `if(outputs('isOneOnOne'), concat('1-1/', outputs('otherPersonName'), '/', outputs('dateLocal')), concat(outputs('dateLocal'), ' ', outputs('safeSubject')))`

**6. SharePoint: Create new folder**
Site: your site. Library: Meetings. Folder path: `outputs('folderPath')`. (The action succeeds if the folder exists; if your tenant returns an error on duplicates, wrap in a Scope with *Configure run after → has failed* → continue.)

**7. OneDrive for Business: Get file content** — File: the trigger's `Id`.
**8. SharePoint: Create file** — Folder path: `/Meetings/@{outputs('folderPath')}`. File name: `transcript-@{outputs('dateLocal')}.@{last(split(triggerOutputs()?['body/Name'], '.'))}`. File content: from step 7.

**9. SharePoint: Get folder metadata using path** (or *Get file metadata using path* on the created file) → gives you `Link to item` / the folder's web URL. If your connector version has no folder-link output, compose it: `concat('<site url>/Meetings/', uriComponent(outputs('folderPath')))`.

**10. OneNote (Business): Create page in a section**
Notebook: yours. Section: `if(outputs('isOneOnOne'), '1-1', 'Meetings')` — the action needs a fixed section from the dropdown, so use a *Condition* on `isOneOnOne` with one Create-page action in each branch. Page content (HTML):

```html
<html><head><title>@{outputs('dateLocal')} — @{outputs('subject')}</title></head>
<body>
<p><b>Date:</b> @{outputs('dateLocal')} &nbsp; <b>With:</b> @{outputs('attendees')}</p>
<p><b>Folder:</b> <a href="@{outputs('folderUrl')}">@{outputs('folderPath')}</a> — drop notes and attachments there</p>
<p><b>Teams recap:</b> <a href="@{outputs('event')?['webLink']}">open the meeting</a> (Recap tab has the AI notes if transcription ran)</p>
<h2>Summary</h2><p><i>generated by the evening prep prompt or the Meeting Summariser agent — paste here if you want it kept</i></p>
<h2>My actions</h2><p></p>
<h2>Open points</h2><p></p>
</body></html>
```

**11. Microsoft Teams: Post message in a chat or channel** — Post as: Flow bot. Post in: Chat with Flow bot. Recipient: you. Message: `Filed: @{outputs('folderPath')} — @{outputs('folderUrl')} . Drop your notes and attachments there. OneNote page created in @{if(outputs('isOneOnOne'),'1-1','Meetings')}.`

Save. **Test** by uploading a copy of an old transcript into the trigger folder while a matching past meeting exists in the -4h window (move a calendar copy if needed).

## Things that go wrong, in order

1. **No event found** (the transcript arrived long after the meeting, or it was someone else's meeting): folder is `<date> Unfiled meeting`. Rename it; nothing else breaks. If this is frequent, widen the -4h window.
2. **Attendee count wrong for 1-1s** because of a room or a shared mailbox in the invite: the meeting files under `Meetings/` instead of `1-1/`. Cheaper fix than expressions: name recurring 1-1s "1-1 <name>" and change `isOneOnOne` to `startsWith(outputs('subject'), '1-1')`.
3. **OneNote action fails** with a DLP or "section not found" error: remove steps 10 (the SharePoint folder is the record; the agent reads SharePoint anyway). OneNote is a convenience here, not the system of record.
4. **Transcript trigger fires before the file is complete**: add the 2-minute Delay.

## Optional second flow — "something was added"

SharePoint: *When a file is created (properties only)* in Meetings → Condition: file name does not start with `transcript-` → Teams message "Added <name> to <folder>". Useful only if you often forget which folders you've already dropped notes into. Skip it at first.
