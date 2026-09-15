# 3 · Evening prep — scheduled prompt

Where: Copilot Chat → schedule weekdays at 18:00. This is the "check this before my next meeting" step, done for you: for each meeting tomorrow it reads the Meetings library (filled by flow 2 plus your dropped notes), summarises the last occurrences, lists open actions and proposes an agenda. Output in the Chats list; read it at 18:05 or with the morning brief.

Adjust the two placeholders: the library name/site and your OneNote notebook name (if you want it to also read pages you wrote by hand).

```
Prepare me for tomorrow's meetings. Use my calendar for tomorrow, and the SharePoint document library "Meetings" on site "<site name>" (transcripts, my notes and attachments are filed there in folders named "<date> <subject>", and 1-1s under "1-1/<person>/<date>"). Also read my OneNote notebook "<notebook name>", sections "Meetings" and "1-1", if you can. Local time zone Europe/Zurich. Never invent decisions or actions: everything must come from a transcript, a note or a page; cite the folder or page it came from in brackets.

For each meeting on my calendar tomorrow (skip all-day events, focus blocks and events I declined), output:

## HH:MM <subject> — with <names>
- **Last time(s):** the 1–3 most recent folders/pages whose subject matches or whose attendees overlap; date and one line each. If none: "no history found".
- **Where we left it:** 3–5 bullets on what was discussed and decided, cited.
- **Open actions on me:** table | action | raised on | source |. Only explicit commitments.
- **Open actions on others:** table | who | action | raised on | source |.
- **Not yet answered:** questions raised and not settled, cited.
- **Proposed agenda:** 3–5 numbered items, their open items first, then mine. If nothing is open and there is no history: "1. Nothing carried over — consider a short check-in or cancelling."
- **Bring:** one line: which file in the folder or which mail thread to have open.

For recurring 1-1s, use only the person's 1-1 folder/section and never include health, private life or performance ratings; write "(personal topic noted on <date>)" instead.

End with "## Actions to add to To Do" — every "open action on me" above, one per line, as "action — due if stated — from <subject>".
```

## Notes

- If Copilot answers that it can't read the library, check the library is indexed (it is, for SharePoint sites you have access to; OneDrive-only libraries sometimes lag a few hours after creation) and that the site name is exact.
- For meetings with no history the section is three lines; that is correct — don't tune the prompt to pad it.
- The last section is the manual step: add what you accept to To Do. If you find you always accept everything, the prompt is doing its job.
