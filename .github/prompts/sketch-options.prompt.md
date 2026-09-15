---
mode: agent
description: Sketch 2–3 candidate solution approaches from discovery.md
---
Engagement: `engagements/${input:engagement}`.
1. Read `state.json`; if `kind` is not `proposal`, stop — options only apply to proposals. Read `discovery.md`. If any blocking Q is open, stop and say so.
2. Write `options.md` per `.github/instructions/options.instructions.md`. Make the options genuinely different in shape (e.g., minimal/rules-based vs. agentic vs. process-change-only), not three flavours of one idea. At least one option must be deliberately small.
3. Run `python scripts/validate.py engagements/${input:engagement}/options.md` and fix errors.
4. Stop. Do not recommend. List which H-priority needs each option leaves uncovered.
