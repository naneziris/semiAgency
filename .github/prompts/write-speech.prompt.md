---
mode: agent
description: Write per-slide speaker notes with emphasis markup
---
Engagement: `engagements/${input:engagement}`.
1. Read `deck.json`, `proposal.md`, `brand/voice.md`. Read `inputs/audience.md` if it exists and treat it as the definition of the audience, overriding the one-line `audience` in state.json.
2. Write `speech.md` per `.github/instructions/speech.instructions.md`.
3. Run `python scripts/timing.py engagements/${input:engagement}` and adjust until total time fits with slack. Then run `python scripts/validate.py engagements/${input:engagement}/speech.md`.
4. Tell the user: total minutes, the longest slide, and which slides have no emphasis words.
