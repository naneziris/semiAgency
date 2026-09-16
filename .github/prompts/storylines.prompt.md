---
mode: agent
description: "[deck] Two storylines + recommendation for a non-proposal deck (gate G3 follows)"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Agent: `@analyst`.
1. Read `state.json`. If `kind` is not `deck`, stop: proposals use `/proposal`. If `gates.G1.passed` is false, stop and ask the user to verify `content.md` first.
2. Read `content.md`, `brand/components.md`, `brand/examples/*.json`, `brand/voice.md` if present, and `inputs/audience.md` if it exists (it overrides the one-line `audience` in state.json).
3. If `normalized/manifest.json` lists a `.pptx` input (a draft deck), S1 MUST be "evolve the draft" (its slide order kept, re-framed for the audience, listing slides to drop or merge) and S2 MUST be "re-sequence" (the order this audience needs). Otherwise choose two contrasting tellings freely. Write `storylines.md` per `.github/instructions/storylines.instructions.md`; the Coverage list references every K id and the F ids each slide carries.
4. Run `python scripts/validate.py <dir>/storylines.md`.
5. Stop. Give your recommendation in 3 lines. Next: `python scripts/status.py --pass` (it asks S1 or S2).
