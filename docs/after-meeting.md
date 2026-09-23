# After a meeting — do this

You just came out of a meeting. This page is the whole flow; you do not need to know which runbook you are on. Two windows in VS Code: the **terminal** and **Copilot Chat in agent mode**.

## 1. Start (2 minutes, terminal)

```
python scripts/new_engagement.py
```

It asks what you need (a proposal with options, a deck, or just a record and your actions), the subject, a folder name (Enter accepts the suggestion), and — for proposals and decks — stakeholders, audience and the length of the slot. Then it opens `inputs/` for you and waits.

Put in `inputs/`:

| file | what |
|---|---|
| `transcript.md` | the Teams transcript. If you built the Harbour Office flow (`m365/02`), it's already filed in the meeting's folder in the SharePoint *Meetings* library; download it from there. None arrived? In M365 Copilot Chat (Work): *"Reproduce the transcript of my meeting '<title>' on <date> as `[hh:mm:ss] Speaker: text` lines, in order, without summarising."* Save the answer as `inputs/transcript.md`. |
| `notes.md` | your own notes, as they are |
| documents | anything the stakeholders gave you: `.docx`, `.pptx`, `.md`. A PDF: open it in Word, save as `.docx` (the built-in PDF reader is best-effort). |

Press Enter. The script lists what it found, warns about anything it cannot read, and prints the one prompt to paste next. Never edit `inputs/` afterwards — every fact will cite these files.

For a proposal or a deck, spend 10 minutes on `inputs/audience.md` (who is in the room, what they decide, what they push back on, their words). Skipping it is the most common reason the storylines feel generic.

## 2. Let Copilot write the first artifact (Copilot Chat)

Paste the prompt the script printed — one of:

```
/discovery-synthesize engagement=<name>     proposal  -> discovery.md
/content engagement=<name>                  deck      -> content.md
/meeting-notes engagement=<name>            meeting   -> notes.md + tasks.json
```

Copilot ingests the inputs, writes the artifact with a citation on every row, validates it, and stops. It ends by telling you the 3 items it is least sure about.

## 3. Check, then pass the gate (terminal)

```
python scripts/status.py
```

It prints where you are, the checklist for the open gate, and the exact command that passes it. Do the checklist in the artifact — for the first gate that means jumping to the cited timestamps and confirming the 3 flagged items, and moving anything you cannot cite to *Unverified*. Then:

```
python scripts/status.py --pass
```

It shows the checklist once more, asks for the option or storyline when the gate needs one, and records the gate.

## 4. Repeat 2 and 3 until status says done

`status.py` always prints the next prompt to paste and the next command to run, so the loop is: paste the prompt, read what Copilot produced, run `status.py`, do the checklist, `--pass`. The gates you will meet:

| gate | proposal | deck | meeting |
|---|---|---|---|
| G1 facts — never skip | after `/discovery-synthesize` | after `/content` | – |
| G2 option — you choose one of 2–3 | after `/options` | – | – |
| G3 storyline — you pick how it is told | after `/proposal` | after `/storylines` | – |
| G4 visual — you open the real deck | after `/deck-outline` + `build_deck.py` | same | – |
| G5 tasks — nothing hits the tracker unreviewed | after `/team-tasks` | – | after `/meeting-notes` |

Two things stay manual by design: the dry run (`/speech` writes the notes and `timing.py` checks the length, but you rehearse out loud with a timer) and reading the proposal as the stakeholder would before G3.

## Coming back later

The scripts and the prompts default to the engagement you started last (`engagements/CURRENT`), so `python scripts/status.py` with nothing else tells you where you left off. Another engagement in parallel: `python scripts/new_engagement.py --use <name>` switches, or pass the name explicitly (`engagement=<name>` in a prompt, `engagements/<name>` to a script).

Blocking questions still open at G1? Do not pass it. `python scripts/followup_agenda.py` writes the agenda and an `.ics` for the follow-up; after that meeting save it as `inputs/followup-1.md`, run `/merge-followup file=inputs/followup-1.md`, check only the new rows, then pass G1.

Changed your mind about an option or a storyline? Re-pass that earlier gate; everything after it is cleared and regenerated from the file above it. Fix upstream, re-run — never patch a downstream file by hand.

Details per kind, if you want them: `docs/runbooks/proposal.md`, `deck.md`, `meeting.md`.
