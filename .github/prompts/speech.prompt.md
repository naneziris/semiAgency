---
mode: agent
description: "[proposal, deck] Per-slide speaker notes with emphasis markup, timed"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Agent: `@analyst`.
1. Read `state.json`; if `gates.G4.passed` is false, warn (the deck may still change) but continue if the user says so. Read `deck.json`, the content source (`proposal.md` or `content.md`), `brand/voice.md`, and `inputs/audience.md` if it exists.
2. Write `speech.md` per `.github/instructions/speech.instructions.md`.
3. Run `python scripts/timing.py <dir>` and adjust until total time fits with slack. Then `python scripts/validate.py <dir>/speech.md`.
4. Stop. Tell the user: total minutes, the longest slide, which slides have no emphasis words, and to run `python scripts/build_deck.py --notes-only` (timing check, then the notes are embedded).
