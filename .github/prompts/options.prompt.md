---
mode: agent
description: "[proposal] Sketch 2–3 genuinely different solution approaches (gate G2 follows)"
---
Engagement: `${input:engagement}`; if that is empty, use the one line in `engagements/CURRENT`. `<dir>` = `engagements/<that name>`. Agent: `@analyst`.
1. Read `state.json`; if `kind` is not `proposal`, stop — options only apply to proposals. If `gates.G1.passed` is false, stop: the facts in `discovery.md` must be checked first (gate G1); in the terminal, `python scripts/status.py` shows the checklist and the command that passes it. Read `discovery.md`; if any blocking Q is open, stop and say so, and that the next step is a follow-up meeting: in the terminal, `python scripts/followup_agenda.py` writes its agenda and invite; afterwards `/merge-followup file=inputs/followup-1.md` in Copilot Chat.
2. Write `options.md` per `.github/instructions/options.instructions.md`. Make the options different in shape (e.g., minimal/rules-based vs. agentic vs. process-change-only), not three flavours of one idea. At least one option deliberately small. Fill `**Value**` honestly: an option whose new capability is `none — efficiency only` is allowed and often right; an option that dresses up time saved as a new capability is not.
3. Run `python scripts/validate.py <dir>/options.md` and fix errors.
4. Stop. Do not recommend. List which H-priority needs each option leaves uncovered. Next, in the terminal: `python scripts/status.py --pass` (it asks which option).
