# 1 · Daily brief — scheduled prompt (on the map: Radio Tower)

Where: Microsoft 365 Copilot Chat (app, web, Teams or Outlook) → type the prompt below → in the prompt box, choose **Schedule** (clock icon) → weekdays, 07:00, Europe/Zurich. The answer appears each morning in the **Chats** list, marked as scheduled. Up to 10 scheduled prompts per user; this is your first.

Copy from the line below to the end of the block. Keep it as one message.

```
Write my morning brief for today. Use my calendar, my inbox since yesterday 17:00, and my To Do tasks. Local time zone Europe/Zurich. Max 350 words. Never invent a deadline, an ask or a commitment: if a mail implies something without asking, say "implied". Do not paste email bodies; a gist is at most two sentences. Ignore automated system mail (build servers, ticket auto-updates, out-of-office, calendar responses).

Format exactly:

# <Weekday> <date>
One line: kind of day (meeting-heavy / focus / travel), number of meetings, hours free between 08:30 and 18:00.

## Top 3
The three things that matter most today, numbered, one line each with why now (deadline, person waiting, meeting prep). This is your judgement — state it plainly.

## Today
Timeline, one line per event: HH:MM–HH:MM title — with whom (up to 3 names, then +N) — a note if useful: no agenda in the invite body, I am organizer, tentative. Mark overlapping events with ⟂ CLASH and suggest which to move or shorten. Mark gaps of 60 minutes or more as focus slots and say what to use them for, taken from Top 3.

## Waiting on me
To Do tasks overdue or due today; then emails since yesterday 17:00 that explicitly ask me for something, one line each: who — what — stated deadline or "no date". Mark urgency high when it is due today/tomorrow or someone is blocked.

## Waiting on others
Things I asked people for in mails I sent in the last 5 working days that have no reply yet, one line each with the person.

## Prepare
For each meeting today: one line on what to bring, from recent mail threads with the attendees, or "nothing found".

## Everything else
One line: how many emails need no action, and how many I should decide on myself (list their subjects only).
```

## Variants

- **Monday.** A second scheduled prompt, Mondays only, with "since Friday 17:00" instead of "since yesterday 17:00"; set the weekday one to Tuesday–Friday.
- **Tomorrow preview.** Add "and tomorrow's first meeting" to the calendar line if you like seeing what you wake up to.

## Check the first three runs

- That "Waiting on me" only lists explicit asks; if it infers, add the sentence "If in doubt, leave it out." after the never-invent sentence.
- That To Do was actually read (it says so in the output). If Copilot answers "I can't access your tasks", remove the To Do line and keep the list in the brief's "Top 3" by hand — tenant-dependent.
- That clashes are real (a tentative event overlapping a real one is not a clash — tell it once in chat; if it persists, add "tentative events never count as clashes").
