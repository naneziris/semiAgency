---
mode: agent
description: "[proposal] Write proposal.md from the chosen option, then two storylines with a recommendation (gate G3 follows)"
---
Engagement: `engagements/${input:engagement}`. Agent: `@analyst`.
1. Read `state.json`. If `kind` is not `proposal`, stop: decks use `/storylines`. Use `gates.G2.chosen_option`; if missing, stop and ask the user to pass G2 first.
2. Read `discovery.md`, `options.md`, and `brand/voice.md` if present.
3. Write `proposal.md` per `.github/instructions/proposal.instructions.md`. Run `python scripts/validate.py engagements/${input:engagement}/proposal.md` and fix errors, especially traceability gaps.
4. Read `brand/components.md` and `brand/examples/*.json`. Write `storylines.md` per `.github/instructions/storylines.instructions.md`: two genuinely different tellings of THIS proposal for the audience in `state.json` (`audience`, `minutes`; `inputs/audience.md` overrides). Run validate on it.
5. Stop. Summarize: the 3 proposal claims you are least sure about (gate G3 check) and your storyline recommendation in 3 lines. Next: `python scripts/status.py <dir> --pass G3 --storyline S1|S2`.
