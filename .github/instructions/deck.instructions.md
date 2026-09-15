---
applyTo: "engagements/**/deck.json"
---
# deck.json rules
- Only `kind` values listed in `brand/components.md`. Only the `fields` tags that component lists.
- A slide may instead be `{"clone": "inputs/<file>.pptx#<n>", "refs": [...]}` to keep an existing finished slide verbatim (same corporate master only; `validate.py` checks). Use it only for slides that already have complete content, never for title-only slides.
- String fields: one line. List fields: bullets; prefix `  - ` for level-2.
- Respect each component's stated capacity (max bullets, max chars per tag) from `brand/components.md`.
- Every content slide has `"refs"` with the ids it covers: N/O ids for proposals, K/F ids for `deck`-kind engagements. Title and section slides may omit refs.
- Slide count: within the range `brand/examples/` shows for the target duration in `meta.minutes`.
- `meta.storyline` must equal `state.json` `gates.G3.chosen_storyline`, and the slide sequence must follow that storyline's `Slide outline` table in `storylines.md` (same order, same kinds; titles may be polished, refs may be extended but not dropped).
