---
mode: agent
description: Turn the approved proposal + chosen storyline into deck.json using only corporate components
---
Engagement: `engagements/${input:engagement}`.
1. Read `state.json`. If `gates.G3.passed` is false or `chosen_storyline` is null, stop and tell the user to pass G3 first.
2. Read `brand/components.md` (allowed kinds, tags, capacities), the chosen storyline's section in `storylines.md`, and the content source: `proposal.md` when `kind` is `proposal`, `content.md` when `kind` is `deck`.
3. Write `deck.json` per `.github/instructions/deck.instructions.md`, following the chosen storyline's slide outline exactly in order and kinds; fill each slide's fields from the content source with citations preserved as `refs` (N/O ids for proposals, K/F ids for decks), not as visible text. Set `meta.storyline`. If a draft `.pptx` is among the inputs, keep slides that are already complete with a `clone` entry (see deck.instructions.md) rather than re-typing them.
4. Run `python scripts/validate.py engagements/${input:engagement}/deck.json` then `python scripts/storyboard.py engagements/${input:engagement}`.
5. Stop. Tell the user to review `storyboard.html`, then run `python scripts/build_deck.py engagements/${input:engagement}` and open the result in PowerPoint (gate G4).
