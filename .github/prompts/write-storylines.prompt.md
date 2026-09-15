---
mode: agent
description: Two storylines + recommendation for a non-proposal deck (kind = deck)
---
Engagement: `engagements/${input:engagement}`.
1. Read `state.json`. If `kind` is not `deck`, stop: proposals use `/write-proposal`. If `gates.G1.passed` is false, stop and ask the user to verify `content.md` first.
2. Read `content.md`, `brand/components.md` Read `inputs/audience.md` if it exists and treat it as the definition of the audience, overriding the one-line `audience` in state.json., `brand/examples/*.json`, `brand/voice.md` if present.
3. If `normalized/manifest.json` lists a `.pptx` input (a draft deck), S1 MUST be "evolve the draft" (its slide order kept, re-framed for the audience, listing slides to drop or merge) and S2 MUST be "re-sequence" (the order this audience needs). Otherwise choose two contrasting tellings freely. Write `storylines.md` per `.github/instructions/storylines.instructions.md`, with two tellings of the SAME key messages for the audience and duration in `state.json`; the Coverage list references K ids (all of them) and the F ids each slide carries.
4. Run `python scripts/validate.py engagements/${input:engagement}/storylines.md`.
5. Stop. Give your recommendation in 3 lines and tell the user to record it with `python scripts/status.py <dir> --pass G3 --storyline S1|S2`.
