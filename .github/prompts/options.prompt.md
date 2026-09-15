---
mode: agent
description: "[proposal] Sketch 2–3 genuinely different solution approaches (gate G2 follows)"
---
Engagement: `engagements/${input:engagement}`. Agent: `@analyst`.
1. Read `state.json`; if `kind` is not `proposal`, stop — options only apply to proposals. If `gates.G1.passed` is false, stop: verify facts first. Read `discovery.md`; if any blocking Q is open, stop and say so.
2. Write `options.md` per `.github/instructions/options.instructions.md`. Make the options different in shape (e.g., minimal/rules-based vs. agentic vs. process-change-only), not three flavours of one idea. At least one option deliberately small.
3. Run `python scripts/validate.py engagements/${input:engagement}/options.md` and fix errors.
4. Stop. Do not recommend. List which H-priority needs each option leaves uncovered. Next: `python scripts/status.py <dir> --pass G2 --option O<n>`.
