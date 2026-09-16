---
mode: agent
description: "[deck] Notes/docs/draft deck → content.md: key messages and facts, cited (gate G1 follows)"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Agent: `@analyst`.
0. Read `state.json`. If `kind` is `proposal`, stop: use `/discovery-synthesize`. If `meeting`, stop: use `/meeting-notes`.
1. Run `python scripts/ingest.py <dir>` and read `normalized/manifest.json`. A `.pptx` input is a draft deck: `ingest.py` gives one section per slide (`[doc:draft.pptx slide 4]`); titles become candidate key messages, slides with real content become cited facts, title-only slides land under Unverified unless another input backs them.
2. Read everything in `normalized/`, and `inputs/audience.md` if it exists (it overrides the one-line `audience`).
3. Write `content.md` per `.github/instructions/content.instructions.md`: K ids for key messages, F ids for facts and figures, each cited.
4. Run `python scripts/validate.py <dir>/content.md` and fix errors.
5. Stop. Tell the user how many K and F you found, which are Unverified, and the 3 numbers to double-check at gate G1.
