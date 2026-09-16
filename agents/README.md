# Shared agents — build sheets

Standalone Agent Builder agents meant to be **shared with colleagues**, not part of an engagement flow. They don't touch this workspace, don't automate anything, and don't need OneNote, schedules or write access — which is why they survive the constraints recorded in `docs/parked.md`. Same format as `m365/`: name, description, knowledge, starter prompts, an `=== INSTRUCTIONS ===` block to paste, and what to check in the first runs.

| # | sheet | what it is | shared with | build time |
|---|---|---|---|---|
| 1 | `fit-finder.md` | takes a general AI idea someone saw and turns it into a brief for *their* team: what it would be here, what new value it creates (not just hours saved), what to build it with inside the tenant, and a two-day test | anyone in the unit | 20 min + writing the context file |

## Entry bar

An agent gets a sheet here only if someone other than Nikos is expected to use it. If after a month nobody but the author has opened it, move the sheet to `docs/parked.md` with one line on why.

## Sharing

Agent Builder → the agent → **Share** → people or the unit's group → they get it under *Agents* in Copilot Chat and in Teams. Post the link once in the team channel with the first starter prompt as the example. Updates to the instructions are live for everyone immediately; note the date of the last change at the top of the sheet.
