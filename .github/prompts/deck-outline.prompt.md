---
mode: agent
description: "[proposal, deck] Chosen storyline → deck.json using only corporate components, then storyboard (gate G4 follows)"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Agent: `@analyst`.
1. Read `state.json`. If `gates.G3.passed` is false or `chosen_storyline` is null, stop: a storyline must be chosen first (gate G3). In the terminal: `python scripts/status.py --pass`, which asks S1 or S2.
2. Read `brand/components.md` (allowed kinds, tags, capacities), the chosen storyline's section in `storylines.md`, and the content source: `proposal.md` when `kind` is `proposal`, `content.md` when `kind` is `deck`.
3. Write `deck.json` per `.github/instructions/deck.instructions.md`, following the chosen storyline's slide outline exactly (order and kinds); fill fields from the content source with citations preserved as `refs` (N/O ids for proposals, K/F ids for decks), not as visible text. Set `meta.storyline`. If a draft `.pptx` is among the inputs, keep slides that are already complete with a `clone` entry rather than re-typing them.
4. Run `python scripts/validate.py <dir>/deck.json` then `python scripts/storyboard.py <dir>`.
5. Stop. Tell the user to review `storyboard.html`, then run `python scripts/build_deck.py` (builds and lints), open the result in PowerPoint (gate G4), then `python scripts/status.py --pass`.
