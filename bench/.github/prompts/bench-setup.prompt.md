---
mode: agent
description: "Interview me for 5–10 tasks where AI recently failed me and file them as bench cases"
---
You are helping me build a personal benchmark of the models in the Copilot picker. Read `README.md` first (the section "Rules that make the numbers mean something"). Look at `cases/_example/` to see the target shape of a case.

Interview me, **one question at a time**, and write files as we go. Do not batch. Do not propose tasks yourself; the cases must be mine.

1. Ask: "Think of the last month. Which tasks did you give an AI (any tool) where the result needed heavy rework, several rounds, or you gave up and did it yourself? List as many as come to mind — one line each." Wait.
2. For each task I listed, in order, ask the four questions below, then create the case before moving to the next task:
   - The prompt, as I would type it in real life (not polished). If I would attach files, ask me to drop them into `cases/<case>/task/context/` now and wait until I say they are there; then list what you found there and reference the files by name in `prompt.md`.
   - What went wrong last time, concretely (this becomes the top of `task/notes.md` under "Why this is a bench case", with the month).
   - What I would tell an intern before handing this over: audience, house style, things that must or must not appear (`task/notes.md`).
   - Is there a version of the result I was happy with? If yes, ask me to put it in `cases/<case>/grading/gold/`.
   Case folder name: lower-case, hyphens, 2–4 words, e.g. `exec-summary-status`, `nps-dashboard`. Create `task/prompt.md`, `task/notes.md`, `task/context/` (even if empty), `grading/` (empty except `gold/` if given). **Do not write `grading/checks.md` now** — checks are written after I have seen outputs, with `/bench-feedback`.
3. Stop when I have 5–10 cases or say "enough". Then print a table: case | one-line description | context files | gold yes/no. If fewer than 5, tell me honestly that the benchmark will be noisy and suggest which of my earlier one-liners to add next.
4. End with the exact next step: "Select a model in the picker, then run `/bench-run case=<first case> model=<its id>`; repeat per model. Or `python scripts/bench_cli.py --models a,b,c` if you have the Copilot CLI."

Push back if a task is one that any model does fine (e.g. "summarise this email"): those do not discriminate between models. Ask for the harder version of it.
